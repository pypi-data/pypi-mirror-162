# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['sync_version']

package_data = \
{'': ['*']}

install_requires = \
['environs>=9.5.0,<10.0.0',
 'icecream>=2.1.1,<3.0.0',
 'install>=1.3.5,<2.0.0',
 'logzero>=1.7.0,<2.0.0',
 'tomlkit>=0.10.1,<0.11.0',
 'typer>=0.4.1,<0.5.0']

entry_points = \
{'console_scripts': ['sync-version = sync_version.__main__:app']}

setup_kwargs = {
    'name': 'sync-version',
    'version': '0.1.4',
    'description': 'Sync __version__ in __init__.py with version in pyproject.toml',
    'long_description': '# sync-version\n[![pytest](https://github.com/ffreemt/sync-version/actions/workflows/routine-tests.yml/badge.svg)](https://github.com/ffreemt/sync-version/actions)[![python](https://img.shields.io/static/v1?label=python+&message=3.8%2B&color=blue)](https://www.python.org/downloads/)[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)[![PyPI version](https://badge.fury.io/py/sync_version.svg)](https://badge.fury.io/py/sync_version)\n\nsync-version descr\n\n## Install it\n\n```shell\npip install sync-version\n\n# or pip install git+https://github.com/ffreemt/sync-version\n# poetry add git+https://github.com/ffreemt/sync-version\n# git clone https://github.com/ffreemt/sync-version && cd sync-version\n```\n\n## Use it\n```python\n\npoetry version prerelease\nsync-version  # or python -m sync_version\n\npoetry version patch\nsync-version  # or python -m sync_version\n\n# dry-run\nsync-version --dry-run\n\n# debug and dry-run\nsync-version --debug --dry-run\n\n```\n',
    'author': 'ffreemt',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/ffreemt/sync-version',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8.3,<4.0.0',
}


setup(**setup_kwargs)
