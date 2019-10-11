import os
import re
import time

from src.error.error import BuildException


class IOSProject:
    project_path: str
    application_id: str
    application_name: str
    version_name: str
    version_code: str
    xcodeproj_name: str
    xcworkspace_name: str
    export_ipa_name: str

    def __init__(self, path="ios"):
        self._format_ipa_name = ""
        self._info_plist_path = ""
        self.project_path = os.path.abspath(path)
        self.__load_info()

    @property
    def scheme(self):
        return self.xcodeproj_name.replace(".xcodeproj", "")

    @property
    def short_application_id(self):
        return self.application_id.split(".")[-1]

    @property
    def format_ipa_name(self):
        """
        格式化ipa输出名称
        :return:
        """
        if not len(self._format_ipa_name):
            # 命名规则 = 包名最后一项 + 版本号 + 时间 + ipa
            prefix = (self.short_application_id + "-" + self.version_name + "_" + self.version_code + "_")
            self._format_ipa_name = prefix + time.strftime("%Y%m%d_%H.%M", time.localtime()) + ".ipa"
        return self._format_ipa_name

    def __load_info(self):
        self.__load_plist_path(self.project_path)
        if not len(self._info_plist_path):
            raise BuildException("iOS 工程加载失败")
        self.__load_version_info()
        # 1. 读取工程信息
        self.__load_xcode_project_info()
        # 2. 读取应用 id
        self.__load_application_id()
        # 3. 加载应用名称
        self.__load_application_name()
        # 4. 判断是否加载成功
        if not len(self.application_id) or not len(self.version_code):
            raise BuildException("iOS 工程加载失败2")

    def __load_version_info(self):
        """
        加载 plist版本信息
        :return:
        """
        with open(self._info_plist_path, 'r', errors="ignore") as f:
            info_con = f.read()
            # 3. 读取版本号
            pattern = r"<key>CFBundleShortVersionString</key>[\s\n]*<string>([\.|\S]+)</string>"
            result = re.search(pattern, info_con)
            self.version_name = result and result.group(1) or "1.0"
            pattern = r"<key>CFBundleVersion</key>[\s\n]*<string>([\.|\S]+)</string>"
            result = re.search(pattern, info_con)
            self.version_code = result and result.group(1) or "1"

    def __load_application_name(self):
        with open(self._info_plist_path, 'r', errors="ignore") as f:
            info_con = f.read()
            # 2. 读取应用名称 没有时取应用 id 最后面
            pattern = r"<key>CFBundleDisplayName</key>.*\n.*<string>(.+)</string>"
            results = re.search(pattern, info_con)
            if results:
                self.application_name = results.group(1)
            else:
                self.application_name = self.short_application_id

    def __load_xcode_project_info(self):
        """
        加载 xcode 工程信息
        :return:
        """
        items = os.listdir(self.project_path)
        for item in items:
            if item.endswith(".xcodeproj"):
                self.xcodeproj_name = item
            elif item.endswith(".xcworkspace"):
                self.xcworkspace_name = item

    def __load_application_id(self):
        """
        加载应用包名配置
        :return:
        """
        pattern = r"PRODUCT_BUNDLE_IDENTIFIER\s=\s(.*\.\w+);"
        with open(self.__get_project_pbxproj_path(), 'r', errors="ignore") as f:
            con = f.read()
            self.application_id = re.search(pattern, con).group(1)

    def __get_project_pbxproj_path(self):
        """
        iOS 找到包名配置文件路径
        :return:
        """
        return os.path.join(self.project_path, self.xcodeproj_name, "project.pbxproj")

        # 应用 id 后缀

    def __load_plist_path(self, root, target="Info.plist", depth=5):
        """
        # 查找 plist - 递归5层目录查找
        :param root: 路径
        :param target: 文件名
        :param depth:  深度
        :return:
        """
        # 遍历到指定深度
        if depth < 0:
            return
        # 忽略目录
        for v in ["Pods", "Tests", ".framework", ".app"]:
            if v in root:
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
                self.__load_plist_path(path, target, depth=depth - 1)
            elif item == target:
                # 包涵 CFBundleDisplayName 才是真的
                with open(path, 'r', errors='ignore') as f:
                    if "CFBundleName" in f.read():
                        self._info_plist_path = path
