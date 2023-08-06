# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['flagg', 'flagg.interface', 'flagg.utils']

package_data = \
{'': ['*']}

install_requires = \
['autome>=0.2.1,<0.3.0', 'click>=8.1.3,<9.0.0']

setup_kwargs = {
    'name': 'flagg',
    'version': '0.1.0',
    'description': 'Formal Languages Analyzer Generator',
    'long_description': None,
    'author': 'João Vitor Maia',
    'author_email': 'maia.tostring@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
