# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['animal_language']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'animal-language',
    'version': '0.1.0',
    'description': 'Customize a word set, and then use the words in this set to represent any sentence.',
    'long_description': None,
    'author': 'chnzzh',
    'author_email': 'chnzzh@outlook.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
