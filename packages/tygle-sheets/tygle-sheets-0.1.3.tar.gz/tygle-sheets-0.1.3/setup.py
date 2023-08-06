# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['tygle_sheets',
 'tygle_sheets.rest',
 'tygle_sheets.types',
 'tygle_sheets.types.enums',
 'tygle_sheets.types.resources',
 'tygle_sheets.types.resources.spreadsheets',
 'tygle_sheets.types.resources.spreadsheets.chains',
 'tygle_sheets.types.resources.values',
 'tygle_sheets.types.responses',
 'tygle_sheets.types.responses.values']

package_data = \
{'': ['*']}

install_requires = \
['tygle>=0.2,<0.3']

setup_kwargs = {
    'name': 'tygle-sheets',
    'version': '0.1.3',
    'description': '',
    'long_description': '# tygle-sheets\n',
    'author': 'shmookoff',
    'author_email': 'shmookoff@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
