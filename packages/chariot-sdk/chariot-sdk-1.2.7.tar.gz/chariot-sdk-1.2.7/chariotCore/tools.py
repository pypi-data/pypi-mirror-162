
import yaml
import os
import logging
import shutil
import jinja2
from typing import *
from chariotCore.templates import *

####
#
#   此文件用于存放task.py中所使用的各种方法
#
####

#   需要添加新的预设类型时，请修改typesDict
types_dict = {
    "string": "str",
    "bytes": "str",
    "boolean": "bool",
    "float": "float",
    "date": "str",
    "object": "dict",
    "password": "str",
    "integer": "int",
    "file": "dict",
    "any": "Any"
    }

module_dict = {
    "actions":"动作",
    "triggers":"触发器",
    "indicator_receivers":"情报接收器",
    "alarm_receivers":"告警接收器"
    }

logging.basicConfig(level=logging.DEBUG,format="")
def log(level="debug",msg=""):
    """
    #   设置不同级别的log输出
    参数说明：
    level:str,    #   log等级，levels = debug, info, attention, warning, error, critical
    msg:str,    #   log信息
    """

    #   输出带颜色log需要执行一次os.system("")
    os.system("")

    if level == "debug":
        logging.debug("\033[32m" + f"{level.upper()} | {msg}" + "\033[0m")

    elif level == "info": 
        logging.info(f"{level.upper()} | {msg}")

    elif level == "attention":
        logging.info("\033[94m" + f"{level.upper()} | {msg}" + "\033[0m")

    elif level == "warning":
        logging.warning("\033[93m\n====================== 警 告 ======================\n\n" + f"{level.upper()} | {msg}" + "\n\n===================================================\n\033[0m")

    elif level == "error":
        logging.error("\033[91m\n====================== 错 误 ======================\n\n" + f"{level.upper()} | {msg}" + "\n\n===================================================\n\033[0m")

    elif level == "critical":
        logging.critical("\033[91m\n=================== 严 重 错 误 ===================\n\n" + f"{level.upper()} | {msg}" + "\n\n===================================================\n\033[0m")


def pathCheck(path:str):
    """
    #   路径检测和文件类型检测
    参数说明：
    path:str,    #   yaml文件绝对路径

    #   检测不通过时抛出异常
    """

    #   路径检测
    if  not os.path.exists(path):
        raise Exception(f"yaml文件路径错误，请检查路径是否正确：\n{path}")
                
    #   文件类型检测
    elif not any(path.endswith(end) for end in ["yml","yaml"]):
        raise Exception(f"文件类型错误，请检查是否为yaml文件：\n{path}")


def readYaml(work_path:str,yaml_path:str) -> dict:
    """
    #   yaml文件读取
    参数说明：
    work_path:str,      #   当前工作区绝对路径
    yaml_path:str,      #   yaml文件相对路径

    #   以dict形式返回yaml中的数据
    #   读取失败时抛出异常
    """

    #   获取yaml文件的绝对路径
    yaml_path = os.path.join(work_path,yaml_path)

    log("info","读取yaml文件中......")

    #   路径检测和文件类型检测
    pathCheck(yaml_path)

    #   打开文件
    try:
        file_readbytes = open(yaml_path,"rb")
        yaml_bytes = file_readbytes.read()
        file_read = open(yaml_path,"r",encoding="utf-8")
        yaml_original = file_read.read()
    except UnicodeDecodeError:
        raise Exception("编码格式错误\n请将yaml文件转成utf-8编码格式")

    except Exception as error:
        raise Exception(f"yaml文件打开失败，错误未知：\n{error}")

    #   换行格式检测
    file_readbytes.close()
    if yaml_bytes.find(b"\r") != -1:
        log("warning",(r"检测到yaml文件中存在'\r'换行符" + "\n请尽量使用LF换行格式，以防不可知的错误"))
    
    #   yaml数据读取
    file_read.close()
    yaml_data = yaml.load(yaml_original, Loader=yaml.FullLoader)
            
    

    #   插件必要元数据检测
    log("debug","检验yaml插件元数据中")
    yamlDataCheck(yaml_data)
    log("debug","插件元数据检验通过")

    log("info",f"yaml文件读取完成")

    return yaml_data


