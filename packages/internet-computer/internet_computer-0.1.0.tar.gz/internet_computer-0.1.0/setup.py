# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['internet_computer', 'internet_computer.tools']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=6.0,<7.0', 'pymongo>=4.2.0,<5.0.0', 'requests>=2.28.1,<3.0.0']

setup_kwargs = {
    'name': 'internet-computer',
    'version': '0.1.0',
    'description': 'internet_computer provides tools for querying and working with the Internet Computer.',
    'long_description': None,
    'author': 'Ryan Cammer',
    'author_email': 'ryancammer@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
