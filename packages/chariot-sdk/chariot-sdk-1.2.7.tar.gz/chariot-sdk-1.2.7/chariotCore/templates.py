

model_header = """
from pydantic import BaseModel
from typing import *

# 可自行修改增加校验精准度

"""

model_template = """
class {{ className }}(BaseModel):
    {% if args %}{% for argName, argType in args %}
    {{ argName }}: {{ argType }}
    {% endfor %}{% else %}
    ...
    {% endif %}"""

action_template = """
from SDK.subassembly import Actions
from SDK.base import *

from .models import {{ connModel }}, {{ inputModel }}, {{ outputModel }}



class {{ actionsName }}(Actions):

    def __init__(self):
        #   初始化
        super().__init__()
        self.name = "{{ name }}"
        self.inputModel = {{ inputModel }}
        self.outputModel = {{ outputModel }}
        self.connModel = {{ connModel }}


    def connection(self, data={}):
        #   write your code
        {% if connetionKeys %}{% for key in connetionKeys %}
        {{ key }} = data.get("{{ key }}"){% endfor %}{% else %}
        ...    
        {% endif %}
    
    def run(self, params={}):
        #   write your code
        #   可调用self._popEmpty()去除载荷中的空参数
        {% if inputKeys %}{% for key in inputKeys %}
        {{ key }} = params.get("{{ key }}"){% endfor %}{% else %}
        ...
        {% endif %}
"""

triggers_template = """
from SDK.subassembly import Triggers
from SDK.base import *

from .models import {{ connModel }}, {{ inputModel }}, {{ outputModel }}



class {{ triggersName }}(Triggers):

    def __init__(self):
        #   初始化
        super().__init__()
        self.name = "{{ name }}"
        self.inputModel = {{ inputModel }}
        self.outputModel = {{ outputModel }}
        self.connModel = {{ connModel }}


    def connection(self, data={}):
        #   write your code
        {% if connetionKeys %}{% for key in connetionKeys %}
        {{ key }} = data.get("{{ key }}"){% endfor %}{% else %}
        ...    
        {% endif %}

    def run(self, params={}):
        #   write your code
        #   可调用self._popEmpty()去除载荷中的空参数
        #   返回必须使用 self.send({})
        {% if inputKeys %}{% for key in inputKeys %}
        {{ key }} = params.get("{{ key }}"){% endfor %}{% else %}
        ...
        {% endif %}
"""


alarm_receivers_template = """
from SDK.subassembly import AlarmReceivers
from SDK.base import *

from .models import {{ connModel }}, {{ inputModel }}, {{ outputModel }}



class {{ alarm_receiversName }}(AlarmReceivers):

    def __init__(self):
        #   初始化
        super().__init__()
        self.name = "{{ name }}"
        self.inputModel = {{ inputModel }}
        self.outputModel = {{ outputModel }}
        self.connModel = {{ connModel }}


    def connection(self, data={}):
        #   write your code
        {% if connetionKeys %}{% for key in connetionKeys %}
        {{ key }} = data.get("{{ key }}"){% endfor %}{% else %}
        ...    
        {% endif %}

    def run(self, params={}):
        #   write your code
        #   可调用self._popEmpty()去除载荷中的空参数
        #   返回必须使用 self.send({})
        {% if inputKeys %}{% for key in inputKeys %}
        {{ key }} = params.get("{{ key }}"){% endfor %}{% else %}
        ...
        {% endif %}

"""


