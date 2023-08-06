# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['expiring_lru_cache']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'expiring-lru-cache',
    'version': '0.0.2',
    'description': 'LRU caching with expiration period.',
    'long_description': '# expiring_lru_cache\n\n<p align="left">\n  <a href="https://dataroots.io"><img alt="Maintained by dataroots" src="https://dataroots.io/maintained-rnd.svg" /></a>\n  <a href="https://pypi.org/project/expiring-lru-cache/"><img alt="Python versions" src="https://img.shields.io/pypi/pyversions/expiring-lru-cache" /></a>\n  <a href="https://pypi.org/project/expiring-lru-cache/"><img alt="PiPy" src="https://img.shields.io/pypi/v/expiring-lru-cache" /></a>\n  <a href="https://pepy.tech/project/expiring-lru-cache"><img alt="Downloads" src="https://pepy.tech/badge/expiring-lru-cache" /></a>\n  <a href="https://github.com/psf/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg" /></a>\n  <a href="http://mypy-lang.org/"><img alt="Mypy checked" src="https://img.shields.io/badge/mypy-checked-1f5082.svg" /></a>\n  <a href="https://app.codecov.io/gh/datarootsio/expiring-lru-cache"><img alt="Codecov" src="https://codecov.io/github/datarootsio/expiring-lru-cache/main/graph/badge.svg" /></a>\n  <a href="https://github.com/datarootsio/expiring-lru-cache/actions"><img alt="test" src="https://github.com/datarootsio/expiring-lru-cache/actions/workflows/tests.yml/badge.svg" /></a>\n</p>\n\n`expiring_lru_cache` is a minimal drop-in replacement of `functools.lru_cache`. It\nallows the user to specify a time interval (in secs) after which the cache is\ninvalidated and reset.\n\n## Usage\n\nHere an example cached function whose cache will invalidate after 10 seconds.\n\n```python\nfrom expiring_lru_cache import lru_cache\n\n@lru_cache(expires_after=10)\ndef my_plus_one_func(x: int) -> int:\n    return x + 1\n```\n\nHere an example cached function whose cache will invalidate after 1 day. Note that the\nconvenience variables `MINUTES`, `HOURS` and `DAYS` are available within the\n`expiring_lru_cache` namespace.\n\n```python\nfrom expiring_lru_cache import lru_cache, DAYS\n\n\n@lru_cache(expires_after=1 * DAYS)\ndef my_plus_one_func(x: int) -> int:\n    return x + 1\n```\n',
    'author': 'Bart Smeets',
    'author_email': 'bart@dataroots.io',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://datarootsio.github.io/expiring-lru-cache/',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
