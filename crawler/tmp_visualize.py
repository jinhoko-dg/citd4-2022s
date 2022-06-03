import json
import re
import datetime
from influxdb import InfluxDBClient

# output file format

output_json = { "ohlcv": [] }

# db query

host, port = ('localhost', 8086)
client = InfluxDBClient(host=host, port=port)
client.switch_database('krx')

query_str = "select time, open, high, low, close, volume from prices where ticker = '005930' order by time"

resp = client.query(query_str)
assert resp.error == None

data = resp.raw['series'][0]['values']

def timeConvert(t: str) -> int :
	date_format = datetime.datetime.strptime(t, "%Y-%m-%dT%H:%M:%SZ")
	return int(datetime.datetime.timestamp(date_format)*1000)


for item in data:
	t,o,h,l,c,v = item
	ls = [ timeConvert(t), o,h,l,c,v ]
	output_json['ohlcv'].append(ls)


# write file
output_filename = "tmp_vis_005930.json"
with open(output_filename, 'w') as outfile:
    json.dump(output_json, outfile, indent=2)
