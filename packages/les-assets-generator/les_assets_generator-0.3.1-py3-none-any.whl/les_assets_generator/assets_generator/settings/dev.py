import os

from les_assets_generator.assets_generator.settings.base import *  # noqa: F401,F403

os.environ["DJANGO_SETTINGS_MODULE"] = "assets_generator.settings.dev"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "e!m3b-!+@$=5t+=^vnw2l)7i6gi_fw^h=v(=0ojxfn^bx4z=!o"

# SECURITY WARNING: define the correct hosts in production!
ALLOWED_HOSTS = ["*"]

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
