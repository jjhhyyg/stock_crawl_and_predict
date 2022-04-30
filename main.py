import os.path

from StockCrawler import StockCodeCrawler, StockDataCrawler
from flask import Flask, render_template
from Func import df2json
from Menu import Menu

if __name__ == '__main__':
    code_crawler = StockCodeCrawler()
    menu = Menu()
    code = None

    while True:
        # 打印主菜单
        menu.welcome()
        opcode = input()
        if opcode == '1':
            stock_name = input("请输入股票名称：")
            code = code_crawler.get_code(stock_name)
            if code is None:
                continue
        elif opcode == '2':
            code = input("请输入股票代码：")
        elif opcode == 'e':
            break
        else:
            continue

        # 从网络爬取数据或从本地获取数据
        data_crawler = StockDataCrawler()
        data_crawler.set_code(code)

        # 选择在线/离线获取
        while True:
            if os.path.exists(f'./raw_data/{code}.csv'):
                print("存在本地数据")
            method = input("是否选择在线获取数据？(Y/N)")
            if method == 'Y':
                method = 1
                break
            elif method == 'N':
                method = 0
                break
            else:
                print("请输入Y或者N")
        df = data_crawler.get_data(start='19900101', end='', online=method)
        if df is None:
            continue

        df2json(df)

        app = Flask(__name__)


        @app.route('/')
        def index():
            return render_template('index.html')


        app.run(host='localhost', port=5000)
