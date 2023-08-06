# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['duckgo']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.1,<3.0']

setup_kwargs = {
    'name': 'duckgo',
    'version': '0.1.0',
    'description': 'Search DuckDuckGo for websites, images, etc.',
    'long_description': None,
    'author': 'Wanasit T',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
