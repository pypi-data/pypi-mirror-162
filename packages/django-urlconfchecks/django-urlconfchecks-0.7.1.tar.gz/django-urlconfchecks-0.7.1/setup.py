# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['django_urlconfchecks',
 'tests',
 'tests.dummy_project',
 'tests.dummy_project.urls']

package_data = \
{'': ['*']}

install_requires = \
['Django>=3.2', 'typer[all]>=0.4.1,<0.5.0']

extras_require = \
{'dev': ['tox>=3.20.1,<4.0.0',
         'virtualenv>=20.2.2,<21.0.0',
         'twine>=3.3.0,<4.0.0',
         'pre-commit>=2.12.0,<3.0.0',
         'toml>=0.10.2,<0.11.0',
         'bump2version>=1.0.1,<2.0.0',
         'Markdown>=3.3.4,<4.0.0'],
 'doc': ['mkdocs>=1.1.2,<2.0.0',
         'mkdocs-include-markdown-plugin>=3.2.3,<4.0.0',
         'mkdocs-material>=8.1.8,<9.0.0',
         'mkdocstrings>=0.17,<0.20',
         'mkdocs-material-extensions>=1.0.1,<2.0.0',
         'mkdocs-autorefs>=0.2.1,<0.5.0',
         'Markdown>=3.3.4,<4.0.0'],
 'test': ['black>=22.3.0',
          'isort>=5.8.0,<6.0.0',
          'flake8>=4.0.1,<6.0.0',
          'flake8-docstrings>=1.6.0,<2.0.0',
          'mypy>=0.931,<0.972',
          'pytest>=6.2.4,<8.0.0',
          'pytest-cov>=3.0.0,<4.0.0',
          'pytest-django>=4.5.2,<5.0.0']}

entry_points = \
{'console_scripts': ['urlconfchecks = django_urlconfchecks.cli:app']}

setup_kwargs = {
    'name': 'django-urlconfchecks',
    'version': '0.7.1',
    'description': 'a python package for type checking the urls and associated views.',
    'long_description': "# Django UrlConf Checks\n\n[![pypi](https://img.shields.io/pypi/v/django-urlconfchecks.svg)](https://pypi.org/project/django-urlconfchecks/)\n[![python](https://img.shields.io/pypi/pyversions/django-urlconfchecks.svg)](https://pypi.org/project/django-urlconfchecks/)\n[![Build Status](https://github.com/AliSayyah/django-urlconfchecks/actions/workflows/dev.yml/badge.svg)](https://github.com/AliSayyah/django-urlconfchecks/actions/workflows/dev.yml)\n[![codecov](https://codecov.io/gh/AliSayyah/django-urlconfchecks/branch/main/graphs/badge.svg)](https://codecov.io/github/AliSayyah/django-urlconfchecks)\n[![License](https://img.shields.io/github/license/AliSayyah/django-urlconfchecks.svg)](https://www.gnu.org/licenses/gpl-3.0.en.html)\n\ndjango-urlconfchecks is a static type checker that checks your URLconf parameter types with argument types specified in associated views.\nIt leverages the Django's static check system.\n\n* [Documentation](https://AliSayyah.github.io/django-urlconfchecks)\n* [GitHub](https://github.com/AliSayyah/django-urlconfchecks)\n* [PyPI](https://pypi.org/project/django-urlconfchecks/)\n\n## Installation\n\n    pip install django-urlconfchecks\n\n## Usage\n\nYou can use this package in different ways:\n\n### As a Django app\n\nAdd `django_urlconfchecks` to your `INSTALLED_APPS` list in your `settings.py` file.\n\n```python\n    INSTALLED_APPS = [\n    ...\n    'django_urlconfchecks',\n]\n```\n\n### As a command line tool\n\nRun this command from the root of your project, were `manage.py` is located:\n\n```bash\n$ urlconfchecks --help\n\n    Usage: urlconfchecks [OPTIONS]\n\n      Check all URLConfs for errors.\n\n    Options:\n      --version\n      -u, --urlconf PATH    Specify the URLconf to check.\n      --install-completion  Install completion for the current shell.\n      --show-completion     Show completion for the current shell, to copy it or\n                            customize the installation.\n      --help                Show this message and exit.\n```\n\n### As a pre-commit hook\n\nAdd the following to your `.pre-commit-config.yaml` file:\n\n```yaml\n  - repo: https://github.com/AliSayyah/django-urlconfchecks\n    rev: 0.7.1\n    hooks:\n      - id: django-urlconfchecks\n```\n\nFor more information, see the [usage documentation](https://alisayyah.github.io/django-urlconfchecks/usage/).\n\n## Features\n\nUsing this package, URL pattern types will automatically be matched with associated views, and in case of mismatch, an\nerror will be raised.\n\nExample:\n\n```python\n# urls.py\nfrom django.urls import path\n\nfrom . import views\n\nurlpatterns = [\n    path('articles/<str:year>/', views.year_archive),\n    path('articles/<int:year>/<int:month>/', views.month_archive),\n    path('articles/<int:year>/<int:month>/<slug:slug>/', views.article_detail),\n]\n```\n\n```python\n# views.py\n\ndef year_archive(request, year: int):\n    pass\n\n\ndef month_archive(request, year: int, month: int):\n    pass\n\n\ndef article_detail(request, year: int, month: int, slug: str):\n    pass\n```\n\noutput will be:\n\n```\n(urlchecker.E002) For parameter `year`, annotated type int does not match expected `str` from urlconf\n```\n\n* TODO\n    - Should only warn for each unhandled Converter once.\n    - Regex patterns perhaps? (only RoutePattern supported at the moment).\n\n## Credits\n\n- [Luke Plant](https://github.com/spookylukey) for providing the idea and the initial code.\n- This package was created with [Cookiecutter](https://github.com/audreyr/cookiecutter) and\n  the [waynerv/cookiecutter-pypackage](https://github.com/waynerv/cookiecutter-pypackage) project template.\n",
    'author': 'ali sayyah',
    'author_email': 'ali.sayyah2@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/AliSayyah/django-urlconfchecks',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.7.0,<4',
}


setup(**setup_kwargs)
