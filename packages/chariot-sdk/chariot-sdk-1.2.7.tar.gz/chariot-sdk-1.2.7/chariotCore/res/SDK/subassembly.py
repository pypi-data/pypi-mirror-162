

try:
    from .base import *
except:
    from base import *

import traceback
import requests


class Actions(object):

    def __init__(self):

        self._output = {
            "version": "v1",
            "type": "action_event",
            "body":{}
            }

        #   name 按规范应小写且用下划线隔开单词
        self.name = ""

        #   入参 校验类
        self.inputModel = None

        #   出参 校验类
        self.outputModel = None

        #   连接器 校验类
        self.connModel = None


    def connection(self, data:dict):

        ...


    def run(self, params):

        ...


    def _test(self,connection_data):
        """
        #   运行连接器
        参数说明：
        conection_data:dict,    #   连接数据

        此过程用方法单独写出来方便测试连接器部分
        """
        
        log("info",f"获取连接器数据：\n{connection_data}")

        #   校验入参数据
        log("info","校验连接器数据")
        checkModel(connection_data,self.connModel)
        
        log("info","运行连接器中")

        try:
            self.connection(connection_data)
            log("info","连接器运行正常")
            log("info","构建连接器运行信息")
            output = self._buildOutput({},True)
            return output

        except Exception as error:
            #   收集错误信息
            log("error",f"连接器发生异常，错误原因：\n  {error}")

            error_trace = traceback.format_exc()
            log("error",f"详细错误信息：\n{error_trace}")

            log("info","构建连接器错误信息")
            output = self._buildOutput({},False,error_trace)
            return output

        

    def _run(self, input_data:dict, connection_data:dict):
        """
        #   运行全流程
        参数说明：
        input_data:dict,    #   入参数据
        conection_data:dict,    #   连接数据
        """
        log("info","插件运行中")

        #   运行connection
        output = self._test(connection_data)

        #   连接器异常时直接返回错误输出
        if output["body"]["status"] == "False":
            return output

        #   运行run
        try:

            log("info",f"获取功能数据：\n{input_data}")

            #   校验功能数据
            log("info","校验功能入参数据")
            checkModel(input_data, self.inputModel)

            log("info","执行功能中")

            output_data = self.run(input_data)

            log("info","功能执行完成")

        except Exception as error:
            #   收集错误信息
            log("error",f"功能执行异常，错误原因：\n  {error}")

            error_trace = traceback.format_exc()
            log("error",f"详细错误信息：\n{error_trace}")

            #   构建错误输出的output
            log("info","构建错误返回信息")
            output = self._buildOutput({},False,error_trace)

        else:
            #   当运作正常时才需要做出参验证
            log("info","校验功能出参数据")
            checkModel(output_data, self.outputModel)
            #   构建output
            log("info","构建输出数据")
            output = self._buildOutput(output_data,True)

        return output


    def _buildOutput(self,output_data:dict={},status:bool=True,error_trace:str=""):
        """
        #   构建出参信息，包括日志信息
        参数说明：
        output_data:dict,   #   输出信息
        status:bool,    #   run执行状态，执行成功为True，不成功为False
        error_trace:str,  #   详细的错误信息，用于给开发人员看
        """

        try:
            from .base import log_data
        except:
            from base import log_data

        output = self._output

        output["body"]["output"] = output_data

        output["body"]["status"] = str(status)
        output["body"]["log"] = log_data
        output["body"]["error_trace"] = error_trace

        print(output)

        return output

    
    def _popEmpty(self,params):
        """
        #   采用深度遍历算法剔除载荷中的所有空参数，注意是所有！！！
        #   空参数包括："",{},None,[]
        参数说明：
        params:dict/list,   #   需要剔除空参数的字典或列表

        返回剔除完毕的字典或列表
        """
        params_temp = params.copy()
        if type(params) == dict:
            for key in params:
                if type(params[key]) in [list,dict]:
                    params_temp[key] = self._popEmpty(params_temp[key])
                if params_temp[key] in ["",{},None,[]]:
                    params_temp.pop(key)
            return params_temp
        if type(params) == list:
            for l in range(len(params)):
                if params[l] in ["",{},None,[]]:
                    params_temp.pop(l)
                    return self._popEmpty(params_temp)
                if type(params_temp[l]) in [list,dict]:
                    params_temp[l] = self._popEmpty(params_temp[l])
        return params_temp


