import base64
import hashlib
import hmac
import os
import time
import urllib.parse
from datetime import datetime

import pytest
import requests

data = {
    "failed": 0,
    "passed": 0,
}


def pytest_addoption(parser):
    # 自定义增加配置
    parser.addini(
        "send_when",
        help="什么时候发送测试结果，ervery表示每次都发送 on_fail表示只有失败是才发送",
    )
    parser.addini("send_api", help="发送api地址")


def pytest_collection_finish(session: pytest.Session):
    # 获取：用例加载完成之后执行此钩子函数，包含了全部的用例
    data["total"] = len(session.items)
    print(f"\n[进程 {os.getpid()}] 收集到的用例列表:")
    for i, item in enumerate(session.items, 1):
        print(f"  {i}. {item.nodeid}")
    print(f"总共: {data['total']} 个用例\n")


def pytest_runtest_logreport(report: pytest.TestReport):
    # 获取每个测试用例是否通过
    # print(report)
    if report.when == "call":
        # print("本次用例的执行结果是：", report.outcome)
        data[report.outcome] += 1
        print(f"DEBUG: 累计 passed={data['passed']}, 当前用例={report.nodeid}")
        print("pytest_runtest_logreport:", report.when, data)


def pytest_configure(config: pytest.Config):
    # 在配置文件加载完毕之后执行，在所有测试用例执行之前执行
    data["start_time"] = datetime.now()  # .strftime('%Y-%m-%d %H:%M:%S')
    # print(f"{datetime.now()} - {__name__}pytest开始执行")
    # 将配置保存到data全局变量
    data["send_when"] = config.getini("send_when")
    data["send_api"] = config.getini("send_api")
    print("pytest_configure", data)


def pytest_unconfigure(config):
    # 在配置卸载完毕之后执行，在所有测试用例执行完毕后执行
    data["end_time"] = datetime.now()  # .strftime('%Y-%m-%d %H:%M:%S')
    # print(f"{datetime.now()}pytest结束执行")
    data["duration"] = data["end_time"] - data["start_time"]
    data["pass_ratio"] = f"{data['passed'] / data['total']:.2%}" if data["total"] else 0
    print("pytest_unconfigure：", data)
    send_result()


# def send_result(access_token, secret, msg, at_user_ids=None, at_mobiles=None, is_at_all=False)
def send_result(at_user_ids=None, at_mobiles=None, is_at_all=False):
    """
    发送钉钉自定义机器人群消息
    :param access_token: 机器人webhook的access_token
    :param secret: 机器人安全设置的加签secret
    :param msg: 消息内容
    :param at_user_ids: @的用户ID列表
    :param at_mobiles: @的手机号列表
    :param is_at_all: 是否@所有人
    :return: 钉钉API响应
    """
    print(data["send_when"], data["failed"])
    if data["send_when"] == "on_fail" and data["failed"] == 0:
        return
    if not data["send_api"]:
        return

    access_token = "065ccda1a350f7fa306d3821e290eb1ca7a4ab61d52751d8e1f960c2d3bc8943"
    secret = "SEC1808f6a12a1d30997d00b35b67e5ad0b24f57a5ed22e423accc9b83e37d602bd"
    timestamp = str(round(time.time() * 1000))
    string_to_sign = f"{timestamp}\n{secret}"
    hmac_code = hmac.new(
        secret.encode("utf-8"), string_to_sign.encode("utf-8"), digestmod=hashlib.sha256
    ).digest()
    sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
    url = f'{data["send_api"]}?access_token={access_token}&timestamp={timestamp}&sign={sign}'
    content = f"""
           测试开始：{data['start_time'].strftime('%Y-%m-%d %H:%M:%S')}
           测试耗时：{str(data['duration'])}
           测试用例总数：{data['total']}
           测试成功的数：{data['passed']}
           测试失败的数：{data['failed']}
           测试通过率：{data['pass_ratio']}
       """

    body = {
        "at": {
            "isAtAll": str(is_at_all).lower(),
            "atUserIds": at_user_ids or [],
            "atMobiles": at_mobiles or [],
        },
        "text": {"content": "测试消息：" + content},
        "msgtype": "text",
    }
    headers = {"Content-Type": "application/json"}
    try:
        resp = requests.post(url, json=body, headers=headers)
        print("发送结果状态：", resp.status_code)
        print("发送结果：", resp.json())
    except Exception as e:
        print(f"发送失败：{e}")
        pass
    data["send_done"] = 1


"""
核心收获：
1.主进程 vs 子进程
    主进程是"组织者"，子进程是"执行者"
    每个进程独立运行，有自己的配置和生命周期
2.配置文件加载机制
    -c 参数指定配置文件，优先级最高
    没有 -c 时按正常顺序查找
    主进程读项目配置，子进程读临时配置
3.钩子函数的调用时机
    pytest_configure：每个进程启动时执行一次
    pytest_unconfigure：每个进程结束时执行一次
    不是所有用例执行完，而是当前进程的所有用例执行完
4.输出中的小细节
    . 是 pytest 的进度标记
    输出顺序受缓冲机制影响
    看似矛盾的输出都有合理解释
"""
