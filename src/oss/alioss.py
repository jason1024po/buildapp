import re
import sys

from src.error.error import BuildException


class AliOSS:

    def __init__(self, access_key_id: str, access_key_secret: str, end_point: str, bucket_name: str):
        # 上次进度-限制相同进度打印
        self._last_percent = 0

        # oss url
        self.end_point = end_point
        self.bucket_name = bucket_name
        self.oss_url = self.__get_oss_url()

        # 初始化阿里 oss
        import oss2
        _auth = oss2.Auth(access_key_id, access_key_secret)
        self._bucket = oss2.Bucket(_auth, end_point, bucket_name)

    # 上传文件
    def put_file(self, object_name: str, file_path: str):
        print("正在上传到阿里云:", object_name, file_path)
        try:
            res = self._bucket.put_object_from_file(object_name, file_path, progress_callback=self.__print_percent)
            print(res.resp.response)
            if res.status != 200:
                raise BuildException("上传到阿里云(返回结果失败)")
        except Exception as e:
            print(e)
            raise BuildException("上传到阿里云失败")

    # 上传文本
    def put_object(self, object_name: str, data):
        print("正在上传到阿里云:", object_name)
        # 这里使用 utf8 编码会乱码
        try:
            res = self._bucket.put_object(object_name, data.encode('gbk'))
            print(res.__dict__)
            if res.status != 200:
                raise BuildException("上传到阿里云(返回结果失败)")
        except Exception as e:
            raise BuildException("上传到阿里云失败")

    # 进度打印
    def __print_percent(self, consumed_bytes, total_bytes):
        if total_bytes:
            rate = int(100 * (float(consumed_bytes) / float(total_bytes)))
            if rate == self._last_percent:
                return
            print('\r正在上传-{0}% '.format(rate), end='')
            sys.stdout.flush()

    # oss url
    def __get_oss_url(self):
        find = re.findall(r'^https*://', self.end_point)
        prefix = find[0] if find else 'http://'
        url = self.end_point.replace(prefix, "")
        return prefix + self.bucket_name + "." + url
