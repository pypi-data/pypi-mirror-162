# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['gendiff', 'gendiff.scripts']

package_data = \
{'': ['*']}

entry_points = \
{'console_scripts': ['gendiff = gendiff.scripts.gendiff:main']}

setup_kwargs = {
    'name': 'mo-gendiff',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Max Odinokiy',
    'author_email': 'max.odinokiy@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
