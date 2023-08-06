# 全栈自动化测试框架

## 支持平台
* 支持安卓、IOS、H5、Web、接口、windows、mac

## 环境部署

* 安装allure：
    - 下载地址： https://github.com/allure-framework/allure2/releases
    - windows: 直接下载allure的zip包，解压到本地，然后配置到环境变量
    - mac：使用brew命令安装
      * 安装brew：/usr/bin/ruby -e "$(curl -fsSL https://cdn.jsdelivr.net/gh/ineo6/homebrew-install/install)"
      * brew install allure
* 安装python依赖库
    - 默认：pip install -i https://pypi.tuna.tsinghua.edu.cn/simple qrunner
    - mac端：pip install -i https://pypi.tuna.tsinghua.edu.cn/simple qrunner[mac]
    - windows端：pip install -i https://pypi.tuna.tsinghua.edu.cn/simple qrunner[win]