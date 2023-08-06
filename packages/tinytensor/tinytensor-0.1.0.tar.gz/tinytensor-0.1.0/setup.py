# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['tinytensor', 'tinytensor.postprocessing', 'tinytensor.preprocessing']

package_data = \
{'': ['*']}

install_requires = \
['onnxruntime>=1.10.0,<2.0.0', 'tokenizers>=0.11.0,<0.12.0']

setup_kwargs = {
    'name': 'tinytensor',
    'version': '0.1.0',
    'description': 'tinytensor',
    'long_description': None,
    'author': 'theblackcat102',
    'author_email': 'theblackcat102@github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
