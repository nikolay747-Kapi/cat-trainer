[app]

# Название и пакет
title = Cat Training Coach
package.name = cattrainingcoach
package.domain = org.cattraining

# Исходники
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json,ttf
version = 1.0

# Зависимости. pillow убран: приложению он не нужен (KivyMD использует его только в
# палитре цветов), а его сборка тянет freetype с download.savannah.gnu.org,
# который часто отвечает 502/504 и роняет сборку.
requirements = python3==3.11.9,hostpython3==3.11.9,kivy==2.3.1,kivymd==1.2.0

# Экран
orientation = portrait
fullscreen = 0

# Разрешения: только вибрация
android.permissions = VIBRATE

# Android
android.api = 33
android.minapi = 24
android.ndk = 25b
android.archs = arm64-v8a
android.accept_sdk_license = True
android.allow_backup = True

# Загрузчик
p4a.bootstrap = sdl2

[buildozer]
log_level = 2
warn_on_root = 1
