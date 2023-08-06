# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['dragontail']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'dragontail',
    'version': '0.0.1',
    'description': '',
    'long_description': None,
    'author': 'Dan H',
    'author_email': 'dan@tutonics.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
