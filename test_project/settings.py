# Bare ``settings.py`` for running tests for django_auxilium

DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'django_auxilium.sqlite'
    }
}

INSTALLED_APPS = [
    'django_auxilium',
]

MIDDLEWARE_CLASSES = []

STATIC_URL = '/static/'
SECRET_KEY = 'foo'
