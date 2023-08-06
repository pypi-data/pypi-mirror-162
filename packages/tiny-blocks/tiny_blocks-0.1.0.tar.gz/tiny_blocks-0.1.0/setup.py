# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['tiny_blocks',
 'tiny_blocks.extract',
 'tiny_blocks.load',
 'tiny_blocks.transform']

package_data = \
{'': ['*']}

install_requires = \
['PyMySQL>=1.0.2,<2.0.0',
 'SQLAlchemy>=1.4.39,<2.0.0',
 'boto3>=1.24.43,<2.0.0',
 'cryptography>=37.0.4,<38.0.0',
 'minio>=7.1.11,<8.0.0',
 'pandas>=1.4.3,<2.0.0',
 'psycopg2>=2.9.3,<3.0.0',
 'pydantic>=1.9.1,<2.0.0',
 'requests>=2.28.1,<3.0.0']

setup_kwargs = {
    'name': 'tiny-blocks',
    'version': '0.1.0',
    'description': 'Tiny Block Operations for Data Pipelines',
    'long_description': None,
    'author': 'Jose Vazquez',
    'author_email': 'josevazjim88@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
