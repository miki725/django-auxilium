# Bare ``settings.py`` for running tests for django_auxilium

DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'django_auxilium.sqlite'
    }
}

INSTALLED_APPS = (
    #'django.contrib.auth',
    #'django.contrib.contenttypes',
    'django_nose',
    'django_auxilium',
)

TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
NOSE_ARGS = (
    '--all-modules',
    '--with-doctest',
    '--with-coverage',
    '--cover-package=django_auxilium',
)

STATIC_URL = '/static/'
SECRET_KEY = 'foo'
