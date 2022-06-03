import json
from flask import Flask
from flask import jsonify
from flask_cors import CORS, cross_origin

from db import DB
from mapping import *
import datetime

from analysis import *

# https://hleecaster.com/flask-introduction/

app = Flask(__name__)
CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

# connect database
db = DB()
db.connect()

# set mapping
ticker_mapping = getTickerMapping()
name_mapping = getNameMapping()

# TODO change basic chart period
BASIC_CHART_PERIOD=100

def getBasicChart(ticker, period):
	q = f"""
		select * from 
			(select
				time, close, open, high, low
			from prices
			where
				ticker = '{ticker}'
				and time <= '{period}'
			order by time desc
			limit {BASIC_CHART_PERIOD}) as t
		order by time asc
	"""
	data = db.query(q)
	result = ""
	for d in data:
		tmp = ""
		for cnt, it in enumerate(d):
			if isinstance(it, datetime.datetime):
				it = it.strftime('%Y-%m-%d')

			if cnt != len(d)-1:
				tmp += '"' + str(it) + '",'
			else:
				tmp+= '"' + str(it) + '"\n'
		result += tmp
	
	return result

def getNameTicker(ticker:str):
	
	if ticker.isdigit():
		# if string
		return (ticker_mapping[ticker], ticker)
	else:
		# if string
		name = ticker
		return (name, name_mapping[ticker])

def postProcessVData(vdata):
	output = {}
	for vid in vdata.keys():
		data = vdata[vid]
		# data = [(ticker, data)]
		result = ""
		for d in data:
			tmp = ""
			for cnt, it in enumerate(d):
				if isinstance(it, datetime.datetime):
					it = it.strftime('%Y-%m-%d')
				if cnt != len(d)-1:
					tmp += '"' + str(it) + '",'
				else:
					tmp+= '"' + str(it) + '"\n'
			result += tmp
		output[vid] = result
	return output


@app.route('/query/<ticker>/<period>')
def user(ticker, period):
	# parse
	try:
		(name, ticker) = getNameTicker(ticker)
	except:
		return jsonify( {'ok': 1} )
	# check date
	if not isMarketOpen(period):
		return jsonify( {'ok': 2})

	data = {}
	# basic
	data['ok'] = 0
	data['name'] = name
	data['ticker'] = ticker
	data['date'] = period
	# ticker price data
	data['ticker-price'] = getBasicChart(ticker, period)
	data['graph-data'], data['nl'], data['node-values'] = getGraphData(name, ticker, period)
	data['node-values'] = postProcessVData(data['node-values'])

	# return
	return jsonify(data)

if __name__ == '__main__':
	app.run(debug=False, host='0.0.0.0', port=30003)