from .base import *

DEBUG = False
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["your.domain.com"])

DATABASES = {
    "default": env.db_url("DATABASE_URL")
}

# Security hardening
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
