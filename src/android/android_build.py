import subprocess
import os

from pathlib import Path

from src.dingding.dingding import DingDing
from src.error.error import BuildException
from src.oss.oss import OSS

from src.android.android_project import AndroidProject


# 打包 Android 相关
from src.pgyer.pgyer import PGY


class AndroidBuild:
    # 默认打包目录
    android_release_dir = ""
    # 默认打包名称
    default_apk_name = "app-release.apk"
    # 默认打包路径
    default_apk_path = ""

    def __init__(self, path=".", android_release_dir="app/build/outputs/apk/release"):
        self.path = path
        self.android_release_dir = android_release_dir
        # 加载 Android 项目信息
        self.project = AndroidProject(self.path)
        self.default_apk_path = os.path.join(self.android_release_dir, self.default_apk_name)

    # 上传到蒲公英
    def build_to_pgy(self):
        try:
            self.__build()
            # 上传到蒲公英
            result = PGY.upload(self.__get_new_apk_path())
            DingDing.send_with_pgy_response(result)
        except BuildException as e:
            self.__send_failure_message(e.message)
            raise e

    # 上传到阿里 oss
    def build_to_ali_oss(self):
        try:
            self.__build()
            # 上传到阿里云
            name = os.path.join(self.project.get_application_id_suffix(), self.__get_new_apk_name())
            url = OSS.put_file(name, self.__get_new_apk_path())
            print("上传成功:", url)
            # 发送消息到钉钉
            self.__send_success_message(url)
            return True
        except BuildException as e:
            self.__send_failure_message(e.message)
            raise e

    # 发送成功消息
    def __send_success_message(self, data):
        app_name = self.project.application_name
        version_name = self.project.version_name
        version_code = self.project.version_code
        DingDing.send_prod_message(app_name, version_name, version_code, data)

    # 发送失败消息
    def __send_failure_message(self, message='无'):
        app_name = self.project.application_name
        version_name = self.project.version_name
        version_code = self.project.version_code
        DingDing.send_prod_failure_message(app_name, "Android", version_name, version_code, message)

    # 清理并打包 apk
    def __build(self):
        if self.project.is_error:
            raise BuildException("Android工程目录错误")
        # 1. 删除旧包
        print("正在清除旧包...")
        self.__remove_all()
        # 2. 打包apk
        print("开始打包apk...")
        self.__build_apk()
        print(self.default_apk_path)
        # 3. 判断文件是否成功
        if not Path(self.default_apk_path).is_file():
            raise BuildException("文件不存在，打包失败")
        # 4. 重命名
        self.__rename_apk()

    # 新包名
    def __get_new_apk_name(self):
        return self.project.get_format_apk_name()

    # 新包名路劲
    def __get_new_apk_path(self):
        return os.path.join(self.android_release_dir, self.__get_new_apk_name())

    # 重命名
    def __rename_apk(self):
        os.rename(self.default_apk_path, self.__get_new_apk_path())

    # 打包 apk
    def __build_apk(self):
        if os.system("cd {} && ./gradlew assembleRelease".format(self.path)):
            raise BuildException("gradle 打包失败~")

    # 清除旧包
    def __remove_all(self):
        print(self.android_release_dir)
        if os.path.isdir(self.android_release_dir):
            for name in os.listdir(self.android_release_dir):
                os.remove(os.path.join(self.android_release_dir, name))
