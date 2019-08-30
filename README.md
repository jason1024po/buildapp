### 说明
* 一个支持 Flutter、ReactNative、原生 Android、iOS 的打包工具
* iOS/Android上传到蒲公英
* Android上传阿里云
* iOS上传到TestFlight
* 发送消息到钉钉
* 自动读取版本号来重命名上传包的文件名
* [这里查看运行效果图](https://github.com/xushengjiang0/buildapp/raw/master/doc/images/img1.png)

### 安装
使用Python3编写，所以得自行安装相关环境<br/>
目前项目只在Mac上面跑过 <br/>
安装依赖 `pipenv sync` <br/>
我不是Python大神，如果有安装问题大家自行根据错误来解决吧。
### 配置*
打开src/config/config.py进行配置 <br/>
最低配置是把蒲公英配置上，其它不配置的也行。 <br/>
*Android需要配置keystore <br/>
*iOS需要配置导出plist文件(放到项目中即可，然后在 config.py中配置下文件名即可) <br/>
*以上两项为必须配置，网上都相关教程，自行配置
### 使用
克隆本项目到你的工程中(也可以是其它地方) 然后运行： <br/>
 `python3 ./buildapp/main.py` <br/>
根据提示选择下面的打包方式<br/>
 11. apk ➣ 蒲公英 ➣ 钉钉<br/>
 12. apk ➣ 阿里云 ➣ 钉钉<br/>
 21. ipa ➣ 蒲公英 ➣ 钉钉<br/>
 22. ipa ➣ TestFlight ➣ 钉钉
### 相关文章
 1. 还在整理中...
 

