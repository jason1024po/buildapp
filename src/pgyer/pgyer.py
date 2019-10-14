import json

import requests
from pathlib import Path

from src.config.config import *
from src.error.error import BuildException


class PGY:
    end_point = "https://www.pgyer.com/apiv2/app/upload"

    @classmethod
    def upload(cls, file_path):
        if not len(PGY_USER_KEY) or not len(PGY_API_KEY):
            # UserWarning
            raise BuildException("请检查蒲公英配置~")
        if not Path(file_path).is_file():
            raise BuildException("要上传的文件不存在:")
        print("开始上传: " + file_path)
        result = cls.__upload(file_path)
        print("上传成功: https://www.pgyer.com/" + result['buildShortcutUrl'])
        return result

    @classmethod
    def __upload(cls, file_path: str):
        with open(file_path, "rb") as f:
            # 文件
            files = {"file": f}
            # header 信息
            headers = {"enctype": "multipart/form-data"}
            # 字段数据
            data = {"userKey": PGY_USER_KEY, "_api_key": PGY_API_KEY}
            # 开始请求
            try:
                r = requests.post(cls.end_point, headers=headers, data=data, files=files)
                response = r.json()
                if response["code"] != 0:
                    raise BuildException("上传到蒲公英失败")
                return response["data"]
            except Exception:
                raise BuildException("上传到蒲公英失败2")
