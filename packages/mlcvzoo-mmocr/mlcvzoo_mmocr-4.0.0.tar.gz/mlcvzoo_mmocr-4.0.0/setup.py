# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['mlcvzoo_mmocr', 'mlcvzoo_mmocr.third_party']

package_data = \
{'': ['*']}

install_requires = \
['mlcvzoo_base>=4,<5',
 'mlcvzoo_mmdetection>=4,<5',
 'mmcv-full>=1.3.4,!=1.3.18,<=1.6.0',
 'mmdet>=2.11.0,<3.0.0',
 'mmocr>=0.3,<=0.6',
 'nptyping>=2.2,<3.0',
 'numpy>=1.19.2,!=1.19.5',
 'opencv-contrib-python>=4.5,<5.0,!=4.5.5.64,!=4.6.0.66',
 'opencv-python>=4.5,<5.0,!=4.5.5.64,!=4.6.0.66',
 'protobuf<=3.20',
 'pycocotools>=2.0.2,<3.0.0',
 'related-mltoolbox>=1.0,<2.0',
 'torch>=1.9,<2.0',
 'torchvision>=0.10,<0.11',
 'yaml-config-builder>=6.0,<7.0']

setup_kwargs = {
    'name': 'mlcvzoo-mmocr',
    'version': '4.0.0',
    'description': 'MLCVZoo MMOCR Package',
    'long_description': '# MLCVZoo MMOCR\n\nThe MLCVZoo is an SDK for simplifying the usage of various (machine learning driven)\ncomputer vision algorithms. The package **mlcvzoo_mmocr** is the wrapper module for\nthe [mmocr framework](https://github.com/open-mmlab/mmocr).\n\nFurther information about the MLCVZoo can be found [here](../README.md).\n\n## Install\n`\npip install mlcvzoo-mmocr\n`\n\n## Technology stack\n\n- Python\n',
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
