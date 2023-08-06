# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['auve']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'auve',
    'version': '22.8.7',
    'description': 'Simple tool for automatic version number generation',
    'long_description': None,
    'author': 'Marc Scoop',
    'author_email': 'marc.scoop@online.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
