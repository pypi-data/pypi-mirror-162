###################################################
##############   中信一级行业分析 ##################
###################################################

import pandas as pd
import numpy as np
import sqlalchemy
from sqlalchemy import create_engine
import psycopg2
import warnings
warnings.filterwarnings("ignore")

db_share = create_engine('postgresql+psycopg2://postgres:cjsc@10.200.114.87/postgres')
db_share.connect()

def get_industries_val(start_day = '2001-01-01', end_day = '2050-01-01', db = db_share):
	val_industries = pd.read_sql("""SELECT * FROM "中信行业指数每日估值" WHERE
		                           "日期" >= '{}' AND "日期" <= '{}' """.format(start_day, end_day), con=db)
	return val_industries

def get_industries_return(start_day = '2001-01-01', end_day = '2050-01-01', db = db_share):
	ret_industries  = pd.read_sql("""SELECT * FROM "中信行业指数日收益率" WHERE
		                           "日期" >= '{}' AND "日期" <= '{}' """.format(start_day, end_day), con=db)
	return ret_industries

def get_industries_estimate(start_day = '2001-01-01', end_day = '2050-01-01', db = db_share):
	est_industries = pd.read_sql("""SELECT * FROM "中信行业指数一致预期" WHERE
		                           "日期" >= '{}' AND "日期" <= '{}' """.format(start_day, end_day), con = db)
	return est_industries

def get_industries_fa(start_day = '2001-01-01', end_day = '2050-01-01', db = db_share):
	fa_industries = pd.read_sql("""SELECT * FROM "中信行业指数主要财务指标" WHERE
		                           "报告期" >= '{}' AND "报告期" <= '{}' """.format(start_day, end_day), con=db)
	return fa_industries	
