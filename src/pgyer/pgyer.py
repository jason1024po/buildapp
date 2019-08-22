import json

import requests
from pathlib import Path

from src.config.config import *
from src.dingding.dingding import send_with_pgy_response

PGY_UPLOAD_RUL = "https://www.pgyer.com/apiv2/app/upload"

def upload_to_pgy(path):
    if not len(PGY_USER_KEY) or not len(PGY_API_KEY):
        print("请检查蒲公英配置~")
        return
    if not Path(path).is_file():
        print("要上传的文件不存在:" + path)
        return
    else:
        print("开始上传...")
        print(path)

    # 文件
    files = {"file": open(path, "rb")}
    # header 信息
    headers = {"enctype": "multipart/form-data"}
    # 字段数据
    data = {"userKey": PGY_USER_KEY, "_api_key": PGY_API_KEY}
    # 开始请求
    r = requests.post(PGY_UPLOAD_RUL, headers=headers, data=data, files=files)
    # 请求结果
    if r.status_code == requests.codes.ok:
        print("上传完成！！!")
        response = r.json()
        # 发送到钉钉
        send_with_pgy_response(response["data"])
    else:
        print("上传失败,Code:" + r.status_code)
