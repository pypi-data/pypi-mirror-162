# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pynodal']

package_data = \
{'': ['*'], 'pynodal': ['.ipynb_checkpoints/*']}

install_requires = \
['matplotlib>=3.5.2,<4.0.0', 'pandas>=1.4.3,<2.0.0']

setup_kwargs = {
    'name': 'pynodal',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Mariana Vasconcelos',
    'author_email': 'mari.aspennl@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
