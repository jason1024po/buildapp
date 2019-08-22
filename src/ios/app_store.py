import os
import subprocess

# appStore上传工具
AL_TOOL_PATH = r"/Applications/Xcode.app/Contents/Applications/Application\ " \
               r"Loader.app/Contents/Frameworks/ITunesSoftwareService.framework/Versions/A/Support/altool "


# 解析上传错误消息
def get_error_message(raw: str):
    print(raw)
    if "Code=1091" in raw:
        return "版本号冲突，请修改版本号后再试"
    else:
        return "未知错误,请检查~"


# 上传到 appStore
def upload_to_app_store(ipa: str, user_name: str, password: str):
    # 1. 验证 ipa
    args = [AL_TOOL_PATH, "--validate-app", "-f", ipa, "-u", user_name, "-p", password]
    print("执行命令：", " ".join(args))
    print("正在验证中...")
    process = subprocess.Popen(" ".join(args), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    process.wait()
    res = process.stdout.read().decode('utf-8')
    # 1.1. 验证是否成功
    verify_str = "No errors validating archive at"
    if verify_str not in res:
        print("验证失败")
        return False, get_error_message(res)

    # 2. 开始上传
    args = [AL_TOOL_PATH, "--upload-app", "-t ios", "-f", ipa, "-u", user_name, "-p", password]
    print("执行命令：", " ".join(args))
    print("正在上传中，时间较长，请耐心等待...")
    process = subprocess.Popen(" ".join(args), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    process.wait()
    res = process.stdout.read().decode('utf-8')
    # 2.1 验证是否成功
    verify_str = "No errors uploading"
    if verify_str in res:
        return True, "SUCCESS:上传成功"
    else:
        return False, get_error_message(res)
