[app]
title = Crypto Tapper
package.name = cryptotapper
package.domain = org.yourname
source.dir = .
source.include_exts = py,png,jpg,json
version = 0.1

# Тільки необхідне для роботи
requirements = python3,pygame==2.5.2

orientation = portrait
fullscreen = 1
android.archs = arm64-v8a

# Важливо для нових версій Android
android.api = 33
android.minapi = 21
android.ndk = 25b
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 1
