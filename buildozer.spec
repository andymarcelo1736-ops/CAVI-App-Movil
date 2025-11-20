[app]

# Nombre y Paquete
title = CAVI - AS
package.name = caviapp
package.domain = com.cavi

# Directorios
source.dir = .
source.include_exts = py,png,jpg,kv,atlas

# Versión
version = 0.1

# --- REQUISITOS ACTUALIZADOS ---
# Quitamos las restricciones de versión (==) para usar las más modernas compatibles con NDK 25
# Agregamos 'openssl' que es vital para requests
requirements = python3,kivy,kivymd,requests,openssl,urllib3,chardet,idna

orientation = portrait
fullscreen = 0

# Permisos
android.permissions = INTERNET
android.allow_cleartext_traffic = True

# --- CONFIGURACIÓN ANDROID ---
android.api = 33
android.minapi = 21
android.ndk = 25b
android.accept_sdk_license = True
android.entrypoint = org.kivy.android.PythonActivity
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True

# --- LA CLAVE DEL ÉXITO ---
# Usar la rama 'develop' de python-for-android arregla los errores de compilación recientes
p4a.branch = develop

[buildozer]
log_level = 2
warn_on_root = 1