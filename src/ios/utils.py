# 导出 ipa
import os

from src.error.error import BuildException


# 导出archive
def export_archive(archive_path: str, scheme: str, workspace="", project="", configuration="release"):
    """
    导出 archive
    :param scheme:
    :param archive_path:
    :param workspace:
    :param project:
    :param configuration:
    :return:
    """
    # 2. 配置参数
    archive_args = ["xcodebuild", "archive"]
    # 2.1 判断是否xcworkspace工程（cocoapods）
    if workspace.endswith(".xcworkspace"):
        archive_args += ["-workspace", workspace]
    else:
        archive_args += ["-project", project]
    archive_args += ["-scheme", scheme]
    archive_args += ["-configuration", configuration]
    archive_args += ["-archivePath", archive_path]
    archive_args.append("-quiet")

    print("开始导出archive...")
    print("执行:", " ".join(archive_args))
    if os.system(" ".join(archive_args)):
        raise BuildException('执行导出archive失败')
    # 判断是否成功
    if os.path.isfile(os.path.join(archive_path, "Info.plist")):
        print("导出archive成功: " + archive_path)
    else:
        raise BuildException("导出archive失败！")


def export_ipa(archive_file_path: str, export_ipa_dir: str, export_ipa_path: str, export_plist_path: str):
    """
    导出 ipa
    :param archive_file_path:
    :param export_ipa_dir:
    :param export_ipa_path:
    :param export_plist_path:
    :return:
    """

    args = ["xcodebuild", "-exportArchive"]
    args += ["-archivePath", archive_file_path]
    args += ["-exportPath", export_ipa_dir]
    args += ["-exportOptionsPlist", export_plist_path]
    args += ["-allowProvisioningUpdates", "-quiet"]
    print("正在导出ipa...")
    print("执行:", " ".join(args))
    if os.system(" ".join(args)):
        return False
    # 判断是否成功
    print(export_ipa_path)
    if os.path.isfile(export_ipa_path):
        print("导出ipa成功！")
        return export_ipa_path
    else:
        raise BuildException("导出ipa失败！")
