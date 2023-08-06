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
    val_industries['日期'] = pd.to_datetime(val_industries['日期'])
    return val_industries

def get_industries_return(start_day = '2001-01-01', end_day = '2050-01-01', db = db_share):
    ret_industries  = pd.read_sql("""SELECT * FROM "中信行业指数日收益率" WHERE
                                   "日期" >= '{}' AND "日期" <= '{}' """.format(start_day, end_day), con=db)
    ret_industries['日期'] = pd.to_datetime(ret_industries['日期'])
    return ret_industries

def get_industries_estimate(start_day = '2001-01-01', end_day = '2050-01-01', db = db_share):
    est_industries = pd.read_sql("""SELECT * FROM "中信行业指数一致预期" WHERE
                                   "日期" >= '{}' AND "日期" <= '{}' """.format(start_day, end_day), con = db)
    est_industries['日期'] = pd.to_datetime(est_industries['日期'])
    return est_industries

def get_industries_roe(start_day = '2001-01-01', end_day = '2050-01-01', db = db_share):
    roe_industries = pd.read_sql("""SELECT * FROM "中信行业加权ROE" WHERE
                                   "报告期" >= '{}' AND "报告期" <= '{}' """.format(start_day, end_day), con=db)
    roe_industries['报告期'] = pd.to_datetime(roe_industries['报告期'])
    return roe_industries    



###################################################
##############      生成报告      ##################
###################################################
def generate_report():
    """
        指标说明：
        1. 滑动一致预期指标根据 预期指标_FY1, 预期指标_FY2 加权计算得到。
        定义：M1 最近未公开年报公布月份（今年4月末或者明年4月末）
              M2 当前所处月份
              delta_M = M1 - M2
        
        如果 当前为8月，则delta_M = 明年4月 - 今年8月 = 4 + 12 - 8 = 8
        如果 当前为2月，则delta_M = 今年4月 - 今年2月 = 4 - 2 = 2
        
        滑动一致预期指标 = (delta_M) / 12 x 预期指标_FY1 + (12 - delta_M) / 12 x 预期指标_FY2
    """
    fig = plt.figure(figsize = (20,80))
    ax1 = plt.subplot2grid((7,2),(0,0), colspan=1)
    ax2 = plt.subplot2grid((7,2),(0,1), colspan=1)
    ax3 = plt.subplot2grid((7,2),(1,0), colspan=1)
    ax4 = plt.subplot2grid((7,2),(1,1), colspan=1)
    ax5 = plt.subplot2grid((7,2),(2,0), colspan=1)
    ax6 = plt.subplot2grid((7,2),(2,1), colspan=1)
    ax7 = plt.subplot2grid((7,2),(3,0), colspan=1)
    ax8 = plt.subplot2grid((7,2),(3,1), colspan=1)
    ax9 = plt.subplot2grid((7,2),(4,0), colspan=1)
    ax10= plt.subplot2grid((7,2),(4,1), colspan=1)
    ax11= plt.subplot2grid((7,2),(5,0), colspan=1)
    ax12= plt.subplot2grid((7,2),(5,1), colspan=1)
    ax13= plt.subplot2grid((7,2),(6,0), colspan=1)
    
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
    
    ## 市销率水平
    data = val.loc[val['日期'] == val['日期'].max(),['指数名称','市销率TTM(中位数)']]\
    .sort_values('市销率TTM(中位数)',ascending=False)
    customize_barh(data, x_label='市销率TTM(中位数)', y_label='指数名称', title ='当前市销率TTM中位数', ax=ax5)
    
    ## 股息率水平
    data = val.loc[val['日期'] == val['日期'].max(),['指数名称','股息率(中位数)']]\
    .sort_values('股息率(中位数)',ascending=False)
    customize_barh(data, x_label='股息率(中位数)', y_label='指数名称', title ='当前股息率中位数', ax=ax6)
    
    
    
    ## 市盈率在过去三年中的百分位
    get_percent(val,'市盈率TTM(中位数)', ax=ax7)
    
    ## 市盈率在过去三年中的百分位
    get_percent(val,'市净率(中位数)', ax=ax8)
    
    ## 市盈率在过去三年中的百分位
    get_percent(val,'市销率TTM(中位数)', ax=ax9)
    
    ## 市盈率在过去三年中的百分位
    get_percent(val,'股息率(中位数)', ax=ax10)

    ## 最新财报加权ROE
    fa_industries = get_industries_roe()
    ## 最新两个季度财报
    fa_industries =\
    fa_industries.set_index(['报告期','证券中文简称']).unstack().sort_index().tail(2).stack().reset_index()
    data = \
    fa_industries.groupby(['报告期','指数名称'])[['ROE','成分权重']]\
    .apply(lambda s:np.sum(s['ROE'] * s['成分权重'])/np.sum(s['成分权重']) * 100)\
    .unstack().sort_index().iloc[-1].transpose().sort_values(ascending=False)\
    .to_frame('加权ROE').reset_index()
    customize_barh(data, x_label='加权ROE', y_label='指数名称', title='最新财报加权ROE', ax=ax11)
    
    # 最近财报净利润TTM变化
    data = \
    fa_industries.groupby(['报告期','指数名称'])['扣非净利润TTM'].sum()\
    .unstack().sort_index().pct_change().dropna().last('1D').transpose().reset_index()
    data.columns = ['指数名称','净利润TTM环比增长']
    data = data.sort_values('净利润TTM环比增长',ascending=False)
    customize_barh(data = data, x_label='净利润TTM环比增长', y_label='指数名称',
                   title = '行业扣非净利润TTM环比变化',
                   ax = ax12)

    data = \
    fa_industries.groupby(['报告期','指数名称'])[['扣非净利润TTM']].sum().div(1e8)\
    .reset_index().sort_values('扣非净利润TTM',ascending=False)
    data['报告期'] = data['报告期'].astype('str')
    customize_barh(data, y_label='指数名称',x_label='扣非净利润TTM', hue='报告期',
                   title = '行业扣非净利润TTM总和', ax=ax13)

    fig.suptitle('更新日期：' + latest_date, fontsize=26, x=0.5, y=0.95)
    plt.savefig(latest_date+'行业收益率与估值.png',dpi=256)
    plt.tight_layout()
    plt.show()
    
    # 一致预期历史变化
    index_consensus = get_industries_estimate()
    index_consensus['日期'] = pd.to_datetime(index_consensus['日期'])

    # 净利润一致预期
    print('*'* 40 + '净利润一致预期' + '*' *40)
    est_trend(index_consensus, metric_names = ['一致预期净利润(FY1)','一致预期净利润(FY2)'],
          display_name = '滑动一致预期净利润', axis_label = '净利润（亿元）',
              unit=1e8, prefix=latest_date, suffix='(亿元)', method='pct_change')

    # ROE一致预期
    print('*'* 40 + 'ROE一致预期' + '*' *40)
    est_trend(index_consensus, metric_names = ['一致预期ROE(FY1)','一致预期ROE(FY2)'],
          display_name = '滑动一致预期ROE', axis_label = 'ROE(%)',
              prefix=latest_date)



