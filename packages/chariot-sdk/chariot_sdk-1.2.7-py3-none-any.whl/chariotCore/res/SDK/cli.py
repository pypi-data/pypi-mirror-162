
try:
    from .base import *
    from .chariot import *
except:
    from base import *
    from chariot import *

import sys
import json

def client(plugin):
    """
    #   此方法用于作为起始，根据命令跳转到各个功能
    参数说明：
    plugin:PLUGIN,      #   插件集合类（该类位于生成的插件后的根目录下main.py文件内）

    """
    log("info","正在启动插件")

    #   获取命令
    log("info","获取执行参数：{}".format(sys.argv))
    command = sys.argv[1]

    #   初始化一个插件类对象，此类位于生成插件后的插件根目录下的main.py里
    #   该对象在初始化后会存储所有功能的类
    plugin_object = plugin()
        
    if command == 'run':
        data = getData()
        if not data:
            return
        log("info","执行 run 命令")
        run(data, plugin_object)    

    elif command == "http":
        log("info","执行 http 命令")
        http(plugin_object)

    elif command == 'test':
        data = getData()
        if not data:
            return
        log("info","执行 test 命令")
        test(data, plugin_object)

    else:
        log("error","未知的命令：{}".format(command))
        return

def getData() -> dict:
    """
    #   此方法用于获取需要的运行数据
    #   在千乘系统中，可能并不会传入json数据文件的路径，而是会直接传入json数据或字典数据，此时输入cmd指令长度不足（输入数据不计长度）
    #   所以使用sys.stdin.read()读取可能存在的数据
    """
    if len(sys.argv) >= 3:
        testfile_path = sys.argv[2]
        data = loadData(testfile_path)
    else:
        data = sys.stdin.read()
        if type(data) != dict and data:
            data = json.loads(data)

    if data:
        log("info","获取执行载荷：\n{}".format(data))
        return data
    else:
        log("error","未检测到必要的运行数据")
        return {}

