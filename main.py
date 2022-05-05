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
            print('请输入正确指令！')
            continue

        # 代码需要已0/3/6开头
        if code.startswith('0') or code.startswith('3'):
            code = '1' + code
        elif code.startswith('6'):
            code = '0' + code
        else:
            print("股票代码有误，请检查")
            continue

        # 从网络爬取数据或从本地获取数据
        data_crawler = StockDataCrawler()
        data_crawler.set_code(code)

        # 选择在线/离线获取
        if os.path.exists(f'./raw_data/{code}.csv'):
            method = input("存在本地数据，是否选择获取本地数据？(Y/N)")
            while True:
                if method == 'Y':
                    method = 0
                    break
                elif method == 'N':
                    print('选择获取在线数据')
                    method = 1
                    break
                else:
                    method = input("存在本地数据，是否选择获取本地数据？(Y/N)")
        else:
            print('不存在本地数据，自动选择获取在线数据')
            method = 1

        if method == 1:
            start_date = input('请输入开始日期(如19900101)')
            end_date = input('请输入结束日期(如20211205)')
        else:
            start_date = None
            end_date = None

        df = data_crawler.get_data(start=start_date, end=end_date, online=method)

        if df is None:
            print('数据获取失败，请检查股票代码是否正确，或输入的日期格式是否正确')
            continue

        df2json(df)

        app = Flask(__name__)


        @app.route('/')
        def index():
            return render_template('index.html')


        app.run(host='localhost', port=5000)
