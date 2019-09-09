import os
import sys

from src.project.build import Build
from src.project.project import ProjectType


"""
    in_path : 项目路径 
            1.接收传入的路径
            2.如果没有传入，采用当前路径
            3.如果以上路径不支，查找上线目录
    in_type : 接收传入的类型，不传的话会提示选择
"""

# 处理输入的参数
in_path = ""
in_type = ""
for item in sys.argv:
    if os.path.isdir(item):
        in_path = item
    elif "type" in item:
        arr = item.split('=')
        if len(arr) > 1:
            in_type = arr[1].strip(" ")


# 1. 采用传入的目录
if in_path:
    # 切换目录
    os.chdir(in_path)
    build = Build()
    # 检查项目
    if build.project.project_type == ProjectType.Unknown:
        print("项目路径错误1")
        exit(1)
else:
    # 2. 采用当前目录
    build = Build()
    if build.project.project_type == ProjectType.Unknown:
        print("项目路径错误2")
        exit(1)
    else:
        # 3. 采用上级目录
        os.chdir("..")
        build = Build()
        if build.project.project_type == ProjectType.Unknown:
            print("项目路径错误3")
            exit(1)

# 项目路径正确
print("你的项目为：", build.project.project_type.value)


# 如果没有传入就提醒输入
if not in_type:
    s = input("""请输入要操作的类型：
  11. apk ➣ 蒲公英 ➣ 钉钉
  12. apk ➣ 阿里云 ➣ 钉钉
  21. ipa ➣ 蒲公英 ➣ 钉钉
  22. ipa ➣ TestFlight ➣ 钉钉
➜ """)
    in_type = s.strip(" ")

if in_type == "11":
    print("11. apk ➣ 蒲公英 ➣ 钉钉")
    build.android_release_to_pgy()
elif in_type == "12":
    print("12. apk ➣ 阿里云 ➣ 钉钉")
    build.android_release_to_oss2()
elif in_type == "21":
    print("21. ipa ➣ 蒲公英 ➣ 钉钉")
    build.ios_ad_hoc_to_pgy()
elif in_type == "22":
    print("22. ipa ➣ TestFlight ➣ 钉钉")
    build.ios_release_to_test_flight()
else:
    print("你的参数输入有误:", in_type)




