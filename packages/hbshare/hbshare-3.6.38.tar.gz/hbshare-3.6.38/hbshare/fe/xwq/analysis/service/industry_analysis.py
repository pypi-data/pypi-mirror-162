# -*- coding: utf-8 -*-

from hbshare.fe.xwq.analysis.orm.fedb import FEDB
from hbshare.fe.xwq.analysis.orm.hbdb import HBDB
from hbshare.fe.xwq.analysis.service.industry_analysis_data import get_stock_info
from hbshare.fe.xwq.analysis.utils.const_var import TimeDateFormat
from hbshare.fe.xwq.analysis.utils.timedelta_utils import TimeDateUtil
from datetime import datetime
from scipy import stats
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False
sns.set_style('white', {'font.sans-serif': ['simhei', 'Arial']})
line_color_list = ['#F04950', '#6268A2', '#959595', '#333335', '#EE703F', '#7E4A9B', '#8A662C',
                   '#44488E', '#BA67E9', '#3FAEEE']
bar_color_list = ['#C94649', '#EEB2B4', '#E1777A', '#D57C56', '#E39A79', '#DB8A66', '#E5B88C',
                  '#8588B7', '#B4B6D1', '#55598D', '#628497', '#A9C6CB', '#866EA9', '#B79BC7',
                  '#7D7D7E', '#CACACA', '#A7A7A8', '#606063', '#C4C4C4', '#99999B', '#B7B7B7']
industry_theme_dic = {'银行': '大金融', '非银金融': '大金融', '房地产': '大金融',
                      '食品饮料': '消费', '家用电器': '消费', '医药生物': '消费', '社会服务': '消费', '农林牧渔': '消费', '商贸零售': '消费', '美容护理': '消费',
                      '通信': 'TMT', '计算机': 'TMT', '电子': 'TMT', '传媒': 'TMT', '国防军工': 'TMT',
                      '交通运输': '制造', '机械设备': '制造', '汽车': '制造', '纺织服饰': '制造', '轻工制造': '制造', '电力设备': '制造',
                      '钢铁': '周期', '有色金属': '周期', '建筑装饰': '周期', '建筑材料': '周期', '基础化工': '周期', '石油石化': '周期', '煤炭': '周期', '公用事业': '周期', '环保': '周期',
                      '综合': '其他'}

def get_industry_info():
    industry_info = HBDB().read_industry_info()
    industry_info = industry_info.rename(columns={'flmc': 'INDUSTRY_NAME', 'zsdm': 'INDUSTRY_ID', 'hyhfbz': 'INDUSTRY_VERSION', 'fljb': 'INDUSTRY_TYPE', 'qsrq': 'BEGIN_DATE', 'jsrq': 'END_DATE', 'sfyx': 'IS_NEW'})
    industry_info = industry_info.dropna(subset=['BEGIN_DATE'])
    industry_info['END_DATE'] = industry_info['END_DATE'].replace('', np.nan).fillna('20990101')
    industry_info['BEGIN_DATE'] = industry_info['BEGIN_DATE'].apply(lambda x: datetime.strptime(x, '%Y/%m/%d').strftime('%Y%m%d') if '/' in x else x)
    industry_info['END_DATE'] = industry_info['END_DATE'].apply(lambda x: datetime.strptime(x, '%Y/%m/%d').strftime('%Y%m%d') if '/' in x else x)
    industry_info['BEGIN_DATE'] = industry_info['BEGIN_DATE'].astype(int).astype(str)
    industry_info['END_DATE'] = industry_info['END_DATE'].astype(int).astype(str)
    industry_info['INDUSTRY_VERSION'] = industry_info['INDUSTRY_VERSION'].astype(int)
    industry_info['INDUSTRY_TYPE'] = industry_info['INDUSTRY_TYPE'].astype(int)
    industry_info['IS_NEW'] = industry_info['IS_NEW'].astype(int)
    industry_info = industry_info[industry_info['INDUSTRY_VERSION'] == 3]
    return industry_info

def get_stock_industry():
    stock_industry = HBDB().read_stock_industry()
    stock_industry.to_hdf('D:/Git/hbshare/hbshare/fe/xwq/data/industry_analysis/stock_industry.hdf', key='table', mode='w')
    stock_industry = pd.read_hdf('D:/Git/hbshare/hbshare/fe/xwq/data/industry_analysis/stock_industry.hdf', key='table')
    stock_industry = stock_industry.rename(columns={'zqdm': 'TICKER_SYMBOL', 'flmc': 'INDUSTRY_NAME', 'fldm': 'INDUSTRY_ID', 'hyhfbz': 'INDUSTRY_VERSION', 'fljb': 'INDUSTRY_TYPE', 'qsrq': 'BEGIN_DATE', 'jsrq': 'END_DATE', 'sfyx': 'IS_NEW'})
    stock_industry = stock_industry.dropna(subset=['BEGIN_DATE'])
    stock_industry['END_DATE'] = stock_industry['END_DATE'].fillna('20990101')
    stock_industry['BEGIN_DATE'] = stock_industry['BEGIN_DATE'].astype(int).astype(str)
    stock_industry['END_DATE'] = stock_industry['END_DATE'].astype(int).astype(str)
    stock_industry['INDUSTRY_VERSION'] = stock_industry['INDUSTRY_VERSION'].astype(int)
    stock_industry['INDUSTRY_TYPE'] = stock_industry['INDUSTRY_TYPE'].astype(int)
    stock_industry['IS_NEW'] = stock_industry['IS_NEW'].astype(int)
    stock_industry = stock_industry[stock_industry['INDUSTRY_VERSION'] == 2]
    stock_industry = stock_industry.loc[stock_industry['TICKER_SYMBOL'].str.len() == 6]
    stock_industry = stock_industry.loc[stock_industry['TICKER_SYMBOL'].astype(str).str.slice(0, 1).isin(['0', '3', '6'])]
    return stock_industry

