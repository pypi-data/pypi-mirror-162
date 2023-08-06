# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['mlcvzoo_darknet']

package_data = \
{'': ['*']}

install_requires = \
['mlcvzoo_base>=4.0,<5.0',
 'numpy>=1.19.2,!=1.19.5',
 'opencv-contrib-python>=4.5,<5.0,!=4.5.5.64',
 'opencv-python>=4.5,<5.0,!=4.5.5.64',
 'related-mltoolbox>=1.0,<2.0',
 'yaml-config-builder>=6.0,<7.0']

setup_kwargs = {
    'name': 'mlcvzoo-darknet',
    'version': '3.1.0',
    'description': 'MLCVZoo Darknet Package',
    'long_description': '# MLCVZoo Darknet\n\nThe MLCVZoo is an SDK for simplifying the usage of various (machine learning driven)\ncomputer vision algorithms. The package **mlcvzoo_darknet** is the wrapper module for the\n[darknet framework](https://github.com/AlexeyAB/darknet).\n\nFurther information about the MLCVZoo can be found [here](../README.md).\n\n## Install\n`\npip install mlcvzoo-darknet\n`\n\n## Technology stack\n\n- Python\n',
    'author': 'Maximilian Otten',
    'author_email': 'maximilian.otten@iml.fraunhofer.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://git.openlogisticsfoundation.org/silicon-economy/base/ml-toolbox/mlcvzoo',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