def yamlDataCheck(yaml_data:dict):
    """
    #   插件元数据验证
    参数说明：
    yaml_data:dict,     #   yaml数据

    #   缺失必要参数时抛出异常
    """
    error = ""

    if not yaml_data.get("plugin_spec_version"):
        error+="plugin_spec_version\n"
    if not yaml_data.get("name"):
        error+="name\n"
    if not yaml_data.get("title"):
        error+="title\n"
    if not yaml_data.get("version"):
        error+="version\n"
    if not yaml_data.get("vendor"):
        error+="vendor\n"

    if error:
        error = error[:-1]
        error = "yaml文件中缺失必要参数：\n" + error
        raise Exception(error)

    name = yaml_data.get("name")
    if not name.islower():
        raise Exception(f"插件名称（name）应为全小写：\n{name}")

    if name.find(" ") != -1:
        raise Exception(f'插件名称（name）不能带有空格（" "）\n请用下划线（"_"）代替')


def generateBaseFile(work_path:str):
    """
    #   根据res文件夹的结构生成基础文件
    参数说明：
    work_path:str,    #   当前工作区绝对路径

    #   文件生成失败时抛出异常
    """

    log("info","生成基础文件中")

    #   获取res文件夹
    res_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)),"res")
    #   获取res下每个文件名
    files = os.listdir(res_dir)

    #   逐个遍历生成
    for file_name in files: 
        try:
            #   基础文件
            res = os.path.join(res_dir,file_name)
            #   生成位置
            file_path = os.path.join(work_path,file_name)

            #   若文件存在则跳过生成
            if os.path.exists(file_path):
                log("attention",rf"\{file_name} 已存在，跳过生成")
                continue
            elif os.path.isdir(res):
                shutil.copytree(res,file_path)
            else:
                shutil.copy2(res,file_path)

            log("info",rf"\{file_name} 生成完成")

        except Exception as error:
            raise Exception(rf"\{file_name} 生成失败，错误未知：" + f"\n{error}")

    log("info","基础文件生成完成")

def generateTypesModel(types:dict) -> str:
    """
    #   根据yaml中types参数生成自定义类型的校验内容
    参数说明：
    types:dict,    #   yaml中types参数

    返回需要在models.py文件中写入的所有自定义类型的验证内容
    """
    log("info","生成 自定义类型（types）校验数据中")

    #   所有自定义类型的校验内容
    types_model = ""

    #   获取类名和类的构成参数
    for type_name, type_params in types.items():

        log("info",f"生成 {type_name} 类型校验数据中")

        type_data = {
            #   类名采用全大写
            "className": type_name.upper(),
            #   对类的构成参数进行重构
            "args": yamlSetupData(type_name,type_params)
        }
        #   渲染model字符串
        types_model += renderStrTemplate(type_data, model_template)

        log("info",f"{type_name} 类型校验数据生成完成")

    log("info","自定义类型（types）校验数据生成完成")

    return types_model


def generateConnectionModel(connection_params:dict) -> str:
    """
    #   根据yaml中connection参数生成连接器的入参校验内容
    参数说明：
    connection_params:dict,    #   yaml中connection的载荷

    返回需要在models.py文件中写入的连接器的入参校验内容
    """

    log("info","生成 连接器（connection）校验数据中")

    connection_model = ""

    connection_data = {
        #   类名采用全大写
        "className": "CONNECTION",
        #   对连接器的参数进行重构
        "args": yamlSetupData("connection",connection_params)
        }

    #   渲染model字符串
    connection_model = renderStrTemplate(connection_data,model_template)

    log("info","连接器（connection）校验数据生成完成")

    return connection_model


