'''
Test settings

- Used to run tests fast on the continuous integration server and locally
'''

from .base import *  # noqa

DEBUG = False
TEMPLATES[0]['OPTIONS']['debug'] = False

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': ''
    }
}

TEST_RUNNER = 'django.test.runner.DiscoverRunner'
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]
