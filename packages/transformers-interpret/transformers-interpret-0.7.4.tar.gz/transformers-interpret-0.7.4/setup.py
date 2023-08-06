# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['transformers_interpret', 'transformers_interpret.explainers']

package_data = \
{'': ['*']}

install_requires = \
['captum>=0.3.1,<0.4.0',
 'ipython==7.31.1',
 'pytest>=5.4.2,<6.0.0',
 'transformers>=3.0.0']

setup_kwargs = {
    'name': 'transformers-interpret',
    'version': '0.7.4',
    'description': '',
    'long_description': None,
    'author': 'Charles Pierse',
    'author_email': 'charlespierse@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
