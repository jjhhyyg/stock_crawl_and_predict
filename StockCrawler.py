import os
import sys
import glob
import time
import pandas as pd
import numpy as np
from urllib.request import urlopen, Request
from urllib.parse import urlencode
from bs4 import BeautifulSoup
import re


class StockCodeCrawler:
    """
    爬取股票名称和代码
    """

    def __init__(self):
        self.headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;"
                      "q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
            "Connection": "keep-alive",
            "Host": "app.finance.ifeng.com",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/99.0.4844.74 Safari/537.36"
        }
        self.MAX_PAGE_SIZE = 100

    def update_csv(self):
        """
        更新csv文件，该文件中包含了每只股票对应的代码
        :return: None
        """

        path = sys.path[0] + '\\raw_data'
        # 删除之前的csv
        for csv_file in glob.glob(os.path.join(path, '*.csv')):
            try:
                os.remove(csv_file)
            except FileNotFoundError:
                print("no csv file found!")
            except IsADirectoryError:
                print("the path is not a file but a directory!")

        # 获取股票代码和名称的列表
        code_list = []
        name_list = []

        # 获取股票类型
        stock_dict = self.get_name_dict()
        for key, value in stock_dict.items():
            # 每轮迭代选择一种类型的股票，获取该类型下所有支股票的代码和名称
            data_dict = {'t': value, 'f': 'chg_pct', 'o': 'desc'}

            # 最多爬取MAX_PAGE_SIZE页数据
            for i in np.arange(1, self.MAX_PAGE_SIZE + 1):
                # 访问对应页数的网页
                data_dict['p'] = i
                req = self.create_request(headers=self.headers, dic=data_dict)
                html = urlopen(req)
                bs = BeautifulSoup(html, 'html.parser')

                # 获取该页由股票代码和股票名称组成的列表
                lists = bs.find('div', {'class': 'tab01'})
                data = lists.find_all('a', {'target': '_blank'})
                # data中没东西说明该类型的股票查询完毕，开始查询下一类型的股票
                if not data:
                    print('===============================')
                    print(f"{key} 搜索完毕，查找下一类型股票")
                    print('===============================')
                    break

                print(f"类型：{key}，第{i}页，该页有{len(data)}条数据")

                # 下标为偶数的数据放到code_list中，下标为奇数的数据放到name_list中
                for j in np.arange(0, len(data), 2):
                    item = data[j].get_text().replace(" ", "")
                    code_list.append(item)
                for j in np.arange(1, len(data), 2):
                    item = data[j].get_text().replace(" ", "")
                    name_list.append(item)

        df = pd.DataFrame(columns=['code', 'name'], data={
            'code': code_list,
            'name': name_list
        })
        df.drop_duplicates(inplace=True)
        df.dropna(inplace=True)
        df.set_index(['name'], inplace=True)
        df.to_csv('raw_data/code.csv', encoding='utf-8_sig')

    def create_request(self, root="https://app.finance.ifeng.com/list/stock.php", headers=None, dic=None, method='GET'):
        """
        创建一个请求
        :param headers: 请求头
        :param root: 待请求网页
        :param dic: 请求数据，字典类型
        :param method: GET或POST
        :return: Request对象
        """
        # 选择默认的请求头
        if headers is None:
            headers = self.headers
        # 默认不带请求数据
        if dic is None:
            dic = ""

        params = urlencode(dic)
        url = root + '?' + params
        req = Request(url=url, headers=headers, method=method)
        return req

    def get_name_dict(self):
        """
        获取所有股票类型
        :param bs: BeautifulSoup对象，存储html网页源代码
        :return: {股票类型:股票标号} 的字典
        """
        req = self.create_request()
        html = urlopen(req)
        bs = BeautifulSoup(html, 'html.parser')
        all_a = bs.find_all('a')
        res = {}
        for a in all_a:
            a = str(a)
            m = re.match(r'^<a href="\?t=([a-zA-Z]+)">(.*)</a>$', a)
            if m is not None:
                res[m.group(2)] = m.group(1)
        return res

    def get_code(self, name):
        """
        获取股票名称对应的代码
        :param name: 股票名称
        :return: 代码存在则返回对应代码，否则返回None
        """
        df = None
        try:
            df = pd.read_csv("./raw_data/code.csv")
        except FileNotFoundError:
            print("数据源缺失，三秒后开始重新爬取数据！")
            time.sleep(3)
            self.update_csv()
        finally:
            result = df[df['name'] == name]
            if len(result) == 0:
                print("没有该股票名称对应的股票代码，请确认股票名称正确！")
            else:
                return result.iloc[0].at['code']


class StockDataCrawler:
    """
    爬取股票历史数据
    """

    def __init__(self):
        self.code = None

    def set_code(self, code):
        self.code = code

    def get_data(self, start, end, online):
        """
        获取一段时间内的股票数据
        :param start: 开始日期
        :param end: 结束日期
        :param online: 获取数据的方式
        :return: DataFrame对象，如果股票代码有误，返回None
        """

        # 查找本地是否存在对应的csv文件，如果存在，直接读取该csv，否则更新
        code = str(self.code)
        file_name = f"./raw_data/{code}.csv"
        if not online and os.path.exists(file_name):
            print("Loading data locally.")
            df = pd.read_csv(file_name)
            return df

        else:
            print("Fetching data...")
            # 在线获取/更新股票历史数据
            url_mod = "http://quotes.money.163.com/service/chddata.html?code=%s&start=%s&end=%s"

            url = url_mod % (code, start, end)
            df = pd.read_csv(url, encoding='gb2312')
            if len(df) == 0:
                print("股票代码有误，请检查")
                return None

            else:
                df.to_csv(f"./raw_data/{self.code}.csv", encoding='utf-8_sig')
                return df