def generateModel(module:str,module_data:dict) -> str:
    """
    #   根据yaml中各个组件的参数生成组件的入参和出参校验数据
    参数说明：
    module:str,     #   组件，module = actions, triggers, indicator_receivers, alarm_receivers
    actions:dict,    #   yaml中actions参数

    返回需要在models.py文件中写入的动作的入参和出参校验数据
    """

    log("info",f"生成 {module_dict[module]}（{module}）校验数据中")

    model = ""

    for module_key,key_params in module_data.items():

        log("info",f"生成 {module_key} 校验数据中")

        #   获取输入与输出载荷
        input_params = key_params.get("input")
        output_params = key_params.get("output")

        input_class_name = module_key.upper() + "_INPUT"
        output_class_name = module_key.upper() + "_OUTPUT"

        log("info",f"生成 {module_key}: input 校验数据中")
        input_data = {
            #   类名采用全大写
            "className": input_class_name,
            #   对输入的参数进行重构
            "args": yamlSetupData("input",input_params)
            }
        log("info",f"{module_key}: input 校验数据生成完成")

        log("info",f"生成 {module_key}: output 校验数据中")
        output_data = {
            "module":module,
            "className":output_class_name,
            "args": yamlSetupData("output",output_params)
            }
        log("info",f"{module_key}: output 校验数据生成完成")

        model += renderStrTemplate(input_data,model_template)

        #   告警接收器和情报接收器的出参校验数据在转发信息时使用，所以校验数据特殊
        if module == "alarm_receivers":
            model += renderStrTemplate(output_data,alarm_receivers_model_template)
        elif module == "indicator_receivers":
            model += renderStrTemplate(output_data,indicator_receivers_model_template)
        else:
            model += renderStrTemplate(output_data,model_template)

        log("info",f"{module_key} 校验数据生成完成")

    log("info",f"{module_dict[module]}（{module}）校验数据生成完成")

    return model


def generateModelFile(work_path:str,model_module:str,model_data:str):
    """
    #   根据目录及校验数据生成校验文件model.py
    参数说明：
    work_path:str,    #   当前工作区绝对路径
    model_module:str,     #   校验的组件，model_module = actions, triggers, indicator_receivers, alarm_receivers
    model_data:str,     #   校验数据

    文件生成失败时抛出异常
    """

    log("info",rf"生成 {model_module}\models.py 校验文件中")

    try:
        #   生成校验对象的文件夹
        path = os.path.join(work_path,model_module)
        if not os.path.exists(path):
            os.mkdir(path)

        #   生成校验文件
        file_path = os.path.join(path,"models.py")
        #   覆盖原有文件
        with open(file_path,"w",encoding="utf-8",newline="\n") as file:
            file.write(model_data)

    except Exception as error:
        raise Exception(rf"{model_module} 的校验文件（models.py）生成失败，错误未知：" + f"\n{error}")

    log("info",rf"{model_module}\models.py 校验文件生成完成")


