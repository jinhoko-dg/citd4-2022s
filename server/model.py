import datetime
from datetime import datetime as dt
import pandas
import psycopg2 as pg2

import math
import statistics

import matplotlib.pyplot as plt
import talib
import numpy as np


from db import DB

db = DB()
db.connect()

class DataSource:
	def __init__(self, params) -> None:
		self.params = params
		self.num_values = None
		self.T = []
		self.Y = []

	def getValue(self, time):
		return self.Y[ self.T.index(time) ]
	
	def getValues(self, delta, start=None, end=None):
		assert( delta>0 )
		if start:
			st_idx = self.T.index(start)
			return self.Y[ st_idx : st_idx+delta+1 ]
		elif end:
			en_idx = self.T.index(end)
			return self.Y[ en_idx-delta : en_idx+1 ]

	def getTimes(self, delta, start=None, end=None):
		assert( delta>0 )
		if start:
			st_idx = self.T.index(start)
			return self.T[ st_idx : st_idx+delta+1 ]
		elif end:
			en_idx = self.T.index(end)
			return self.T[ en_idx-delta : en_idx+1 ]

	def getTrend(self, time):
		raise NotImplementedError

class Vertex:
	def __init__(self, source=None, child=None, title='') -> None:
		self.title = title
		self.source = source
		self.child = child

		self.description = ""
		self.mode2 = False

	def getValue(self, time): # node value from -1 to 1, +1 means sangseung yo in
		return 0

	def getTimeValues(self, delta, start=None, end=None): # TODO need to optimize
		assert( delta>0 )
		anysource = None
		if self.child:
			anysource = self.child[0].source[0] # only works for level 1
		elif self.source:
			anysource = self.source[0]
		if start:
			st_idx = anysource.T.index(start)
			period = anysource.T[ st_idx : st_idx+delta+1 ]
		elif end:
			en_idx = anysource.T.index(end)
			period = anysource.T[ en_idx-delta : en_idx+1 ]
		
		if self.mode2:	 # TODO
			return [ (p, self.getValue2(p)) for p in period]
		else:
			return [ (p, self.getValue(p)) for p in period]

	def getDescription(self):
		return self.description

class Edge:
	def __init__(self, src:Vertex, dst:Vertex, title='') -> None:
		self.src = src
		self.dst = dst
		self.title = title

	def getAnalysis(self, time):
		# return priority, value, nl
		raise NotImplementedError

"""
FROM HERE
"""
def timeDelta(start, delta):
	# input : 2020-12-01
	st = dt.strptime(start, "%Y-%m-%d")
	delta = datetime.timedelta(days=delta)
	en = st + delta
	return en.strftime("%Y-%m-%d")

class TickerDataSource(DataSource):
	def __init__(self, params) -> None:
		super().__init__(params)
		self.q = """
			select
				time,
				close
			from prices
			where
				ticker = '{}'
				and time >= '{}' and time <= '{}'
			order by time asc
		"""
		q = self.q.format(self.params[0], '2019-01-01', '2021-12-31')
		data = db.query(q)
		for d in data:
			self.T.append( d[0].strftime('%Y-%m-%d') )
			self.Y.append( d[1] )

class SlowStochDataSource(DataSource):
	def __init__(self, params) -> None:
		super().__init__(params)
		self.q = """
			select
				time,
				high, low, close
			from prices
			where
				ticker = '{}'
				and time >= '{}' and time <= '{}'
			order by time asc
		"""
		q = self.q.format(self.params[0], '2019-01-01', '2021-12-31')
		data = db.query(q)
		t = [ d[0].strftime('%Y-%m-%d') for d in data ]
		h = np.array([ float(d[1]) for d in data ])
		l = np.array([ float(d[2]) for d in data ])	
		c = np.array([ float(d[3]) for d in data ])
		slowk = talib.STOCH(h,l,c, self.params[1],self.params[2],0,self.params[3],0)[0]
		slowk = slowk[~np.isnan(slowk)]
		loss = len(h) - len(slowk)
		self.T = t[loss:]
		self.Y = slowk.tolist()
		assert(len(self.T) == len(self.Y))

class IndexDataSource(DataSource):
	def __init__(self, params) -> None:
		super().__init__(params)
		self.q = """
			select
				time,
				close
			from daily_index_prices
			where
				ticker = '{}'
				and time >= '{}' and time <= '{}'
			order by time asc
		"""
		q = self.q.format(self.params[0], '2019-01-01', '2021-12-31')
		data = db.query(q)
		for d in data:
			self.T.append( d[0].strftime('%Y-%m-%d') )
			self.Y.append( d[1] )
		
