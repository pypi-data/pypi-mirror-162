# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['subgrounds', 'subgrounds.pagination', 'subgrounds.subgraph']

package_data = \
{'': ['*']}

install_requires = \
['pandas>=1.4.2,<2.0.0',
 'pathlib>=1.0.1,<2.0.0',
 'pipe>=2.0,<3.0',
 'requests>=2.27.1,<3.0.0']

extras_require = \
{'dash': ['dash>=2.3.1,<3.0.0']}

setup_kwargs = {
    'name': 'subgrounds',
    'version': '1.0.1',
    'description': 'A Pythonic data access layer for applications querying data from The Graph Network.',
    'long_description': None,
    'author': None,
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Protean-Labs/subgrounds',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
