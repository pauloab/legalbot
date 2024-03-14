import os
from celery import Celery
from django.conf import settings
from pathlib import Path

import sys

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# allow importing from other modules
OTHER_TEAM_WORK_PARENT_DIR = BASE_DIR.parent
sys.path.append(str(OTHER_TEAM_WORK_PARENT_DIR))

from etl.etl import start_etl_process


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

celery = Celery("app")

celery.config_from_object("django.conf:settings", namespace="CELERY")


celery.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