def generateModuleFile(work_path:str,module:str,module_data:dict,connection_keys:list) -> list:
    """
    #   生成所有功能的运行文件
    参数说明：
    work_path:str,    #   当前工作区绝对路径
    module:str,     #   组件，module = actions, triggers, indicator_receivers, alarm_receivers
    module_data:dict,    #   yaml中组件的参数
    connection_keys:list,   #   连接器参数列表

    返回功能列表 key_list，用于生成入口文件 main.py
    文件生成失败时抛出异常
    """

    #   用于记录要在初始化文件（__init__.py）中写入的功能导入（import）
    init_list = []

    #   功能列表 key_list，用于生成入口文件 main.py
    key_list = []

    log("info",f"生成 {module_dict[module]}（{module}）所有功能中")

    #   遍历组件内每一个功能和功能的参数
    for module_key,params in module_data.items():
        try:

            log("info",rf"生成 {module}\{module_key}.py 文件中")

            key_data = {}

            #   根据不同组件使用不同的文件生成模板
            if module == "actions":
                #   功能名采用全大写
                key_class_name = module_key.upper() + "_ACTION"
                key_data["actionsName"] = key_class_name

                init_list.append([module_key,key_class_name])

                if params.get("input"):
                    input_keys = list(params["input"].keys())
                else:
                    input_keys = []

                key_template = action_template
                key_test_template = actions_test_template

            elif module == "triggers":

                key_class_name = module_key.upper() + "_TRIGGER"
                key_data["triggersName"] = key_class_name

                init_list.append([module_key,key_class_name])

                if params.get("input"):
                    input_keys = list(params["input"].keys())
                else:
                    input_keys = []

                key_template = triggers_template
                key_test_template = triggers_test_template

            elif module == "indicator_receivers":

                key_class_name = module_key.upper() + "_INDICATOR_RECEIVER"
                key_data["indicator_receiversName"] = key_class_name

                init_list.append([module_key,key_class_name])
                
                if params.get("input"):
                    input_keys = list(params["input"].keys())
                else:
                    input_keys = []

                key_template = indicator_receivers_template
                key_test_template = indicator_receivers_test_template

            elif module == "alarm_receivers":

                key_class_name = module_key.upper() + "_ALARM_RECEIVER"
                key_data["alarm_receiversName"] = key_class_name

                init_list.append([module_key,key_class_name])
                
                if params.get("input"):
                    input_keys = list(params["input"].keys())
                else:
                    input_keys = []

                key_template = alarm_receivers_template
                key_test_template = alarm_receivers_test_template

            #   功能列表，用于生成入口文件 main.py
            key_list.append(key_class_name)

            #   设置input, output类名
            input_class_name = module_key.upper() + "_INPUT"
            output_class_name = module_key.upper() + "_OUTPUT"

            key_data.update({
                "name": module_key,
                "inputModel": input_class_name,
                "outputModel": output_class_name,
                "connModel": "CONNECTION",
                "connetionKeys":connection_keys,
                "inputKeys":input_keys
                })

            #   渲染组件内不同功能文件内容
            key = renderStrTemplate(key_data,key_template)
            key_path = os.path.join(work_path,module)
            file_path = os.path.join(key_path,f"{module_key}.py")

            #   当功能文件存在时不写入，以防覆盖原本已写的功能
            if not os.path.exists(file_path):
                with open(file_path,"w",encoding="utf-8",newline="\n") as file:
                    file.write(key)   
            else:
                log("attention",rf"{module}\{module_key}.py 已存在，已跳过生成")
                
            log("info",rf"{module}\{module_key}.py 生成完成")

        except Exception as error:
            raise Exception(rf"{module}\{module_key}.py 生成失败，原因未知：" + f"\n{error}")


        try:

            log("info",rf"生成 tests\{module_key}.json 测试文件中")

            #   渲染动作测试文件内容
            test = renderStrTemplate({"title":module_key},key_test_template)

            tests_path = os.path.join(work_path,"tests")
            file_path = os.path.join(tests_path,f"{module_key}.json")
            #   当测试文件存在时不写入，以防覆盖原本的测试数据
            if not os.path.exists(file_path):
                with open(file_path,"w",encoding="utf-8",newline="\n") as file:
                    file.write(test)         

            else:
                log("attention",rf"tests\{module_key}.json 测试文件已存在，已跳过生成")

            log("info",rf"tests\{module_key}.json 测试文件生成完成")

        except Exception as error:
            raise Exception(f"{module_key}.json 动作测试文件生成失败，原因未知：" + f"\n{error}")


    try:

        log("info",rf"生成 初始化文件 {module}\__init__.py 中")
        file_path = os.path.join(key_path,"__init__.py")
        init = renderStrTemplate({"init_list":init_list},init_template)
        with open(file_path,"w",encoding="utf-8",newline="\n") as file:
            file.write(init)
        log("info",rf"初始化文件 {module}\__init__.py 生成完成")

    except Exception as error:
        raise Exception(rf"初始化文件 {module}\__init__.py 生成失败，原因未知：" + f"\n{error}")


    log("info",f"{module_dict[module]}（{module}）所有功能生成完成")
    
    return key_list


