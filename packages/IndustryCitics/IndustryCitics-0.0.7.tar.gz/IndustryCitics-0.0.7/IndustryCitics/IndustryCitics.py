###################################################
##############   中信一级行业分析 ##################
###################################################

import pandas as pd
import numpy as np
import sqlalchemy
from sqlalchemy import create_engine
import psycopg2
import warnings
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib as mpl
from scipy.stats import rankdata
font_name = "STKaiti"
mpl.rcParams['font.family']=font_name
mpl.rcParams['font.size']=30
mpl.rcParams['axes.unicode_minus']=False
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
	print('new')
	fa_industries = pd.read_sql("""SELECT * FROM "中信行业指数主要财务指标" WHERE
		                           "报告期" >= '{}' AND "报告期" <= '{}' """.format(start_day, end_day), con=db)
	return fa_industries	


def generate_report():
	val = get_industries_val()
	N = 252 * 3

	fig = plt.figure(figsize = (20,20))
	ax1 = plt.subplot2grid((2,2),(0,0), colspan=1)
	ax2 = plt.subplot2grid((2,2),(0,1), colspan=1)
	ax3 = plt.subplot2grid((2,2),(1,0), colspan=1)
	ax4 = plt.subplot2grid((2,2),(1,1), colspan=1)

	val.sort_values('日期',inplace=True)

	# 市盈率水平
	val.loc[val['日期'] == val['日期'].max(),['指数名称','市盈率TTM(中位数)']]\
	.sort_values('市盈率TTM(中位数)').set_index(['指数名称']).plot(kind = 'barh',ax=ax1)
	ax1.get_legend().remove()
	ax1.set_ylabel(None)
	ax1.grid(axis='x')
	ax1.set_title('市盈率TTM(中位数)', fontsize=18)

	# 市净率水平
	val.loc[val['日期'] == val['日期'].max(),['指数名称','市净率(中位数)']]\
	.sort_values('市净率(中位数)').set_index(['指数名称']).plot(kind = 'barh',ax=ax2)
	ax2.get_legend().remove()
	ax2.set_ylabel(None)
	ax2.grid(axis='x')
	ax2.set_title('市净率(中位数)', fontsize=18)

	# 市盈率在过去三年中的百分位
	pe_percent = \
	val.set_index(['日期','指数名称'])['市盈率TTM(中位数)'].unstack()\
	.iloc[-(N+1):].rolling(N).apply(lambda x: rankdata(x)[-1]/len(x))
	current_pe = pe_percent.last('1D').transpose()
	current_pe.columns = ['市盈率TTM在过去三年中分位数']
	current_pe.mul(100).sort_values('市盈率TTM在过去三年中分位数').plot(kind='barh',ax=ax3)
	ax3.get_legend().remove()
	ax3.set_ylabel(None)
	ax3.grid(axis='x')
	ax3.set_title('市盈率TTM在过去三年中分位数',fontsize=20)

	# 市净率在过去三年中的百分位
	pb_percent = \
	val.set_index(['日期','指数名称'])['市净率(中位数)'].unstack()\
	.iloc[-(N+1):].rolling(N).apply(lambda x: rankdata(x)[-1]/len(x))
	current_pb = pb_percent.last('1D').transpose()
	current_pb.columns = ['市净率在过去三年中分位数']
	current_pb.mul(100).sort_values('市净率在过去三年中分位数').plot(kind='barh',ax=ax4)
	ax4.get_legend().remove()
	ax4.set_ylabel(None)
	ax4.grid(axis='x')
	ax4.set_title('市净率在过去三年中分位数',fontsize=20)
	plt.savefig('行业估值情况.png',dpi=256)
	plt.show()

	
	# 一致预期历史变化
	index_consensus = get_industries_estimate()
	index_consensus['日期'] = pd.to_datetime(index_consensus['日期'])

	# 净利润一致预期
	display('*'* 40 + '净利润一致预期' + '*' *40)
	est_trend(index_consensus, metric_names = ['一致预期净利润(FY1)','一致预期净利润(FY2)'],
          display_name = '滑动一致预期净利润', axis_label = '净利润（亿元）', unit=1e8)

	# ROE一致预期
	display('*'* 40 + 'ROE一致预期' + '*' *40)
	est_trend(index_consensus, metric_names = ['一致预期ROE(FY1)','一致预期ROE(FY2)'],
          display_name = '滑动一致预期ROE', axis_label = 'ROE(%)')


def est_trend(index_consensus, metric_names, display_name, axis_label, unit=1):
    # 转换为月频率
    index_consensus.sort_values('日期',inplace=True)
    index_consensus_month = \
    index_consensus.groupby([index_consensus['日期'].dt.year,
                             index_consensus['日期'].dt.month,
                             index_consensus['指数名称']]).tail(1)

    #### 平滑化处理 以每年4月30日分界
    index_consensus_month['month'] = index_consensus_month['日期'].dt.month
    index_consensus_month['weight1'] = (16.5 - index_consensus_month['month']) % 12 / 12
    index_consensus_month['weight2'] = 1 - index_consensus_month['weight1']
    index_consensus_month[display_name] = \
    index_consensus_month[metric_names[0]] * index_consensus_month['weight1'] + \
    index_consensus_month[metric_names[1]] * index_consensus_month['weight2']
    
    industries_sort = \
    index_consensus_month[['指数名称',display_name]].groupby('指数名称').mean()\
    .sort_values(display_name,ascending=False).index.tolist()

    fig = plt.figure(figsize = (20,5*15))
    axes = []
    for i in range(0,15):
        axes.append(plt.subplot2grid((15,2),(i,0), colspan=1))
        axes.append(plt.subplot2grid((15,2),(i,1), colspan=1))
    for i, ind in enumerate(industries_sort):
        index_consensus_month.query("""指数名称 == '{}'""".format(ind))[['日期',display_name]]\
        .set_index('日期').div(unit).plot(marker = 'o', linestyle = '--', 
                                       linewidth = 1.5, ax = axes[i])
        axes[i].grid(axis='y')
        axes[i].get_legend().remove()
        axes[i].set_title(ind)
        axes[i].set_xlabel('')
        axes[i].set_ylabel(axis_label)
    fig.tight_layout()
    plt.savefig(display_name+'.png',dpi = 256)
    plt.show()