def customize_barh(data, x_label, y_label, ax, title='', hue=None):
    """自定义直方图格式"""
    if hue is None:
        plots = \
        sns.barplot(x = x_label,
                    y = y_label,
                    data = data,
                    orient = 'h',
                    color = 'blue',
                    alpha = 0.4,
                    ax = ax)
    else:
        plots = \
        sns.barplot(x = x_label,
                    y = y_label,
                    data = data,
                    orient = 'h',
                    hue=hue,
                    alpha = 0.4,
                    palette=["C0", "C1", "C2", "k"],
                    ax = ax)        
    for bar in plots.patches:
        plots.annotate(format(bar.get_width(), '.2f'),
                       (bar.get_x() + bar.get_width(),
                        bar.get_y()+ bar.get_height()),
                       ha='left', va='bottom',
                        xytext=(0, 8),
                       textcoords='offset points')
    ax.grid(axis='x')
    ax.set_ylabel(None)
    ax.set_xlabel(None)
    ax.set_title(title, fontsize = 22)
    plt.draw()

def est_trend(index_consensus, metric_names,
              display_name, axis_label,
              prefix = '', suffix = '(%)',
              unit=1, method = 'diff'):
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

    fig = plt.figure(figsize = (20,5*17))
    axes = []
    axes.append(plt.subplot2grid((17,2),(0,0),colspan=1,rowspan=2))
    axes.append(plt.subplot2grid((17,2),(0,1),colspan=1,rowspan=2))
    
    #### 当前行业一致预期汇总
    data = \
    index_consensus_month.set_index(['日期','指数名称'])[display_name].unstack()\
    .sort_index().last('1D').stack().sort_values(ascending=False).div(unit)\
    .to_frame(display_name).reset_index().drop('日期',axis=1)
    customize_barh(data=data, x_label=display_name, y_label='指数名称',
                   title = display_name+suffix, ax = axes[0])
    
    if method == 'diff':
        data_diff = \
        index_consensus_month.set_index(['日期','指数名称'])[display_name].unstack()\
        .sort_index().div(unit).diff().iloc[[-1]].stack().sort_values(ascending=False)\
        .to_frame(display_name).reset_index().drop('日期',axis=1)
        customize_barh(data=data_diff, x_label=display_name, y_label='指数名称',
                   title = display_name+'与月初差值'+suffix, ax = axes[1])
    else:
        data_diff = \
        index_consensus_month.set_index(['日期','指数名称'])[display_name].unstack()\
        .sort_index().div(unit).pct_change().iloc[[-1]].stack().sort_values(ascending=False)\
        .to_frame(display_name).reset_index().drop('日期',axis=1)
        customize_barh(data=data_diff, x_label=display_name, y_label='指数名称',
                   title = display_name+'相对月初增长(%)', ax = axes[1])

    for i in range(2,17):
        axes.append(plt.subplot2grid((17,2),(i,0), colspan=1))
        axes.append(plt.subplot2grid((17,2),(i,1), colspan=1))
        
    for i, ind in enumerate(industries_sort):
        i += 2
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

def get_percent(data, label, N = 252*3, ax=None):
    percent = \
    data.set_index(['日期','指数名称'])[label].unstack()\
    .iloc[-(N+1):].rolling(N).apply(lambda x: rankdata(x)[-1]/len(x))
    current_percent = percent.last('1D').transpose()
    current_percent.columns = [label+'三年中百分位']
    df_plot = \
    current_percent.mul(100).sort_values(label+'三年中百分位',ascending=False).reset_index()
    if ax:
        customize_barh(df_plot,
                       x_label=label+'三年中百分位',
                       y_label='指数名称',
                       title=label+'三年中百分位',
                       ax=ax)
    return df_plot