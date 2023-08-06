# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['lunarapi']

package_data = \
{'': ['*']}

install_requires = \
['Pillow>=9.2.0,<10.0.0',
 'aiohttp>=3.6.0,<3.8.0',
 'discord.py',
 'python-dotenv>=0.20.0,<0.21.0']

setup_kwargs = {
    'name': 'lunarapi',
    'version': '0.1.2',
    'description': '',
    'long_description': None,
    'author': 'WinterFe',
    'author_email': 'winter@lunardev.group',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
