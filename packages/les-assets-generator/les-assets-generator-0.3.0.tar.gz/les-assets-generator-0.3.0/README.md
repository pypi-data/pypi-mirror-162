Lyon e-Sport assets generator

This website help you to generate assets from an image and GET parameters

[![PyPI](https://img.shields.io/pypi/v/les-assets-generator.svg)](https://pypi.python.org/pypi/les-assets-generator)
[![PyPI versions](https://img.shields.io/pypi/pyversions/les-assets-generator.svg)](https://pypi.python.org/pypi/les-assets-generator)
![Python test](https://github.com/lyon-esport/assets-generator/workflows/Python%20test/badge.svg)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

# Requirements
- Python (check version in pyproject.toml)

# Install
```
pip install les-assets-generator
```

# Dev
Install [Poetry](https://python-poetry.org/docs/master/#installing-with-the-official-installer) with version >= 1.2.0a1

Install and setup dependencies
```
poetry install
poetry shell
pre-commit install
```

### Run pre-commit
```
pre-commit run --all-files
```

# Configuration
### Production only

Set the environnement for production (.env file or env vars)

Dev: les_assets_generator.assets_generator.settings.dev

Prod: les_assets_generator.assets_generator.settings.production

```dotenv
DJANGO_SETTINGS_MODULE="les_assets_generator.assets_generator.settings.production"

# Database URL following https://github.com/jazzband/dj-database-url#url-schema
DATABASE_URL="sqlite:////opt//assets-generator//db.sqlite3"

# Folder that store static files
DJANGO_STATIC_ROOT="/var/www/assets-generator/static"

# Folder that store media files
DJANGO_MEDIA_ROOT="/var/www/assets-generator/media"

# Django allowed host like .lyon-esport.fr
DJANGO_ALLOWED_HOST=""

# Django log level
DJANGO_LOG_LEVEL=""

# Set the secret key for session and other thinks
SECRET_KEY=""

# Used to generate example URL in django admin like https://assets.lyon-esport.fr
DEFAULT_DOMAIN=""

# Set allowed google email domain like lyon-esport.fr
GOOGLE_DOMAIN=""
```

# Run

    $ export DJANGO_SETTINGS_MODULE="les_assets_generator.assets_generator.settings.production"
    $ python -m les_assets_generator.manage makemigrations
    $ python -m les_assets_generator.manage migrate
    $ python -m les_assets_generator.manage compilemessages

## Dev

    $ cd les_assets_generator
    $ python -m les_assets_generator.manage runserver

## Production

    $ python -m les_assets_generator.manage collectstatic --noinput
    $ gunicorn les_assets_generator.assets_generator.wsgi:application --bind localhost:8000 --workers 3

# i18n
https://docs.djangoproject.com/en/4.1/topics/i18n/translation/#message-files

# Licence

The code is under CeCILL license.

You can find all details here: https://cecill.info/licences/Licence_CeCILL_V2.1-en.html

# Credits

Copyright © Lyon e-Sport, 2022

Contributor(s):

-Ortega Ludovic - ludovic.ortega@lyon-esport.fr
