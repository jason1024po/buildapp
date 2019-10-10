import os
import subprocess

from src.error.error import BuildException


class TestFlight:
    # apple上传工具地址
    _al_tool_path = r"/Applications/Xcode.app/Contents/Applications/Application\ " \
                    r"Loader.app/Contents/Frameworks/ITunesSoftwareService.framework/Versions/A/Support/altool "

    # 上传到 TestFlight
    @classmethod
    def upload(cls, ipa: str, user_name: str, password: str):
        # 0. 检查帐号
        if not user_name or not password:
            raise BuildException("没有配置apple帐号")
        # 1. 验证ipa
        cls.__verify_ipa(ipa, user_name, password)
        # 2. 开始上传
        cls.__upload_ipa(ipa, user_name, password)

    # 验证 ipa
    @classmethod
    def __verify_ipa(cls, ipa: str, user_name: str, password: str):
        # 1. 验证 ipa
        args = [cls._al_tool_path, "--validate-app", "-f", ipa, "-u", user_name, "-p", password]
        print("执行命令：", " ".join(args))
        print("正在验证中...")
        process = subprocess.Popen(" ".join(args), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        process.wait()
        res = process.stdout.read().decode('utf-8')
        # 1.1. 验证是否成功
        verify_str = "No errors validating archive at"
        if verify_str not in res:
            print("验证失败")
            raise BuildException(cls.__get_error_message(res))
        print("验证成功:SUCCESS")

    # 上传ipa
    @classmethod
    def __upload_ipa(cls, ipa: str, user_name: str, password: str):
        args = [cls._al_tool_path, "--upload-app", "-t ios", "-f", ipa, "-u", user_name, "-p", password]
        print("执行命令：", " ".join(args))
        print("正在上传中，时间较长，请耐心等待...")
        process = subprocess.Popen(" ".join(args), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        process.wait()
        res = process.stdout.read().decode('utf-8')
        # 2.1 验证是否成功
        verify_str = "No errors uploading"
        if verify_str not in res:
            raise BuildException(cls.__get_error_message(res))
        print("上传成功:SUCCESS")

    # 解析上传错误消息
    @classmethod
    def __get_error_message(cls, raw: str):
        print(raw)
        if "Code=1091" in raw:
            return "版本号冲突，请修改版本号后再试"
        elif "Code=-21026" in raw:
            return "苹果无法验证身份~"
        elif "Code=-19000" in raw:
            return "网络连接到苹果失败"
        else:
            return "上传到苹果失败,请检查~"