indicator_receivers_template = """
from SDK.subassembly import IndicatorReceivers
from SDK.base import *

from .models import {{ connModel }}, {{ inputModel }}, {{ outputModel }}



class {{ indicator_receiversName }}(IndicatorReceivers):

    def __init__(self):
        #   初始化
        super().__init__()
        self.name = "{{ name }}"
        self.inputModel = {{ inputModel }}
        self.outputModel = {{ outputModel }}
        self.connModel = {{ connModel }}


    def connection(self, data={}):
        #   write your code
        {% if connetionKeys %}{% for key in connetionKeys %}
        {{ key }} = data.get("{{ key }}"){% endfor %}{% else %}
        ...    
        {% endif %}

    def run(self, params={}):
        #   write your code
        #   可调用self._popEmpty()去除载荷中的空参数
        #   返回必须使用 self.send({})
        {% if inputKeys %}{% for key in inputKeys %}
        {{ key }} = params.get("{{ key }}"){% endfor %}{% else %}
        ...
        {% endif %}

"""


actions_test_template = """
{
	"version": "v1",
	"type": "action_start",
	"body": {
		"action": "{{ title }}",
		"meta": {},
		"connection": {},
		"dispatcher": null,
		"input": {}
	}
}

"""

triggers_test_template = """
{
	"version": "v1",
	"type": "trigger_start",
	"body": {
		"trigger": "{{ title }}",
		"meta": {},
		"connection": {},
		"dispatcher": {
			"url": "http://127.0.0.1:8001/send",
			"webhook_url": ""
		},
		"input": {},
      "enable_web": false
	}
}

"""

main_template = """#!/usr/bin/env python

from SDK.cli import client

{% if actionClassees %}
import actions
{% endif %}
{% if triggerClassees %}
import triggers
{% endif %}
{% if indicatorReceiverClassees %}
import indicator_receivers
{% endif %}
{% if alarmReceiverClassees %}
import alarm_receivers
{% endif %}

# 整个程序入口

class {{ pluginName }}(object):

    def __init__(self):

        self.connection = {}
        self.actions = {}
        self.triggers = {}
        self.indicator_receivers = {}
        self.alarm_receivers = {}      
        
        {% for actionClass in actionClassees %}
        self.add_actions(actions.{{ actionClass }}())
        {% endfor %}

        {% for triggerClass in triggerClassees %}
        self.add_triggers(triggers.{{ triggerClass }}())
        {% endfor %}

        {% for indicatorReceiverClasse in indicatorReceiverClassees %}
        self.add_indicator_receivers(indicator_receivers.{{ indicatorReceiverClasse }}())
        {% endfor %}
        
        {% for alarmReceiverClasse in alarmReceiverClassees %}
        self.add_alarm_receivers(alarm_receivers.{{ alarmReceiverClasse }}())
        {% endfor %}

    def add_connection(self, connect):
        self.connection[connect.name] = connect

    def add_actions(self, action):
        self.actions[action.name] = action

    def add_triggers(self, trigger):
        self.triggers[trigger.name] = trigger

    def add_indicator_receivers(self, indicator_receiver):
        self.indicator_receivers[indicator_receiver.name] = indicator_receiver
    
    def add_alarm_receivers(self, alarm_receiver):
        self.alarm_receivers[alarm_receiver.name] = alarm_receiver


def main():

    client({{ pluginName }})


if __name__ == '__main__':

    main()
    
"""

init_template = \
"""{% for name, className in init_list %}
from .{{ name }} import {{ className }}
{% endfor %}"""

