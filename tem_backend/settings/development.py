from .base import *

DEBUG = True
ALLOWED_HOSTS = ["*"]


DATABASES = {
    "default": env.db_url("DATABASE_URL", default="sqlite:///db.sqlite3"
)
}

INSTALLED_APPS += ["debug_toolbar"]
MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")
INTERNAL_IPS = ["127.0.0.1"]

PAYSTACK_PUBLIC_KEY   = env("TEST_PAYSTACK_PUBLIC_KEY")
PAYSTACK_SECRET_KEY   = env("TEST_PAYSTACK_SECRET_KEY")
PAYSTACK_CALLBACK_URL = env("TEST_PAYSTACK_CALLBACK_URL")
PAYSTACK_WEBHOOK_URL = env("TEST_PAYSTACK_WEBHOOK_URL")

DEFAULT_FROM_EMAIL = env("TEST_DEFAULT_FROM_EMAIL")

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"