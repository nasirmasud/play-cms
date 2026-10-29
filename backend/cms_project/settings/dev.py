from .base import *

DEBUG = True

if not SECRET_KEY:
    SECRET_KEY = "dev-insecure-only-do-not-use-in-production"

ALLOWED_HOSTS = ["*"]

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

try:
    from .local import *  # noqa: F403
except ImportError:
    pass
