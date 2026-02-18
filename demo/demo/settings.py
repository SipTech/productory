import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = "productory-oss-demo-key"
DEBUG = True
ALLOWED_HOSTS = [host for host in os.getenv("DEMO_ALLOWED_HOSTS", "*").split(",") if host]
DEMO_ENABLE_JWT = os.getenv("DEMO_ENABLE_JWT", "false").lower() == "true"

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "django_filters",
    "productory_core",
    "productory_catalog",
    "productory_checkout",
    "productory_promotions",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "demo.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "demo.wsgi.application"
ASGI_APPLICATION = "demo.asgi.application"

DATABASES = {
    "default": {
        "ENGINE": os.getenv("DEMO_DB_ENGINE", "django.db.backends.sqlite3"),
        "NAME": os.getenv("DEMO_DB_NAME", str(BASE_DIR / "db.sqlite3")),
        "USER": os.getenv("DEMO_DB_USER", ""),
        "PASSWORD": os.getenv("DEMO_DB_PASSWORD", ""),
        "HOST": os.getenv("DEMO_DB_HOST", ""),
        "PORT": os.getenv("DEMO_DB_PORT", ""),
    }
}

AUTH_PASSWORD_VALIDATORS = []

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Africa/Johannesburg"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

default_authentication_classes = [
    "rest_framework.authentication.SessionAuthentication",
    "rest_framework.authentication.BasicAuthentication",
]
if DEMO_ENABLE_JWT:
    default_authentication_classes.append(
        "rest_framework_simplejwt.authentication.JWTAuthentication"
    )

REST_FRAMEWORK = {
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": default_authentication_classes,
}

PRODUCTORY = {
    "DEFAULT_CURRENCY": "ZAR",
    "DEFAULT_TIMEZONE": "Africa/Johannesburg",
    "DEFAULT_TAX_RATE_PERCENT": "15.00",
    "PRICE_INCLUDES_VAT": True,
    "ENABLE_PROMOTIONS": True,
    "ENABLE_WEBHOOKS": False,
    "DEFAULT_PAGE_SIZE": 20,
}
