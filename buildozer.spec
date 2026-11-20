[app]
# Buildozer configuration for ESON CALCULATOR 🇿🇲
title = ESON CALCULATOR 🇿🇲
pacakge.name = esoncalculator
package.domain = zm.co.esondaniels
source.dir = .
source.include_exts = py,json,kv,png,jpg,ttf,atlas
version = 1.0.0
requirements = python3,kivy,plyer
orientation = portrait
fullscreen = 0
android.permissions = VIBRATE
android.api = 35
android.minapi = 23
android.ndk = 27c
android.archs = arm64-v8a, armeabi-v7a
android.accept_sdk_license = True
android.allow_backup = True

[buildozer]
log_level = 2
warn_on_root = 1
