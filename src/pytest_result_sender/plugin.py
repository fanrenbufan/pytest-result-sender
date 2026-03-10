import pytest
from datetime import datetime,timedelta


data = {
    "failed":0,
    "passed":0,
}

def pytest_collection_finish(session: pytest.Session):
    # 用例加载完成之后执行此钩子函数，包含了全部的用例
    data['total'] = len(session.items)
    print('用例的数量是：',data['total'])

def pytest_runtest_logreport(report:pytest.TestReport):
    # 获取每个测试用例是否通过
    print(report)
    if report.when == 'call':
        print('本次用例的执行结果是：',report.outcome)
        data[report.outcome] += 1
def pytest_configure(config):

    data['start_time'] = datetime.now()# .strftime('%Y-%m-%d %H:%M:%S')
    # 在配置文件加载完毕之后执行，在所有测试用例执行之前执行
    print(f"{datetime.now()} - {__name__}pytest开始执行")


def pytest_unconfigure(config):
    data['end_time'] = datetime.now()# .strftime('%Y-%m-%d %H:%M:%S')
    # 在配置卸载完毕之后执行，在所有测试用例执行之后执行
    print(f"{datetime.now()}pytest结束执行")

    data['duration'] = data['end_time'] - data['start_time']
    data['pass_ratio'] = f"{data['passed'] / data['total']:.2%}"
    print(data)
    assert timedelta(seconds=3) > data['duration'] > timedelta(seconds=2)
    assert data['total'] == 3
    assert data['passed'] == 2
    assert data['failed'] == 1
    assert data['pass_ratio'] == "66.67%"


