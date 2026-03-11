from pathlib import Path

import pytest

from pytest_result_sender import plugin

pytest_plugins = "pytester"


@pytest.fixture(autouse=True)
def mock():
    print("进入mock")
    bak_data = plugin.data
    print(bak_data)
    plugin.data = {
        "failed": 0,
        "passed": 0,
    }
    print("plugin.data", plugin.data)
    print("bak_data", bak_data)
    # 创建一个干净测试环境
    yield
    # 恢复测试环境
    plugin.data = bak_data
    print("mock", plugin.data)


@pytest.mark.parametrize("send_when", ["every", "on_fail"])  # 参数化
def test_send_when(
    send_when, pytester: pytest.Pytester, tmp_path: Path
):  # 一定要把参数放到函数中
    """
    :param send_when: 在参数化测试中，代表不同配置的值
    :param pytester: 用于测试自己
    :param tmp_path:用于生成和保存一个临时的配置文件
    :return:
    """
    print("进入test_send_when")
    # 生成一个配置文件
    config_path = tmp_path.joinpath("pytest.ini")
    # 不能缩进，因为[pytest] 必须从行首开始，前面不能有空格
    config_path.write_text(
        f"""
[pytest]
send_when = {send_when}
send_api = https://oapi.dingtalk.com/robot/send
"""
    )
    # 实例化：用pytester加载这个配置文件，并把加载结果赋值给config变量
    config = pytester.parseconfig(config_path)
    # 断言配置加载成功
    assert config.getini("send_when") == send_when

    pytester.makepyfile(  # 构造一个场景：用例全部测试通过
        """
        def test_pass():
            ...
        """
    )
    # -c的作用：读取 -c 指定的配置文件，完全忽略项目根目录的 pytest.ini的相同配置项
    pytester.runpytest("-c", str(config_path))

    print("test_send_when结束：", plugin.data)

    # 断言插件有没有发送结果
    if send_when == "every":
        assert plugin.data["send_done"] == 1
    else:
        assert plugin.data.get("send_done") is None


@pytest.mark.parametrize("send_api", ["", "https://oapi.dingtalk.com/robot/send"])
def test_send_api(send_api, pytester: pytest.Pytester, tmp_path: Path):
    print("进入test_send_api")
    # 生成一个配置文件
    config_path = tmp_path.joinpath("pytest.ini")
    # 不能缩进，因为[pytest] 必须从行首开始，前面不能有空格
    config_path.write_text(
        f"""
[pytest]
send_when = every
send_api = {send_api}
    """
    )
    # 实例化：用pytester加载这个配置文件，并把加载结果赋值给config变量
    config = pytester.parseconfig(config_path)
    # 断言配置加载成功
    assert config.getini("send_api") == send_api

    pytester.makepyfile(  # 构造一个场景：用例全部测试通过
        """
        def test_pass():
            ...
        """
    )
    # -c的作用：读取 -c 指定的配置文件，完全忽略项目根目录的 pytest.ini的相同配置项
    pytester.runpytest("-c", str(config_path))

    print("test_send_api结束：", plugin.data)

    # 断言插件有没有发送结果
    if send_api:
        assert plugin.data["send_done"] == 1
    else:
        assert plugin.data.get("send_done") is None
