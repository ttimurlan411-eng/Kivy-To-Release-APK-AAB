[app]
title = Сапер
package.name = saper
package.domain = org.example.saper
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1
requirements = python3,kivy
orientation = portrait

fullscreen = 0
android.api = 33
android.minapi = 24
android.sdk = 20
android.ndk = 25c
android.archs = arm64-v8a
android.enable_androidx = True
android.allow_backup = True
android.copy_libs = 1

[buildozer]
log_level = 2
warn_on_root = 1
