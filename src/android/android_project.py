import re
import os
import time


# Android项目相关信息
class AndroidProject:
    # 应用名称
    application_name = ""
    # 应用 id
    application_id = ""
    # 显示版本号
    version_name = ""
    # 内部版本号
    version_code = ""
    # 配置文件
    _app_build_gradle_path = "app/build.gradle"
    # flutter 版本号配置文件
    _local_properties_path = "local.properties"
    # 格式化后的名称
    _format_apk_name = ""
    # 是否出错
    is_error = False

    def __init__(self, path):
        if not os.path.isdir(os.path.join(path, "app")):
            self.is_error = True
            return
        self.path = path
        self.load()

    # 加载数据
    def load(self):
        print(os.getcwd())
        # 获取 applicationId
        path = os.path.join(self.path, self._app_build_gradle_path)

        # 应用名称
        with open(self.get_strings_xml_path(), 'r', errors="ignore") as f:
            con = f.read()
            self.application_name = re.search(r'<string name="app_name">(.+)</string>', con).group(1)
        # 应用 id 、版本信息
        with open(path, 'r', errors="ignore") as f:
            con = f.read()
            self.application_id = re.search(r'applicationId\s\"(.*.\w+)\"', con).group(1)
            self.version_name = re.search(r'versionName\s"([.|\d]+)"', con).group(1)
            self.version_code = re.search(r'versionCode\s(\d+)', con).group(1)
        # 获取版本信息Flutter
        if not "isFlutter":
            read_path = os.path.join(self.path, self._local_properties_path)
            with open(read_path, "r", errors="ignore") as f:
                values = {}
                for line in f.readlines():
                    arr = line.strip("\n").split("=")
                    if len(arr) > 1:
                        values[arr[0]] = arr[1]
                if "flutter.versionCode" in values:
                    self.version_code = values["flutter.versionCode"]
                if "flutter.versionName" in values:
                    self.version_name = values["flutter.versionName"]

    # 格式化apk输出名称
    def get_format_apk_name(self):
        if not len(self._format_apk_name):
            # 命名规则 = 包名最后一项 + 版本号 + 时间 + apk
            prefix = (
                    self.get_application_id_suffix()
                    + "-"
                    + self.version_name
                    + "_"
                    + self.version_code
                    + "_"
            )
            self._format_apk_name = (
                    prefix + time.strftime("%Y%m%d_%H.%M", time.localtime()) + ".apk"
            )
        return self._format_apk_name

    # 应用 id 后缀
    def get_application_id_suffix(self):
        return self.application_id.split(".")[-1]

    # Android 名称 配置路径
    def get_strings_xml_path(self):
        return os.path.join(self.path, 'app/src/main/res/values/strings.xml')
