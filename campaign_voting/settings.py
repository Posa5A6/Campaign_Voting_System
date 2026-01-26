"""
Django settings for campaign_voting project (Render-ready).
"""

from pathlib import Path
import os

import dj_database_url
from dotenv import load_dotenv

# -------------------------
# Paths
# -------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env for local dev only (Render env vars override)
load_dotenv(BASE_DIR / ".env")

# -------------------------
# Security
# -------------------------
SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")
DEBUG = os.environ.get("DEBUG", "0") == "1"

# ✅ Hosts (Render + local)
ALLOWED_HOSTS = [
    "campaign-voting-system.onrender.com",
    "localhost",
    "127.0.0.1",
]

# If you use a custom domain later, add it here.
CSRF_TRUSTED_ORIGINS = [
    "https://campaign-voting-system.onrender.com",
]

# If you ever want dynamic hosts from env:
# extra_hosts = [h.strip() for h in os.environ.get("ALLOWED_HOSTS", "").split(",") if h.strip()]
# ALLOWED_HOSTS += extra_hosts

# -------------------------
# Applications
# -------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "voting",
]

# -------------------------
# Middleware
# -------------------------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # ✅ static on Render
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# -------------------------
# URLs / Templates
# -------------------------
ROOT_URLCONF = "campaign_voting.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],  # ✅ templates folder
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "campaign_voting.wsgi.application"

# -------------------------
# Database
# -------------------------
# ✅ Render provides DATABASE_URL if you attached a PostgreSQL DB
import dj_database_url
DATABASES = {
  "default": dj_database_url.config(default=os.environ.get("DATABASE_URL"))
}

# -------------------------
# Password validation
# -------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# -------------------------
# Internationalization
# -------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Kolkata"
USE_I18N = True
USE_TZ = True

# -------------------------
# Static files (CSS/JS/Images)
# -------------------------
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"      # ✅ collectstatic output
STATICFILES_DIRS = [BASE_DIR / "static"]    # ✅ your local static folder

# ✅ WhiteNoise storage
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# -------------------------
# Login / Sessions
# -------------------------
LOGIN_URL = "/login/"
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# -------------------------
# Email (keep creds in Render env vars, NOT in code)
# -------------------------
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

EMAIL_HOST = "smtp-relay.brevo.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True

EMAIL_HOST_USER = os.environ.get("BREVO_SMTP_LOGIN", "")
EMAIL_HOST_PASSWORD = os.environ.get("BREVO_SMTP_KEY", "")



EMAIL_TIMEOUT = 10  # prevents hanging
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", EMAIL_HOST_USER)
# -------------------------
# Production security (Render)
# -------------------------
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

