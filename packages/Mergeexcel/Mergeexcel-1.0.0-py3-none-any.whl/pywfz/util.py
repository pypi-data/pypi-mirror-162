import numpy as np
import pandas as pd
def budget_read_data(file_name,sheet_name):
    data_1 = pd.read_excel(file_name, sheet_name)
    col_selected = ['支付主体', '项目', '收款人名称', '归属利润中心', '支付类别', '币种', '支付金额（元）', '预计支付日期']
    flag = data_1['支付主体'].notnull()
    data_1_res = data_1.loc[flag, col_selected]
    return(data_1_res)
def budget_read_data_batch(file_names,sheet_name):
    data_1 = pd.read_excel(file_name, sheet_name)
    col_selected = ['支付主体', '项目', '收款人名称', '归属利润中心', '支付类别', '币种', '支付金额（元）', '预计支付日期']
    flag = data_1['支付主体'].notnull()
    data_1_res = data_1.loc[flag, col_selected]
    return(data_1_res)