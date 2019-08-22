import os
import sys

import oss2

from src.config.config import *


class AliOSS:
    # 上次进度-限制相同进度打印
    _last_percent = 0

    def __init__(self, access_key_id: str, access_key_secret: str, end_point: str, bucket: str):
        self.access_key_id = access_key_id
        self.access_key_secret = access_key_secret
        self.end_point = end_point
        self.bucket = bucket
        # 初始化阿里 oss
        _auth = oss2.Auth(access_key_id, access_key_secret)
        self._bucket = oss2.Bucket(_auth, ALI_OSS_END_POINT, bucket)

    def put_file(self, key: str, filename: str):
        print("正在上传到阿里云:", key, filename)
        res = self._bucket.put_object_from_file(
            key, filename, progress_callback=self.percentage)
        print(res.resp.__dict__)
        print(res.__dict__)
        return res.status == 200

    def put_object(self, key: str, data):
        print("正在上传到阿里云:", key)
        res = self._bucket.put_object(key, data.encode('gbk'))
        print(res.__dict__)
        return res.status == 200

    # 进度打印
    def percentage(self, consumed_bytes, total_bytes):
        if total_bytes:
            rate = int(100 * (float(consumed_bytes) / float(total_bytes)))
            if rate == self._last_percent:
                return
            print('\r正在上传-{0}% '.format(rate), end='')
            sys.stdout.flush()


# 上传文件到阿里OSS
def put_file_to_ali_oss(key, file_path):
    if not _check_ali_oss_conf():
        print("没有阿里oss相关配置")
        return
    if not key:
        print("上传文件名不存在")
        return
    if not os.path.isfile(file_path):
        print("上传件不存在")
        return
    ali_oss = _get_ali_oss()
    if ali_oss.put_file(key, file_path):
        url = ALI_OSS_END_POINT.replace("https://", "").replace("http://", "")
        return "https://" + ALI_OSS_BUCKET_NAME + "." + url + "/" + key
    else:
        return ""


# 上传文本到阿里 OSS
def put_text_to_ali_oss(key, text):
    if not _check_ali_oss_conf():
        print("没有阿里oss相关配置")
        return
    if not key:
        print("上传文件名不存在")
        return
    ali_oss = _get_ali_oss()
    if ali_oss.put_object(key, text):
        url = ALI_OSS_END_POINT.replace("https://", "").replace("http://", "")
        return "https://" + ALI_OSS_BUCKET_NAME + "." + url + "/" + key
    else:
        return ""


def _get_ali_oss():
    return AliOSS(ALI_OSS_ACCESS_KEY_ID, ALI_OSS_ACCESS_KEY_SECRET, ALI_OSS_END_POINT, ALI_OSS_BUCKET_NAME)


#   检查oss配置是否正确
def _check_ali_oss_conf():
    return ALI_OSS_ACCESS_KEY_ID and ALI_OSS_ACCESS_KEY_SECRET and ALI_OSS_END_POINT and ALI_OSS_BUCKET_NAME
