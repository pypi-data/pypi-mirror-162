#encoding:utf-8
import random,time
import os,sys,jsonpath
import platform as pf
curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)
from time import sleep
import shutil

from loguru import logger
from pywebio.input import FLOAT,NUMBER,input_group,select, textarea,file_upload,checkbox,radio,actions
from pywebio.output import close_popup, output, put_file, put_html, put_image, put_markdown, put_text,popup,put_link,put_code,put_row,put_processbar,set_processbar,put_error,put_warning,toast,put_grid,put_button,put_table,use_scope,span,clear,remove
from pywebio import start_server,session,platform
from core.bladeTest.main import RemoteRunner,generateHtmlReport,running
from core.jmeterTool.swagger2jmeter import swagger2jmeter
from core.jmeterTool.har2jmeter import har2jmeter
from core.xmind2excel import makeCase
from core.utils import CFacker,getDateTime,parseJmeterXml,getTimeStamp,getDateTime,formatStr2Timestamp,timeStampStr2FormatTime,jsonPrettyOutput
from core.mqttUtil import NormalMqttGetter,NormalMqttSender
from core.kafkaUtil import general_sender,continue_orderMsg,general_orderMsg,general_orderMsgWithFilter,kafkaFetchServerWithFilter,kafkaFetchServer
from functools import partial
from multiprocessing import Process
import decimal,websockets,asyncio
import json
from functools import partial

import pywebio.output as output
import pywebio.input as inputs
import pywebio.pin as pin
from pywebio.session import hold




@use_scope('content',clear=True)
def businessProcess():
    session.set_env(title='testToolKit')
    clear('content')
    select_type = select("选择你要做的操作:",["指令生成","指令生成发送--","属性上报--","点位生成--"])
    if select_type=="指令生成":
        commandGenerator()




def modle2command(deviceId,modle_str):
    '''
    用法：
    将数据库xxxx表中字段model_content当做参数modle_str；会生成下发指令的集合
    如：
                                    {
                                "cmd": {
                                    "command": "door_status_set",
                                    "function": "door",
                                    "param":{"door_status_value":"['1', '0']"}
                                },
                                "deviceId": "123456"
                                }
    表示，可以下发的值包含['1', '0']
    '''

    totalCommand=""
    jstr=json.loads(modle_str)#rawStr2)
    productId=jsonpath.jsonpath(jstr, "$.standardFunctions[*].identifier")
    for num, p_id in enumerate(productId):
        totalCommand=totalCommand+"##############################"+"\n"
        commands=jsonpath.jsonpath(jstr, "$.standardFunctions["+str(num)+"].commands[*]")
        if commands:
            for command in commands:
                # print('--'*10)
                totalCommand=totalCommand+"-----------------------------"+"\n"
                # print(command['identifier'])
                function_id=command['identifier']
                # print(f"#######{command['inputs']}")
                command_value=[]
                if command['inputs']!=[] :
                    # print(command['inputs'][0]['identifier'])
                    command_id=command['inputs'][0]['identifier']
                    # print(command['inputs'][0]['dataType'])
                    command_type=command['inputs'][0]['dataType']
                    
                    if command['inputs'][0].__contains__('specifications'):
                        
                        values=command['inputs'][0]['specifications']
                        # print(values)
                        for value in values:
                            # print(value['value'])
                            command_value.append(value['value'])
                    elif command['inputs'][0].__contains__('specification'):
                        minNum=None
                        maxNum=None
                        acc=None
                        values=command['inputs'][0]['specification']
                        # print(f"##################################################{values}")
                        if values!="{}":
                            if values.__contains__('min'):
                                # print(values['min'])
                                minNum=int(values['min'])
                                command_value.append(minNum-1)
                            if values.__contains__('max'):
                                # print(values['max'])
                                maxNum=int(values['max'])
                                command_value.append(maxNum+1)
                            # if values.__contains__('digit'):
                                # print(values['digit'])
                            # if values.__contains__('step'):
                                # print(values['step'])
                            if values.__contains__('accuracy'):
                                # print(values['accuracy'])
                                acc=int(values['accuracy'])
                                command_value.append(round((minNum+maxNum)/2,acc))
                                command_value.append(round((minNum+maxNum)/2,acc+1))
                                command_value.append((minNum+maxNum)//2)
                # print(p_id)
                # print(function_id)
                # print(command_id)
                # print(command_value)
                commandStr=f'''
                                        {{
                                        "cmd": {{
                                            "command": "{function_id}",
                                            "function": "{p_id}",
                                            "param":{{"{command_id}":"{command_value}"}}
                                        }},
                                        "deviceId": "{deviceId}"
                                        }}
                '''
                totalCommand=totalCommand+commandStr+"\n"
            return totalCommand
            # print(totalCommand)

def commandGenerator():
    output.put_markdown("## 请输入设备信息和模型信息：")
    pin.put_input(name='deviceId',label='设备信息,设备id')
    pin.put_textarea(name='modleJson',label='模型信息,物模型定义Json字符串',rows=10)
    def getValueAndCall():
        deviceId=pin.pin.deviceId
        modleJson=pin.pin.modleJson

        output.put_text(modle2command(deviceId, modleJson))

    output.put_button(label='提交', onclick=lambda :getValueAndCall())


if __name__=='__main__':
    start_server(businessProcess,port=9999,debug=True,cdn=False,auto_open_webbrowser=True)
