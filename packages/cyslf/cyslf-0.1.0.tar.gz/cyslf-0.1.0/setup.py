# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['cyslf']

package_data = \
{'': ['*']}

install_requires = \
['geopy>=2.2.0,<3.0.0',
 'numpy>=1.23.1,<2.0.0',
 'pandas>=1.4.3,<2.0.0',
 'tqdm>=4.64.0,<5.0.0']

entry_points = \
{'console_scripts': ['make-teams = cyslf.make_teams:main',
                     'prepare-player-data = cyslf.prepare_player_data:main']}

setup_kwargs = {
    'name': 'cyslf',
    'version': '0.1.0',
    'description': 'CYS League Formation',
    'long_description': None,
    'author': 'Evan Tey',
    'author_email': 'evantey14@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
