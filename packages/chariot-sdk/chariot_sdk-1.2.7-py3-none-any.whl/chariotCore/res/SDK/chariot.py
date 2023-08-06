
import json

try:
    from .web import *
    from .base import *
except:
    from web import *
    from base import *

def run(data:dict, plugin_object):
    """
    #   运行功能的整个流程
    参数说明：
    data:dict,      #   运行功能时的必要的json数据
    plugin_object:PLUGIN,      #   插件集合对象（类位于生成的插件后的根目录下main.py文件内）

    """
    
    log("info","尝试获取数据中的 body")

    #   必要的参数位于data内的body下
    data_body = data.get("body")
    if not data_body:
        log("error","body 为空")
        return

    log("info","检测需要运行的组件")
    #   检查json数据是使用在哪个组件上的
    if data_body.get("action"):
        runAction(data_body["action"],data_body,plugin_object)

    elif data_body.get("trigger"):
        runTrigger(data_body["trigger"],data_body,plugin_object)

    elif data_body.get("alarm"):
        runAlarmReceiver(data_body["alarm"],data_body,plugin_object)

    elif data_body.get("receiver"):
        runIndicatorReceiver(data_body["receiver"],data_body,plugin_object)

    else:
        log("info","未检测到需要运行的组件")


def runAction(action_name:str,data:dict,plugin_object):
    """
    #   运行动作
    参数说明：
    action_name:str,    #动作名
    data:dict,      #   运行功能时的必要的数据
    plugin_object:PLUGIN,      #   插件集合对象（类位于生成的插件后的根目录下main.py文件内）

    出现异常时，会将异常信息放入log，但不会抛出异常
    """
    log("info","运行 动作(Action) 中")

    #   根据动作名在插件根目录下的 main.py 文件内的动作列表内选取对应的动作类，并初始化一个对象
    action = plugin_object.actions[action_name]
    #   获取连接器数据
    connection_data = data.get("connection")
    #   获取入参
    input_data = data.get("input")

    action._run(input_data,connection_data)

    log("info","动作(Action) 运行结束")


def runTrigger(trigger_name:str,data:dict,plugin_object):
    """
    #   运行触发器
    参数说明：
    action_name:str,    #动作名
    data:dict,      #   运行功能时的必要的数据
    plugin_object:PLUGIN,      #   插件集合对象（类位于生成的插件后的根目录下main.py文件内）

    出现异常时，会将异常信息放入log，但不会抛出异常
    """
    log("info","运行 触发器(Trigger) 中")

    enable_web = data.get("enable_web")

    #   使用web服务
    if enable_web:

        server = Server(plugin_object)
        server.runserver()

    else:
        #   根据动作名在插件根目录下的 main.py 文件内的动作列表内选取对应的动作类，并初始化一个对象
        trigger = plugin_object.triggers[trigger_name]

        connection_data = data.get("connection")

        input_data = data.get("input")

        dispatcher_url = data.get("dispatcher").get("url")

        trigger._run(input_data,connection_data,dispatcher_url)

    log("info","触发器(Trigger) 运行结束")

def runAlarmReceiver(alarm_receiver_name:str,data:dict,plugin_object):
    """
    #   运行告警接收器
    参数说明：
    action_name:str,    #动作名
    data:dict,      #   运行功能时的必要的数据
    plugin_object:PLUGIN,      #   插件集合对象（类位于生成的插件后的根目录下main.py文件内）

    出现异常时，会将异常信息放入log，但不会抛出异常
    """
    log("info","运行 告警接收器(Alarm Receiver) 中")

    enable_web = data.get("enable_web")

    #   使用web服务
    if enable_web:

        server = Server(plugin_object)
        server.runserver()

    else:
        #   根据动作名在插件根目录下的 main.py 文件内的动作列表内选取对应的动作类，并初始化一个对象
        alarm_receiver = plugin_object.alarm_receivers[alarm_receiver_name]

        connection_data = data.get("connection")

        input_data = data.get("input")

        dispatcher_url = data.get("dispatcher").get("url")

        alarm_receiver._run(input_data,connection_data,dispatcher_url)


    log("info","告警接收器(Alarm Receiver) 运行结束")

def runIndicatorReceiver(indicator_receiver_name:str,data:dict,plugin_object):
    """
    #   运行情报接收器
    参数说明：
    action_name:str,    #动作名
    data:dict,      #   运行功能时的必要的数据
    plugin_object:PLUGIN,      #   插件集合对象（类位于生成的插件后的根目录下main.py文件内）

    出现异常时，会将异常信息放入log，但不会抛出异常
    """
    log("info","运行 情报接收器(IndicatorReceiver) 中")

    enable_web = data.get("enable_web")

    #   使用web服务
    if enable_web:

        server = Server(plugin_object)
        server.runserver()

    else:
        #   根据动作名在插件根目录下的 main.py 文件内的动作列表内选取对应的动作类，并初始化一个对象
        indicator_receiver = plugin_object.indicator_receivers[indicator_receiver_name]

        connection_data = data.get("connection")

        input_data = data.get("input")

        dispatcher_url = data.get("dispatcher").get("url")

        indicator_receiver._run(input_data,connection_data,dispatcher_url)

    log("info","情报接收器(IndicatorReceiver) 运行结束")

def test(data:dict,plugin_object):
    """
    #   只运行连接器部分
    参数说明：
    data:dict,      #   运行功能时的必要的json数据
    plugin_object:PLUGIN,      #   插件集合对象（类位于生成的插件后的根目录下main.py文件内）
    """
    #   必要的参数位于data内的body下
    data_body = data.get("body",{})
    connection_data = data_body.get("connection")

    #   检查json数据是使用在哪个组件上的
    if data_body.get("action"):
        action_name = data_body["action"]
        action = plugin_object.actions[action_name]
        action._test(connection_data)

    elif data_body.get("trigger"):
        trigger_name = data_body["trigger"]
        trigger = plugin_object.triggers[trigger_name]
        trigger._test(connection_data)

    elif data_body.get("alarm"):
        alarm_name = data_body["alarm"]
        alarm = plugin_object.alarm_receivers[alarm_name]
        alarm._test(connection_data)

    elif data_body.get("receiver"):
        receiver_name = data_body["receiver"]
        receiver = plugin_object.indicator_receivers[receiver_name]
        receiver._test(connection_data)


def http(plugin_object):
    """
    #   启动rest服务接口
    参数说明：
    plugin_object:PLUGIN,      #   插件集合对象（类位于生成的插件后的根目录下main.py文件内）
    """
    server = Server(plugin_object)
    server.runserver()