# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['sitri',
 'sitri.providers',
 'sitri.providers.base',
 'sitri.providers.contrib',
 'sitri.providers.contrib.vault',
 'sitri.settings',
 'sitri.settings.contrib',
 'sitri.settings.contrib.vault',
 'sitri.strategy']

package_data = \
{'': ['*']}

extras_require = \
{'all': ['redis==4.3.4',
         'vedis==0.7.1',
         'pyyaml==6.0',
         'hvac==0.11.2',
         'pydantic==1.9.1',
         'structlog==22.1.0',
         'ujson==5.4.0'],
 'hvac': ['hvac==0.11.2'],
 'pyyaml': ['pyyaml==6.0'],
 'redis': ['redis==4.3.4'],
 'settings': ['hvac==0.11.2', 'pydantic==1.9.1'],
 'structlog': ['structlog==22.1.0'],
 'ujson': ['ujson==5.4.0'],
 'vedis': ['vedis==0.7.1']}

setup_kwargs = {
    'name': 'sitri',
    'version': '2.1.2',
    'description': 'Library for one endpoint config managment',
    'long_description': '<p align="center">\n  <a href="https://github.com/elastoo-team/sitri">\n    <img src="https://raw.githubusercontent.com/Elastoo-Team/sitri/master/docs/_static/full_logo.jpg">\n  </a>\n  <h1 align="center">\n    Sitri - powerful settings & configs for python\n  </h1>\n</p>\n\n[![PyPI](https://img.shields.io/pypi/v/sitri)](https://pypi.org/project/sitri/)\n[![codecov](https://codecov.io/gh/Elastoo-Team/sitri/branch/master/graph/badge.svg)](https://codecov.io/gh/elastoo-team/sitri)\n[![Maintainability](https://api.codeclimate.com/v1/badges/625f1d869adbf4128f75/maintainability)](https://codeclimate.com/github/Elastoo-Team/sitri/maintainability)\n![Code Climate technical debt](https://img.shields.io/codeclimate/tech-debt/Elastoo-Team/sitri)\n[![Build Status](https://img.shields.io/endpoint.svg?url=https%3A%2F%2Factions-badge.atrox.dev%2FElastoo-Team%2Fsitri%2Fbadge&style=popout)](https://actions-badge.atrox.dev/Elastoo-Team/sitri/goto)\n[![Read the Docs](https://img.shields.io/readthedocs/sitri)](https://sitri.readthedocs.io)\n\nSitri - library for managing authorization and configuration data from a single object with possibly different or identical providers\n\n#  Installation\n\n```bash\npoetry add sitri -E "all"\n```\n\nor\n```bash\npip3 install sitri[all]\n```\n\n*Extras* packs and providers:\n\n    1. all - all providers and settings module.\n    2. settings - pydantic, providers with settings-support.\n    3. redis - for redis provider.\n    4. hvac - for HashiCorp Vault provider.\n    5. vedis - for vedis provider.\n    6. pyyaml - for YAML provider.\n    7. structlog - structlog package if your app does not provide structlog (optional, default logging package also support).\n    8. ujson - speed-up your json provider (optional).\n\n\n# Basics with SystemProvider\n\n```python\nfrom sitri.providers.contrib import SystemConfigProvider\nfrom sitri import Sitri\n\nconf = Sitri(\n    config_provider=SystemConfigProvider(prefix="basics"),\n)\n```\nSystem provider use system environment for get config data. For unique - sitri lookup to "namespace" by prefix.\n\nExample:\n\n*In console:*\n```bash\nexport BASICS_NAME=Huey\n```\n\n*In code:*\n```python\nname = conf.get_config("name")\n\nprint(name)  # output: Huey\n```\n\n#  Docs\nRead base API references and other part documentation on https://sitri.readthedocs.io/\n',
    'author': 'Alexander Lavrov',
    'author_email': 'egnod@ya.ru',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Egnod/sitri',
    'packages': packages,
    'package_data': package_data,
    'extras_require': extras_require,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)
