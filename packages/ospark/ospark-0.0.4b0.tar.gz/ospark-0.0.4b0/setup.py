# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ospark',
 'ospark.backbone',
 'ospark.data',
 'ospark.data.generator',
 'ospark.models',
 'ospark.nn',
 'ospark.nn.block',
 'ospark.nn.cell',
 'ospark.nn.component',
 'ospark.nn.layers',
 'ospark.nn.metrics',
 'ospark.nn.optimizer',
 'ospark.ocr',
 'ospark.predictor',
 'ospark.samples',
 'ospark.trainer',
 'ospark.utility']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'ospark',
    'version': '0.0.4b0',
    'description': 'Building powerful model & Enjoy it!',
    'long_description': None,
    'author': 'ospark-org',
    'author_email': 'donggicai1991@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<3.10',
}


setup(**setup_kwargs)
