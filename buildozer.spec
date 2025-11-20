[app]

# Nombre y Paquete
title = CAVI - AS
package.name = caviapp
package.domain = com.cavi

# Directorios y Archivos
source.dir = .
source.include_exts = py,png,jpg,kv,atlas

# Versión
version = 0.1

# --- REQUISITOS (Versiones estables para GitHub Actions) ---
requirements = python3,kivy==2.2.1,kivymd==1.1.1,requests,urllib3,chardet,idna

# Pantalla
orientation = portrait
fullscreen = 0

# Permisos y Red
android.permissions = INTERNET
android.allow_cleartext_traffic = True

# --- CONFIGURACIÓN ANDROID ---
android.api = 31
android.minapi = 21
android.ndk = 25b
android.accept_sdk_license = True
android.entrypoint = org.kivy.android.PythonActivity
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True

[buildozer]
log_level = 2

warn_on_root = 1
