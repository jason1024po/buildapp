import os
from urllib.parse import urljoin

from src.error.error import BuildException
from src.oss.alioss import AliOSS
from src.config.config import *


class OSS:
    @classmethod
    def put_file(cls, object_name, file_path):
        if not cls.__check_config():
            raise BuildException("没有阿里oss相关配置")
        if not object_name:
            raise BuildException("上传文件名不存在")
        if not cls.__check_file_path(file_path):
            raise BuildException("上传件不存在")
        cls.__get_ali_oss().put_file(object_name, file_path)
        # 上传成功
        full_url = urljoin(cls.__get_ali_oss().oss_url, object_name)
        return full_url

    # 上传文本到阿里 OSS
    @classmethod
    def put_text(cls, object_name, text):
        if not cls.__check_config():
            raise BuildException("没有阿里oss相关配置")
        if not object_name:
            raise BuildException("上传件不存在")
        cls.__get_ali_oss().put_object(object_name, text)
        full_url = urljoin(cls.__get_ali_oss().oss_url, object_name)
        print("上传成功: " + full_url)
        return full_url

    # 检查oss配置是否正确
    @classmethod
    def __check_config(cls):
        return ALI_OSS_ACCESS_KEY_ID and ALI_OSS_ACCESS_KEY_SECRET and ALI_OSS_END_POINT and ALI_OSS_BUCKET_NAME

    @classmethod
    def __check_file_path(cls, path):
        return os.path.isfile(path)

    @classmethod
    def __get_ali_oss(cls):
        return AliOSS(ALI_OSS_ACCESS_KEY_ID, ALI_OSS_ACCESS_KEY_SECRET, ALI_OSS_END_POINT, ALI_OSS_BUCKET_NAME)








