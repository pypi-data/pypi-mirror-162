# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['arcane']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'arcane-date',
    'version': '0.1.2',
    'description': 'A package to work with dates',
    'long_description': '# Arcane date\n\nThis package helps us to work with dates\n',
    'author': 'Arcane',
    'author_email': 'product@arcane.run',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
