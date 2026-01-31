# ------------- Buildozer 配置文件模板 -------------
[app]

# (str) 应用名称
title = MyTradeApp

# (str) 包名 (安卓唯一标识)
package.name = mytradeapp

# (str) 包名域名，一般随便写
package.domain = org.example

# (str) 源代码目录或主文件
source.dir = .

# (list) 包含的文件扩展名
source.include_exts = py,png,jpg,kv

# (list) Python 依赖库
requirements = python3,kivy==2.2.1,requests

# (str) Python 主入口文件
entrypoint = main.py

# (str) APP 图标（可选）
# icon.filename = %(source.dir)s/icon.png

# (str) 应用版本
version = 0.1

# (str) 需要的最小 Android API
android.minapi = 21

# (str) Android SDK 目标版本
android.sdk = 33

# (str) Android NDK 版本
android.ndk = 25b

# (bool) 是否允许多点触控
android.multidex = True

# (str) 屏幕方向
orientation = portrait

# (bool) 是否启用 Kivy log
log_level = 2

# (str) 编译模式
android.release = False

# (bool) 是否打包成 debug APK（测试用）
android.debug = True

# (str) 输出 APK 路径（可不改）
# bin/

# (bool) 是否使用 SDL2 渲染（Kivy 默认）
android.presplash = splash.png

# (bool) 使用 Kivy 默认 window
fullscreen = 0

# ------------- Android 配置（可选） -------------
[buildozer]

# 构建工具
# buildozer 默认命令可用