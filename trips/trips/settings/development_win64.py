from .common import *

# Настройки для отладки под Windows x64

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1', '192.168.0.103']

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

ENABLE_DEMO_REQUEST = True

# Залипуха для винды, чтобы pydf подхватил экзешник wkhtmltopdf.exe
# (в пакете python-pdf идёт только сборка wkhtmltopdf под линукс)
if os.name == 'nt':
    os.environ['WKHTMLTOPDF_PATH'] = os.path.join(BASE_DIR, 'bin', 'windows-x86_64',
                                                  'wkhtmltox-0.12.5-1.mxe-cross-win64', 'wkhtmltopdf.exe')
