import re
import os
import time


# Android项目相关信息
from src.error.error import BuildException


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

    def __init__(self, path):
        self._format_apk_name = ""
        if not os.path.isdir(os.path.join(path, "app")):
            raise BuildException("Android:工程信息读取错误")
        self.path = path
        self.__load_data()

    def __load_data(self):
        """
        加载相加信息
        :return:
        """
        self.application_name = self.__load_application_name()
        self.__load_version_info()

    def __load_version_info(self):
        """
        加载版本相关信息
        :return:
        """
        path = os.path.join(self.path, self._app_build_gradle_path)
        # 应用 id 、版本信息
        with open(path, 'r', errors="ignore") as f:
            con = f.read()
            self.application_id = re.search(r'applicationId\s\"(.*.\w+)\"', con).group(1)
            result = re.search(r'versionName\s"([.|\d]+)"', con)
            self.version_name = result and result.group(1) or "1.0"
            result = re.search(r'versionCode\s(\d+)', con)
            self.version_code = result and result.group(1) or "1"

    def __load_application_name(self):
        """
        加载应用名称
        :return:
        """
        try:
            with open(self._strings_xml_path) as f:
                con = f.read()
                return re.search(r'<string name="app_name">(.+)</string>', con).group(1)
        except IOError:
            with open(self._manifest_xml_path) as f:
                con = f.read()
                result = re.search(r'android:label="(.+)"', con)
                return result and result.group(1) or "未知名称"

    @property
    def format_apk_name(self):
        """
        # 格式化apk输出名称
        :return:
        """
        if not len(self._format_apk_name):
            # 命名规则 = 包名最后一项 + 版本号 + 时间 + apk
            prefix = self.short_application_id + "-" + self.version_name + "_" + self.version_code + "_"
            self._format_apk_name = prefix + time.strftime("%Y%m%d_%H.%M", time.localtime()) + ".apk"
        return self._format_apk_name

    @property
    def short_application_id(self):
        """
        # 应用 id 后缀
        :return:
        """
        return self.application_id.split(".")[-1]

    @property
    def _strings_xml_path(self):
        """
        # Android 名称 配置路径
        :return:
        """
        return os.path.join(self.path, 'app/src/main/res/values/strings.xml')

    @property
    def _manifest_xml_path(self):
        """
        # AndroidManifest 路径
        :return:
        """
        return os.path.join(self.path, 'app/src/main/AndroidManifest.xml')
