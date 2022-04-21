"""
绘画类
"""
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.dates as mdate

plt.rcParams['font.sans-serif'] = 'Simhei'
plt.rcParams['axes.unicode_minus'] = False


class Plotter:
    def __init__(self):
        pass

    def plot_df(self, df):
        """
        绘制折线图
        :param df: DataFrame对象，储存有股票历史数据，且有"日期"和"收盘价"两列数据
        :return: None
        """
        data = df.sort_index(ascending=False).loc[:, ['日期', '收盘价']]
        data.set_index('日期', inplace=True)
        x = pd.to_datetime(data.index)
        ax = plt.gca()
        plt.style.use('ggplot')
        ax.xaxis.set_major_locator(mdate.YearLocator())
        ax.xaxis.set_major_formatter(mdate.DateFormatter('%Y-%m'))  # 横坐标标签显示的日期格式
        plt.xticks(pd.date_range(x[0], x[-1], freq='6M'))  # 横坐标日期范围及间隔
        plt.yticks()  # 设置纵坐标，使用range()函数设置起始、结束范围及间隔步长
        plt.xlabel("时间")
        plt.ylabel("当日收盘价")
        plt.title("实际数据")
        plt.plot(x, data['收盘价'], alpha=0.6)
        plt.show()
