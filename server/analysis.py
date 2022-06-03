
import enum
from re import M
from graph import *
from model import *

def determineFundamental(v):
	# TODO UPDATE
	for T in [IndexVertex]:
		if isinstance(v, T):
			return '1'
	for T in [TickerVertex]:
		if isinstance(v, T):
			return '2'
	return '0'

def isEdgeFundamental(e:Edge):
	if determineFundamental(e.src)>=1 and determineFundamental(e.dst)>=1:
		return True
	else:
		return False

def redistributeWeights(weights):
	ss = sum(weights)
	assert(ss>0)
	return [ w / ss for w in weights]

def postWeights(weights, smalls):
	smalls_cnt = sum(smalls)
	for idx, w in enumerate(weights):
		if smalls[idx]:
			weights[idx] = 0.2/smalls_cnt
	return weights

def postAnal(anals, posts):
	result = []
	for idx, anal in enumerate(anals):
		result.append( ( anal[0], (posts[idx], anal[1][1], anal[1][2])) )
	return result

"""
Design
"""
def vColorMapping(val):
	# val from -1 to +1
	red = int(255 * (val + 1) / 2.0)
	blue = 255 - red
	red_color = str(hex(red).zfill(2))[2:].zfill(2)
	blue_color = str(hex(blue).zfill(2))[2:].zfill(2)
	return '#'+red_color+'22'+blue_color

def eWidthMapping(e):
	# input 0 to 1
	var_e = e # TODO

	# from 2 to 10
	return var_e*14 + 2

def getGraphData(name, ticker, period):
	
	time = period
	s0 = TickerDataSource( (ticker, ))
	s1 = SlowStochDataSource((ticker, 5,3,3))
	s2 = SlowStochDataSource((ticker, 10,6,6))
	s3 = SlowStochDataSource((ticker, 20,12,12))
	s4 = IndexDataSource( ("1150", ))	# TODO fixed sector
	s5 = IndexDataSource( ("1001", )) # TODO 

	# construct graph
	v0 = TickerVertex(source=[s0], title=name)
	v1 = SlowStochVertex(source=[s1], title='SlowStoch(5,3,3)')
	v2 = SlowStochVertex(source=[s2], title='SlowStoch(10,6,6)')
	v3 = SlowStochVertex(source=[s3], title='SlowStoch(20,12,12)')
	v4 = MultiStochVertex( child=[v1, v2, v3], title='MultiStoch')
	
	v5 = IndexVertex(source=[s4], title='Sector of '+name)
	v6 = IndexVertex(source=[s5], title='KOSPI')

	e1 = SlowStochTickerEdge(v1, v0, 'short term stochastic')
	e2 = SlowStochTickerEdge(v2, v0, 'mid term stochastic')
	e3 = SlowStochTickerEdge(v3, v0, 'long term stochastic')
	e4 = MultiStochTickerEdge(v4, v0, 'aggregated stochastic')

	e5 = IndexTickerEdge(v5, v0, "involved sector")
	e6 = IndexIndexEdge(v6, v5, "market-sector")

	vertices = [v0, v1, v2, v3, v4, v5, v6]
	edges = [e1, e2, e3, e4, e5, e6]

	fundAnal = [] # (pr, val, nl)
	techAnal = [] # (pr, val, nl)
	fundAnalStr = "(Example) 종목이 소속된 섹터에 커플링되어 상승하고 있습니다."
	techAnalStr = ""

	"""
	Analyze and Generate NL
	"""
	# TODO analyze and refer to set of edges
	techAnal.append( (e1, e1.getAnalysis(time)) ) # priority, value, nl
	techAnal.append( (e2, e2.getAnalysis(time)) ) 
	techAnal.append( (e3, e3.getAnalysis(time)) )
	techAnal.append( (e4, e4.getAnalysis(time)) )
	
	# TODO analyze edges with multiple edges
		# handle these separately. only in edges
		# postpone this for later

	# aggregate and distribute edge priority // maintain separate analysis between technical and fundamental
		# this is core
	SMALL_THRESHOLD = 0.2
	techVals = [ t[1][0] for t in techAnal ] 
	print(techVals)
	techSmallVals = [ True if t < SMALL_THRESHOLD else False for t in techVals ]
	reTechVals = redistributeWeights(techVals)
	postTechVals = postWeights(reTechVals, techSmallVals)
	print(postTechVals)
		# update anal
	postTechAnal = postAnal(techAnal, postTechVals)	# [e, (priority, value, nl)]
	# TODO do also for fundamental

	# generate NL
	for e, tup in sorted(postTechAnal, key = lambda t: -t[1][1] ):
		nl = tup[2]
		techAnalStr += nl + ' '

	# aggregate results
	allMap = {}
	for it in postTechAnal:
		allMap[it[0]] = it[1]
	# TODO del this
	allMap[e5] = (0.1, 0, 0)
	allMap[e6] = (0.1, 0, 0)
	
	"""
	generate output format
	"""
	result = []
	# vertex
	for vid, v in enumerate(vertices):
		result.append({
			'data': {
				'id': 'v'+str(vid),
				'name': v.title,
				# style
				'bg': vColorMapping(v.getValue(period)),
				'sz': '60' if vid == 0 else '40',
				'fund': determineFundamental(v),
				'desc': v.getDescription()
			}
		})
	# childs
	childId = 0
	for vid, v in enumerate(vertices):
		if v.child:
			for cv in v.child:
				result.append({
					'data':{
						'id': 'ee'+str(childId),
						'source': 'v'+str(vertices.index(cv)),
						'target': 'v'+str(vertices.index(v)),
						# style
						'dot': '1'
					}
				})
				childId+=1
	# edges
	for eid, e in enumerate(edges):
		result.append({
			'data':{
				'id': 'e'+str(eid),
				'source': 'v'+str(vertices.index(e.src)),
				'target': 'v'+str(vertices.index(e.dst)),
				'name': e.title,
				# style
				'dot': '0',
				'width': str(eWidthMapping(allMap[e][0]))
			}
		})
	
	"""
	Give values
	"""
	vdata = {}
	for vid, v in enumerate(vertices):
		realvid = 'v'+str(vid)
		data = v.getTimeValues(100, end = time) # TODO delta = 100
		vdata[realvid] = data

	return result, (fundAnalStr, techAnalStr), vdata
