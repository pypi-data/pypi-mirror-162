# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['markdown_gds']

package_data = \
{'': ['*']}

install_requires = \
['Markdown>=3.4.1,<4.0.0']

setup_kwargs = {
    'name': 'markdown-gds',
    'version': '0.1.0',
    'description': 'A Python markdown extension for GDS',
    'long_description': None,
    'author': 'Sam Dudley',
    'author_email': 'samuel.dudley@digital.trade.gov.uk',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
