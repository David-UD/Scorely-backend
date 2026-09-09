from .base import *  # noqa: F401, F403

DEBUG = False

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='').split(',')  # noqa: F405

CORS_ALLOW_ALL_ORIGINS = False
