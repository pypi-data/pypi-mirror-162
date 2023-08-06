# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['fenkeysmanagement']

package_data = \
{'': ['*']}

install_requires = \
['tabulate>=0.8.10,<0.9.0']

entry_points = \
{'console_scripts': ['fenkm = fenkeysmanagement:main']}

setup_kwargs = {
    'name': 'fenkeysmanagement',
    'version': '1.0.0',
    'description': '',
    'long_description': None,
    'author': 'brodokk',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
