# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['watchmap']

package_data = \
{'': ['*'], 'watchmap': ['templates/*']}

install_requires = \
['fitparse>=1.2.0,<2.0.0',
 'folium>=0.12.1,<0.13.0',
 'matplotlib>=3.5.2,<4.0.0',
 'pandas>=1.4.3,<2.0.0',
 'plotly>=5.9.0,<6.0.0']

entry_points = \
{'console_scripts': ['watchmap = watchmap:run']}

setup_kwargs = {
    'name': 'watchmap',
    'version': '1.0.1',
    'description': 'Plots Activities (run, walk, swim, etc) from a Garmin device',
    'long_description': None,
    'author': 'nbr23',
    'author_email': 'max@23.tf',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
