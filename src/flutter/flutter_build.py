import os

from .project import FlutterProject


class FlutterBuild:
    android_release_dir = "build/app/outputs/apk/release"

    def __init__(self, path="./"):
        self.path = path
        self.project = FlutterProject(path)

    def build_apk(self):
        if os.system("flutter build apk".format(self.path)):
            return True
        return False

    def build_ios(self):
        if os.system("flutter build ios".format(self.path)):
            return True
        return False
