# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['rahul_poetrypypi']

package_data = \
{'': ['*']}

install_requires = \
['pendulum>=2.1.2,<3.0.0']

setup_kwargs = {
    'name': 'rahul-poetrypypi',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Rahul Salgare',
    'author_email': 'rahulsalgare@gofynd.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
