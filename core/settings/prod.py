from django.core.exceptions import ImproperlyConfigured

from .base import *

DEBUG = False
if SECRET_KEY == "development-only-insecure-key":
    raise ImproperlyConfigured("DJANGO_SECRET_KEY must be set for production.")
if not ALLOWED_HOSTS:
    raise ImproperlyConfigured("DJANGO_ALLOWED_HOSTS must be set for production.")
SECURE_CONTENT_TYPE_NOSNIFF = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
