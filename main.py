import sys

from src.project.build import Build
from src.project.project import ProjectType

build = Build()
print("你的项目为：", build.project.project_type.value)

if build.project.project_type == ProjectType.Unknown:
    print("请切换到项目路径后运行本程序")
    exit(1)

# 接收传入的类型
in_type = ""
for item in sys.argv:
    if "type" in item:
        arr = item.split('=')
        if len(arr) > 1:
            in_type = arr[1].strip(" ")
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