def updateModuleFile(work_path:str):
    """
    #   对1.2.6版本sdk做的actions, triggers, alarm_receivers, indicator_receivers进行兼容性改动
    主要改动为规范化类名
    参数说明：
    work_path:str,    #   当前工作区绝对路径

    **该方法预计在将来某一个版本中会被删除**

    改动失败时抛出异常
    """
    modules = ["action", "trigger", "alarm_receiver", "indicator_receiver"]

    try:

        #   遍历每一个模块
        for module in modules:
            path = os.path.join(work_path,module + "s")

            if os.path.exists(path):
                files = os.listdir(path)

                #   遍历每一个文件
                for file in files:

                    #   排除可能存在的缓存文件
                    if file.endswith(".py") and file != "models.py":
                        file_path = os.path.join(path,file)

                        with open(file_path,"r",encoding="utf-8") as f:
                            data = f.read()

                            #   旧文件一般类名命名方式都是 f"{功能名}{模块名}S"，如
                            #   "EXAMPLEACTIONS"，模块名不够清晰，因此需要规范
                            #   新文件类命名方式则采用 f"{功能名}_{模块名}"，如 "EXAMPLE_ACTION"

                            if data.find(module.upper() + "S") != -1 and data.find("_" + module.upper()) == -1:

                                log("attention",rf"检测到旧版本的功能文件 \{module}\{file}，执行兼容性更新")

                                data = data.replace(module.upper() + "S","_" + module.upper())
                                data = data.replace("INPUT","_INPUT")
                                data = data.replace("OUTPUT","_OUTPUT")
                                data = data.replace(" Core\r\n"," *\r\n")   #   CRLF
                                data = data.replace(" Core\n"," *\n")   #   LF
                                data = data.replace("# 初始化\r\n",
                                                    "# 初始化\r\n        super().__init__()\r\n") #   CRLF
                                data = data.replace("# 初始化\n",
                                                    "# 初始化\n        super().__init__()\n") #   LF

                                log("attention","兼容性更新完成")

                        with open(file_path,"w",encoding="utf-8") as f:
                            f.write(data)
            else:
                pass
    except Exception as error:
        raise Exception(f"兼容措施执行失败，错误未知：\n{error}")


def generateMainFile(work_path:str,plugin_name:str,
                     actions_list:list,
                     triggers_list:list,
                     indicator_receivers_list:list,
                     alarm_receivers_list:list):
    """
    #   生成入口文件
    参数说明：
    work_path:str,      #   当前工作区绝对路径
    plugin_name:str,    #   插件名称
    actions_list:list,      #   动作列表
    triggers_list:list,     #   触发器列表
    indicator_receivers_list:list,      #   情报接收器列表
    alarm_receivers_list:list,          #   告警接收器列表

    生成失败时抛出异常
    """

    log("info","生成入口文件 \main.py 中")

    try:
        main_data = {
            "pluginName": plugin_name.upper() + "_PLUGIN",
            "actionClassees": actions_list,
            "triggerClassees": triggers_list,
            "indicatorReceiverClassees": indicator_receivers_list,
            "alarmReceiverClassees": alarm_receivers_list
            }

        file_path = os.path.join(work_path,"main.py")

        main_data = renderStrTemplate(main_data,main_template)

        with open(file_path,"w",encoding="utf-8",newline="\n") as file:
            file.write(main_data)

    except Exception as error:
        raise Exception(r"入口文件 \main.py 生成失败，错误未知：" + f"\n{error}")

    log("info",r"入口文件文件 \main.py 生成完成")


def generateHelpFile(work_path:str,yaml_data:dict):
    """
    #   生成帮助文件
    参数说明：
    work_path:str,      #   当前工作区绝对路径
    yaml_data:dict,     #   yaml文件数据

    **此方法生成的文件基本用不上，预计在将来版本删除**

    生成失败时抛出异常
    """

    log("info",r"生成帮助文件 \help.md 中")

    try:
        file_path = os.path.join(work_path,"help.md")
        help_data = renderStrTemplate(yaml_data,help_template)
        with open(file_path,"w",encoding="utf-8",newline="\n") as file:
            file.write(help_data)

    except Exception as error:
        raise Exception(r"生成帮助文件 \help.md 失败，原因未知：" + f"\n{error}")

    log("info",r"帮助文件 \help.md 生成完成")


def generateUtilFile(work_path:str):
    """
    #   生成通用文件存储的文件夹，在此文件夹下放置各个功能需要共用的方法
    参数说明：
    work_path:str,      #   当前工作区绝对路径

    生成失败时抛出异常
    """

    log("info",r"生成通用文件存储文件夹 \util 中")

    try:
        util_path = os.path.join(work_path,"util")

        if not os.path.exists(util_path):
            os.mkdir(util_path)
        else:
            log("attention",r"\util 文件夹已存在，已跳过生成")

    except Exception as error:
        raise Exception(r"通用文件存储文件夹 \util 失败，原因未知：" + f"\n{error}")

    log("info",r"通用文件存储文件夹 \util 生成完成")