class TickerVertex(Vertex):
	def __init__(self, source=None, child=None, title='') -> None:
		super().__init__(source, child, title)
		self.description = "종목의 가격입니다."
		self.mode2 = True

	def getValue(self, time):
		# diff between 1 week
		vals = self.source[0].getValues(5, end=time)
		before_5 = vals[0]
		now = vals[-1]
		diff_percent =  ( (now-before_5) / before_5 ) * 100.0

		# to -1 1
		if diff_percent < 0:
			return max(-1, diff_percent/10 )
		elif diff_percent > 0:
			return min(1, diff_percent/10 )
		return 0

	def getValue2(self, time):
		return self.source[0].getValue(time)

class IndexVertex(Vertex):
	def __init__(self, source=None, child=None, title='') -> None:
		super().__init__(source, child, title)
		self.description = "종목과 관련된 지표의 가격입니다."
		self.mode2 = True


	def getValue(self, time):
		# diff between 1 week
		vals = self.source[0].getValues(5, end=time)
		before_5 = vals[0]
		now = vals[-1]
		diff_percent =  ( (now-before_5) / before_5 ) * 100.0

		# to -1 1
		if diff_percent < 0:
			return max(-1, diff_percent/10 )
		elif diff_percent > 0:
			return min(1, diff_percent/10 )
		return 0
	
	def getValue2(self, time):
		return self.source[0].getValue(time)

class SlowStochVertex(Vertex):
	def __init__(self, source=None, child=None, title='') -> None:
		super().__init__(source, child, title)
		self.strMap = {
			'periodStr': ''
		}
		self.description = "주가의 모멘텀을 판단하는 기술적 자표입니다. 수치가 높을 시 주가가 과열, 낮을 시 침체했음을 의미합니다."
		if source[0].params[1] >= 5:
			self.strMap['periodStr'] = '단기적'
		if source[0].params[1] >= 10:
			self.strMap['periodStr'] = '중기적'
		if source[0].params[1] >= 20:
			self.strMap['periodStr'] = '장기적'

	def getValue(self, time):
		stochval = self.source[0].getValue(time)
		# map 100 - 0 to -1 - 1 
		# 100 is overbuy, 0 is oversell
		return (stochval / 50.0 - 1)
		
class MultiStochVertex(Vertex):
	def __init__(self, source=None, child=None, title='') -> None:
		super().__init__(source, child, title)
		self.description = "여러 시간 간격의 모멘텀을 종합적으로 판단하는 합성 지표입니다."
	
	def getValue(self, time):
		v1 = self.child[0].source[0].getValue(time) # 533
		v2 = self.child[1].source[0].getValue(time) # 1066
		v3 = self.child[2].source[0].getValue(time) # 201212

		if v1 < 20 and v2 < 20 and v3 < 20: # down
			return -1
		elif v1 > 80 and v2 > 80 and v3 > 80: # up
			return 1
		else:
			return 0
		
class SlowStochTickerEdge(Edge):
	def __init__(self, src: Vertex, dst: Vertex, title='') -> None:
		super().__init__(src, dst, title)

	def getAnalysis(self, time):
		vVal = self.src.source[0].getValue(time) # 0 to 100
		weight = abs(vVal-50) / 50.0
		
		nl = ""
		if vVal < 20:
			nl = "{}으로 침체 상태입니다.".format(self.src.strMap['periodStr'])
		if vVal >= 80:
			nl = "{}으로 과열 상태입니다.".format(self.src.strMap['periodStr'])
		# return priority, value, nl
		return (weight, self.src.getValue(time), nl)
	
class MultiStochTickerEdge(Edge):
	def __init__(self, src: Vertex, dst: Vertex, title='') -> None:
		super().__init__(src, dst, title)
	def getAnalysis(self, time):
		val = self.src.getValue(time)
		nl = ""
		weight = 0
		if val == 1:
			weight = 1.0
			nl = "전 구간에서 과열 상태이므로 매수에 유의하는 것이 좋습니다."
		elif val == -1:
			weight = 1.0
			nl = "전 구간에서 침체 상태이므로 반등의 기회가 있습니다."
		return(weight, val, nl)

class IndexTickerEdge(Edge):
	def __init__(self, src: Vertex, dst: Vertex, title='') -> None:
		super().__init__(src, dst, title)

class IndexIndexEdge(Edge):
	def __init__(self, src: Vertex, dst: Vertex, title='') -> None:
		super().__init__(src, dst, title)
	

if __name__ == "__main___":
	ds = TickerDataSource( ('005930',) )
	ssds = SlowStochDataSource( ('005930', 5,3,3) )
