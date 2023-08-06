# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['bloodymary', 'bloodymary.formats']

package_data = \
{'': ['*']}

install_requires = \
['cli-toolkit>=2.1.5,<3.0.0', 'pandas>=1.4.3,<2.0.0']

setup_kwargs = {
    'name': 'bloodymary',
    'version': '0.2',
    'description': 'Utility for parsing and processing blood pressure measurements',
    'long_description': None,
    'author': 'Ilkka Tuohela',
    'author_email': 'hile@iki.fi',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
