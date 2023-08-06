# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['sage_acsv']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'sage-acsv',
    'version': '0.0.5',
    'description': 'A SageMath package with algorithms for analytic combinatorics in several variables.',
    'long_description': None,
    'author': 'Benjamin Hackl',
    'author_email': 'devel@benjamin-hackl.at',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
