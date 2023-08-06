
import json
from json import JSONDecodeError
import os
import logging
import time

from pydantic import ValidationError

try:
    from . import models
except:
    import models

####
#
#   集成SDK中各种需要用上的方法
#
####



#   日志数据
log_data = ""

logging.basicConfig(level=logging.INFO,format="[%(asctime)s] %(levelname)s\n  %(message)s",datefmt="%Y-%m-%d %H:%M:%S")

def log(level="debug",msg=""):
    """
    #   设置不同级别的log输出
    参数说明：
    level:str,    #   log等级，levels = debug, info, attention, warning, error, critical
    msg:str,    #   log信息
    """
    global log_data

    msg = str(msg)

    #   输出带颜色log需要执行一次os.system("")
    os.system("")

    if level == "debug":
        
        logging.debug("\033[32m" + msg + "\033[0m")

    elif level == "info": 

        logging.info(msg)

    elif level == "attention":

        logging.info("\033[94m" + msg + "\033[0m")

    elif level == "warning":

        logging.warning("\033[93m" + msg + "\033[0m")

    elif level == "error":

        logging.error("\033[91m" + msg + "\033[0m")

    elif level == "critical":

        logging.critical("\033[91m" + msg + "\033[0m")

    #   时间戳
    log_time = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())

    log_data += f"[{log_time}] {level.upper()}\n  {msg}\n"


def clearLog():
    """
    #   清空日志
    
    docker内多次运行插件时，会产生大量日志，故需要此方法
    """
    global log_data
    log_data = ""


def loadData(path:str) -> dict:
    """
    #   读取json文件内的数据
    参数说明:
    path:str,   #   json文件路径

    返回dict形式的数据
    读取失败时抛出异常
    """
    try:

        if not os.path.exists(path):
            raise Exception(f"路径错误：\n{path}")

        with open(path,"r",encoding="utf-8") as file:

            data = json.load(file)
            #   校验数据格式
            checkModel(data,models.PLUGIN_TEST_MODEL)

        return data

    except JSONDecodeError:
        raise Exception("json数据文件格式转换错误，请检查json文件的格式")

    except Exception as error:
        raise Exception(f"数据文件 {os.path.basename(path)} 读取失败，原因如下：\n{error}")


def checkJsonData(data:dict):
    """
    **此方法暂时弃用**
    #   校验json数据结构
    参数说明：
    data:dict,  #   文件数据

    任何对json数据文件的通用校验方法都在此处添加
    当不符合规范时抛出异常
    """
    if not data:
        raise Exception("json文件内无数据")

    if not data.get("body"):
        raise Exception('json文件内缺少 "body" 参数')


def checkModel(data:dict,model) -> dict:
    """
    #   根据models.py内的校验数据校验data内的参数是否符合要求，并尽可能返回规范化的数据
    参数说明：
    data:dict,  #   数据
    model,      #   校验数据

    注意：数据校验很重要，校验不通过时该方法应当能够立即中断插件的运行，所以请尽可能不要在try内使用此方法

    pydantic库会尝试去规范化进入的数据，即转换原来的数据至规定的格式
    如，123 -> 123.0 （输入为int，规定为float）， False -> "False" （输入为boolean，规定为str）

    校验失败时抛出异常
    """
    try:
        log("info",f"根据 {model.__name__} 校验数据中")

        data = model(**data).json()

        log("info","校验完成")

        return json.loads(data)

    #   pydantic 会在它正在验证的数据中发现错误时引发 ValidationError
    except ValidationError as errors:
        #   当有多个参数验证不通过时，会有多个错误
        errors = json.loads(errors.json())
        error_log = "数据参数验证不通过"
        for error in errors:  
            error_log += f"\n错误参数：{error['loc']}\n错误原因：{error['msg']}"
        raise Exception(error_log)
