import os
import pickle
from pydoc import cli
from tqdm import tqdm
import pandas
import logging
import pprint

import psycopg2 as pg2

path = "./tmp-index/"

psql_hostname = 'localhost'
psql_dbname = 'krx'
psql_user = 'postgres'
psql_password = 'admindxdp0516'
psql_port = 5432

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

print("# files to insert ::: ")
print(len(files))
print('\n')

if input("Do You Want To Continue? [y/n] ") != "y":
	print("terminating....")
	exit(0)

for file in tqdm(files):

	try:
		# open data
		with open(file, 'rb') as f:
			data = pickle.load(f)
		
		# data = {'idx' , df }
		query_values = []
		for ticker in data.keys():
			df = data[ticker]
			for row in df.iterrows():

				date = row[0].strftime('%Y-%m-%d 00:00:00')
				query_values.append(
					[
						date, ticker, 
						float(row[1]['open']), float(row[1]['high']), float(row[1]['low']), float(row[1]['close']), int(row[1]['volume']),
						int(row[1]['value']), int(row[1]['market_cap'])
					]
				)
		
		# bulk write
		query_format = """
					INSERT INTO daily_index_prices
					(time, ticker, open, high, low, close, volume, value, market_cap)
					VALUES
					(%s, %s, %s, %s, %s, %s, %s, %s, %s);
				"""
		cur.executemany(query_format, query_values)

		"""
		Lastly, commit
		"""
		conn.commit()
			
	except pg2.DatabaseError as e:
		print(e)
		if conn:
			conn.close()
			print(f"{file} : ERROR")
			exit(1)
		
	print(f"{file} : done")