help_template = """
# {{ name }}

## About
{{ name }}



## Connection

{% if connection %}


{% for field_name, field_data in connection.items() -%}

{% if loop.index == 1 -%}
|Name|Type|Required|Description|Default|Enum|
|----|----|--------|-----------|-------|----|
{%- endif %}
|{%- if field_data.title -%}
{{ field_data.title['zh-CN'] }}
{%- else -%}
None
{%- endif -%}|{{ field_data.type }}|{{ field_data.required }}|{%- if field_data.description -%}
{{ field_data.description['zh-CN'] }}
{%- else -%}
None
{%- endif -%}|{{ field_data.default|default('None') }}|{{ field_data.enum|default('None') }}|

{%- endfor %}


{% endif %}


## Actions

{% if actions %}

{% for action, actionData in actions.items() %}

### {{ action }}

---

{% for action_name,action_data in actionData.items() %}

{% if action_name == 'input' %}
#### Input

{% for field_name, field_data in action_data.items() -%}

{% if loop.index == 1 -%}
|Name|Type|Required|Description|Default|Enum|
|----|----|--------|-----------|-------|----|
{%- endif %}
|{%- if field_data.title -%}
{{ field_data.title['zh-CN'] }}
{%- else -%}
None
{%- endif -%}|{{ field_data.type }}|{{ field_data.required }}|{%- if field_data.description -%}
{{ field_data.description['zh-CN'] }}
{%- else -%}
None
{%- endif -%}|{{ field_data.default|default('None') }}|{{ field_data.enum|default('None') }}|


{%- endfor %}

{% endif %}


{% if action_name == 'output' %}
#### Output

{% for field_name, field_data in action_data.items() -%}

{% if loop.index == 1 -%}
|Name|Type|Required|Description|Default|Enum|
|----|----|--------|-----------|-------|----|
{%- endif %}
|{%- if field_data.title -%}
{{ field_data.title['zh-CN'] }}
{%- else -%}
None
{%- endif -%}|{{ field_data.type }}|{{ field_data.required }}|{%- if field_data.description -%}
{{ field_data.description['zh-CN'] }}
{%- else -%}
None
{%- endif -%}|{{ field_data.default|default('None') }}|{{ field_data.enum|default('None') }}|


{%- endfor %}


{% endif %}



{% endfor %}

{% endfor %}

{% endif %}



## Triggers

---

{% if triggers %}


{% for trigger, triggerData in triggers.items() %}

### {{ trigger }}

---

{% for trigger_name,trigger_data in triggerData.items() %}

{% if trigger_name == 'input' %}
#### Input

{% for field_name, field_data in trigger_data.items() -%}

{% if loop.index == 1 -%}
|Name|Type|Required|Description|Default|Enum|
|----|----|--------|-----------|-------|----|
{%- endif %}
|{%- if field_data.title -%}
{{ field_data.title['zh-CN'] }}
{%- else -%}
None
{%- endif -%}|{{ field_data.type }}|{{ field_data.required }}|{%- if field_data.description -%}
{{ field_data.description['zh-CN'] }}
{%- else -%}
None
{%- endif -%}|{{ field_data.default|default('None') }}|{{ field_data.enum|default('None') }}|


{%- endfor %}

{% endif %}


{% if action_name == 'output' %}
#### Output

{% for field_name, field_data in action_data.items() -%}

{% if loop.index == 1 -%}
|Name|Type|Required|Description|Default|Enum|
|----|----|--------|-----------|-------|----|
{%- endif %}
|{%- if field_data.title -%}
{{ field_data.title['zh-CN'] }}
{%- else -%}
None
{%- endif -%}|{{ field_data.type }}|{{ field_data.required }}|{%- if field_data.description -%}
{{ field_data.description['zh-CN'] }}
{%- else -%}
None
{%- endif -%}|{{ field_data.default|default('None') }}|{{ field_data.enum|default('None') }}|


{%- endfor %}


{% endif %}



{% endfor %}

{% endfor %}

{% endif %}


## Types

{% if types %}

{% for type_name, type_data in types.items() %}

### {{ type_name }}

{% for field_name, field_data in type_data.items() -%}

{% if loop.index == 1 -%}
|Name|Type|Required|Description|Default|Enum|
|----|----|--------|-----------|-------|----|
{%- endif %}
|{%- if field_data.title -%}
{{ field_data.title['zh-CN'] }}
{%- else -%}
None
{%- endif -%}|{{ field_data.type }}|{{ field_data.required }}|{%- if field_data.description -%}
{{ field_data.description['zh-CN'] }}
{%- else -%}
None
{%- endif -%}|{{ field_data.default|default('None') }}|{{ field_data.enum|default('None') }}|

{%- endfor %}

{% endfor %}

{% endif %}


## 版本信息
- {{ version }}

## 参考引用
"""


