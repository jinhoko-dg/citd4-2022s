import datetime
import pandas
import psycopg2 as pg2

import math
import statistics

import matplotlib.pyplot as plt
from talib.abstract import *

from db import DB

from model import *

db = DB()
db.connect()

# class Vertex:
# 	def __init__(self, type, source=None, child=None, title='') -> None:
# 		# set title
# 		self.title = title
# 		# there should be one source or child
# 		if source:
# 			# connect datasource
# 			self.source = source
# 		elif child:
# 			# get children
# 			self.source = [ c.source for c in child ]
# 		else:
# 			raise Exception("error!")
	
# class Edge:
# 	def __init__(self, src, dst, title='') -> None:
# 		pass
# 	def performAnalysis(self, time):
# 		# return direction, weight
# 		pass
# 	def getExplanation(self, time):
# 		pass


# TODO change
ticker = '035420'
sectoridx = '1150'




# vertices = []
# edges = []
# rootVertex = None

# for vertex in 
	# get recent up/down

# for edge in edges:
	# perform analysis
	# direction, weight
