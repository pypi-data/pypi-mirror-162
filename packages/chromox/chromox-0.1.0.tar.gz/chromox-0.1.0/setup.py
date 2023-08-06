# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['chromox', 'chromox.protein_descriptors']

package_data = \
{'': ['*']}

install_requires = \
['numpy']

setup_kwargs = {
    'name': 'chromox',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'jfwu',
    'author_email': 'jfwu.ai@hotmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