def generateTestServerFile(work_path:str,
                           actions_list:list,
                           triggers_list:list,
                           indicator_receivers_list:list,
                           alarm_receivers_list:list):
    """
    #   生成本地REST测试服务器文件
    参数说明：
    work_path:str,      #   当前工作区绝对路径
    actions_list:list,      #   动作列表
    triggers_list:list,     #   触发器列表
    indicator_receivers_list:list,      #   情报接收器列表
    alarm_receivers_list:list,          #   告警接收器列表

    生成失败时抛出异常
    """

    log("info",r"生成本地REST测试服务器数据文件 \testserver.py 中")

    testserver_file_content = testserver_head_template

    if actions_list:

        testserver_file_content = "\nfrom actions import *" + testserver_file_content
  
        for action in actions_list:

            action_data = {
                "class_name":action,
                "name":action.replace("_ACTION","").lower()
                }

            testserver_file_content += renderStrTemplate(action_data,testserver_actions_template)

    if triggers_list:

        testserver_file_content = "\nfrom triggers import *" + testserver_file_content

        for trigger in triggers_list:

            trigger_data = {
                "class_name":trigger,
                "name":trigger.replace("_TRIGGER","").lower()
                }

            testserver_file_content += renderStrTemplate(trigger_data,testserver_triggers_template)

    if indicator_receivers_list:

        testserver_file_content = "\nfrom indicator_receivers import *" + testserver_file_content

        for indicator_receiver in indicator_receivers_list:

            indicator_receiver_data = {
                "class_name":indicator_receiver,
                "name":trigger.replace("_INDICATOR_RECEIVER","").lower()
                }

            testserver_file_content += renderStrTemplate(indicator_receiver_data,testserver_indicator_receivers_template)
            
    if alarm_receivers_list:

        testserver_file_content = "\nfrom alarm_receivers import *" + testserver_file_content

        for alarm_receiver in alarm_receivers_list:

            alarm_receiver_data = {
                "class_name":alarm_receiver,
                "name":alarm_receiver.replace("_ALARM_RECEIVER","").lower()
                }

            testserver_file_content += renderStrTemplate(alarm_receiver_data,testserver_alarm_receivers_template)

    testserver_file_content += testserver_tail_template

    try:

        testserver_file_path = os.path.join(work_path,"testserver.py")

        with open(testserver_file_path,"w",encoding="utf-8") as file:

            file.write(testserver_file_content)

    except Exception as error:
        raise Exception("本地REST测试服务器数据文件 \testserver.py 生成失败")

    log("info",r"本地REST测试服务器数据文件 \testserver.py 生成完成")


def yamlSetupData(param_name:str,params:dict) -> list:   
    """
    #   整理构成参数方便调用
    参数说明：
    param_name:str,     #   集合名称（自定义类名称、输入集合名称、输出集合名称）
    params:dict,    #   构成参数

    将构成参数整理成：
    [['值1', "Literal['枚举值1','枚举值2'] = 默认值"], ['值2', '类型 = 默认值'],['值3','Optional[List[类型]] = 默认值']]

    例如：
    [['value1', 'dict = None'], ['value2', "Literal['123', '321'] = None"]]

    构成参数中的关键数据：
    构成参数的类型（type）   #   在出现枚举集合时，可缺失，其他情况下不可缺失
    是否必填（required）  #   可缺失，缺省为False
    默认值（default）    #   可缺失，缺省为None
    枚举集合（enum）   #   可缺失，缺省为None
    """
    params_list = []
    
    if params:
        #   从构成参数中提取必要的数据
        for value,value_param in params.items():
            
            #   构成参数的类型
            value_type = value_param.get("type")

            #   是否必填
            value_required = value_param.get("required", False)

            #   默认值
            value_default = value_param.get("default")

            #   枚举值
            value_enum = value_param.get("enum")

            #   检验构成参数的必要数据是否符合规范
            log("debug",f"检验 {value} 的构成参数中")
            paramsCheck(value_type,value_default,value_enum)
            log("debug",f"{value} 的构成参数检验通过")

            #   根据typesDict将不同类型转换成python中的类型，在默认值和枚举集合存在时附加两者
            value_type = typeTransform(value_type, value_required, value_default, value_enum)

            params_list.append([value, value_type])

    else:
        log("attention",f"{param_name} 为空，已跳过 {param_name} 校验数据生成")
            
    return params_list


