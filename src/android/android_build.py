import subprocess
import os

from pathlib import Path

from src.ali.oss import put_file_to_ali_oss
from src.dingding.dingding import send_prod_message, send_prod_fault_message
from src.pgyer.pgyer import upload_to_pgy

from src.android.android_project import AndroidProject


# 打包 Android 相关
class AndroidBuild:
    # 默认打包目录
    android_release_dir = ""
    # 默认打包名称
    default_apk_name = "app-release.apk"
    # 默认打包路径
    default_apk_path = ""

    # 加载 Android 项目信息
    android_project = None

    def __init__(self, path=".", android_release_dir="app/build/outputs/apk/release"):
        self.path = path
        self.android_release_dir = android_release_dir
        self.android_project = AndroidProject(self.path)
        self.default_apk_path = os.path.join(self.android_release_dir, self.default_apk_name)

    # 重命名
    def _rename_apk(self):
        os.rename(self.default_apk_path, self.get_new_apk_path())

    # 新包名
    def get_new_apk_name(self):
        return self.android_project.get_format_apk_name()

    # 新包名路劲
    def get_new_apk_path(self):
        return os.path.join(self.android_release_dir, self.get_new_apk_name())

    # 清除旧包
    def _remove_all(self):
        print(self.android_release_dir)
        if os.path.isdir(self.android_release_dir):
            for name in os.listdir(self.android_release_dir):
                os.remove(os.path.join(self.android_release_dir, name))

    def build_apk(self):
        if os.system("cd {} && ./gradlew assembleRelease".format(self.path)):
            print("打包失败~")
            return False
        return True

    # 上传到蒲公英
    def build_to_pgy(self):
        if self.build():
            # 上传到蒲公英
            upload_to_pgy(self.get_new_apk_path())
            return True
        else:
            print("打包失败了！")
            return False

    # 上传到阿里 oss
    def build_to_ali_oss(self):
        if self.build():
            # 上传到阿里云
            name = os.path.join(self.android_project.get_application_id_suffix(), self.get_new_apk_name())
            url = put_file_to_ali_oss(name, self.get_new_apk_path())
            if url:
                print("上传成功:", url)
                # 发送消息到钉钉
                app_name = self.android_project.application_name
                version_name = self.android_project.version_name
                version_code = self.android_project.version_code
                send_prod_message(app_name, version_name, version_code, url)
                return True
            else:
                print("上传失败：", url)
                self.send_fault_message()
                return False
        else:
            print("打包失败了！")
            self.send_fault_message()
            return False

    # 发送失败消息
    def send_fault_message(self):
        app_name = self.android_project.application_name
        version_name = self.android_project.version_name
        version_code = self.android_project.version_code
        send_prod_fault_message(app_name, "Android", version_name, version_code, "无")

    # 清理并打包 apk
    def build(self):
        if self.android_project.is_error:
            print("Android工程目录错误")
            return False
        # 删除旧包
        print("正在清除旧包...")
        self._remove_all()

        # 打包apk
        print("开始打包apk...")
        if not self.build_apk():
            return False
        print(self.default_apk_path)
        # 判断文件是否成功
        if not Path(self.default_apk_path).is_file():
            print("文件不存在，打包失败")
            return False
        else:
            self._rename_apk()
            return True
