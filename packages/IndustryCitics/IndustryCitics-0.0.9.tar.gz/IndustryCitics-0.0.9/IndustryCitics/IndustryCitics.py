###################################################
##############   中信一级行业分析 ##################
###################################################

import pandas as pd
import numpy as np
import sqlalchemy
from sqlalchemy import create_engine
import psycopg2
import warnings
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib as mpl
from scipy.stats import rankdata
font_name = "STKaiti"
mpl.rcParams['font.family']=font_name
mpl.rcParams['font.size']=12
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

def get_industries_roe(start_day = '2001-01-01', end_day = '2050-01-01', db = db_share):
    fa_industries = pd.read_sql("""SELECT * FROM "中信行业加权ROE" WHERE
                                   "报告期" >= '{}' AND "报告期" <= '{}' """.format(start_day, end_day), con=db)
    return fa_industries    



###################################################
##############      生成报告      ##################
###################################################
def generate_report():
    """
        最终报告生成:
        1. YYYY-MM-DD-
    """
    fig = plt.figure(figsize = (20,60))
    # fig = plt.subplots(figsize = (2,5))
    ax1 = plt.subplot2grid((4,2),(0,0), colspan=1)
    ax2 = plt.subplot2grid((4,2),(0,1), colspan=1)
    ax3 = plt.subplot2grid((4,2),(1,0), colspan=1)
    ax4 = plt.subplot2grid((4,2),(1,1), colspan=1)
    ax5 = plt.subplot2grid((4,2),(2,0), colspan=1)
    ax6 = plt.subplot2grid((4,2),(2,1), colspan=1)
    ax7 = plt.subplot2grid((4,2),(3,0), colspan=1)
    
    # 本周及今年以来行业收益率情况
    ret_industries = get_industries_return()
    ret_industries['日期'] = pd.to_datetime(ret_industries['日期'])
    ret_industries['year'] = ret_industries['日期'].dt.year
    ret_industries['week'] = ret_industries['日期'].dt.week
    max_year = ret_industries['year'].max()
    max_week = ret_industries.loc[ret_industries['year'] == max_year,'week'].max()
    latest_date = str(ret_industries['日期'].max())[:10]
    
    ## 今年以来收益率
    data = \
    ret_industries.query("""year=={}""".format(max_year)).groupby('指数名称')\
    ['涨跌幅'].apply(lambda x: 100*(np.prod(x/100 + 1) - 1)).sort_values(ascending=False).to_frame('涨跌幅').reset_index()
    customize_barh(data, x_label='涨跌幅', y_label='指数名称', title='今年以来收益率', ax=ax1)
    
    ## 最近一周收益率
    data = \
    ret_industries.set_index(['日期','指数名称'])['涨跌幅'].unstack().sort_index()\
    .iloc[-5:].div(100).add(1).prod().sub(1).mul(100)\
    .sort_values(ascending=False).to_frame('涨跌幅').reset_index()
    customize_barh(data, x_label='涨跌幅', y_label='指数名称', title='近五个交易日收益率', ax=ax2)

    
    # 估值水平
    val = get_industries_val()
    N = 252 * 3
    val.sort_values('日期',inplace=True)

    ## 市盈率水平
    data = val.loc[val['日期'] == val['日期'].max(),['指数名称','市盈率TTM(中位数)']]\
    .sort_values('市盈率TTM(中位数)',ascending=False)
    customize_barh(data, x_label='市盈率TTM(中位数)', y_label='指数名称', title='当前市盈率TTM中位数', ax=ax3)

    ## 市净率水平
    data = val.loc[val['日期'] == val['日期'].max(),['指数名称','市净率(中位数)']]\
    .sort_values('市净率(中位数)',ascending=False)
    customize_barh(data, x_label='市净率(中位数)', y_label='指数名称', title ='当前市净率中位数', ax=ax4)

    ## 市盈率在过去三年中的百分位
    pe_percent = \
    val.set_index(['日期','指数名称'])['市盈率TTM(中位数)'].unstack()\
    .iloc[-(N+1):].rolling(N).apply(lambda x: rankdata(x)[-1]/len(x))
    current_pe = pe_percent.last('1D').transpose()
    current_pe.columns = ['市盈率TTM在过去三年中百分位']
    data = \
    current_pe.mul(100).sort_values('市盈率TTM在过去三年中百分位',ascending=False).reset_index()
    customize_barh(data, x_label='市盈率TTM在过去三年中百分位', y_label='指数名称', title='市盈率TTM在过去三年中百分位',
                   ax=ax5)

    ## 市净率在过去三年中的百分位
    pb_percent = \
    val.set_index(['日期','指数名称'])['市净率(中位数)'].unstack()\
    .iloc[-(N+1):].rolling(N).apply(lambda x: rankdata(x)[-1]/len(x))
    current_pb = pb_percent.last('1D').transpose()
    current_pb.columns = ['市净率在过去三年中百分位']
    data = \
    current_pb.mul(100).sort_values('市净率在过去三年中百分位',ascending=False).reset_index()
    customize_barh(data, x_label='市净率在过去三年中百分位', y_label='指数名称', title='市净率在过去三年中百分位', ax=ax6)

    # 最新财报加权ROE
    roe = get_industries_roe()
    data = \
    roe.groupby(['报告期','指数名称'])[['ROE','成分权重']]\
    .apply(lambda s:np.sum(s['ROE'] * s['成分权重'])/np.sum(s['成分权重']) * 100)\
    .unstack().sort_index().iloc[-1].transpose().sort_values(ascending=False)\
    .to_frame('加权ROE').reset_index()
    customize_barh(data, x_label='加权ROE', y_label='指数名称', title='最新财报加权ROE', ax=ax7)

    fig.suptitle('更新日期：' + latest_date, fontsize=26, x=0.5, y=0.9)
    plt.savefig(latest_date+'行业收益率与估值.png',dpi=256)
    plt.tight_layout()
    plt.show()
    
    # 一致预期历史变化
    index_consensus = get_industries_estimate()
    index_consensus['日期'] = pd.to_datetime(index_consensus['日期'])

    # 净利润一致预期
    print('*'* 40 + '净利润一致预期' + '*' *40)
    est_trend(index_consensus, metric_names = ['一致预期净利润(FY1)','一致预期净利润(FY2)'],
          display_name = '滑动一致预期净利润', axis_label = '净利润（亿元）', unit=1e8, prefix=latest_date)

    # ROE一致预期
    print('*'* 40 + 'ROE一致预期' + '*' *40)
    est_trend(index_consensus, metric_names = ['一致预期ROE(FY1)','一致预期ROE(FY2)'],
          display_name = '滑动一致预期ROE', axis_label = 'ROE(%)', prefix=latest_date)

