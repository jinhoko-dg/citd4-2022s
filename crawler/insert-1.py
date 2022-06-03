import os
import pickle
from pydoc import cli
from tqdm import tqdm
import pandas
import logging
import pprint

import psycopg2 as pg2

path = "./tmp/"

psql_hostname = 'localhost'
psql_dbname = 'krx'
psql_user = 'postgres'
psql_password = 'admindxdp0516'
psql_port = 5432


INVESTOR_MAPPING = {
	'금융투자' : 'FIIN',
	'보험' : 'INSR',
	'투신' : 'INTR',
	'사모' : 'PRFD',
	'은행' : 'BANK',
	'기타금융' : 'ETCO', 		# added later
	'연기금 등' : 'PENF' ,
	'기관합계' : 'NET_ORGN',	# SUM of organization
	'기타법인' : 'ETCC',
	'개인' : 'INDV',
	'외국인' : 'FRGN',
	'기타외국인' : 'ETCF',
	'전체' : 'NET_ALL' 			# SUM of all investors
}

DB_ERR = False
def check_db():
	try:
		conn = pg2.connect(
			database=psql_dbname,
			user=psql_user,
			password=psql_password,
			host=psql_hostname,
			port= psql_port
		)
		conn.autocommit = True
		cur = conn.cursor()
		cur.execute('SELECT version()')
		ver = cur.fetchone()

	except Exception as e:
		print('db error!')
		DB_ERR = True
	else:
		print(ver)
	finally:
		if conn:
			conn.close()
if DB_ERR:
	exit(0)

# parse files
files = []
paths = os.listdir(path)
for p in paths:
	if p.endswith('.pickle'):
		files.append(path + p)

# TODO add start and end dates and filter files by names

# TODO Debug
#files = files[:1]

# check database
check_db()
conn = pg2.connect(
			database=psql_dbname,
			user=psql_user,
			password=psql_password,
			host=psql_hostname,
			port= psql_port
		)
cur = conn.cursor()


# options
	# data[0]
options = {
	# data 0
	"INSERT_DAILY_PRICES": False,
	"INSERT_DAILY_TRADE_META": False,
	# data 1
	"INSERT_DAILY_TRADES_PER_SUBJECT": False,
	# data 2
	"INSERT_DAILY_FOREIGNER_HOLD": False,
	# data 3 4
	"INSERT_DAILY_SHORT": True,
}
print("Options to be executed ::: ")
pp = pprint.PrettyPrinter(indent=2)
pp.pprint(options)
print('\n')

print("# files to insert ::: ")
print(len(files))
print('\n')

if input("Do You Want To Continue? [y/n] ") != "y":
	print("terminating....")
	exit(0)


