# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['python_flux']

package_data = \
{'': ['*']}

install_requires = \
['jsonmerge>=1.8,<2.0']

setup_kwargs = {
    'name': 'python-flux',
    'version': '0.8.3',
    'description': 'Librería que utiliza generadores de python para simular procesamiento de flujo de datos',
    'long_description': None,
    'author': 'Juan Pablo Bochard',
    'author_email': 'jbochard@despegar.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
