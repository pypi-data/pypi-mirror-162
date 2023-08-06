"""
tracker 用于季度回顾/半年度回顾等场景
"""
import numpy as np
import pandas as pd
import hbshare as hbs
from datetime import datetime
from hbshare.quant.Kevin.quant_room.MyUtil.data_loader import get_fund_nav_from_sql, get_trading_day_list


class FundTracker:
    def __init__(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date
        self._load_data()

    @staticmethod
    def _load_benchmark(start_date, end_date, benchmark_id):
        sql_script = "SELECT JYRQ as TRADEDATE, ZQDM, SPJG as TCLOSE from funddb.ZSJY WHERE" \
                     " ZQDM = '{}' " \
                     "and JYRQ >= {} and JYRQ <= {}".format(benchmark_id, start_date, end_date)
        res = hbs.db_data_query('readonly', sql_script, page_size=5000)
        data = pd.DataFrame(res['data'])
        benchmark_df = data.set_index('TRADEDATE')['TCLOSE']

        return benchmark_df

    def _load_data(self):
        config_df = pd.read_excel('D:\\量化产品跟踪\\tracker\\config.xlsx', sheet_name=2)

        trading_day_list = get_trading_day_list(self.start_date, self.end_date, frequency="week")

        fund_dict = config_df.set_index('管理人')['fund_id'].to_dict()
        fund_nav = get_fund_nav_from_sql(self.start_date, self.end_date, fund_dict).reindex(
            trading_day_list).fillna(method='bfill')
        benchmark_series = self._load_benchmark(self.start_date, self.end_date, '000905').reindex(
            trading_day_list).pct_change().dropna()
        return_df = fund_nav.pct_change().dropna().sub(benchmark_series, axis=0).sort_index()
        # 修正
        return_df.loc[:"20210806", '伯兄'] = np.NAN
        return_df.loc[:"20210618", '概率'] = np.NAN
        return_df.loc[:"20211231", '白鹭'] = np.NAN

        nav_df = (1 + return_df).cumprod()

        # 月度收益
        nav_df['trade_date'] = nav_df.index
        nav_df['trade_dt'] = nav_df['trade_date'].apply(lambda x: datetime.strptime(x, "%Y%m%d"))
        nav_df['month'] = nav_df['trade_dt'].apply(lambda x: x.month)
        nav_df['year'] = nav_df['trade_dt'].apply(lambda x: x.year)
        nav_df['date'] = nav_df['year'].map(str) + '.' + nav_df['month'].map(str)
        month_end = nav_df[nav_df['month'].shift(-1) != nav_df['month']]['trade_date'].tolist()

        month_excess = nav_df.reindex(month_end)[return_df.columns].pct_change().dropna()
        month_excess = pd.merge(month_excess, nav_df[['date']], left_index=True, right_index=True)
        month_excess = month_excess.set_index('date').T

        # 分标签分析
        return_df = pd.merge(
            return_df.T, config_df.set_index('管理人')[['规模', '策略频率', '风格敞口']], left_index=True, right_index=True)

        writer = pd.ExcelWriter("D:\\量化产品跟踪\\tracker\\分标签净值.xlsx", engine="xlsxwriter")

        # 规模分析
        tmp = return_df.groupby('规模')[return_df.columns].mean().T.sort_index()
        nav_df = (1 + tmp).cumprod()
        cols = nav_df.columns.tolist()
        nav_df['trade_date'] = nav_df.index
        nav_df = nav_df.reset_index(drop=True)
        nav_df = nav_df[['trade_date'] + cols]
        nav_df.to_excel(writer, sheet_name='规模分类', index=False)

        # 频段分析
        tmp = return_df.groupby('策略频率')[return_df.columns].mean().T.sort_index()
        nav_df = (1 + tmp).cumprod()
        cols = nav_df.columns.tolist()
        nav_df['trade_date'] = nav_df.index
        nav_df = nav_df.reset_index(drop=True)
        nav_df = nav_df[['trade_date'] + cols]
        nav_df.to_excel(writer, sheet_name='频率分类', index=False)

        # 频段分析
        tmp = return_df.groupby('风格敞口')[return_df.columns].mean().T.sort_index()
        nav_df = (1 + tmp).cumprod()
        cols = nav_df.columns.tolist()
        nav_df['trade_date'] = nav_df.index
        nav_df = nav_df.reset_index(drop=True)
        nav_df = nav_df[['trade_date'] + cols]
        nav_df.to_excel(writer, sheet_name='风格敞口分类', index=False)

        writer.save()
        writer.close()


if __name__ == '__main__':
    FundTracker('20210903', '20220708').run()