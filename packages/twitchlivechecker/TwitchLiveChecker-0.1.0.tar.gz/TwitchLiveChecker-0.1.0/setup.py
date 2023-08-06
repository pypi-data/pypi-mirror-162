# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['twitchlivechecker']

package_data = \
{'': ['*']}

install_requires = \
['bs4>=0.0.1,<0.0.2', 'requests>=2.28.1,<3.0.0']

setup_kwargs = {
    'name': 'twitchlivechecker',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'n00bady',
    'author_email': 'kaz00@vivaldi.net',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