"""
Each commit is done / undone per file
"""
for file in tqdm(files):

	try:
		print(f"{file} : START")
		# open and get data
		with open(file, 'rb') as f:
			data = pickle.load(f)

		# get date and timestamp
		fpath = os.path.basename(file)
		fname = fpath.split('.')[0]
		assert len(fname) == 8
		date_tup = (fname[0:4],fname[4:6], fname[6:])
		timestamp_str = f"{date_tup[0]}-{date_tup[1]}-{date_tup[2]} 00:00:00"
		
		"""
		"INSERT_DAILY_PRICES"
		"INSERT_DAILY_TRADE_META"
		"""
		# insert to prices
		df = data[0]
		tick_values = []
		for row in df.iterrows():
			ticker = row[0]
			values = {}
			values['open_int'] = int(row[1]['open'])
			values['high_int'] = int(row[1]['high'])
			values['low_int'] = int(row[1]['low'])
			values['close_int'] = int(row[1]['close'])
			values['volume_int'] = int(row[1]['volume'])
			values['delta_float'] = float(row[1]['delta'])
			values['value_int'] = int(row[1]['value'])
			values['market_cap_int'] = int(row[1]['market_cap'])
			values['total_shares_int'] = int(row[1]['total_shares'])
			#print(ticker, values)
			tick_values.append( (ticker, values) )
		print(len(tick_values))
		
		# "INSERT_DAILY_PRICES"
		if options['INSERT_DAILY_PRICES']:

			# check data empty
				# all daily prices should be empty
			query_str = f"SELECT * FROM prices WHERE time = '{timestamp_str}' AND time_unit = '1d'"
			cur.execute(query_str)
			result = cur.fetchall()
			num_tups = len(result)
			assert num_tups == 0

			query_values = []
			for stock in tick_values:
				ticker, values = stock
				# insert for (time, ticker, unit=1d) to prices
				query_values.append(
					[
						timestamp_str, ticker, '1d',
						values['open_int'], values['high_int'], values['low_int'], values['close_int'], values['volume_int']
					]	
				)
			# bulk write
			query_format = """
						INSERT INTO prices
						(time, ticker, time_unit, open, high, low, close, volume)
						VALUES
						(%s, %s, %s, %s, %s, %s, %s, %s);
					"""
			cur.executemany(query_format, query_values)
				
		if options['INSERT_DAILY_TRADE_META']:

			query_values = []
			for stock in tick_values:
				ticker, values = stock
				# insert for (time, ticker) to daily_trade_meta
				query_values.append(
					[
						timestamp_str, ticker,
						values['volume_int'], values['value_int'], values['market_cap_int'], values['total_shares_int'], values['delta_float']
					]
				)
			# bulk write
			query_format = """
				INSERT INTO daily_trade_meta
				(time, ticker, trade_volume, trade_value, market_cap, total_shares, delta)
				VALUES
				(%s, %s, %s, %s, %s, %s, %s);
			"""
			cur.executemany(query_format, query_values)

		"""
		"INSERT_DAILY_TRADES_PER_SUBJECT"
		"""
		# Parse per_subject data
		dtps_data = data[1]
		subject_engkeys_sorted = sorted( [ key for key in list(INVESTOR_MAPPING.values()) ] ) # BANK, D, .... 

		if options["INSERT_DAILY_TRADES_PER_SUBJECT"]:
			
			# check data empty
				# all tickers for timestamp should be empty
			query_str = f"SELECT * FROM daily_trades_per_subject WHERE time = '{timestamp_str}'"
			cur.execute(query_str)
			result = cur.fetchall()
			num_tups = len(result)
			assert num_tups == 0
			
			query_values = []
			# ticker_values shares ticker ordering with data 0
			for idx, stock in enumerate(tick_values):
				ticker, _ = stock

				trade:dict = dtps_data[idx]
				# convert etcfin
				if '기타금융' in trade.keys():
					trade['ETCO'] = trade.pop('기타금융')
				
				fields = []
				
				for key in subject_engkeys_sorted:
					prefix = key.lower() + '_'
					if key in trade.keys():
						fields.append( trade[key]['volume_sell'] )
						fields.append( trade[key]['volume_buy'] )
						fields.append( trade[key]['volume_netbuy'] )
						fields.append( trade[key]['value_sell'] )
						fields.append( trade[key]['value_buy'] )
						fields.append( trade[key]['value_netbuy'] )
					else:
						fields.append('NULL')
						fields.append('NULL')
						fields.append('NULL')
						fields.append('NULL')
						fields.append('NULL')
						fields.append('NULL')
				
				# insert for (time, ticker) to daily_trades_per_subject
				value_tuple = [ timestamp_str, ticker ]
				for f in fields:
					value_tuple.append(f)
				query_values.append(value_tuple)

			assert len(query_values) == len(tick_values)
			# bulk insert
			assert len(subject_engkeys_sorted) == 13
			partial = ""
			for key in subject_engkeys_sorted :
				prefix = key.lower() + '_'
				partial += (prefix + 'sell_vol' + ', ')
				partial += (prefix + 'buy_vol' + ', ')
				partial += (prefix + 'netbuy_vol' + ', ')
				partial += (prefix + 'sell_value' + ', ')
				partial += (prefix + 'buy_value' + ', ')
				if key is not subject_engkeys_sorted[-1]:
					partial += (prefix + 'netbuy_value' + ', ')
				else:
					partial += (prefix + 'netbuy_value')

			# -1 for last one w.o comma, +2 for first 2 cols, and 13*6 for data cols
			query_format =	\
				"INSERT INTO daily_trades_per_subject (time, ticker, " +	\
				partial + \
				") VALUES (" + \
				("%s, "* (13*6-1+2)) + \
				"%s);"
			
			cur.executemany(query_format, query_values)

		"""
		"INSERT_DAILY_FOREIGNER_HOLD"
		"""
		df = data[2]
		if options['INSERT_DAILY_FOREIGNER_HOLD']:

			tick_values = []
			for row in df.iterrows():
				ticker = row[0]
				values = {}
				values['foreigner_hold_vol'] = int(row[1]['foreigner_hold_vol'])
				values['foreigner_hold_rate'] = float(row[1]['foreigner_hold_rate'])
				values['foreigner_limit_vol'] = int(row[1]['foreigner_limit_vol'])
				values['foreigner_limit_consumption_rate'] = float(row[1]['foreigner_limit_consumption_rate'])
				#print(ticker, values)
				tick_values.append( (ticker, values) )

			# check data empty
				# all daily prices should be empty
			query_str = f"SELECT * FROM daily_foreigner_hold WHERE time = '{timestamp_str}'"
			cur.execute(query_str)
			result = cur.fetchall()
			num_tups = len(result)
			assert num_tups == 0

			query_values = []
			for stock in tick_values:
				ticker, values = stock
				# insert for (time, ticker, unit=1d) to prices
				query_values.append(
					[
						timestamp_str, ticker,
						values['foreigner_hold_vol'], values['foreigner_hold_rate'],
						values['foreigner_limit_vol'], values['foreigner_limit_consumption_rate']
					]	
				)
			# bulk write
			query_format = """
						INSERT INTO daily_foreigner_hold
						(time, ticker, foreigner_hold_vol, foreigner_hold_rate, foreigner_limit_vol, foreigner_limit_consumption_rate)
						VALUES
						(%s, %s, %s, %s, %s, %s);
					"""
			#print( query_values, query_format)
			cur.executemany(query_format, query_values)

		"""
		"INSERT_DAILY_SHORT"
		"""
		df_trades = data[3]
		df_balances = data[4]
		if options['INSERT_DAILY_SHORT']:

			# check data empty
				# all daily prices should be empty
			query_str = f"SELECT * FROM daily_short WHERE time = '{timestamp_str}'"
			cur.execute(query_str)
			result = cur.fetchall()
			num_tups = len(result)
			assert num_tups == 0

			tick_values = {}
			query_values = []
			for mkt_idx in [0,1,2] : # kpi, kdq, knx				
				for row in df_trades[mkt_idx].iterrows():
					ticker = row[0]
					tick_values[ticker] = {}

					tick_values[ticker]['short_volume'] = int(row[1]['volume']['short'])
					tick_values[ticker]['short_value'] = int(row[1]['value']['short'])
					
				for row in df_balances[mkt_idx].iterrows():
					ticker = row[0]
					
					tick_values[ticker]['short_balance_volume'] = int(row[1]['balance'])
					tick_values[ticker]['short_balance_value'] = int(row[1]['value'])

			for ticker in tick_values.keys():
				my_data = tick_values[ticker]
				query_values.append(
					[
						timestamp_str, ticker,
						my_data['short_volume'], my_data['short_value'], my_data['short_balance_volume'], my_data['short_balance_value']
					]
				 )

			# bulk write
			query_format = """
						INSERT INTO daily_short
						(time, ticker, short_volume, short_value, short_balance_volume, short_balance_value)
						VALUES
						(%s, %s, %s, %s, %s, %s);
					"""
			#print( query_values, query_format)
			cur.executemany(query_format, query_values)

		"""
		Lastly, commit
		"""
		conn.commit()

	except pg2.DatabaseError as error:
		print(error)
		if conn:
			conn.close()
			print(f"{file} : ERROR")
			exit(1)

	print(f"{file} : DONE")




