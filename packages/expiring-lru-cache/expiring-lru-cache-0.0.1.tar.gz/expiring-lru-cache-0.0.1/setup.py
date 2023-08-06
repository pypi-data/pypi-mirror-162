# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['expiring_lru_cache']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'expiring-lru-cache',
    'version': '0.0.1',
    'description': 'LRU caching with expiration period.',
    'long_description': None,
    'author': 'Bart Smeets',
    'author_email': 'bart@dataroots.io',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