def paramsCheck(value_type: None, value_default: None, value_enum: None):
    """
    #   检验构成参数的必要数据是否符合规范
    参数说明：
    value_type,     #   参数类型
    value_default:,    #   构成参数的默认值
    value_enum,     #   构成参数的枚举集合

    #   检验不通过时抛出异常
    """
    if not value_type and not value_enum:
        raise Exception(f"类型与枚举集合都为空\n类型（type）与枚举集合（enum）请至少填写一项")
    
    if value_type and not types_dict.get(value_type):
        if value_type.startswith("[]") and not types_dict.get(value_type[2:]):
            log("attention",f"未知类型的列表组合：{value_type}，如果是自定义类型请忽略此信息")
        elif not value_type.startswith("[]") and not types_dict.get(value_type[2:]):
            log("attention",f"未知的类型：{value_type}，如果是自定义类型请忽略此信息")

    if value_enum and not isinstance(value_enum,list):
        raise Exception("枚举集合（enum）填写不符合规范")

    if value_default and value_enum and value_default not in value_enum:
        raise Exception(f"默认值 {value_default}\n无法在枚举的集合中找到")

    if value_enum == []:
        raise Exception("枚举集合为空集：[]")


def typeTransform(value_type: str, value_required: bool, value_default: None, value_enum: None):
    """
    #   根据typesDict将不同类型转换成python中的类型，在默认值和枚举集合存在时附加两者
    参数说明：
    value_type:str,     #   参数类型
    value_default:Any type,    #   构成参数的默认值
    value_enum:list,     #   构成参数的枚举集合

    默认值在 required = true 且无 default 参数时为空，默认值在 required = false 时且无 default 参数时为None

    例如：
    ['error1', 'dict =  None']
    ['error_code1', "Literal[['123', '321'], ['124', '321']]"]
    ['error2','Optional[List[dict]] = None']
    ['error_code2', 'Optional[List[TEST_TYPE]] = None']
    ['error_code2', "Literal['123','321'] = None"]
    """
    #   存在枚举集合时
    if value_enum:
        argType = f"Literal{value_enum}"

    #   非枚举集合时，尝试从typeDict中获取预设类
    else:
        argType = types_dict.get(value_type)

    #   无法直接获取到预设类
    if not argType:

        #   是否为列表
        if value_type.startswith("[]"):

            #   查看是否为预设类的列表形式
            #   Optional，意为此参数可以为None或已经声明的类型
            if types_dict.get(value_type[2:]):
                #   预设类的列表形式将直接取预设类型的 列表 形式
                argType = f"Optional[List[{types_dict.get(value_type[2:])}]]"
            else:
                #   非预设类的列表形式将取自定义类型的全大写的 列表 形式
                argType = f"Optional[List[{value_type[2:].upper()}]]"

        else:
            #   非预设类直接采用自定义类型的全大写形式
            argType = value_type.upper()

    #   不需要必填且没有默认值时，则默认值给None，这样在运行测试时，非必填的参数能够通过参数校验
    if not value_required and value_default == None:
        argType += " = None"

    #   当存在默认值时，则给默认值
    elif value_default != None:
        #   注意，当默认值为字符串时，要加 ""
        if isinstance(value_default,str):
            argType += f' = "{value_default}"'
        else:
            argType += f" = {value_default}"

    return argType


def renderStrTemplate(data:dict,template):
    """
    #   根据template.py内的模板渲染字符串
    参数说明：
    data,     #     需要渲染的数据
    template,    #      渲染的模板
    """
    template = jinja2.Template(template)
    res = template.render(data)

    return res