import os
import shutil
from enum import Enum, unique
from pathlib import Path

from src.config.config import *
from src.dingding.dingding import DingDing
from src.error.error import BuildException
from src.ios.ios_project import IOSProject

from src.ios.test_flight import TestFlight
from src.ios.utils import export_ipa, export_archive
from src.oss.oss import OSS
from src.pgyer.pgyer import PGY

# iOS 导出类型
@unique
class ExportType(Enum):
    Debug = "debug"
    AdHoc = "release"
    Release = "release.appStore"


class IOSBuild:

    # 项目信息
    project: IOSProject

    # 导出类型
    export_type = ExportType.Debug

    # 导出 plist 路径
    export_options_debug_path = ""
    export_options_adhoc_path = ""
    export_options_app_store_path = ""

    def __init__(self, path="ios"):
        self.path = path
        self.project = IOSProject(self.path)
        self.__load_export_plist(self.path)

    # 打包到蒲公英
    def build_to_pgy(self):
        try:
            self.export_type = ExportType.AdHoc
            self.__build()
            print("正在上传到蒲公英...")
            result = PGY.upload(self.export_ipa_path)
            DingDing.send_with_pgy_response(result)
        except BuildException as e:
            self.__send_failure_message(e.message)
            raise e

    # 上传到苹果
    def build_to_app_store(self):
        self.export_type = ExportType.Release
        try:
            self.__build()
            TestFlight.upload(self.export_ipa_path, APPLE_USERNAME, APPLE_PASSWORD)
            # 上传到阿里云
            url = self.__put_success_message()
            self.__send_success_message(url)
        except BuildException as e:
            self.__send_failure_message(str(e))
            raise e

    def __build(self):
        self.__export_archive()
        self.__export_ipa()

    # 发送失败消息
    def __send_failure_message(self, msg):
        app_name = self.project.application_name
        DingDing.send_prod_failure_message(app_name, "iOS", self.project.version_name, self.project.version_code, msg)

    # 发送成功消息
    def __send_success_message(self, data):
        # 发送消息到钉钉
        app_name = self.project.application_name
        version_name = self.project.version_name
        version_code = self.project.version_code
        DingDing.send_prod_message(app_name, version_name, version_code, data)

    def __put_success_message(self):
        ipa_name = self.project.format_ipa_name
        name = os.path.join(self.project.short_application_id, "ipa", ipa_name + ".txt")
        text = "{}-请等待十分钟后从TestFlight测试此版本-{}({})".format(self.project.application_name,
                                                          self.project.version_name,
                                                          self.project.version_code)
        url = OSS.put_text(name, text)
        return url

    # 导出archive
    def __export_archive(self):
        # 1. 删除缓存
        self.__clean_archive()
        path = self.archive_file_path
        scheme = self.project.scheme
        xcworkspace = self.get_abspath(self.project.xcworkspace_name)
        configuration = str(self.export_type.value).replace(".appStore", "")
        xcodeproj = self.get_abspath(self.project.xcodeproj_name)
        export_archive(path, scheme, xcworkspace, xcodeproj, configuration)

    # 导出 ipa
    def __export_ipa(self):
        # 清除旧包
        print("正在清除ipa...")
        print("rm", self.export_ipa_path)
        self.__clean_ipa()
        export_ipa(self.archive_file_path, self.export_ipa_dir, self.export_ipa_path, self.export_plist_path)

    def __clean_archive(self):
        print("正在清除archive...")
        print("rm", self.archive_file_path)
        if os.path.isdir(self.archive_file_path):
            shutil.rmtree(self.archive_file_path)

    def __clean_ipa(self):
        if os.path.isdir(self.export_ipa_dir):
            shutil.rmtree(self.export_ipa_dir)

    def get_abspath(self, path):
        return os.path.abspath(os.path.join(self.path, path))

    @property
    def export_ipa_dir(self):
        return os.path.join(str(Path.home()), "tmp", "ipa", self.project.application_id)

    @property
    def export_ipa_path(self):
        return os.path.join(self.export_ipa_dir, self.project.scheme + ".ipa")

    @property
    def archive_dir(self):
        return os.path.join(str(Path.home()), "tmp/", "archive")

    @property
    def archive_file_path(self):
        return os.path.join(self.archive_dir, self.project.application_id + ".xcarchive")

    @property
    def export_plist_path(self):
        if self.export_type == ExportType.Release:
            return self.export_options_app_store_path
        elif self.export_type == ExportType.AdHoc:
            return self.export_options_adhoc_path
        else:
            return self.export_options_debug_path

    # 递归查找导出所需plist文件
    def __load_export_plist(self, root, depth=5):
        # 遍历到指定深度
        if depth < 0:
            return
        # 读取目录
        items = os.listdir(root)
        # 遍历目录
        for item in items:
            # 忽略隐藏目录
            if item.startswith("."):
                continue
            # 是目录接着往下找
            path = os.path.join(root, item)
            if os.path.isdir(path):
                self.__load_export_plist(path, depth=depth - 1)
            elif item == EXPORT_DEBUG_PLIST_NAME:
                self.export_options_debug_path = path
            elif item == EXPORT_AD_HOC_PLIST_NAME:
                self.export_options_adhoc_path = path
            elif item == EXPORT_APP_STORE_PLIST_NAME:
                self.export_options_app_store_path = path
