
from fastapi import FastAPI
import uvicorn
import typing
import json

try:
    from . import models
    from .base import *
except:
    import models
    from base import *


app = FastAPI(title="TANZE", version="1.2.7", description="自写sdk, 增加 test接口可以测试连接器，连接器并不为单例的，第一执行的组件")

# web 调用 自写方法 关键
plugins = None

class Server(object):
    """
    #   此类用于快速调试API，但目前由于需要直接对接系统，因此在1.2.7版本sdk中没有功能上的改动

    **预计在将来某一个版本中被另外一种测试方法替代**

    """
    def __init__(self,plugin_object):

        global plugins
        plugins = plugin_object

        
    @staticmethod
    @app.post("/actions/{action_name}")
    def actions(action_name, plugin_stdin: typing.Optional[models.PLUGIN_TEST_MODEL]=None):

        clearLog()

        action = plugins.actions[action_name]

        # 取出body
        data = plugin_stdin.dict()
        checkModel(data,models.PLUGIN_TEST_MODEL)
        data_body = data.get("body")

        # 获取input
        input_data = data_body.get("input")
        connection_data = data_body.get("connection")

        # 执行 外部run 相关操作
        output = action._run(input_data, connection_data)

        return output


    @staticmethod
    @app.post("/actions/{action_name}/test")
    def actions_test(action_name: str, plugin_stdin: typing.Optional[models.PLUGIN_TEST_MODEL]=None):
        
        clearLog()

        action = plugins.actions[action_name]

        # 取出body
        data = plugin_stdin.dict()
        checkModel(data,models.PLUGIN_TEST_MODEL)
        data_body = data.get("body")

        # 获取input
        connection_data = data_body.get("connection")

        output = action._test(connection_data)

        return output


    @staticmethod
    @app.post("/triggers/{trigger_name}")
    def triggers(trigger_name: str, plugin_stdin: typing.Optional[models.PLUGIN_TEST_MODEL]):

        clearLog()

        # 外部类
        trigger = plugins.triggers[trigger_name]


        # 取出body
        data = plugin_stdin.dict()
        checkModel(data,models.PLUGIN_TEST_MODEL)
        data_body = data.get("body")

        # 获取input
        input_data = data_body.get("input")
        connection_data = data_body.get("connection")
        dispatcher_url = data_body.get("dispatcher").get("url")

        # 执行　外部run 相关操作
        output = trigger._run(input_data, connection_data, dispatcher_url)

        return output


    @staticmethod
    @app.post("/triggers/{trigger_name}/test")
    def trigger_test(trigger_name: str, plugin_stdin: typing.Optional[models.PLUGIN_TEST_MODEL] = None):

        clearLog()

        # 外部类
        trigger = plugins.triggers[trigger_name]

        # 取出body
        data = plugin_stdin.dict()
        checkModel(data,models.PLUGIN_TEST_MODEL)
        data_body = data.get("body")

        # 获取input
        connection_data = data_body.get("connection")

        output = trigger._test(connection_data)

        return output


    @staticmethod
    @app.post("/alarm_receivers/{alarm_receiver_name}")
    def alarm_receivers(alarm_receiver_name: str, plugin_stdin: typing.Optional[models.PLUGIN_TEST_MODEL]):
        
        clearLog()

        # 外部类
        alarm_receiver = plugins.alarm_receivers[alarm_receiver_name]

        # 取出body
        data = plugin_stdin.dict()
        checkModel(data,models.PLUGIN_TEST_MODEL)
        data_body = data.get("body")

        # 获取input
        input_data = data_body.get("input")
        connection_data = data_body.get("connection")
        dispatcher_url = data_body.get("dispatcher").get("url")

        # 执行　外部run 相关操作
        output = alarm_receiver._run(input_data, connection_data, dispatcher_url)

        return output


    @staticmethod
    @app.post("/alarm_receivers/{alarm_receiver_name}/test")
    def alarm_receivers_test(alarm_receiver_name: str, plugin_stdin: typing.Optional[models.PLUGIN_TEST_MODEL] = None):
        
        clearLog()

        # 外部类
        alarm_receiver = plugins.alarm_receivers[alarm_receiver_name]

        # 取出body
        data = plugin_stdin.dict()
        checkModel(data,models.PLUGIN_TEST_MODEL)
        data_body = data.get("body")

        # 获取input
        connection_data = data_body.get("connection")

        output = alarm_receiver._test(connection_data)

        return output


    @staticmethod
    @app.post("/indicator_receivers/{indicator_receiver_name}")
    def indicator_receivers(indicator_receiver_name: str, plugin_stdin: typing.Optional[models.PLUGIN_TEST_MODEL]):
        
        clearLog()
        
        # 外部类
        indicator_receiver = plugins.indicator_receivers[indicator_receiver_name]

        # 取出body
        data = plugin_stdin.dict()
        checkModel(data,models.PLUGIN_TEST_MODEL)
        data_body = data.get("body")

        # 获取input
        input_data = data_body.get("input")
        connection_data = data_body.get("connection")
        dispatcher_url = data_body.get("dispatcher").get("url")

        # 执行　外部run 相关操作
        output = indicator_receiver._run(input_data, connection_data, dispatcher_url)

        return output

    @staticmethod
    @app.post("/indicator_receivers/{indicator_receiver_name}/test")
    def indicator_receivers_test(indicator_receiver_name: str, plugin_stdin: typing.Optional[models.PLUGIN_TEST_MODEL] = None):
        
        clearLog()
        
        # 外部类
        indicator_receiver = plugins.indicator_receivers[indicator_receiver_name]

        # 取出body
        data = plugin_stdin.dict()
        checkModel(data,models.PLUGIN_TEST_MODEL)
        data_body = data.get("body")

        # 获取input
        connection_data = data_body.get("connection")

        output = indicator_receiver._test(connection_data)

        return output

    def runserver(self):
        uvicorn.run(app, host="0.0.0.0", port=10001)


