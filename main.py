import sys

from src.android.android_build import AndroidBuild
from src.ios.ios_build import IOSBuild

for item in sys.argv:
    if "type" in item:
        arr = item.split('=')
        if len(arr) > 1:
            in_type = arr[1].strip(" ")

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
    AndroidBuild("android").build_to_pgy()
elif in_type == "12":
    print("12. apk ➣ 阿里云 ➣ 钉钉")
    AndroidBuild("android").build_to_ali_oss()
elif in_type == "21":
    print("21. ipa ➣ 蒲公英 ➣ 钉钉")
    IOSBuild("ios").build_test()
elif in_type == "22":
    print("22. ipa ➣ TestFlight ➣ 钉钉")
    IOSBuild("ios").build_to_app_store()
else:
    print("你的参数输入有误:", in_type)




