from .development_win64 import *

# Настройки для отладки под Windows x64 с выводом отладочных сообщений о доступе к БД

# Logging
# https://docs.djangoproject.com/en/3.2/topics/logging

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'extended': {
            'format': '{levelname} {asctime} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'trips.file': {
            'level': 'INFO',
            'class': 'main.logging.handlers.CustomLogFileHandler',
            'filename': 'log/django_site.log',
            'formatter': 'extended',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        }
    },
    'loggers': {
        '': {
            'handlers': ['trips.file'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.db.backends': {
            'level': 'DEBUG',
            'handlers': ['console'],
        }
    },
}
