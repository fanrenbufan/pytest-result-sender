from datetime import datetime

print("我也来试试")


def pytest_configure(config):
    # 在配置文件加载完毕之后执行，在所有测试用例执行之前执行
    print(f"{datetime.now()} - {__name__}pytest开始执行")


def pytest_unconfigure(config):
    # 在配置卸载完毕之后执行，在所有测试用例执行之后执行
    print(f"{datetime.now()}pytest结束执行")
