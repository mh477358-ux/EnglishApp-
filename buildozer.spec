[app]

title = English Vocabulary
package.name = englishvocabulary
package.domain = org.mh477358
source.dir = .
source.include_exts = py,kv,png,jpg,jpeg,atlas,ttf,otf
version = 0.1.0

requirements = python3,kivy,plyer,arabic-reshaper,python-bidi
orientation = portrait
fullscreen = 0

android.permissions = INTERNET
android.api = 35
android.minapi = 24
android.archs = arm64-v8a
android.accept_sdk_license = True

p4a.branch = develop

[buildozer]

log_level = 2
warn_on_root = 1
