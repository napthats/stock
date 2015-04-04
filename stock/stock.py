import pandas as pd
import os
import dateutil.parser
import matplotlib.pyplot as plt

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

stock_df = pd.concat(stock_dict, axis=1)
stock_df.set_index(pd.Series(stock_df.index).map(lambda x: str(x)).map(dateutil.parser.parse), inplace=True)

rmean_stock_df2 = pd.rolling_mean(stock_df, 50, min_periods=40)
rmean_stock_df = pd.ewma(stock_df, 50, min_periods=40)

rmean_rmax_stock_df = pd.rolling_max(rmean_stock_df, 400, min_periods=320)

rmean_ismax_stock_df = rmean_stock_df == rmean_rmax_stock_df

#rmean_isdec2inc_stock_df = pd.rolling_apply(rmean_stock_df, 3, lambda l: l[0] > l[1] and l[1] < l[2]).applymap(lambda x: True if x == 1 else False)
rmean_isdec2incinc_stock_df = pd.rolling_apply(rmean_stock_df, 12, lambda x: x[0] > x[1] and x[1] < x[2] and x[2] < x[3] and x[3] < x[4] and x[4] < x[5] and x[5] < x[6] and x[6] < x[7] and x[7] < x[8] and x[8] < x[9] and x[9] < x[10] and x[10] < x[11]).applymap(lambda x: True if x == 1 else False)

#rmean_isinc2dec_stock_df = pd.rolling_apply(rmean_stock_df, 3, lambda l: l[0] < l[1] and l[1] > l[2]).applymap(lambda x: True if x == 1 else False)

def extract_incstock(ord, window):
    if ord <= 0 or window <= 0 or ord + window > stock_df.index.size:
        return pd.Series()
    incinc_bool_table = rmean_isdec2incinc_stock_df[ord:ord+window].any()
    incinc_code_array = incinc_bool_table[incinc_bool_table].keys()
    result_code_list = []
    for code in incinc_code_array:
        for check_ord in range(ord-1,-1,-1):
            if rmean_ismax_stock_df[code][check_ord]:
                result_code_list.append(code)
                break
            if rmean_isdec2incinc_stock_df[code][check_ord]:
                break
    return pd.Series(result_code_list)

def plot_stock(code):
    stock_df[code].plot()
    rmean_stock_df[code].plot()


