# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['jrpyefficient']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'jrpyefficient',
    'version': '0.0.1',
    'description': 'Jumping Rivers: Efficient Data Science in Python',
    'long_description': None,
    'author': 'Jumping Rivers',
    'author_email': 'info@jumpingrivers.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7',
}


setup(**setup_kwargs)
