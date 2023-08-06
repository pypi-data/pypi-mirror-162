# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['climail']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'climail',
    'version': '1.9.3',
    'description': 'A Command Line Interface email client written in python.',
    'long_description': None,
    'author': 'HRLO77',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
