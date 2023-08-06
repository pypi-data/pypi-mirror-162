"""
雪球产品测算
"""
import hbshare as hbs
import pandas as pd
from hbshare.fe.common.util.data_loader import get_trading_day_list


def snow_ball_simulation(start_date, end_date, duration, knock_in_price, knock_out_price):
    """
    start_date: 回测起始时间
    end_date: 回测结束时间
    duration: 合约期限
    knock_in_price: 敲入价格
    knock_out_price: 敲出价格
    """
    sql_script = "SELECT JYRQ as TRADEDATE, ZQMC as INDEXNAME, SPJG as TCLOSE from funddb.ZSJY WHERE ZQDM = '{}' " \
                 "and JYRQ >= {} and JYRQ <= {}".format('000905', start_date, end_date)
    index_df = pd.DataFrame(hbs.db_data_query('readonly', sql_script, page_size=5000)['data'])
    index_series = index_df.set_index('TRADEDATE')['TCLOSE']
    # 每个月底发一只雪球产品
    month_end_list = get_trading_day_list(start_date, end_date, frequency="month")

    res_df = pd.DataFrame(index=month_end_list[:-duration], columns=['c1', 'c2', 'c3', 'ko_time', 'lose_ratio'])

    for i in range(duration, len(month_end_list)):
        period_start = month_end_list[i - duration]
        period_end = month_end_list[i]

        period_data = index_series.loc[period_start: period_end]
        period_data = period_data / period_data.iloc[0]
        ko_date_list = [x for x in month_end_list if period_start < x <= period_end]

        if period_data.loc[ko_date_list].gt(knock_out_price).sum() > 0:  # 情形1：敲出获利
            tmp = period_data.loc[ko_date_list].to_frame('nav')
            tmp.loc[tmp['nav'] > knock_out_price, 'sign'] = 1
            ko_time = tmp.index.to_list().index(tmp['sign'].first_valid_index()) + 1
            res_df.loc[period_start, 'c1'] = 1
            res_df.loc[period_start, 'ko_time'] = ko_time
        elif period_data[1:].min() >= knock_in_price:  # 情形2：既未敲出也未敲入
            res_df.loc[period_start, 'c2'] = 1
        else:
            res_df.loc[period_start, 'c3'] = 1
            lose_ratio = \
                max(0, (period_data.loc[period_start] - period_data.loc[period_end]) / period_data.loc[period_start])
            res_df.loc[period_start, 'lose_ratio'] = lose_ratio * (-1)

    print(res_df[res_df.columns[:3]].sum() / res_df.shape[0])
    print(res_df['ko_time'].mean())
    print(res_df['lose_ratio'].mean())

if __name__ == '__main__':
    snow_ball_simulation('20100101', '20220531', 12, 0.8, 1.03)
