import os
import pickle
from tqdm import tqdm
import pandas


INVESTOR_MAPPING = {
	'금융투자' : 'FIIN',
	'보험' : 'INSR',
	'투신' : 'INTR',
	'사모' : 'PRFD',
	'은행' : 'BANK',
	'기타금융' : 'ETCF', 		# added later
	'연기금 등' : 'PENF' ,
	'기관합계' : 'NET_ORGN',	# SUM of organization
	'기타법인' : 'ETCC',
	'개인' : 'INDV',
	'외국인' : 'FRGN',
	'기타외국인' : 'ETCF',
	'전체' : 'NET_ALL' 			# SUM of all investors
}

IM_KEY = INVESTOR_MAPPING.keys()
IM_VALUE = INVESTOR_MAPPING.values()

path = "./tmp/"

def test(f):

	# tests
	with open(f, 'rb') as f:
		data = pickle.load(f)

	def myassert( pred, msg ):
		if not pred:
			raise Exception(f"{msg}")

	myassert( len(data) == 5 , "wrong length")
	(step1_df, step2_results, step3_df, step4_1_df_3, step4_2_df_3) = data
	num_stocks = len(step1_df)
	myassert( len(step2_results) == num_stocks, "wrong 2")
	myassert( sum( [len(i) for i in step4_1_df_3]) == num_stocks, "wrong 4-1")
	myassert( sum( [len(i) for i in step4_2_df_3]) == num_stocks, "wrong 4-2")
	myassert( len(step3_df) == num_stocks, "wrong 3")
	myassert( step1_df.isna().any().sum() == 0 , "nan in 1" )
	myassert( step3_df.isna().any().sum() == 0 , "nan in 3" )
	for item in step4_1_df_3:
		myassert( item.isna().any().sum() == 0 , "nan in 4_1" )
	for item in step4_2_df_3:
		myassert( item.isna().any().sum() == 0, "nan in 4_2" )
	for stock in step2_results:
		for key in stock.keys():
			myassert( (key in IM_KEY) or (key in IM_VALUE),  "wrong key 2" )
			myassert( len(stock[key]) == 6 ,  "all values missing in 2 " )


files = []
paths = os.listdir(path)
for p in paths:
	if p.endswith('.pickle'):
		files.append(path + p)
	
errorMsg = []
for f in tqdm(files):
	try:
		test(f)
	except Exception as e:
		errorMsg.append(f"{f} : {e}")

for it in errorMsg:
	print(it)
