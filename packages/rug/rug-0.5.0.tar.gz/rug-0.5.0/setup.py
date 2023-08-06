# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['rug']

package_data = \
{'': ['*']}

install_requires = \
['httpx>=0.23,<0.24']

setup_kwargs = {
    'name': 'rug',
    'version': '0.5.0',
    'description': 'Library for fetching various stock data from the internet (official and unofficial APIs).',
    'long_description': '<p align="center">\n    <img src="https://raw.githubusercontent.com/im-n1/rug/master/assets/logo.png">\n</p>\n\n<p align="center">\n    <img src="https://img.shields.io/pypi/v/rug.svg?color=0c7dbe">\n    <img src="https://img.shields.io/pypi/l/karpet.svg?color=0c7dbe">\n    <img src="https://img.shields.io/pypi/dm/karpet.svg?color=0c7dbe">\n</p>\n\n# Rug\n\nUniversal library for fetching Stock data from the internet - mostly unofficial\nAPIs - no limits, more free data.\n\n(for Cryptocurrency alternative see [karpet](https://github.com/im-n1/karpet))\n\n* [PyPI](https://pypi.org/project/rug/)\n* [documentation](https://rug.readthedocs.io/en/latest/) ![Documentation Status](https://readthedocs.org/projects/rug/badge/?version=latest)\n\n## Changelog\n\n[changelog](./CHANGELOG.md)\n',
    'author': 'Pavel Hrdina, Patrick Roach',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/im-n1/rug',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
