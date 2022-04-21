from StockCrawler import StockCodeCrawler, StockDataCrawler
from Plotter import Plotter

# 获取股票代码
code_crawler = StockCodeCrawler()
code = code_crawler.get_code("宁德时代")
print(code)

# 从网络爬取数据或从本地获取数据
data_crawler = StockDataCrawler(code)
df = data_crawler.get_data(start='20200101', end='')

plotter = Plotter()
plotter.plot_df(df)
