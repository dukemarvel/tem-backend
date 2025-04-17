from .base import *

DEBUG = True
ALLOWED_HOSTS = ["*"]

# override DB for dev via .env or fallback
DATABASES = {
    "default": env.db_url("DATABASE_URL", default="sqlite:///db.sqlite3"
)
}

INSTALLED_APPS += ["debug_toolbar"]
MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")
INTERNAL_IPS = ["127.0.0.1"]
