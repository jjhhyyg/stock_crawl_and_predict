import json
from datetime import datetime


def df2json(df):
    """
    把股票数据需要的几个部分提取出来并转换为用于可视化显示的json文件
    :param df: 股票数据DataFrame对象
    :return: None
    """

    def time_trans(date):
        return str(int(datetime.timestamp(datetime.strptime(date, '%Y-%m-%d')))) + '000'

    target_df = df.loc[:, ['日期', '开盘价', '最高价', '最低价', '收盘价', '成交量']]
    target_df.sort_values(by=['日期'], inplace=True)
    target_df['日期'] = target_df['日期'].map(time_trans)
    target_arr = target_df.values
    l = target_arr.tolist()
    json_arr = json.dumps(l)
    print(json_arr)
    with open('static/data/data.json', 'w') as f:
        f.write(json_arr)
