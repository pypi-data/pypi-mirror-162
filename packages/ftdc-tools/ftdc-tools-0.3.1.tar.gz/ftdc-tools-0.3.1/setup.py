# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['ftdc_tools']

package_data = \
{'': ['*']}

install_requires = \
['aiofile>=3.7.4,<4.0.0']

setup_kwargs = {
    'name': 'ftdc-tools',
    'version': '0.3.1',
    'description': '',
    'long_description': None,
    'author': 'Alexander Costas',
    'author_email': 'alexander.costas@mongodb.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<3.11',
}


setup(**setup_kwargs)
