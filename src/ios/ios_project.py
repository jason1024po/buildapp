import os
import re
import time


class IOSProject:
    project_path: str
    application_id: str
    application_name: str
    version_name: str
    version_code: str
    info_plist_path: str = ""
    xcodeproj_name: str
    xcworkspace_name: str
    export_ipa_name: str
    # 是否加载错误
    is_load_error = False
    # ipa 全称
    _format_ipa_name = ""

    def __init__(self, path="ios"):
        self.project_path = os.path.abspath(path)
        # 加载信息
        self.load_info()

    def get_scheme(self):
        scheme = self.xcodeproj_name.replace(".xcodeproj", "")
        return scheme

    #  加载工程及应用信息
    def load_info(self):
        # 1. 查找 plist
        self.find_plist_path(self.project_path, "Info.plist")
        # 1.1 判断是否加载成功
        self.is_load_error = not len(self.info_plist_path)
        if self.is_load_error:
            return
        # 1.2 读取 plist 内容
        with open(self.info_plist_path, 'r', errors="ignore") as f:
            info_con = f.read()
            # 2. 读取应用名称
            pattern = r"<key>CFBundleDisplayName</key>.*\n.*<string>(.+)</string>"
            self.application_name = re.search(pattern, info_con).group(1)
            # 3. 读取版本号
            pattern = r"<key>CFBundleShortVersionString</key>[\s\n]*<string>([\.|\S]+)</string>"
            result = re.search(pattern, info_con)
            self.version_name = result and result.group(1) or "1.0"
            pattern = r"<key>CFBundleVersion</key>[\s\n]*<string>([\.|\S]+)</string>"
            result = re.search(pattern, info_con)
            self.version_code = result and result.group(1) or "1"
            # 4. 先读取工程信息
            self.load_xcode_project_info()
            # 5. 再读取应用 id
            self.load_application_id()
            # 6. 判断是否加载成功
            self.is_load_error = not len(
                self.application_id) or not len(self.application_name)

    # 格式化apk输出名称
    def get_format_ipa_name(self):
        if not len(self._format_ipa_name):
            # 命名规则 = 包名最后一项 + 版本号 + 时间 + apk
            prefix = (
                    self.get_application_id_suffix()
                    + "-"
                    + self.version_name
                    + "_"
                    + self.version_code
                    + "_"
            )
            self._format_ipa_name = (
                    prefix + time.strftime("%Y%m%d_%H.%M", time.localtime()) + ".ipa"
            )
        return self._format_ipa_name

    # 加载 xcode 工程信息
    def load_xcode_project_info(self):
        items = os.listdir(self.project_path)
        for item in items:
            if item.endswith(".xcodeproj"):
                self.xcodeproj_name = item
            elif item.endswith(".xcworkspace"):
                self.xcworkspace_name = item

    # iOS 找到包名配置文件路径
    def get_project_pbxproj_path(self):
        return os.path.join(self.project_path, self.xcodeproj_name, "project.pbxproj")

    # 加载应用 包名配置
    def load_application_id(self):
        pattern = r"PRODUCT_BUNDLE_IDENTIFIER\s=\s(.*\.\w+);"
        with open(self.get_project_pbxproj_path(), 'r', errors="ignore") as f:
            con = f.read()
            self.application_id = re.search(pattern, con).group(1)

        # 应用 id 后缀
    def get_application_id_suffix(self):
        return self.application_id.split(".")[-1]

    # 查找 plist - 递归5层目录查找
    def find_plist_path(self, root, target, depth=5):
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
                self.find_plist_path(path, target, depth=depth - 1)
            elif item == target:
                # 包涵 CFBundleDisplayName 才是真的
                with open(path, 'r', errors='ignore') as f:
                    if "CFBundleDisplayName" in f.read():
                        self.info_plist_path = path
