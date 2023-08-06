# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['brish']

package_data = \
{'': ['*']}

install_requires = \
['icecream>=2.1.0,<3.0.0']

setup_kwargs = {
    'name': 'brish',
    'version': '0.3.4.2',
    'description': 'A bridge between zsh and Python.',
    'long_description': None,
    'author': 'NightMachinary',
    'author_email': 'rudiwillalwaysloveyou@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/NightMachinary/brish',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.0,<4.0.0',
}


setup(**setup_kwargs)
