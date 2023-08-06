# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['honors_board_extractor',
 'honors_board_extractor.boards',
 'honors_board_extractor.charts',
 'honors_board_extractor.config',
 'honors_board_extractor.scripts']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp[speedups]>=3.6.2,<4.0.0',
 'click>=7.1.2,<8.0.0',
 'motor>=2.2.0,<3.0.0',
 'pandas>=1.1.2,<2.0.0']

entry_points = \
{'console_scripts': ['create-boards = honors_board_extractor.scripts.cli:main']}

setup_kwargs = {
    'name': 'honors-board-extractor',
    'version': '1.1.5',
    'description': 'pulls data from honors board api and outputs as json',
    'long_description': None,
    'author': 'Jake Loughridge',
    'author_email': 'james.loughridge@afficienta.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