class Triggers(object):

    def __init__(self):

        self._output = {
            "version": "v1",
            "type": "trigger_event",
            "body":{}
            }

        #   name 按规范应小写且用下划线隔开单词
        self.name = ""

        #   缓存uid
        self.cache_uid = ""

        #   发送到
        self.dispatcher_url = ""

        #   入参 校验类
        self.inputModel = None

        #   出参 校验类
        self.outputModel = None

        #   连接器 校验类
        self.connModel = None


    def connection(self, data:dict):

        ...

    def run(self, params):

        ...

    def _test(self,connection_data):
        """
        #   运行连接器
        参数说明：
        conection_data:dict,    #   连接数据
        """
        
        log("info",f"获取连接器数据：\n{connection_data}")

        #   校验入参数据
        log("info","校验连接器数据")
        checkModel(connection_data,self.connModel)

        log("info","运行连接器中")

        try:
            self.connection(connection_data)
            log("info","连接器运作正常")
            log("info","构建连接器运行信息")
            output = self._buildOutput({},True)
            return output

        except Exception as error:
            #   收集错误信息
            log("error",f"连接器异常，错误原因：\n  {error}")

            error_trace = traceback.format_exc()
            log("error",f"详细错误信息：\n{error_trace}")

            log("info","构建连接器错误信息")
            output = self._buildOutput({},False,error_trace)
            return output

    def _run(self,input_data,connection_data,dispatcher_url):
        """
        #   运行全流程
        参数说明：
        input_data:dict,    #   入参数据
        conection_data:dict,    #   连接数据
        """
        log("info","插件运行中")

        self.dispatcher_url = dispatcher_url

        #   运行connection
        output = self._test(connection_data)

        #   连接器异常时直接返回错误输出
        if output["body"]["status"] == "False":
            return output

        #   运行run
        try:
            
            log("info",f"获取功能数据：\n{input_data}")

            #   校验入参数据
            log("info","校验入参数据")
            checkModel(input_data,self.inputModel)

            log("info","执行功能中")

            #   正常情况下，触发器、情报接收器、告警接收器都是处于轮询状态，不会主动跳出
            self.run(input_data)

            log("info","功能执行完成")

        except Exception as error:
            #   收集错误信息
            log("error",f"功能执行异常，错误原因：\n  {error}")

            error_trace = traceback.format_exc()
            log("error",f"详细错误信息：\n{error_trace}")

            #   构建错误输出的output
            log("info","构建错误返回信息")
            output = self._buildOutput({},False,error_trace)

        else:
            output = self._buildOutput({},True)

        return output


    def send(self,data:dict={},needCheck:bool=True):
        """
        #   转发信息
        参数说明：
        data:dict,  #   需要转发的信息
        needCheck:bool, #   是否需要对转发的信息进行出参验证

        """
        #   触发器、情报接收器、告警接收器的出参数据在转发时进行验证
        if needCheck:
            checkModel(data, self.outputModel)

        log("info","转发数据中：\n{}".format(data))

        response = requests.post(self.dispatcher_url,json=data,verify=False)

        log("info",f"发送完成，状态码：{response.status_code}\n  返回信息：{response.text}")

        return response

    def _buildOutput(self,output_data:dict={},status:bool=True,error_trace:str=""):
        """
        #   构建出参信息，包括日志信息
        参数说明：
        output_data:dict,   #   输出信息
        status:bool,    #   run执行状态，执行成功为True，不成功为False
        error_trace:str,  #   详细的错误信息，用于给开发人员追踪错误
        """

        try:
            from .base import log_data
        except:
            from base import log_data

        output = self._output
        output["body"]["output"] = output_data

        output["body"]["status"] = str(status)
        output["body"]["log"] = log_data
        output["body"]["error_trace"] = error_trace

        print(output)

        return output


    def _popEmpty(self,params):
        """
        #   采用深度遍历算法剔除载荷中的所有空参数，注意是所有！！！
        #   空参数包括："",{},None,[]
        参数说明：
        params:dict/list,   #   需要剔除空参数的字典或列表

        返回剔除完毕的字典或列表
        """
        params_temp = params.copy()
        if type(params) == dict:
            for key in params:
                if type(params[key]) in [list,dict]:
                    params_temp[key] = self._popEmpty(params_temp[key])
                if params_temp[key] in ["",{},None,[]]:
                    params_temp.pop(key)
            return params_temp
        if type(params) == list:
            for l in range(len(params)):
                if params[l] in ["",{},None,[]]:
                    params_temp.pop(l)
                    return self._popEmpty(params_temp)
                if type(params_temp[l]) in [list,dict]:
                    params_temp[l] = self._popEmpty(params_temp[l])
        return params_temp


class IndicatorReceivers(Triggers):
    """
    #   情报接收器目前实现原理上和触发器没有区别
    """
    def __init__(self):
        super().__init__()
        self._output["type"] = "indicator_receiver_event"


class AlarmReceivers(Triggers):
    """
    #   告警接收器目前实现原理上和触发器没有区别
    """  
    def __init__(self):
        super().__init__()
        self._output["type"] = "alarm_receiver_event"