class IndustryAnalysis:
    def __init__(self, file_path, start_date, end_date, last_report_date, report_date, con_date, sw_type, select_industry=[]):
        self.file_path = file_path
        self.start_date = start_date
        self.end_date = end_date
        self.sw_type = sw_type
        self.last_report_date = last_report_date
        self.report_date = report_date
        self.con_date = con_date

        if len(select_industry) == 0:
            self.industry_info = get_industry_info()
            self.industry_info = self.industry_info[self.industry_info['INDUSTRY_TYPE'] == self.sw_type]
            self.industry_info = self.industry_info[self.industry_info['IS_NEW'] == 1]
            self.industry_info = self.industry_info[['INDUSTRY_NAME', 'INDUSTRY_ID', 'BEGIN_DATE', 'END_DATE']]
            self.industry_id_name_dic = self.industry_info[['INDUSTRY_ID', 'INDUSTRY_NAME']].set_index('INDUSTRY_ID')['INDUSTRY_NAME'].to_dict()
            self.industry_name_id_dic = self.industry_info[['INDUSTRY_ID', 'INDUSTRY_NAME']].set_index('INDUSTRY_NAME')['INDUSTRY_ID'].to_dict()
            self.select_industry = self.industry_info['INDUSTRY_NAME'].unique().tolist()
        else:
            self.select_industry = select_industry

    def IndustryMarketValue(self):
        ind_mv = FEDB().read_industry_data(['REPORT_DATE', 'INDUSTRY_ID', 'INDUSTRY_NAME', 'INDUSTRY_TYPE', 'MARKET_VALUE'], 'industry_technology', self.sw_type)
        ind_mv = ind_mv[ind_mv['INDUSTRY_NAME'].isin(self.select_industry)]
        ind_mv['MARKET_VALUE'] = ind_mv['MARKET_VALUE'].apply(lambda x: round(x / 10000000000.0, 2))
        ind_mv = ind_mv.pivot(index='INDUSTRY_NAME', columns='REPORT_DATE', values='MARKET_VALUE')
        date_list = sorted(list(ind_mv.columns))[-12:]
        rank_list = list(ind_mv[max(date_list)].sort_values(ascending=False).index)
        ind_mv = ind_mv.reset_index()
        ind_mv['INDUSTRY_NAME'] = ind_mv['INDUSTRY_NAME'].astype('category')
        ind_mv['INDUSTRY_NAME'].cat.reorder_categories(rank_list, inplace=True)
        ind_mv = ind_mv.sort_values('INDUSTRY_NAME')
        ind_mv = ind_mv.set_index('INDUSTRY_NAME')[date_list]
        #####画热力图#####
        plt.figure(figsize=(12, 8))
        sns.heatmap(ind_mv, annot=True, fmt='.2f', cmap='OrRd')
        plt.xlabel('')
        plt.ylabel('行业市值（百亿）')
        plt.tight_layout()
        plt.savefig('{0}market_value_heatmap.png'.format(self.file_path))
        return

    def IndustryRet(self):
        ind_ret = FEDB().read_industry_data(['REPORT_DATE', 'INDUSTRY_ID', 'INDUSTRY_NAME', 'INDUSTRY_TYPE', 'RET'], 'industry_technology', self.sw_type)
        ind_ret = ind_ret[ind_ret['INDUSTRY_NAME'].isin(self.select_industry)]
        ind_ret['RET'] = ind_ret['RET'].apply(lambda x: round(x * 100.0, 2))
        ind_ret = ind_ret.pivot(index='INDUSTRY_NAME', columns='REPORT_DATE', values='RET')
        date_list = sorted(list(ind_ret.columns))[-12:]
        rank_list = list(ind_ret[max(date_list)].sort_values(ascending=False).index)
        ind_ret = ind_ret.reset_index()
        ind_ret['INDUSTRY_NAME'] = ind_ret['INDUSTRY_NAME'].astype('category')
        ind_ret['INDUSTRY_NAME'].cat.reorder_categories(rank_list, inplace=True)
        ind_ret = ind_ret.sort_values('INDUSTRY_NAME')
        ind_ret = ind_ret.set_index('INDUSTRY_NAME')[date_list]
        #####画热力图#####
        plt.figure(figsize=(12, 8))
        sns.heatmap(ind_ret, annot=True, fmt='.2f', cmap='OrRd')
        plt.xlabel('')
        plt.ylabel('行业季度涨跌幅（%）')
        plt.tight_layout()
        plt.savefig('{0}ret_heatmap.png'.format(self.file_path))
        return

    def IndustryTech(self):
        ind_tech = FEDB().read_industry_data(['REPORT_DATE', 'INDUSTRY_ID', 'INDUSTRY_NAME', 'INDUSTRY_TYPE', 'RET', 'VOL', 'BETA', 'ALPHA'], 'industry_technology', self.sw_type)
        ind_tech = ind_tech[ind_tech['INDUSTRY_NAME'].isin(self.select_industry)]
        ind_tech['RET'] = ind_tech['RET'].apply(lambda x: round(x * 100.0, 2))
        ind_tech['VOL'] = ind_tech['VOL'].apply(lambda x: round(x * 100.0, 2))
        ind_tech['BETA'] = ind_tech['BETA'].apply(lambda x: round(x, 2))
        ind_tech['ALPHA'] = ind_tech['ALPHA'].apply(lambda x: round(x * 100.0, 2))
        #####画热力图#####
        fig, ax = plt.subplots(2, 2, figsize=(24, 16))
        tech_list = [['RET', 'VOL'], ['BETA', 'ALPHA']]
        for i in range(2):
            for j in range(2):
                ind_item = ind_tech.pivot(index='INDUSTRY_NAME', columns='REPORT_DATE', values=tech_list[i][j])
                date_list = sorted(list(ind_item.columns))[-12:]
                rank_list = list(ind_item[max(date_list)].sort_values(ascending=False).index)
                ind_item = ind_item.reset_index()
                ind_item['INDUSTRY_NAME'] = ind_item['INDUSTRY_NAME'].astype('category')
                ind_item['INDUSTRY_NAME'].cat.reorder_categories(rank_list, inplace=True)
                ind_item = ind_item.sort_values('INDUSTRY_NAME')
                ind_item = ind_item.set_index('INDUSTRY_NAME')[date_list]
                ylabel = '涨跌幅（%）' if tech_list[i][j] == 'RET' else '波动率（%）' if tech_list[i][j] == 'VOL' else 'BETA' if tech_list[i][j] == 'BETA' else 'ALPHA（%）'
                axij = sns.heatmap(ind_item, ax=ax[i][j], annot=True, fmt='.2f', cmap='OrRd')
                axij.set_xlabel('')
                axij.set_ylabel(ylabel)
        plt.tight_layout()
        plt.savefig('{0}tech_heatmap.png'.format(self.file_path))
        return

    def IndustryNewhigh(self):
        ind_newhigh = pd.read_excel('D:/Git/hbshare/hbshare/fe/xwq/data/new_high/2022年创历史新高个股汇总.xlsx', index_col=0)
        ind_newhigh['股票代码'] = ind_newhigh['股票代码'].apply(lambda x: str(x).zfill(6))
        ind_newhigh['创新高日期'] = ind_newhigh['创新高日期'].apply(lambda x: str(x))
        stock_info = get_stock_info()[['TICKER_SYMBOL', 'SAMPLE_DATE']].rename(columns={'TICKER_SYMBOL': '股票代码', 'SAMPLE_DATE': '入选样本日期'})
        ind_newhigh = ind_newhigh.merge(stock_info, on=['股票代码'], how='inner')
        ind_newhigh = ind_newhigh[ind_newhigh['创新高日期'] >= ind_newhigh['入选样本日期']]
        ind_newhigh = ind_newhigh[(ind_newhigh['创新高日期'] > self.last_report_date) & (ind_newhigh['创新高日期'] <= self.report_date)]
        ind_newhigh = ind_newhigh.sort_values(['股票代码', '创新高日期']).drop_duplicates('股票代码', keep='first')
        ind_newhigh = ind_newhigh.reset_index().drop(['index', '入选样本日期', '创新高日期', '区间内首次创新高', '区间内收盘价最高', '收盘价格'], axis=1)
        ind_newhigh_sw1 = ind_newhigh[['申万一级行业', '股票代码']].groupby('申万一级行业').count().rename(columns={'股票代码': '创新高数量'})
        ind_newhigh_sw1['创新高数量'] = ind_newhigh_sw1['创新高数量'].astype(int)
        ind_newhigh_sw1 = ind_newhigh_sw1.reindex(self.select_industry).fillna(0)
        ind_newhigh_sw1 = ind_newhigh_sw1.reset_index().sort_values('创新高数量', ascending=False)
        #####画柱状图#####
        plt.figure(figsize=(12, 6))
        sns.barplot(x='申万一级行业', y='创新高数量', data=ind_newhigh_sw1, palette=[bar_color_list[0]])
        plt.xlabel('')
        plt.ylabel('创新高个股数量')
        plt.xticks(rotation=90)
        plt.tight_layout()
        plt.savefig('{0}new_high_bar.png'.format(self.file_path))

        fig, ax = plt.subplots(2, 2, figsize=(12, 8))
        ind_newhigh_top4 = ind_newhigh_sw1['申万一级行业'].unique().tolist()[:4]
        new_high_list = [[ind_newhigh_top4[0], ind_newhigh_top4[1]], [ind_newhigh_top4[2], ind_newhigh_top4[3]]]
        for i in range(2):
            for j in range(2):
                ind_newhigh_sw2 = ind_newhigh[ind_newhigh['申万一级行业'] == new_high_list[i][j]]
                ind_newhigh_sw2 = ind_newhigh_sw2[['申万二级行业', '股票代码']].groupby('申万二级行业').count().rename(columns={'股票代码': '创新高数量'})
                ind_newhigh_sw2['创新高数量'] = ind_newhigh_sw2['创新高数量'].astype(int)
                ind_newhigh_sw2 = ind_newhigh_sw2.reset_index().sort_values('创新高数量', ascending=False)
                ax[i][j].pie(ind_newhigh_sw2['创新高数量'].values, labels=ind_newhigh_sw2['申万二级行业'].values, autopct= '%0.2f%%', colors=line_color_list)
                ax[i][j].set_xlabel(new_high_list[i][j])
                ax[i][j].set_ylabel('')
        plt.tight_layout()
        plt.savefig('{0}new_high_pie.png'.format(self.file_path))
        return

    def IndustryVal(self):
        ind_pe = FEDB().read_industry_data(['TRADE_DATE', 'INDUSTRY_ID', 'INDUSTRY_NAME', 'INDUSTRY_TYPE', 'PE_TTM'], 'industry_daily_valuation', self.sw_type)
        ind_pe = ind_pe[ind_pe['INDUSTRY_NAME'].isin(self.select_industry)]
        ind_pe_latest = ind_pe[ind_pe['TRADE_DATE'] == ind_pe['TRADE_DATE'].max()]
        ind_pe_min = ind_pe[['INDUSTRY_NAME', 'PE_TTM']].groupby('INDUSTRY_NAME').min().reset_index().rename(columns={'PE_TTM': 'PE_TTM_MIN'})
        ind_pe_mean = ind_pe[['INDUSTRY_NAME', 'PE_TTM']].groupby('INDUSTRY_NAME').mean().reset_index().rename(columns={'PE_TTM': 'PE_TTM_MEAN'})
        ind_pe_median = ind_pe[['INDUSTRY_NAME', 'PE_TTM']].groupby('INDUSTRY_NAME').median().reset_index().rename(columns={'PE_TTM': 'PE_TTM_MEDIAN'})
        ind_pe_max = ind_pe[['INDUSTRY_NAME', 'PE_TTM']].groupby('INDUSTRY_NAME').max().reset_index().rename(columns={'PE_TTM': 'PE_TTM_MAX'})
        ind_pe_quantile = ind_pe[['INDUSTRY_NAME', 'TRADE_DATE', 'PE_TTM']].groupby('INDUSTRY_NAME').apply(lambda x: (1.0 - np.count_nonzero(x.sort_values('TRADE_DATE')['PE_TTM'].iloc[-1] <= x['PE_TTM']) / x['PE_TTM'].size) * 100.0)
        ind_pe_quantile = pd.DataFrame(ind_pe_quantile).reset_index().rename(columns={0: 'PE_TTM_QUANTILE'})
        ind_pe_disp = ind_pe_latest.merge(ind_pe_min, on=['INDUSTRY_NAME'], how='left') \
                                   .merge(ind_pe_mean, on=['INDUSTRY_NAME'], how='left') \
                                   .merge(ind_pe_median, on=['INDUSTRY_NAME'], how='left') \
                                   .merge(ind_pe_max, on=['INDUSTRY_NAME'], how='left') \
                                   .merge(ind_pe_quantile, on=['INDUSTRY_NAME'], how='left')
        ind_pe_disp = ind_pe_disp.sort_values('PE_TTM_QUANTILE')
        for col in ['PE_TTM', 'PE_TTM_QUANTILE', 'PE_TTM_MIN', 'PE_TTM_MEAN', 'PE_TTM_MEDIAN', 'PE_TTM_MAX']:
            ind_pe_disp[col] = ind_pe_disp[col].apply(lambda x: round(x, 2))
        ind_pe_disp['PE_TTM_QUANTILE'] = ind_pe_disp['PE_TTM_QUANTILE'].apply(lambda x: '{0}%'.format(x))
        ind_pe_disp = ind_pe_disp[['INDUSTRY_NAME', 'PE_TTM_QUANTILE', 'PE_TTM', 'PE_TTM_MIN', 'PE_TTM_MEAN', 'PE_TTM_MEDIAN', 'PE_TTM_MAX']]
        ind_pe_disp.columns = ['行业名称', '分位水平', 'PE_TTM', '最小值', '平均值', '中位数', '最大值']
        ind_pe_disp.to_excel('{0}pe_ttm_disp.xlsx'.format(self.file_path))
        ind_pe = ind_pe.pivot(index='TRADE_DATE', columns='INDUSTRY_NAME', values='PE_TTM').sort_index()
        ind_list = ind_pe_disp['行业名称'].unique().tolist()[::-1]
        ind_pe_list = [ind_pe[ind] for ind in ind_list]
        ind_pe_latest['INDUSTRY_NAME'] = ind_pe_latest['INDUSTRY_NAME'].astype('category')
        ind_pe_latest['INDUSTRY_NAME'].cat.reorder_categories(ind_list, inplace=True)
        ind_pe_latest = ind_pe_latest.sort_values('INDUSTRY_NAME')
        plt.figure(figsize=(12, 12))
        plt.boxplot(ind_pe_list, labels=ind_list, vert=False, flierprops={'marker': 'o', 'markersize': 1}, meanline=True, showmeans=True)
        plt.scatter(ind_pe_latest['PE_TTM'], range(1, len(ind_pe_latest) + 1), marker='o')
        plt.tight_layout()
        plt.savefig('{0}pe_ttm_box.png'.format(self.file_path))

        rank_list = [self.report_date, self.last_report_date]
        ind_pe = FEDB().read_industry_data(['REPORT_DATE', 'INDUSTRY_ID', 'INDUSTRY_NAME', 'INDUSTRY_TYPE', 'PE_TTM'], 'industry_valuation', self.sw_type)
        ind_pe = ind_pe[ind_pe['INDUSTRY_NAME'].isin(self.select_industry)]
        ind_pe = ind_pe[ind_pe['REPORT_DATE'].isin(rank_list)]
        ind_pe['PE_TTM'] = ind_pe['PE_TTM'].apply(lambda x: round(x, 2))
        ind_pe = ind_pe.sort_values(['REPORT_DATE', 'PE_TTM'], ascending=[False, False])
        ind_pe = ind_pe[['REPORT_DATE', 'INDUSTRY_NAME', 'PE_TTM']]
        ind_pe.columns = ['报告日期', '行业名称', 'PE_TTM']
        #####画柱状图#####
        plt.figure(figsize=(12, 6))
        sns.barplot(x='行业名称', y='PE_TTM', data=ind_pe, hue='报告日期', hue_order=rank_list, palette=[bar_color_list[0], bar_color_list[7]])
        plt.xlabel('')
        plt.ylabel('PE_TTM')
        plt.xticks(rotation=90)
        plt.legend(loc=1)
        plt.tight_layout()
        plt.savefig('{0}pe_ttm_bar.png'.format(self.file_path))

        rank_list = [self.report_date, self.last_report_date]
        ind_pb = FEDB().read_industry_data(['REPORT_DATE', 'INDUSTRY_ID', 'INDUSTRY_NAME', 'INDUSTRY_TYPE', 'PB_LF'], 'industry_valuation', self.sw_type)
        ind_pb = ind_pb[ind_pb['INDUSTRY_NAME'].isin(self.select_industry)]
        ind_pb = ind_pb[ind_pb['REPORT_DATE'].isin(rank_list)]
        ind_pb['PB_LF'] = ind_pb['PB_LF'].apply(lambda x: round(x, 2))
        ind_pb = ind_pb.sort_values(['REPORT_DATE', 'PB_LF'], ascending=[False, False])
        ind_pb = ind_pb[['REPORT_DATE', 'INDUSTRY_NAME', 'PB_LF']]
        ind_pb.columns = ['报告日期', '行业名称', 'PB_LF']
        #####画柱状图#####
        plt.figure(figsize=(12, 6))
        sns.barplot(x='行业名称', y='PB_LF', data=ind_pb, hue='报告日期', hue_order=rank_list, palette=[bar_color_list[0], bar_color_list[7]])
        plt.xlabel('')
        plt.ylabel('PB_LF')
        plt.xticks(rotation=90)
        plt.legend(loc=1)
        plt.tight_layout()
        plt.savefig('{0}pb_lf_bar.png'.format(self.file_path))

        ind_val = FEDB().read_industry_data(['REPORT_DATE', 'INDUSTRY_ID', 'INDUSTRY_NAME', 'INDUSTRY_TYPE', 'PE_TTM', 'PB_LF'], 'industry_valuation', self.sw_type)
        ind_val = ind_val[ind_val['INDUSTRY_NAME'].isin(self.select_industry)]
        ind_val['PE_TTM'] = ind_val['PE_TTM'].apply(lambda x: round(x, 2))
        ind_val['PB_LF'] = ind_val['PB_LF'].apply(lambda x: round(x, 2))
        #####画热力图#####
        fig, ax = plt.subplots(1, 2, figsize=(24, 8))
        val_list = ['PE_TTM', 'PB_LF']
        for i in range(2):
            ind_item = ind_val.pivot(index='INDUSTRY_NAME', columns='REPORT_DATE', values=val_list[i])
            date_list = sorted(list(ind_item.columns))[-12:]
            rank_list = list(ind_item[max(date_list)].sort_values(ascending=False).index)
            ind_item = ind_item.reset_index()
            ind_item['INDUSTRY_NAME'] = ind_item['INDUSTRY_NAME'].astype('category')
            ind_item['INDUSTRY_NAME'].cat.reorder_categories(rank_list, inplace=True)
            ind_item = ind_item.sort_values('INDUSTRY_NAME')
            ind_item = ind_item.set_index('INDUSTRY_NAME')[date_list]
            axi = sns.heatmap(ind_item, ax=ax[i], annot=True, fmt='.2f', cmap='OrRd')
            axi.set_xlabel('')
            axi.set_ylabel(val_list[i])
        plt.tight_layout()
        plt.savefig('{0}val_heatmap.png'.format(self.file_path))
        return

    def IndustryFmt(self):
        date_list = ['20191231', '20201231', '20210331', '20210630', '20210930', '20211231', '20220331']
        ind_fmt = FEDB().read_industry_data(['REPORT_DATE', 'INDUSTRY_ID', 'INDUSTRY_NAME', 'INDUSTRY_TYPE', 'NET_PROFIT_ACCUM_YOY'], 'industry_fundamental_derive', self.sw_type)
        ind_fmt = ind_fmt[ind_fmt['INDUSTRY_NAME'].isin(self.select_industry)]
        ind_fmt = ind_fmt[ind_fmt['REPORT_DATE'].isin(date_list)]
        ind_fmt = ind_fmt.pivot(index='INDUSTRY_NAME', columns='REPORT_DATE', values='NET_PROFIT_ACCUM_YOY').reset_index()
        ind_fmt['THEME'] = ind_fmt['INDUSTRY_NAME'].apply(lambda x: industry_theme_dic[x])
        ind_fmt['THEME'] = ind_fmt['THEME'].astype('category')
        ind_fmt['THEME'].cat.reorder_categories(['周期', '制造', '消费', '大金融', 'TMT', '其他'], inplace=True)
        ind_fmt = ind_fmt.sort_values(['THEME', self.report_date], ascending=[True, False])
        for date in date_list:
            ind_fmt[date] = ind_fmt[date].apply(lambda x: '{0}%'.format(round(x * 100.0, 2)))
        ind_fmt = ind_fmt[['THEME', 'INDUSTRY_NAME'] + date_list]
        ind_fmt.columns = ['主题', '行业', '2019A', '2020A', '2021Q1', '2021Q2', '2021Q3', '2021A', '2022Q1']
        ind_fmt.to_excel('{0}net_profit_accum_yoy_disp.xlsx'.format(self.file_path))

        for index_name in ['ROE_TTM', 'GROSS_INCOME_RATIO_TTM']:
            ylabel = 'ROE_TTM' if index_name == 'ROE_TTM' else '毛利率_TTM'

            rank_list = [self.report_date, self.last_report_date]
            ind_fmt = FEDB().read_industry_data(['REPORT_DATE', 'INDUSTRY_ID', 'INDUSTRY_NAME', 'INDUSTRY_TYPE', index_name], 'industry_fundamental', self.sw_type)
            ind_fmt = ind_fmt[ind_fmt['INDUSTRY_NAME'].isin(self.select_industry)]
            ind_fmt = ind_fmt[ind_fmt['REPORT_DATE'].isin(rank_list)]
            ind_fmt[index_name] = ind_fmt[index_name].apply(lambda x: round(x, 2))
            ind_fmt = ind_fmt.sort_values(['REPORT_DATE', index_name], ascending=[False, False])
            ind_fmt = ind_fmt[['REPORT_DATE', 'INDUSTRY_NAME', index_name]]
            ind_fmt.columns = ['报告日期', '行业名称', index_name]
            #####画柱状图#####
            plt.figure(figsize=(12, 6))
            sns.barplot(x='行业名称', y=index_name, data=ind_fmt, hue='报告日期', hue_order=rank_list, palette=[bar_color_list[0], bar_color_list[7]])
            plt.xlabel('')
            plt.ylabel(ylabel + '（%）')
            plt.xticks(rotation=90)
            plt.legend(loc=1)
            plt.tight_layout()
            plt.savefig('{0}{1}_bar.png'.format(self.file_path, index_name.lower()))

            industry_list = ind_fmt[ind_fmt['报告日期'] == self.report_date]['行业名称'].unique().tolist()
            mom_abs = FEDB().read_industry_data(['REPORT_DATE', 'INDUSTRY_ID', 'INDUSTRY_NAME', 'INDUSTRY_TYPE', index_name + '_MOM_ABS'], 'industry_fundamental_derive', self.sw_type)
            mom_abs = mom_abs[mom_abs['INDUSTRY_NAME'].isin(self.select_industry)]
            mom_abs = mom_abs[mom_abs['REPORT_DATE'].isin([self.report_date])]
            mom_abs[index_name + '_MOM_ABS'] = mom_abs[index_name + '_MOM_ABS'].apply(lambda x: round(x, 2))
            mom_abs['INDUSTRY_NAME'] = mom_abs['INDUSTRY_NAME'].astype('category')
            mom_abs['INDUSTRY_NAME'].cat.reorder_categories(industry_list, inplace=True)
            mom_abs = mom_abs.sort_values('INDUSTRY_NAME')
            mom_abs = mom_abs[['REPORT_DATE', 'INDUSTRY_NAME', index_name + '_MOM_ABS']]
            mom_abs.columns = ['报告日期', '行业名称', index_name + '_MOM_ABS']
            #####画柱状图#####
            plt.figure(figsize=(12, 6))
            sns.barplot(x='行业名称', y=index_name + '_MOM_ABS', data=mom_abs, palette=[bar_color_list[0]])
            plt.xlabel('')
            plt.ylabel(ylabel + '环比变化（%）')
            plt.xticks(rotation=90)
            plt.tight_layout()
            plt.savefig('{0}{1}_mom_abs_bar.png'.format(self.file_path, index_name.lower()))

            yoy = FEDB().read_industry_data(['REPORT_DATE', 'INDUSTRY_ID', 'INDUSTRY_NAME', 'INDUSTRY_TYPE', index_name + '_YOY'], 'industry_fundamental_derive', self.sw_type)
            yoy = yoy[yoy['INDUSTRY_NAME'].isin(self.select_industry)]
            yoy = yoy[yoy['REPORT_DATE'].isin(rank_list)]
            yoy[index_name + '_YOY'] = yoy[index_name + '_YOY'].apply(lambda x: round(x * 100.0, 2))
            yoy = yoy.sort_values(['REPORT_DATE', index_name + '_YOY'], ascending=[False, False])
            yoy = yoy[['REPORT_DATE', 'INDUSTRY_NAME', index_name + '_YOY']]
            yoy.columns = ['报告日期', '行业名称', index_name + '_YOY']
            #####画柱状图#####
            plt.figure(figsize=(12, 6))
            sns.barplot(x='行业名称', y=index_name + '_YOY', data=yoy, hue='报告日期', hue_order=rank_list, palette=[bar_color_list[0], bar_color_list[7]])
            plt.xlabel('')
            plt.ylabel(ylabel + '同比增速（%）')
            plt.xticks(rotation=90)
            plt.legend(loc=1)
            plt.tight_layout()
            plt.savefig('{0}{1}_yoy_bar.png'.format(self.file_path, index_name.lower()))
        return

    def IndustryCon(self):
        ind_con_sw1 = FEDB().read_industry_data(['REPORT_DATE', 'INDUSTRY_ID', 'INDUSTRY_NAME', 'INDUSTRY_TYPE', 'EXCEED_RATIO_NEW'], 'industry_consensus', self.sw_type)
        ind_con_sw1 = ind_con_sw1[ind_con_sw1['INDUSTRY_NAME'].isin(self.select_industry)]
        ind_con_sw1 = ind_con_sw1[ind_con_sw1['REPORT_DATE'] == self.con_date]
        ind_con_sw1['EXCEED_RATIO_NEW'] = ind_con_sw1['EXCEED_RATIO_NEW'].apply(lambda x: round(x * 100.0, 2))
        ind_con_sw1 = ind_con_sw1.set_index('INDUSTRY_NAME').reindex(self.select_industry).fillna(0)
        ind_con_sw1 = ind_con_sw1.reset_index().sort_values('EXCEED_RATIO_NEW', ascending=False)
        ind_con_sw1 = ind_con_sw1[['REPORT_DATE', 'INDUSTRY_NAME', 'EXCEED_RATIO_NEW']]
        ind_con_sw1.columns = ['报告日期', '行业名称', '超预期个股占比（%）']
        #####画柱状图#####
        plt.figure(figsize=(12, 6))
        sns.barplot(x='行业名称', y='超预期个股占比（%）', data=ind_con_sw1, palette=[bar_color_list[0]])
        plt.xlabel('')
        plt.ylabel('超预期个股占比（%）')
        plt.xticks(rotation=90)
        plt.tight_layout()
        plt.savefig('{0}exceed_ratio_bar.png'.format(self.file_path))

        ind_con_sw2 = FEDB().read_industry_data(['REPORT_DATE', 'INDUSTRY_ID', 'INDUSTRY_NAME', 'INDUSTRY_TYPE', 'EXCEED_RATIO_NEW'], 'industry_consensus', 2)
        stock_industry = get_stock_industry()
        stock_industry_sw1 = stock_industry[stock_industry['INDUSTRY_TYPE'] == 1].rename(columns={'INDUSTRY_NAME': 'INDUSTRY_NAME_SW1'})
        stock_industry_sw2 = stock_industry[stock_industry['INDUSTRY_TYPE'] == 2].rename(columns={'INDUSTRY_NAME': 'INDUSTRY_NAME_SW2'})
        stock_industry = stock_industry_sw1[['TICKER_SYMBOL', 'INDUSTRY_NAME_SW1']].drop_duplicates().merge(stock_industry_sw2[['TICKER_SYMBOL', 'INDUSTRY_NAME_SW2']].drop_duplicates(), on=['TICKER_SYMBOL'], how='left')
        fig, ax = plt.subplots(2, 2, figsize=(18, 12))
        ind_con_top4 = ind_con_sw1['行业名称'].unique().tolist()[:4]
        ind_con_list = [[ind_con_top4[0], ind_con_top4[1]], [ind_con_top4[2], ind_con_top4[3]]]
        for i in range(2):
            for j in range(2):
                ind_sw2 = ind_con_sw2[ind_con_sw2['INDUSTRY_NAME'].isin(stock_industry[stock_industry['INDUSTRY_NAME_SW1'] == ind_con_list[i][j]]['INDUSTRY_NAME_SW2'].unique().tolist())]
                ind_sw2 = ind_sw2[ind_sw2['REPORT_DATE'] == self.con_date]
                ind_sw2['EXCEED_RATIO_NEW'] = ind_sw2['EXCEED_RATIO_NEW'].apply(lambda x: round(x * 100.0, 2))
                ind_sw2 = ind_sw2.sort_values('EXCEED_RATIO_NEW', ascending=False)
                ind_sw2 = ind_sw2[['REPORT_DATE', 'INDUSTRY_NAME', 'EXCEED_RATIO_NEW']]
                ind_sw2.columns = ['报告日期', '行业名称', '超预期个股占比（%）']
                ax[i][j].pie(ind_sw2['超预期个股占比（%）'].values, labels=ind_sw2['行业名称'].values, autopct='%0.2f%%', colors=line_color_list)
                ax[i][j].set_xlabel(ind_con_list[i][j])
                ax[i][j].set_ylabel('')
        plt.tight_layout()
        plt.savefig('{0}exceed_ratio_pie.png'.format(self.file_path))

        index_name = 'EST_ROE_FY1'
        rank_list = [self.report_date, self.last_report_date]
        ind_con = FEDB().read_industry_data(['REPORT_DATE', 'INDUSTRY_ID', 'INDUSTRY_NAME', 'INDUSTRY_TYPE', index_name], 'industry_consensus', self.sw_type)
        ind_con = ind_con[ind_con['INDUSTRY_NAME'].isin(self.select_industry)]
        ind_con = ind_con[ind_con['REPORT_DATE'].isin(rank_list)]
        ind_con[index_name] = ind_con[index_name].apply(lambda x: round(x, 2))
        ind_con = ind_con.sort_values(['REPORT_DATE', index_name], ascending=[False, False])
        ind_con = ind_con[['REPORT_DATE', 'INDUSTRY_NAME', index_name]]
        ind_con.columns = ['报告日期', '行业名称', '一致预期ROE（%）']
        industry_list = ind_con[ind_con['报告日期'] == self.report_date]['行业名称'].unique().tolist()
        mom_abs = ind_con[ind_con['报告日期'] == self.report_date][['行业名称', '一致预期ROE（%）']].set_index('行业名称') - ind_con[ind_con['报告日期'] == self.last_report_date][['行业名称', '一致预期ROE（%）']].set_index('行业名称')
        mom_abs = pd.DataFrame(mom_abs).rename(columns={'一致预期ROE（%）': '一致预期ROE环比变化（%）'}).reset_index()
        mom_abs['行业名称'] = mom_abs['行业名称'].astype('category')
        mom_abs['行业名称'].cat.reorder_categories(industry_list, inplace=True)
        mom_abs = mom_abs.sort_values('行业名称')
        #####画柱状图#####
        plt.figure(figsize=(12, 6))
        sns.barplot(x='行业名称', y='一致预期ROE（%）', data=ind_con, hue='报告日期', hue_order=rank_list, palette=[bar_color_list[0], bar_color_list[7]])
        plt.xlabel('')
        plt.ylabel('一致预期ROE（%）')
        plt.xticks(rotation=90)
        plt.legend(loc=1)
        plt.tight_layout()
        plt.savefig('{0}{1}_bar.png'.format(self.file_path, index_name.lower()))
        plt.figure(figsize=(12, 6))
        sns.barplot(x='行业名称', y='一致预期ROE环比变化（%）', data=mom_abs, palette=[bar_color_list[0]])
        plt.xlabel('')
        plt.ylabel('一致预期ROE环比变化（%）')
        plt.xticks(rotation=90)
        plt.tight_layout()
        plt.savefig('{0}{1}_mom_abs_bar.png'.format(self.file_path, index_name.lower()))

        index_name = 'EST_ROE_YOY'
        rank_list = [self.report_date, self.last_report_date]
        ind_con = FEDB().read_industry_data(['REPORT_DATE', 'INDUSTRY_ID', 'INDUSTRY_NAME', 'INDUSTRY_TYPE', index_name], 'industry_consensus', self.sw_type)
        ind_con = ind_con[ind_con['INDUSTRY_NAME'].isin(self.select_industry)]
        ind_con = ind_con[ind_con['REPORT_DATE'].isin(rank_list)]
        ind_con[index_name] = ind_con[index_name].apply(lambda x: round(x, 2))
        ind_con = ind_con.sort_values(['REPORT_DATE', index_name], ascending=[False, False])
        ind_con = ind_con[['REPORT_DATE', 'INDUSTRY_NAME', index_name]]
        ind_con.columns = ['报告日期', '行业名称', '一致预期ROE同比增速（%）']
        #####画柱状图#####
        plt.figure(figsize=(12, 6))
        sns.barplot(x='行业名称', y='一致预期ROE同比增速（%）', data=ind_con, hue='报告日期', hue_order=rank_list, palette=[bar_color_list[0], bar_color_list[7]])
        plt.xlabel('')
        plt.ylabel('一致预期ROE同比增速（%）')
        plt.xticks(rotation=90)
        plt.legend(loc=1)
        plt.tight_layout()
        plt.savefig('{0}{1}_bar.png'.format(self.file_path, index_name.lower()))
        return

    def IndustryCrowding(self):
        rank_list = [self.report_date, self.last_report_date]
        ind_daily_crowding = FEDB().read_industry_data(['TRADE_DATE', 'INDUSTRY_ID', 'INDUSTRY_NAME', 'INDUSTRY_TYPE', 'VOL', 'TURNOVER', 'BETA'], 'industry_daily_technology', self.sw_type)
        ind_daily_crowding = ind_daily_crowding[ind_daily_crowding['INDUSTRY_NAME'].isin(self.select_industry)]
        ind_daily_crowding['VOL'] = ind_daily_crowding['VOL'].rolling(60).mean()
        ind_daily_crowding['TURNOVER'] = ind_daily_crowding['TURNOVER'].rolling(60).mean()
        ind_daily_crowding['BETA'] = ind_daily_crowding['BETA'].rolling(60).mean()
        ind_daily_crowding_date = ind_daily_crowding[ind_daily_crowding['TRADE_DATE'] <= self.report_date]
        ind_daily_vol_quantile_date = ind_daily_crowding_date[['INDUSTRY_NAME', 'TRADE_DATE', 'VOL']].groupby('INDUSTRY_NAME').apply(lambda x: stats.percentileofscore(x['VOL'], x.sort_values('TRADE_DATE')['VOL'].iloc[-1]))
        ind_daily_turnover_quantile_date = ind_daily_crowding_date[['INDUSTRY_NAME', 'TRADE_DATE', 'TURNOVER']].groupby('INDUSTRY_NAME').apply(lambda x: stats.percentileofscore(x['TURNOVER'], x.sort_values('TRADE_DATE')['TURNOVER'].iloc[-1]))
        ind_daily_beta_quantile_date = ind_daily_crowding_date[['INDUSTRY_NAME', 'TRADE_DATE', 'BETA']].groupby('INDUSTRY_NAME').apply(lambda x: stats.percentileofscore(x['BETA'], x.sort_values('TRADE_DATE')['BETA'].iloc[-1]))
        ind_crowding_date = (ind_daily_vol_quantile_date + ind_daily_turnover_quantile_date + ind_daily_beta_quantile_date) / 3.0
        ind_crowding_date = pd.DataFrame(ind_crowding_date).reset_index()
        ind_crowding_date.columns = ['行业名称', '行业拥挤度（%）']
        ind_crowding_date['报告日期'] = self.report_date
        ind_crowding_date = ind_crowding_date.sort_values('行业拥挤度（%）', ascending=False)
        industry_list = ind_crowding_date['行业名称'].unique().tolist()
        ind_daily_crowding_last_date = ind_daily_crowding[ind_daily_crowding['TRADE_DATE'] <= self.last_report_date]
        ind_daily_vol_quantile_last_date = ind_daily_crowding_last_date[['INDUSTRY_NAME', 'TRADE_DATE', 'VOL']].groupby('INDUSTRY_NAME').apply(lambda x: stats.percentileofscore(x['VOL'], x.sort_values('TRADE_DATE')['VOL'].iloc[-1]))
        ind_daily_turnover_quantile_last_date = ind_daily_crowding_last_date[['INDUSTRY_NAME', 'TRADE_DATE', 'TURNOVER']].groupby('INDUSTRY_NAME').apply(lambda x: stats.percentileofscore(x['TURNOVER'], x.sort_values('TRADE_DATE')['TURNOVER'].iloc[-1]))
        ind_daily_beta_quantile_last_date = ind_daily_crowding_last_date[['INDUSTRY_NAME', 'TRADE_DATE', 'BETA']].groupby('INDUSTRY_NAME').apply(lambda x: stats.percentileofscore(x['BETA'], x.sort_values('TRADE_DATE')['BETA'].iloc[-1]))
        ind_crowding_last_date = (ind_daily_vol_quantile_last_date + ind_daily_turnover_quantile_last_date + ind_daily_beta_quantile_last_date) / 3.0
        ind_crowding_last_date = pd.DataFrame(ind_crowding_last_date).reset_index()
        ind_crowding_last_date.columns = ['行业名称', '行业拥挤度（%）']
        ind_crowding_last_date['报告日期'] = self.last_report_date
        ind_crowding_last_date = ind_crowding_last_date.sort_values('行业拥挤度（%）', ascending=False)
        ind_crowding = pd.concat([ind_crowding_date, ind_crowding_last_date])
        ind_crowding = ind_crowding.sort_values(['报告日期', '行业拥挤度（%）'], ascending=[False, False])
        mom_abs = ind_crowding_date[['行业名称', '行业拥挤度（%）']].set_index('行业名称') - ind_crowding_last_date[['行业名称', '行业拥挤度（%）']].set_index('行业名称')
        mom_abs = pd.DataFrame(mom_abs).rename(columns={'行业拥挤度（%）': '行业拥挤度环比变化（%）'}).reset_index()
        mom_abs['行业名称'] = mom_abs['行业名称'].astype('category')
        mom_abs['行业名称'].cat.reorder_categories(industry_list, inplace=True)
        mom_abs = mom_abs.sort_values('行业名称')
        #####画柱状图#####
        plt.figure(figsize=(12, 6))
        sns.barplot(x='行业名称', y='行业拥挤度（%）', data=ind_crowding, hue='报告日期', hue_order=rank_list, palette=[bar_color_list[0], bar_color_list[7]])
        plt.xlabel('')
        plt.ylabel('行业拥挤度（%）')
        plt.xticks(rotation=90)
        plt.legend(loc=1)
        plt.tight_layout()
        plt.savefig('{0}ind_crowding_bar.png'.format(self.file_path))
        plt.figure(figsize=(12, 6))
        sns.barplot(x='行业名称', y='行业拥挤度环比变化（%）', data=mom_abs, palette=[bar_color_list[0]])
        plt.xlabel('')
        plt.ylabel('行业拥挤度环比变化（%）')
        plt.xticks(rotation=90)
        plt.tight_layout()
        plt.savefig('{0}ind_crowding_mom_abs_bar.png'.format(self.file_path))
        return

    def IndustryHolding(self):
        # 正常运行中的普通股票型、偏股混合型、灵活配置型公募基金
        fund = HBDB().read_stock_fund_info()
        fund = fund.rename(columns={'jjdm': 'FUND_CODE', 'jjmc': 'FUND_FULL_NAME', 'jjjc': 'FUND_SHORT_NAME', 'clrq': 'BEGIN_DATE', 'zzrq': 'END_DATE', 'ejfl': 'FUND_TYPE', 'kffb': 'OPEN_CLOSE'})
        fund['END_DATE'] = fund['END_DATE'].fillna(20990101)
        fund['BEGIN_DATE'] = fund['BEGIN_DATE'].astype(str)
        fund['END_DATE'] = fund['END_DATE'].astype(str)
        # 成立距计算日期满2年
        date_before = TimeDateUtil.get_previous_date_str(self.report_date, TimeDateFormat.YMD.value, TimeDateFormat.YMD.value, 730)
        fund = fund[(fund['BEGIN_DATE'] <= date_before) & (fund['END_DATE'] >= self.report_date)]
        fund = fund.sort_values(['FUND_FULL_NAME', 'FUND_CODE']).drop_duplicates('FUND_FULL_NAME')
        # 成立以来股票占基金净资产的比例均值不低于60%
        fund_gptzzjb = HBDB().read_fund_gptzzjb_given_codes(fund['FUND_CODE'].unique().tolist())
        fund_gptzzjb = fund_gptzzjb.rename(columns={'jjdm': 'FUND_CODE', 'jsrq': 'REPORT_DATE', 'gptzzjb': 'EQUITY_IN_NA'})
        fund_gptzzjb['REPORT_DATE'] = fund_gptzzjb['REPORT_DATE'].astype(str)
        fund_gptzzjb_mean = fund_gptzzjb[['FUND_CODE', 'EQUITY_IN_NA']].groupby('FUND_CODE').mean().reset_index()
        fund_gptzzjb_mean = fund_gptzzjb_mean[fund_gptzzjb_mean['EQUITY_IN_NA'] >= 60]
        fund = fund[fund['FUND_CODE'].isin(fund_gptzzjb_mean['FUND_CODE'].unique().tolist())]
        # 近2年以来股票占基金净资产的比例均不低于50%
        fund_gptzzjb = fund_gptzzjb[(fund_gptzzjb['REPORT_DATE'] >= date_before) & (fund_gptzzjb['REPORT_DATE'] <= self.report_date)]
        fund_gptzzjb_min = fund_gptzzjb[['FUND_CODE', 'EQUITY_IN_NA']].groupby('FUND_CODE').min().reset_index()
        fund_gptzzjb_min = fund_gptzzjb_min[fund_gptzzjb_min['EQUITY_IN_NA'] >= 50]
        fund = fund[fund['FUND_CODE'].isin(fund_gptzzjb_min['FUND_CODE'].unique().tolist())]
        # 基金持仓
        fund_holding = HBDB().read_fund_holding_given_codes(fund['FUND_CODE'].unique().tolist())
        fund_holding.to_hdf('D:/Git/hbshare/hbshare/fe/xwq/data/mutual_analysis/fund_holding.hdf', key='table', mode='w')
        fund_holding = pd.read_hdf('D:/Git/hbshare/hbshare/fe/xwq/data/mutual_analysis/fund_holding.hdf', key='table')
        fund_holding = fund_holding.rename(columns={'jjdm': 'FUND_CODE', 'jsrq': 'REPORT_DATE', 'zqdm': 'TICKER_SYMBOL', 'zqmc': 'SEC_SHORT_NAME', 'ccsz': 'HOLDING_MARKET_VALUE', 'ccsl': 'HOLDING_AMOUNT', 'zjbl': 'MV_IN_NA'})
        fund_holding['REPORT_DATE'] = fund_holding['REPORT_DATE'].astype(str)
        # 基金重仓
        fund_zc_holding = fund_holding.sort_values(['FUND_CODE', 'REPORT_DATE', 'MV_IN_NA'], ascending=[True, True, False]).groupby(['FUND_CODE', 'REPORT_DATE']).head(10)
        # 股票行业对应关系
        stock_industry = get_stock_industry()
        stock_industry = stock_industry[stock_industry['INDUSTRY_TYPE'] == self.sw_type]
        stock_industry = stock_industry[stock_industry['IS_NEW'] == 1]
        stock_industry = stock_industry[['INDUSTRY_NAME', 'TICKER_SYMBOL']]
        fund_zc_holding_industry = fund_zc_holding.merge(stock_industry, on=['TICKER_SYMBOL'], how='left')
        fund_zc_holding_industry = fund_zc_holding_industry[['REPORT_DATE', 'FUND_CODE', 'INDUSTRY_NAME', 'MV_IN_NA']].groupby(['REPORT_DATE', 'FUND_CODE', 'INDUSTRY_NAME']).sum().reset_index()
        fund_zc_holding_industry = fund_zc_holding_industry[['REPORT_DATE', 'INDUSTRY_NAME', 'MV_IN_NA']].groupby(['REPORT_DATE', 'INDUSTRY_NAME']).mean().reset_index()

        rank_list = [self.report_date, self.last_report_date]
        ind_holding = fund_zc_holding_industry[fund_zc_holding_industry['INDUSTRY_NAME'].isin(self.select_industry)]
        ind_holding = ind_holding[ind_holding['INDUSTRY_NAME'] != '综合']
        ind_holding = ind_holding[ind_holding['REPORT_DATE'].isin(rank_list)]
        ind_holding['MV_IN_NA'] = ind_holding['MV_IN_NA'].apply(lambda x: round(x, 2))
        ind_holding_list = []
        for date in rank_list:
            ind_holding_date = ind_holding[ind_holding['REPORT_DATE'] == date][['INDUSTRY_NAME', 'MV_IN_NA']]
            ind_holding_date = ind_holding_date.set_index('INDUSTRY_NAME').reindex(self.select_industry).fillna(0).reset_index()
            ind_holding_date['REPORT_DATE'] = date
            ind_holding_list.append(ind_holding_date)
        ind_holding = pd.concat(ind_holding_list)
        ind_holding = ind_holding.sort_values(['REPORT_DATE', 'MV_IN_NA'], ascending=[False, False])
        ind_holding = ind_holding[['INDUSTRY_NAME', 'REPORT_DATE', 'MV_IN_NA']]
        ind_holding.columns = ['行业名称', '报告日期', '持仓比例（%）']
        industry_list = ind_holding[ind_holding['报告日期'] == self.report_date]['行业名称'].unique().tolist()
        mom_abs = ind_holding[ind_holding['报告日期'] == self.report_date][['行业名称', '持仓比例（%）']].set_index('行业名称') - ind_holding[ind_holding['报告日期'] == self.last_report_date][['行业名称', '持仓比例（%）']].set_index('行业名称')
        mom_abs = pd.DataFrame(mom_abs).rename(columns={'持仓比例（%）': '持仓比例环比变化（%）'}).reset_index()
        mom_abs['行业名称'] = mom_abs['行业名称'].astype('category')
        mom_abs['行业名称'].cat.reorder_categories(industry_list, inplace=True)
        mom_abs = mom_abs.sort_values('行业名称')
        #####画柱状图#####
        plt.figure(figsize=(12, 6))
        sns.barplot(x='行业名称', y='持仓比例（%）', data=ind_holding, hue='报告日期', hue_order=rank_list, palette=[bar_color_list[0], bar_color_list[7]])
        plt.xlabel('')
        plt.ylabel('持仓比例（%）')
        plt.legend(loc=1)
        plt.xticks(rotation=90)
        plt.tight_layout()
        plt.savefig('{0}ind_holding_bar.png'.format(self.file_path))
        plt.figure(figsize=(12, 6))
        sns.barplot(x='行业名称', y='持仓比例环比变化（%）', data=mom_abs, palette=[bar_color_list[0]])
        plt.xlabel('')
        plt.ylabel('持仓比例环比变化（%）')
        plt.xticks(rotation=90)
        plt.tight_layout()
        plt.savefig('{0}ind_holding_mom_abs_bar.png'.format(self.file_path))
        return

    def get_all(self):
        self.IndustryMarketValue()
        self.IndustryRet()
        self.IndustryTech()
        self.IndustryNewhigh()
        self.IndustryVal()
        self.IndustryFmt()
        self.IndustryCon()
        self.IndustryCrowding()
        self.IndustryHolding()
        return


if __name__ == '__main__':
    file_path = 'D:/Git/hbshare/hbshare/fe/xwq/data/industry_analysis/'
    start_date = '20170101'
    end_date = '20220331'
    last_report_date = '20211231'
    report_date = '20220331'
    con_date = '20211231'
    sw_type = 1
    IndustryAnalysis(file_path, start_date, end_date, last_report_date, report_date, con_date, sw_type).get_all()
    # sw_type = 3
    # select_industry = ['钴', '锂', '铝', '锂电池', '电池化学品', '硅料硅片', '光伏电池组件', '逆变器', '航空装备', '军工电子', '电动乘用车', '车身附件及饰件', '底盘与发动机系统', '空调', '冰洗', '酒店', '白酒', '数字芯片设计', '模拟芯片设计', '半导体设备', '医疗研发外包']
    # IndustryAnalysis(file_path, start_date, end_date, last_report_date, report_date, con_date, sw_type, select_industry).get_all()