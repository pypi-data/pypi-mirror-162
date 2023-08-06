# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['nytid', 'nytid.schedules']

package_data = \
{'': ['*']}

install_requires = \
['ics>=0.7,<0.8', 'requests>=2.27.1,<3.0.0']

setup_kwargs = {
    'name': 'nytid',
    'version': '0.12',
    'description': 'Library to manage teaching schedules',
    'long_description': None,
    'author': 'Daniel Bosk',
    'author_email': 'daniel@bosk.se',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
