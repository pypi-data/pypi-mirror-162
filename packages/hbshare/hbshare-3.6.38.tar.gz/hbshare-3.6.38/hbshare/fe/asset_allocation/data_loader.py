# -*- coding: utf-8 -*-

import pandas as pd
import pymysql
import hbshare as hbs
import warnings
warnings.filterwarnings('ignore', category=pymysql.Warning)


class Loader:
    def __init__(self):
        pass

    def get_df(self, sql, db, page_size=2000):
        data = hbs.db_data_query(db, sql, page_size=page_size, timeout=120)
        pages = data['pages']
        data = pd.DataFrame(data['data'])
        if pages > 1:
            for page in range(2, pages + 1):
                temp_data = hbs.db_data_query(db, sql, page_size=page_size, page_num=page, timeout=120)
                data = pd.concat([data, pd.DataFrame(temp_data['data'])], axis=0)
        return data

    def read_cal(self, start, end):
        sql = "SELECT JYRQ, SFJJ, SFZM, SFYM FROM funddb.JYRL WHERE JYRQ>={0} and JYRQ<={1}".format(start, end)
        df = self.get_df(sql, db='readonly')
        return df

    def read_mutual_index_daily_k_given_indexs(self, indexs, start, end):
        indexs = "'" + "','".join(indexs) + "'"
        sql = "SELECT zsdm AS INDEX_CODE, jzrq AS TRADE_DATE, spjg AS CLOSE_INDEX FROM st_fund.t_st_gm_clzs WHERE m_opt_type <> '03' AND zsdm in ({0}) AND jzrq >= {1} AND jzrq <= {2}".format(indexs, start, end)
        df = self.get_df(sql, db='funduser', page_size=200000)
        return df

    def read_private_index_daily_k_given_indexs(self, indexs, start, end):
        indexs = "'" + "','".join(indexs) + "'"
        sql = "SELECT zsdm AS INDEX_CODE, tjyf AS TRADE_MONTH, spjg AS CLOSE_INDEX FROM st_hedge.t_st_sm_hmzs WHERE m_opt_type <> '03' AND zsdm in ({0}) AND tjyf >= {1} AND tjyf <= {2}".format(indexs, start, end)
        df = self.get_df(sql, db='highuser', page_size=200000)
        return df

    def read_market_index_daily_k_given_indexs(self, indexs, start, end):
        indexs = "'" + "','".join(indexs) + "'"
        sql = "SELECT zqdm AS INDEX_CODE, jyrq AS TRADE_DATE, spjg AS CLOSE_INDEX FROM st_market.t_st_zs_hqql WHERE m_opt_type <> '03' AND zqdm in ({0}) AND jyrq >= {1} AND jyrq <= {2}".format(indexs, start, end)
        df = self.get_df(sql, db='alluser', page_size=200000)
        return df

    def read_mutual_fund_cumret_given_codes(self, codes, start, end):
        codes = "'" + "','".join(codes) + "'"
        sql = "SELECT a.jjdm AS FUND_CODE, b.jzrq AS TRADE_DATE, b.hbcl AS CUM_RET FROM funddb.jjxx1 a, funddb.jjhb b WHERE a.cpfl = '2' AND a.jjdm = b.jjdm AND a.jjzt not in ('3', 'c') AND a.m_opt_type <> '03' AND a.jjdm in ({0}) AND b.jzrq >= {1} AND b.jzrq <= {2}".format(codes, start, end)
        df = self.get_df(sql, db='readonly', page_size=200000)
        return df

    def read_private_fund_adj_nav_given_codes(self, codes, start, end):
        codes = "'" + "','".join(codes) + "'"
        sql = "SELECT a.jjdm AS FUND_CODE, b.jzrq AS TRADE_DATE, b.fqdwjz AS ADJ_NAV FROM st_hedge.t_st_jjxx a, st_hedge.t_st_rhb b WHERE a.cpfl = '4' AND a.jjdm = b.jjdm AND a.jjzt not in ('3') AND a.m_opt_type <> '03' AND a.jjdm in ({0}) AND b.jzrq >= {1} AND b.jzrq <= {2}".format(codes, start, end)
        df = self.get_df(sql, db='highuser', page_size=200000)
        return df

    def read_market_index_market_value_given_indexs(self, indexs, start, end):
        indexs = "'" + "','".join(indexs) + "'"
        sql = "SELECT zqdm AS INDEX_CODE, jyrq AS TRADE_DATE, zsz AS MARKET_VALUE FROM st_market.t_st_zs_hqql WHERE m_opt_type <> '03' AND zqdm in ({0}) AND jyrq >= {1} AND jyrq <= {2}".format(indexs, start, end)
        df = self.get_df(sql, db='alluser', page_size=200000)
        return df

    def read_mutual_fund_market_value_given_codes(self, codes, start, end):
        codes = "'" + "','".join(codes) + "'"
        sql = "SELECT jjdm AS FUND_CODE, jsrq AS REPORT_DATE, jjzzc AS MARKET_VALUE FROM st_fund.t_st_gm_zcpz WHERE m_opt_type <> '03' AND jjdm in ({0}) AND jsrq >= {1} AND jsrq <= {2}".format(codes, start, end)
        df = self.get_df(sql, db='funduser', page_size=200000)
        return df