class Menu:
    """
    用于显示各种控制台菜单提示信息
    """
    def __init__(self):
        pass

    def welcome(self):
        print("-------------------菜单-------------------")
        print("1. 根据股票名称查询(deprecated)")
        print("2. 根据股票代码查询")
        print('e. 退出程序')
        print("------------------------------------------")

