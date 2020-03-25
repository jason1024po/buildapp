import json
import os

import requests

from src.config.config import FIR_API_TOKEN
from src.error.error import BuildException


class FirRequest:
    api_token = FIR_API_TOKEN
    file = ''
    type = ''
    bundle_id = ''
    name = ''
    version = ''
    build = ''
    release_type = 'Adhoc'
    changelog = '测试包'

    def __init__(self, build):
        from src.android.android_build import AndroidBuild
        if isinstance(build, AndroidBuild):
            self.file = build.get_new_apk_path()
            self.type = 'android'
            self.bundle_id = build.project.application_id
            self.name = build.project.application_name
            self.version = build.project.version_name
            self.build = build.project.version_code


class Fir:

    @classmethod
    def upload(cls, request):
        if not isinstance(request, FirRequest):
            raise BuildException('fir请求参数类型错误')

        if not request.api_token:
            raise BuildException('api_token不能为空')
        if not os.path.isfile(request.file):
            raise BuildException('要上传fir的文件不存在')
        cert_resp = Fir.__get_cert(request.type, request.bundle_id, request.api_token)
        binary_resp = Fir.__upload_binary(cert_resp, request)
        if not binary_resp.is_completed:
            raise BuildException('fir上传失败')
        print('上传到fir成功')
        return FirResponse(cert_resp, binary_resp, request)

    # 获取上传凭证
    @classmethod
    def __get_cert(cls, app_type, bundle_id, api_token):
        print('正在获取fir上传凭证')
        data = {
            'type': app_type,
            'bundle_id': bundle_id,
            'api_token': api_token
        }
        req = requests.post(url='http://api.fir.im/apps', data=data)
        cert_resp = req.content
        json_resp = dict(json.loads(cert_resp))
        resp = FirCertResponse.new(json_resp)
        return resp

    # 上传文件
    @classmethod
    def __upload_binary(cls, cert, request):
        if not isinstance(request, FirRequest):
            raise BuildException('fir请求参数类型错误')
        # 拿到相应的token
        if not isinstance(cert, FirCertResponse):
            raise BuildException("fir 解析数据出错")
        cert_key = cert.cert_binary.key
        cert_token = cert.cert_binary.token
        cert_upload_url = cert.cert_binary.upload_url
        print('解析凭证成功')
        print('开始上传，请稍等...')
        with open(request.file, 'rb') as f:
            file = {'file': f}
            param = {
                "key":  cert_key,
                "token": cert_token,
                'x:version': request.version,
                'x:build': request.build,
                "x:name": request.name,
                "x:changelog": request.changelog
            }
            requests.packages.urllib3.disable_warnings()
            req = requests.post(cert_upload_url, files=file, data=param, verify=False)
            json_resp = dict(json.loads(req.content))

            is_completed = json_resp.get('is_completed')
            download_url = json_resp.get('download_url')
            release_id = json_resp.get('release_id')
            resp_obj = FirBinaryResponse(is_completed, download_url, release_id)
        return resp_obj


class FirResponse:
    date = '未知'
    size = '未知'
    content = '内容'

    def __init__(self, cert_resp, binary_resp, request):
        if isinstance(cert_resp, FirCertResponse):
            self._cert_resp = cert_resp
        if isinstance(cert_resp, FirBinaryResponse):
            self._binary_resp = binary_resp
        if isinstance(request, FirRequest):
            self._request = request

    @property
    def app_name(self):
        return self._request.name

    @property
    def version_name(self):
        return self._request.version

    @property
    def version_code(self):
        return self._request.build

    @property
    def type(self):
        if self._cert_resp.type == 'android':
            return 'Android'
        return 'iOS'

    @property
    def download_url(self):
        return self._binary_resp.download_url


class FirCertResponse:
    class Cert:
        key = ''
        token = ''
        upload_url = ''
        custom_headers = ''

        @classmethod
        def new(cls, data):
            obj = cls()
            obj.key = data.get('key')
            obj.token = data.get('token')
            obj.upload_url = data.get('upload_url')
            obj.custom_headers = data.get('custom_headers')
            return obj

    id = ''
    type = ''
    short = ''
    storage = ''
    form_method = ''
    cert = {}
    cert_icon = Cert()
    cert_binary = Cert()

    @classmethod
    def new(cls, data):
        obj = cls()
        if not data.get('cert'):
            raise BuildException('获取fir上传凭证失败')
        obj.id = data.get('id')
        obj.type = data.get('type')
        obj.short = data.get('short')
        obj.storage = data.get('storage')
        obj.form_method = data.get('form_method')
        obj.cert = data.get('cert')
        obj.cert_icon = cls.Cert.new(obj.cert.get('icon'))
        obj.cert_binary = cls.Cert.new(obj.cert.get('binary'))
        return obj


class FirBinaryResponse:
    is_completed = False
    download_url = ''
    release_id = ''

    def __init__(self, is_completed, download_url, release_id):
        self.is_completed = is_completed
        self.download_url = download_url
        self.release_id = release_id

