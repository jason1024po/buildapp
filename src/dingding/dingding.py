import time

import requests
import json

from src.config.config import *

DD_MESSAGE_URL = "https://oapi.dingtalk.com/robot/send?access_token="

# header 信息
headers = {"Content-Type": "application/json"}


def get_build_type(data):
    if data == "1":
        return "iOS"
    elif data == "2":
        return "Android"
    else:
        return "未知"


def send_with_pgy_response(data):
    print(json.dumps(data))
    # 内容
    text = """新版本提醒    
    名称：**{buildName}**-{buildType}    
    版本：**{buildVersion}({buildVersionNo})**(Build {buildBuildVersion})    
    大小：{buildFileSize} MB    
    时间：{buildUpdated}   
    下载：[点击下载本次版本](https://www.pgyer.com/{buildKey})  
    内容：{buildContent}   
    """.format(
        buildName=data["buildName"],
        buildType=get_build_type(data["buildType"]),
        buildVersion=data["buildVersion"],
        buildVersionNo=data["buildVersionNo"],
        buildBuildVersion=data["buildBuildVersion"],
        buildFileSize=int(int(data["buildFileSize"]) / 1024 // 1024),
        buildUpdated=data["buildUpdated"],
        buildKey=data["buildKey"],
        buildContent="测试包"
    )

    body = {
        "msgtype": "actionCard",
        "actionCard": {
            "hideAvatar": "0",
            "btnOrientation": "0",
            "title": "{}".format(data["buildName"]),
            "singleTitle": "点击消息下载最新版本",
            "singleURL": "https://www.pgyer.com/{}".format(data["buildShortcutUrl"]),
            "text": text,
        },
    }

    response = requests.post(url=DD_MESSAGE_URL + DD_ACCESS_TOKEN_DEV, headers=headers, data=json.dumps(body))
    result = response.json()
    print(result)


# 发送正式消息
def send_prod_message(name, version_name, version_code, url):
    if "apk" in url:
        build_type = "Android"
    elif "ipa" in url:
        build_type = "iOS"
    else:
        build_type = "未知"

    text = """### 上传了新版本 \n
名称: **{name}**-{build_type} \n
版本: **v{version_name}({version_code})**  \n
时间: **{time}** \n
[{url}]({url}) """.format(name=name,
                          build_type=build_type,
                          version_name=version_name,
                          version_code=version_code,
                          time=time.strftime("%Y-%m-%d_%H.%M", time.localtime()),
                          url=url)
    body = {
        "msgtype": "markdown",
        "markdown": {
            "title": "{name}-{build_type}".format(name=name, build_type=build_type),
            "text": text
        }
    }
    response = requests.post(url=DD_MESSAGE_URL + DD_ACCESS_TOKEN_PRO, headers=headers, data=json.dumps(body))
    result = response.json()
    print(result)


# 发送打包失败消息
def send_prod_fault_message(name, platform, version_name, version_code, message):
    text = """### 打包失败了！请检查~ \n
名称: **{name}** - {platform} \n
版本: **v{version_name}({version_code})**  \n
时间: **{time}** \n
说明：{message}""".format(name=name,
                       platform=platform,
                       version_name=version_name,
                       version_code=version_code,
                       time=time.strftime("%Y-%m-%d_%H.%M", time.localtime()),
                       message=message)
    body = {
        "msgtype": "markdown",
        "markdown": {
                        "title": "打包失败了",
                        "text": text
        }
    }
    # 开始发送
    response = requests.post(url=DD_MESSAGE_URL + DD_ACCESS_TOKEN_PRO, headers=headers, data=json.dumps(body))
    result = response.json()
    print(result)
