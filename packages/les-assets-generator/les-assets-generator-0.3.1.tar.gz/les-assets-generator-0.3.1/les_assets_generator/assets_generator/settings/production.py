import os

from les_assets_generator.assets_generator.settings.base import *  # noqa: F401,F403

os.environ["DJANGO_SETTINGS_MODULE"] = "assets_generator.settings.production"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("SECRET_KEY")

# SECURITY WARNING: define the correct hosts in production!
ALLOWED_HOSTS = [
    os.getenv("DJANGO_ALLOWED_HOST"),
]
