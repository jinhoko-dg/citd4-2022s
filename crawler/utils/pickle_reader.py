import pickle
import pandas
import json

import sys

filename = sys.argv[1]

with open(filename, 'rb') as f:
	data = pickle.load(f)

print(data)
