import os
import shutil
from enum import Enum, unique
from pathlib import Path

from src.ali.oss import put_text_to_ali_oss
from src.config.config import *
from src.dingding.dingding import send_prod_fault_message, send_prod_message
from src.ios.app_store import upload_to_app_store
from src.ios.ios_project import IOSProject


# iOS 导出类型
from src.pgyer.pgyer import upload_to_pgy


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
        self._load_export_plist(self.path)

    # 打包到蒲公英
    def build_to_pgy(self):
        self.export_type = ExportType.AdHoc
        if self.export_archive() and self.export_ipa():
            print("正在上传到蒲公英...")
            upload_to_pgy(self.get_export_ipa_path())
            return True
        else:
            print("打包失败~")
            return False

    # 上传到苹果
    def build_to_app_store(self):
        self.export_type = ExportType.Release
        if not (self.export_archive() and self.export_ipa()):
            print("导出失败了~")
            app_name = self.project.application_name
            send_prod_fault_message(app_name, "iOS", self.project.version_name, self.project.version_code, "无")
            return False
        ipa_path = self.get_export_ipa_path()
        success, msg = upload_to_app_store(ipa_path, APPLE_USERNAME, APPLE_PASSWORD)
        if success:
            # 上传到阿里云
            ipa_name = self.project.get_format_ipa_name()
            name = os.path.join(self.project.get_application_id_suffix(), "ipa", ipa_name + ".txt")
            text = "{}-请等待十分钟后从TestFlight测试此版本-{}({})".format(self.project.application_name,
                                                              self.project.version_name,
                                                              self.project.version_code)
            url = put_text_to_ali_oss(name, text)
            if url:
                print("上传成功:", url)
                # 发送消息到钉钉
                app_name = self.project.application_name
                version_name = self.project.version_name
                version_code = self.project.version_code
                send_prod_message(app_name, version_name, version_code, url)
                return True
        else:
            app_name = self.project.application_name
            send_prod_fault_message(app_name, "iOS", self.project.version_name, self.project.version_code, msg)
            return False

    # 导出archive
    def export_archive(self):
        # 1. 删除缓存
        print("正在清除archive...")
        print("rm", self.get_archive_file_path())
        self._clean_archive()
        # 2. 配置参数
        archive_args = ["xcodebuild", "archive"]
        # 2.1 判断是否xcworkspace工程（cocoapods）
        if self.project.xcworkspace_name.endswith(".xcworkspace"):
            archive_args += ["-workspace", self.get_abspath(self.project.xcworkspace_name)]
        else:
            archive_args += ["-project", self.get_abspath(self.project.xcodeproj_name)]
        archive_args += ["-scheme", self.project.get_scheme()]
        archive_args += ["-configuration", str(self.export_type.value).replace(".appStore", "")]
        archive_args += ["-archivePath", self.get_archive_file_path()]
        archive_args.append("-quiet")
        print("开始导出archive...")
        print("执行:", " ".join(archive_args))
        if os.system(" ".join(archive_args)):
            return False
        # 判断是否成功
        if os.path.isfile(os.path.join(self.get_archive_file_path(), "Info.plist")):
            print("导出archive成功！")
            print(self.get_archive_file_path())
            return True
        else:
            print("导出archive失败！")
            print(self.get_archive_file_path())
            return False

    def _clean_archive(self):
        if os.path.isdir(self.get_archive_file_path()):
            shutil.rmtree(self.get_archive_file_path())

    def _clean_ipa(self):
        if os.path.isdir(self.get_export_ipa_dir()):
            shutil.rmtree(self.get_export_ipa_dir())

    # 导出 ipa
    def export_ipa(self):
        # 清除旧包
        print("正在清除ipa...")
        print("rm", self.get_export_ipa_path())
        self._clean_ipa()
        # 打包参数
        args = ["xcodebuild", "-exportArchive"]
        args += ["-archivePath", self.get_archive_file_path()]
        args += ["-exportPath", self.get_export_ipa_dir()]
        args += ["-exportOptionsPlist", self._get_export_plist_path()]
        args += ["-allowProvisioningUpdates", "-quiet"]
        print("正在导出ipa...")
        print("执行:", " ".join(args))
        if os.system(" ".join(args)):
            return False
        # 判断是否成功
        if os.path.isfile(self.get_export_ipa_path()):
            print("导出ipa成功！")
            print(self.get_export_ipa_path())
            return True
        else:
            print("导出ipa失败！")
            print(self.get_export_ipa_path())
            return False

    # ipa 路径
    def get_export_ipa_dir(self):
        return os.path.join(str(Path.home()), "tmp", "ipa", self.project.application_id)

    def get_export_ipa_path(self):
        return os.path.join(self.get_export_ipa_dir(), self.project.get_scheme() + ".ipa")

    def get_abspath(self, path):
        return os.path.abspath(os.path.join(self.path, path))

    @staticmethod
    def _get_archive_dir():
        return os.path.join(str(Path.home()), "tmp/", "archive")

    def get_archive_file_path(self):
        return os.path.join(self._get_archive_dir(), self.project.application_id + ".xcarchive")

    # 递归查找导出所需plist文件
    def _load_export_plist(self, root, depth=5):
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
                self._load_export_plist(path, depth=depth - 1)
            elif item == EXPORT_DEBUG_PLIST_NAME:
                self.export_options_debug_path = path
            elif item == EXPORT_AD_HOC_PLIST_NAME:
                self.export_options_adhoc_path = path
            elif item == EXPORT_APP_STORE_PLIST_NAME:
                self.export_options_app_store_path = path

    def _get_export_plist_path(self):
        if self.export_type == ExportType.Release:
            return self.export_options_app_store_path
        elif self.export_type == ExportType.AdHoc:
            return self.export_options_adhoc_path
        else:
            return self.export_options_debug_path

