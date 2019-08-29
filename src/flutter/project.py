import os


class FlutterProject:
    version_code = ""
    version_name = ""

    def __init__(self, path="./"):
        self.path = path
        self.load_info()

    def load_info(self):
        path = os.path.join(self.path, "pubspec.yaml")
        try:
            with open(path, 'r', errors="ignore") as f:
                con = f.readlines()
                for line in con:
                    if "version:" in line:
                        version = line.replace("version:", "").strip(' \n').split('+')
                        if len(version) == 2:
                            self.version_code = version[1]
                            self.version_name = version[0]
        except IOError:
            pass