indicator_receivers_test_template = """
{
	"version": "v1",
	"type": "indicator_receiver_start",
	"body": {
		"receiver": "{{ title }}",
		"meta": {},
		"connection": {},
		"dispatcher": {
			"url": "http://127.0.0.1:8001/send",
			"webhook_url": ""
		},
		"input": {},
      "enable_web": false
	}
}

"""

indicator_receivers_model_types = """
class Indicator(BaseModel):
    uid: str
    type: str
    value: str
    source: str
    reputation: str
    threat_score: int
    rawed: str
    tagsed: Optional[str] = None
    status: Optional[bool] = None
    notes: Optional[str] = None
    casesed: Optional[str] = None
    created_at: str
    updated_at: str


class IndicatorDomain(BaseModel):
    uid: str
    indicator_uid: str
    primary_domain: Optional[str] = None
    admin_name: Optional[str] = None
    organization: Optional[str] = None
    admin_email: Optional[str] = None
    admin_phone: Optional[str] = None
    admin_address: Optional[str] = None
    register_at: Optional[str] = None
    renew_at: Optional[str] = None
    name_provider: Optional[str] = None
    name_servers: Optional[str] = None


class IndicatorUrl(BaseModel):
    uid: str
    indicator_uid: str
    hash: Optional[str] = None
    host: Optional[str] = None


class IndicatorIp(BaseModel):
    uid: str
    indicator_uid: str
    hostname: Optional[str] = None
    geo_country: Optional[str] = None
    geo_location: Optional[str] = None
    open_ports: Optional[str] = None


class IndicatorHash(BaseModel):
    uid: str
    indicator_uid: str
    sha256: Optional[str] = None
    sha1: Optional[str] = None
    md5: Optional[str] = None


class IndicatorEmail(BaseModel):
    uid: str
    indicator_uid: str
    primary_domain: Optional[str] = None


class IndicatorFile(BaseModel):
    uid: str
    indicator_uid: str
    filename: Optional[str] = None
    extension: Optional[str] = None
    size: Optional[str] = None
    sha256: Optional[str] = None
    sha1: Optional[str] = None
    md5: Optional[str] = None


class IndicatorHost(BaseModel):
    uid: str
    indicator_uid: str
    ip: Optional[str] = None
    mac: Optional[str] = None
    bios: Optional[str] = None
    memory: Optional[str] = None
    processors: Optional[str] = None
    os: Optional[str] = None


class IndicatorAccount(BaseModel):
    uid: str
    indicator_uid: str
    username: Optional[str] = None
    email: Optional[str] = None
    account_type: Optional[str] = None
    role: Optional[str] = None
    domain: Optional[str] = None
    organization: Optional[str] = None
"""

indicator_receivers_model_template = """
class {{ className }}(BaseModel):

    indicator: Indicator
    indicator_sub: Union[IndicatorDomain, IndicatorUrl, IndicatorIp, IndicatorHash, IndicatorEmail, IndicatorFile, IndicatorHost, IndicatorAccount, None]

"""


alarm_receivers_test_template = """
{
	"version": "v1",
	"type": "alarm_receiver_start",
	"body": {
		"alarm": "{{ title }}",
		"meta": {},
		"connection": {},
		"dispatcher": {
			"url": "http://127.0.0.1:8001/send",
			"webhook_url": ""
		},
		"input": {},
      "enable_web": false
	}
}

"""

alarm_receivers_model_types = """
class Alarm(BaseModel):
    uid: str
    name: str
    alarm_ip: str
    alarm_type: str
    sip: str
    tip: str
    source: str
    type: str
    reputation: str
    status: Optional[bool] = True
    raw: str
    created_at: str
    updated_at: str
    
"""

alarm_receivers_model_template = """
class {{ className }}(BaseModel):

    alarm: Alarm
    
"""

