import pandas as pd
import os
import dateutil.parser
import matplotlib.pyplot as plt
import statsmodels.api as sm


finance = pd.io.excel.read_excel('data/finance.xls')
finance_columns = pd.Series(['code', 'name', 'price', 'pretax_income_rate', 'net_income_rate', 'net_income', 'EPS', 'BPS', 'ROE', 'long_term_debt', 'total_number_stock', 'PER', 'divident', 'PER_new'])
finance_columns_num = pd.Series([1,1,1,10,10,10,10,10,10,10,10,10,1,1])

ord = 0
columns = [''] * finance.columns.size
for i in range(0, finance_columns.size):
    if (finance_columns_num[i] == 1):
        columns[ord] = finance_columns[i]
        ord += 1
    else:
        for j in range(0,finance_columns_num[i]):
            columns[ord] = finance_columns[i] + '_' + str(j)
            ord += 1

finance.columns = columns
finance = finance[1:]

stock_dir = 'data/stock/'
file_list = pd.Series(os.listdir(stock_dir))
stock_dict = {}

for file in file_list:
    #stock = pd.read_csv(stock_dir + file,header=None,names=['date','open','high','low','close','volume'])
    stock = pd.read_csv(stock_dir + file,header=None,names=['date','close'], usecols=[0,4])
    stock_dict[file.split('.')[0]] = stock.set_index('date').close

stock = pd.concat(stock_dict, axis=1)
stock.set_index(pd.Series(stock.index).map(lambda x: str(x)).map(dateutil.parser.parse), inplace=True)



_, stock_trend = sm.tsa.filters.hpfilter(stock.fillna(method='bfill').fillna(method='ffill'), 1600)

stock_trend_rmax = pd.rolling_max(stock_trend, 400, min_periods=320)

stock_trend_ismax = stock_trend == stock_trend_rmax

stock_trend_isdec2inc = pd.rolling_apply(stock_trend, 3, lambda x: x[0] > x[1] and x[1] < x[2]).applymap(lambda x: True if x == 1 else False)
stock_trend_isinc2dec = pd.rolling_apply(stock_trend, 3, lambda x: x[0] < x[1] and x[1] > x[2]).applymap(lambda x: True if x == 1 else False)

def extract_incstock(ord, window):
    if ord <= 0 or window <= 0 or ord + window > stock.index.size:
        return pd.Series()
    incinc_bool_table = stock_trend_isdec2inc[ord:ord+window].any()
    incinc_code_array = incinc_bool_table[incinc_bool_table].keys()
    result_code_list = []
    for code in incinc_code_array:
        #a
        print(code)
        #a
        is_first = True
        previous_max = None
        previous_day = None
        for check_ord in range(ord-1,-1,-1):
            if stock_trend_isinc2dec[code][check_ord+1]:
                if is_first:
                    print(stock_trend[code][check_ord])
                    if stock_trend_ismax[code][check_ord]:
                        break
                    else:
                        previous_max = stock_trend[code][check_ord]
                        previous_day = stock_trend.index[check_ord]
                        is_first = False
                else:
                    print(stock_trend[code][check_ord])
                    if stock_trend[code][check_ord] > previous_max:
                        if stock_trend_ismax[code][check_ord]:
                            result_code_list.append((code, previous_day, stock_trend_ismax.index[check_ord]))
                            break
                        else:
                            break
    return pd.Series(result_code_list)

def plot_stock(code):
    stock[code].plot()
    stock_trend[code].plot()