def customize_barh(data, x_label, y_label, ax, title=''):
    """自定义直方图格式"""
    plots = \
    sns.barplot(x = x_label,
                y = y_label,
                data = data,
                orient = 'h',
                color = 'blue',
                alpha = 0.4,
                ax = ax)
    for bar in plots.patches:
        plots.annotate(format(bar.get_width(), '.2f'),
                       (bar.get_x() + bar.get_width(),
                        bar.get_y()+ bar.get_height()), ha='center', va='center',
                        xytext=(0, 8),
                       textcoords='offset points')
    ax.grid(axis='x')
    ax.set_ylabel(None)
    ax.set_xlabel(None)
    # ax.set_title(title, fontsize = 20)
    plt.draw()

def est_trend(index_consensus, metric_names, display_name, axis_label, prefix = '', unit=1):
    """一致预期历史变化趋势图"""
    my_dpi = 128
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
        data = \
        index_consensus_month.query("""指数名称 == '{}'""".format(ind))[['日期',display_name]]\
        .set_index('日期').div(unit).reset_index()
        sns.lineplot(data = data, x = '日期', y = display_name, ax = axes[i],
                     marker = 'o', linestyle ='--', linewidth = 2)
        axes[i].grid(axis='y')
        axes[i].set_title(ind, fontsize = 20)
        axes[i].set_xlabel('')
        axes[i].set_ylabel(axis_label)
    fig.tight_layout()
    plt.savefig(prefix+display_name+'.png',dpi = my_dpi)
    plt.show()

generate_report()