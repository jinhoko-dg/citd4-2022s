import psycopg2 as pg2

psql_hostname = 'localhost'
psql_dbname = 'postgres'
psql_user = 'postgres'
psql_password = 'admindxdp0516'
psql_port = 5432

# try:
# 	conn = pg2.connect(
# 		database=psql_dbname,
# 		user=psql_user,
# 		password=psql_password,
# 		host=psql_hostname,
# 		port= psql_port
# 	)
# 	conn.autocommit = True
# 	cur = conn.cursor()

# 	cur.execute('CREATE DATABASE krx')
# 	cur.execute('SELECT version()')
# 	ver = cur.fetchone()

# except Exception as e:
# 	print('db error!')
# else:
# 	print(ver)
# finally:
# 	if conn:
# 		conn.close()

psql_dbname = 'krx'

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
	
	# query = """CREATE TABLE IF NOT EXISTS prices (
	# 	time TIMESTAMP NOT NULL,
	# 	ticker VARCHAR(16) NOT NULL,
	# 	time_unit VARCHAR(8) NOT NULL,
	# 	open BIGINT NOT NULL,
	# 	high BIGINT NOT NULL,
	# 	low BIGINT NOT NULL,
	# 	close BIGINT NOT NULL,
	# 	volume BIGINT NOT NULL
	# )"""

	# query = """CREATE TABLE IF NOT EXISTS daily_trade_meta (
	# 	time TIMESTAMP NOT NULL,
	# 	ticker VARCHAR(16) NOT NULL,
	# 	trade_volume BIGINT NOT NULL,
	# 	trade_value BIGINT NOT NULL,
	# 	market_cap BIGINT NOT NULL,
	# 	total_shares BIGINT NOT NULL,
	# 	delta DOUBLE PRECISION NOT NULL
	# )"""

	# query = """CREATE TABLE IF NOT EXISTS daily_trades_per_subject (
	# 	time TIMESTAMP NOT NULL,
	# 	ticker VARCHAR(16) NOT NULL,

	# 	fiin_sell_vol BIGINT,
	# 	fiin_buy_vol BIGINT,
	# 	fiin_netbuy_vol BIGINT,
	# 	insr_sell_vol BIGINT,
	# 	insr_buy_vol BIGINT,
	# 	insr_netbuy_vol BIGINT,
	# 	intr_sell_vol BIGINT,
	# 	intr_buy_vol BIGINT,
	# 	intr_netbuy_vol BIGINT,
	# 	prfd_sell_vol BIGINT,
	# 	prfd_buy_vol BIGINT,
	# 	prfd_netbuy_vol BIGINT,
	# 	bank_sell_vol BIGINT,
	# 	bank_buy_vol BIGINT,
	# 	bank_netbuy_vol BIGINT,
	# 	etco_sell_vol BIGINT,
	# 	etco_buy_vol BIGINT,
	# 	etco_netbuy_vol BIGINT,
	# 	penf_sell_vol BIGINT,
	# 	penf_buy_vol BIGINT,
	# 	penf_netbuy_vol BIGINT,
	# 	net_orgn_sell_vol BIGINT,
	# 	net_orgn_buy_vol BIGINT,
	# 	net_orgn_netbuy_vol BIGINT,
	# 	etcc_sell_vol BIGINT,
	# 	etcc_buy_vol BIGINT,
	# 	etcc_netbuy_vol BIGINT,
	# 	indv_sell_vol BIGINT,
	# 	indv_buy_vol BIGINT,
	# 	indv_netbuy_vol BIGINT,
	# 	frgn_sell_vol BIGINT,
	# 	frgn_buy_vol BIGINT,
	# 	frgn_netbuy_vol BIGINT,
	# 	etcf_sell_vol BIGINT,
	# 	etcf_buy_vol BIGINT,
	# 	etcf_netbuy_vol BIGINT,		
	# 	net_all_sell_vol BIGINT,
	# 	net_all_buy_vol BIGINT,
	# 	net_all_netbuy_vol BIGINT,
 
	# 	fiin_sell_value BIGINT,
	# 	fiin_buy_value BIGINT,
	# 	fiin_netbuy_value BIGINT,
	# 	insr_sell_value BIGINT,
	# 	insr_buy_value BIGINT,
	# 	insr_netbuy_value BIGINT,
	# 	intr_sell_value BIGINT,
	# 	intr_buy_value BIGINT,
	# 	intr_netbuy_value BIGINT,
	# 	prfd_sell_value BIGINT,
	# 	prfd_buy_value BIGINT,
	# 	prfd_netbuy_value BIGINT,
	# 	bank_sell_value BIGINT,
	# 	bank_buy_value BIGINT,
	# 	bank_netbuy_value BIGINT,
	# 	etco_sell_value BIGINT,
	# 	etco_buy_value BIGINT,
	# 	etco_netbuy_value BIGINT,
	# 	penf_sell_value BIGINT,
	# 	penf_buy_value BIGINT,
	# 	penf_netbuy_value BIGINT,
	# 	net_orgn_sell_value BIGINT,
	# 	net_orgn_buy_value BIGINT,
	# 	net_orgn_netbuy_value BIGINT,
	# 	etcc_sell_value BIGINT,
	# 	etcc_buy_value BIGINT,
	# 	etcc_netbuy_value BIGINT,
	# 	indv_sell_value BIGINT,
	# 	indv_buy_value BIGINT,
	# 	indv_netbuy_value BIGINT,
	# 	frgn_sell_value BIGINT,
	# 	frgn_buy_value BIGINT,
	# 	frgn_netbuy_value BIGINT,
	# 	etcf_sell_value BIGINT,
	# 	etcf_buy_value BIGINT,
	# 	etcf_netbuy_value BIGINT,		
	# 	net_all_sell_value BIGINT,
	# 	net_all_buy_value BIGINT,
	# 	net_all_netbuy_value BIGINT
	# )"""

	# query = """CREATE TABLE IF NOT EXISTS daily_foreigner_hold (
	# 	time TIMESTAMP NOT NULL,
	# 	ticker VARCHAR(16) NOT NULL,
	# 	foreigner_hold_vol BIGINT NOT NULL,
	# 	foreigner_hold_rate DOUBLE PRECISION NOT NULL,
	# 	foreigner_limit_vol BIGINT NOT NULL,
	# 	foreigner_limit_consumption_rate DOUBLE PRECISION NOT NULL
	# )"""

	# query = """CREATE TABLE IF NOT EXISTS daily_short (
	# 	time TIMESTAMP NOT NULL,
	# 	ticker VARCHAR(16) NOT NULL,
	# 	short_volume BIGINT NOT NULL,
	# 	short_value BIGINT NOT NULL,
	# 	short_balance_volume BIGINT NOT NULL,
	# 	short_balance_value BIGINT NOT NULL
	# )"""

	# query = """CREATE TABLE IF NOT EXISTS daily_short (
	# 	time TIMESTAMP NOT NULL,
	# 	ticker VARCHAR(16) NOT NULL,
	# 	short_volume BIGINT NOT NULL,
	# 	short_value BIGINT NOT NULL,
	# 	short_balance_volume BIGINT NOT NULL,
	# 	short_balance_value BIGINT NOT NULL
	# )"""

	query = """CREATE TABLE IF NOT EXISTS daily_index_prices (
		time TIMESTAMP NOT NULL,
		ticker VARCHAR(16) NOT NULL,
		open REAL NOT NULL,
		high REAL NOT NULL,
		low REAL NOT NULL,
		close REAL NOT NULL,
		volume BIGINT NOT NULL,
		value BIGINT NOT NULL,
		market_cap BIGINT NOT NULL
	)"""

	# query = """CREATE TABLE IF NOT EXISTS index_meta (
	# 	ticker VARCHAR(16) NOT NULL,
	# 	base_date TIMESTAMP NOT NULL,
	# 	release_date TIMESTAMP NOT NULL,
	# 	base_price REAL NOT NULL
	# )"""

	cur.execute(query)
	result = cur.fetchone()

except Exception as e:
	print('db error!')
	print(e)
else:
	print(result)
finally:
	if conn:
		conn.close()