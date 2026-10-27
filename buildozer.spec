[app]

# Название и пакет
title = Cat Training Coach
package.name = cattrainingcoach
package.domain = org.cattraining

# Исходники
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json,ttf
version = 1.0

# Зависимости (версии строго по ТЗ)
requirements = python3==3.11.9,hostpython3==3.11.9,kivy==2.3.1,kivymd==1.2.0,pillow

# Экран
orientation = portrait
fullscreen = 0

# Разрешения: только вибрация
android.permissions = VIBRATE

# Android
android.api = 33
android.minapi = 24
android.ndk = 25b
android.archs = arm64-v8a, armeabi-v7a
android.accept_sdk_license = True
android.allow_backup = True

# Загрузчик
p4a.bootstrap = sdl2

[buildozer]
log_level = 2
warn_on_root = 1
