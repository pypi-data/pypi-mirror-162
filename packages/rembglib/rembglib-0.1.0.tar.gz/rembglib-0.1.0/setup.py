# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['rembglib']

package_data = \
{'': ['*']}

install_requires = \
['Pillow>=9.2.0,<10.0.0',
 'PyMatting>=1.1.8,<2.0.0',
 'gdown>=4.5.1,<5.0.0',
 'onnxruntime>=1.12.1,<2.0.0',
 'opencv-python>=4.6.0,<5.0.0',
 'scipy>=1.9.0,<2.0.0']

setup_kwargs = {
    'name': 'rembglib',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Alejandro P. Hall',
    'author_email': 'alejandro.polvillo@myrealfood.app',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<3.10',
}


setup(**setup_kwargs)