testserver_head_template = r"""
from fastapi import FastAPI,HTTPException
import uvicorn
import typing
import json
from SDK.base import * 

description = \
'''
  欢迎使用 1.2.7 版本SDK提供的全新测试系统。\n
  相较于之前的版本的 REST 测试接口，这个版本提供了更加详细的功能细分以及测试数据输入指引。\n
  现在再也不会几个接口测试一大堆功能，一大堆参数还不知道怎么填了。\n
  
  Enjoy it!  -- Matthews_K

'''
test_server = FastAPI(title="Chariot-Plugin Test Server", version="1.2.7", description=description)

"""

testserver_tail_template = """
def runserver():
    os.system("")
    log("attention","在浏览器内输入 http://127.0.0.1:1453/docs 以进行接口测试")
    log("attention","在浏览器内输入 http://127.0.0.1:1453/redoc 以查看帮助文档")
    uvicorn.run(test_server,host="127.0.0.1", port=1453)


if __name__ == '__main__':

    runserver()
"""

testserver_actions_template="""
@test_server.post("/actions/{{ name }}",response_model={{ class_name }}().outputModel,tags=["动作"])
def action_{{ name }}(action_name:str="{{ name }}",
                      connection_data:{{ class_name }}().connModel=None,
                      input_data:{{ class_name }}().inputModel=None):
    
    clearLog()

    connection_data = connection_data.dict()

    input_data = input_data.dict()

    output = {{ class_name }}()._run(input_data,connection_data)

    if output["body"].get("error_trace"):
        raise HTTPException(500,detail=output["body"]["error_trace"])
    else:
        output_data = output["body"]["output"]

    return output_data

"""

testserver_triggers_template="""
@test_server.post("/triggers/{{ name }}",response_model={{ class_name }}().outputModel,tags=["触发器"])
def trigger_{{ name }}(trigger_name:str="{{ name }}",
                       dispatcher_url:str="http://127.0.0.1:8000/send",
                       connection_data:{{ class_name }}().connModel=None,
                       input_data:{{ class_name }}().inputModel=None):
    
    clearLog()

    connection_data = connection_data.dict()

    input_data = input_data.dict()

    output = {{ class_name }}()._run(input_data,connection_data,dispatcher_url)

    if output["body"].get("error_trace"):
        raise HTTPException(500,detail=output["body"]["error_trace"])
    else:
        output_data = output["body"]["output"]

    return output_data

"""

testserver_alarm_receivers_template="""
@test_server.post("/alarm_receivers/{{ name }}",response_model={{ class_name }}().outputModel,tags=["告警接收器"])
def alarm_receiver_{{ name }}(alarm_receiver_name:str="{{ name }}",
                              dispatcher_url:str="http://127.0.0.1:8000/send",
                              connection_data:{{ class_name }}().connModel=None,
                              input_data:{{ class_name }}().inputModel=None):
    
    clearLog()

    connection_data = connection_data.dict()

    input_data = input_data.dict()

    output = {{ class_name }}()._run(input_data,connection_data,dispatcher_url)

    if output["body"].get("error_trace"):
        raise HTTPException(500,detail=output["body"]["error_trace"])
    else:
        output_data = output["body"]["output"]

    return output_data

"""

testserver_indicator_receivers_template="""
@test_server.post("/indicator_receivers/{{ name }}",response_model={{ class_name }}().outputModel,tags=["情报接收器"])
def indicator_receiver_{{ name }}(indicator_receiver_name:str="{{ name }}",
                              dispatcher_url:str="http://127.0.0.1:8000/send",
                              connection_data:{{ class_name }}().connModel=None,
                              input_data:{{ class_name }}().inputModel=None):
    
    clearLog()

    connection_data = connection_data.dict()

    input_data = input_data.dict()

    output = {{ class_name }}()._run(input_data,connection_data,dispatcher_url)

    if output["body"].get("error_trace"):
        raise HTTPException(500,detail=output["body"]["error_trace"])
    else:
        output_data = output["body"]["output"]

    return output_data

"""