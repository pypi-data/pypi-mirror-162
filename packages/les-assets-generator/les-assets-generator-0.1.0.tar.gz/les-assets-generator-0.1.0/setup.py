# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['les_assets_generator',
 'les_assets_generator.app',
 'les_assets_generator.app.migrations',
 'les_assets_generator.assets_generator',
 'les_assets_generator.assets_generator.settings']

package_data = \
{'': ['*'],
 'les_assets_generator': ['assets/*',
                          'locale/fr/LC_MESSAGES/*',
                          'staticfiles/css/*',
                          'staticfiles/img/logo/*',
                          'templates/admin/*']}

install_requires = \
['Django>=4.0.6,<5.0.0',
 'Pillow>=9.2.0,<10.0.0',
 'dj-database-url>=1.0.0,<2.0.0',
 'django-allauth>=0.51.0,<0.52.0',
 'django-colorfield>=0.7.2,<0.8.0',
 'gunicorn>=20.1.0,<21.0.0',
 'python-dotenv>=0.20.0,<0.21.0']

setup_kwargs = {
    'name': 'les-assets-generator',
    'version': '0.1.0',
    'description': '',
    'long_description': 'Lyon e-Sport assets generator\n\nThis website help you to generate assets from an image and GET parameters\n\n![Python test](https://github.com/lyon-esport/assets-generator/workflows/Python%20test/badge.svg)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n\n# Requirements\n- Python (check version in pyproject.toml)\n\n# Install\n```\npip install les-assets-generator\n```\n\n# Dev\nInstall [Poetry](https://python-poetry.org/docs/master/#installing-with-the-official-installer) with version >= 1.2.0a1\n\nInstall and setup dependencies\n```\npoetry install\npoetry shell\npre-commit install\n\n```\n\n### Run pre-commit\n```\npre-commit run --all-files\n```\n\n# Configuration\n### Production only\n\nSet the environnement for production (.env file or env vars)\n\n```dotenv\n# Django allowed host like .lyon-esport.fr\nDJANGO_ALLOWED_HOST = ""\n\n# Django log level\nDJANGO_LOG_LEVEL = ""\n\n# Set the secret key for session and other thinks\nSECRET_KEY = ""\n\n# Set allowed google email domain like lyon-esport.fr\nGOOGLE_DOMAIN = ""\n```\n\n# Run\nDev: les_assets_generator.assets_generator.settings.dev\nProd: les_assets_generator.assets_generator.settings.production\n\n    $ export DJANGO_SETTINGS_MODULE="les_assets_generator.assets_generator.settings.production"\n    $ cd les_assets_generator\n    $ python -m les_assets_generator.manage makemigrations\n    $ python -m les_assets_generator.manage migrate\n    $ python -m les_assets_generator.manage compilemessages\n\n## Dev\n\n    $ python -m les_assets_generator.manage runserver\n\n## Production\n\n    $ python -m les_assets_generator.manage collectstatic --settings=assets_generator.settings.production --noinput\n    $ gunicorn les_assets_generator.assets_generator.wsgi:application --bind 0.0.0.0:8000 --workers 3\n\n# i18n\nhttps://docs.djangoproject.com/en/4.1/topics/i18n/translation/#message-files\n\n# Licence\n\nThe code is under CeCILL license.\n\nYou can find all details here: https://cecill.info/licences/Licence_CeCILL_V2.1-en.html\n\n# Credits\n\nCopyright © Lyon e-Sport, 2022\n\nContributor(s):\n\n-Ortega Ludovic - ludovic.ortega@lyon-esport.fr\n',
    'author': 'Ludovic Ortega',
    'author_email': 'ludovic.ortega@lyon-esport.fr',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/lyon-esport/assets-generator',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
