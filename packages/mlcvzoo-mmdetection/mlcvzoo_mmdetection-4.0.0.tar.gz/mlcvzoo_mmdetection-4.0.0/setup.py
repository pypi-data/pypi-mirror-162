# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['mlcvzoo_mmdetection', 'mlcvzoo_mmdetection.third_party']

package_data = \
{'': ['*']}

install_requires = \
['mlcvzoo_base>=4.0,<5.0',
 'mmcv-full>=1.3,<2.0,!=1.3.18',
 'mmdet>=2.14.0,<3.0.0',
 'numpy>=1.19.2,!=1.19.5',
 'protobuf<=3.20',
 'related-mltoolbox>=1.0,<2.0',
 'torch>=1.9,<2.0',
 'torchvision>=0.10,<0.11',
 'yaml-config-builder>=6.0,<7.0']

extras_require = \
{':platform_machine == "x86_64"': ['pycocotools>=2.0.2,<3.0.0']}

setup_kwargs = {
    'name': 'mlcvzoo-mmdetection',
    'version': '4.0.0',
    'description': 'MLCVZoo MMDetection Package',
    'long_description': '# MLCVZoo MMDetection\n\nThe MLCVZoo is an SDK for simplifying the usage of various (machine learning driven)\ncomputer vision algorithms. The package **mlcvzoo_mmdetection** is the wrapper module for\nthe [mmdetection framework](https://github.com/open-mmlab/mmdetection).\n\nFurther information about the MLCVZoo can be found [here](../README.md).\n\n## Install\n`\npip install mlcvzoo-mmdetection\n`\n\n## Technology stack\n\n- Python\n',
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
