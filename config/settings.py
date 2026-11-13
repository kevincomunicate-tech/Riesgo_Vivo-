"""Configuración de Django para RiesgoVivo.

El proyecto no usa base de datos: los datos se leen desde un CSV con pandas.
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# En producción define DJANGO_SECRET_KEY y DJANGO_DEBUG=False como variables de entorno.
SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY", "django-insecure-solo-para-desarrollo-local-riesgovivo"
)
DEBUG = os.environ.get("DJANGO_DEBUG", "True").lower() == "true"
ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1,testserver").split(",")

INSTALLED_APPS = [
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "emergencias",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# Sin base de datos: no se requiere persistencia (ver README).
DATABASES = {}

LANGUAGE_CODE = "es-co"
TIME_ZONE = "America/Bogota"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --- Configuración propia de RiesgoVivo ---
RIESGOVIVO_CSV_PATH = BASE_DIR / "data" / "emergencias_ungrd.csv"
RIESGOVIVO_MAX_TABLE_ROWS = 200
RIESGOVIVO_DATA_SOURCE_URL = (
    "https://www.datos.gov.co/en/en/Environment-and-Sustainable-Development/"
    "Emergencias-UNGRD-V2/2343-nuqp"
)
