# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['mlcvzoo_yolox',
 'mlcvzoo_yolox.core',
 'mlcvzoo_yolox.data',
 'mlcvzoo_yolox.data.datasets',
 'mlcvzoo_yolox.evaluators',
 'mlcvzoo_yolox.exp',
 'mlcvzoo_yolox.third_party',
 'mlcvzoo_yolox.third_party.yolox',
 'mlcvzoo_yolox.third_party.yolox.exps',
 'mlcvzoo_yolox.third_party.yolox.models',
 'mlcvzoo_yolox.third_party.yolox.tools']

package_data = \
{'': ['*']}

install_requires = \
['mlcvzoo_base>=4.0,<5.0',
 'numpy>=1.19.2,!=1.19.5',
 'opencv-contrib-python>=4.5,<5.0,!=4.5.5.64',
 'opencv-python>=4.5,<5.0,!=4.5.5.64',
 'protobuf<=3.20',
 'related-mltoolbox>=1.0,<2.0',
 'torch>=1.9,<2.0',
 'torchvision>=0.10,<0.11',
 'yaml-config-builder>=6.0,<7.0',
 'yolox>=0.3,<0.4']

extras_require = \
{':python_version < "3.10"': ['backports.strenum>=1.1,<2.0'],
 'tensorrt': ['nvidia-tensorrt==8.2.3.0']}

setup_kwargs = {
    'name': 'mlcvzoo-yolox',
    'version': '5.0.0',
    'description': 'MLCVZoo YOLOX Package',
    'long_description': '# MLCVZoo YOLOX\n\nThe MLCVZoo is an SDK for simplifying the usage of various (machine learning driven)\ncomputer vision algorithms. The package **mlcvzoo_yolox** is the wrapper module for\nthe [yolox Object Detector](https://github.com/Megvii-BaseDetection/YOLOX).\n\nFurther information about the MLCVZoo can be found [here](../README.md).\n\n## Install\n`\npip install mlcvzoo-yolox\n`\n\n## Technology stack\n\n- Python\n',
    'author': 'Maximilian Otten',
    'author_email': 'maximilian.otten@iml.fraunhofer.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://git.openlogisticsfoundation.org/silicon-economy/base/ml-toolbox/mlcvzoo',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
