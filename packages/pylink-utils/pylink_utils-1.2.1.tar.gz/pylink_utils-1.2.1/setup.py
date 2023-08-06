# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pylink_utils', 'pylink_utils.aws_utils', 'pylink_utils.data_tools']

package_data = \
{'': ['*']}

install_requires = \
['awswrangler>=2.16.1,<3.0.0',
 'boto3>=1.24.46,<2.0.0',
 'botocore>=1.27.46,<2.0.0',
 'bs4==0.0.1',
 'lxml==4.8.0',
 'pandas>=1.4.3,<2.0.0']

setup_kwargs = {
    'name': 'pylink-utils',
    'version': '1.2.1',
    'description': '',
    'long_description': None,
    'author': 'douglas-peter',
    'author_email': '76939369+douglas-peter@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Pylink-Waterfall/pylink_utils',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)
