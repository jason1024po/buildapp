import os

from enum import Enum, unique
@unique
class ProjectType(Enum):
    ReactNative = "ReactNative"
    Flutter = "Flutter"
    NativeAndroid = "NativeAndroid"
    NativeIOS = "NativeIOS"
    Unknown = "unknown"


class Project:
    project_type = ProjectType.Unknown

    def __init__(self):
        self.check_project_type()

    # 检查项目类型
    def check_project_type(self):
        if os.path.isfile(os.path.join(os.getcwd(), "pubspec.yaml")):
            # Flutter 项目
            self.project_type = ProjectType.Flutter
        elif os.path.isfile(os.path.join(os.getcwd(), "package.json")):
            # ReactNative 项目
            self.project_type = ProjectType.ReactNative
        elif os.path.isfile(os.path.join(os.getcwd(), "app", "build.gradle")):
            # Android 项目
            self.project_type = ProjectType.NativeAndroid
        else:
            self.project_type = ProjectType.Unknown
            # 判断是否 ios 项目
            items = os.listdir(".")
            for item in items:
                if item.endswith(".xcodeproj") or item.endswith(".xcworkspace"):
                    self.project_type = ProjectType.NativeIOS


