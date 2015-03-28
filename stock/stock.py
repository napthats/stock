import pandas as pd
import os
import dateutil.parser

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
    stock = pd.read_csv(stock_dir + file,header=None,names=['date','open','high','low','close','volume'])
    #stock.date = stock.date.map(lambda x: str(x)).map(dateutil.parser.parse)
    stock_dict[file.split('.')[0]] = stock.set_index('date')

stock_df = pd.concat(stock_dict, axis=1)
stock_df.set_index(pd.Series(stock_df.index).map(lambda x: str(x)).map(dateutil.parser.parse), inplace=True)

rm_stock_df = pd.rolling_mean(stock_df, 50)
