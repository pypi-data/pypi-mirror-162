# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['datafet',
 'datafet.eid',
 'datafet.etl_helpers',
 'datafet.http_endpoints',
 'datafet.http_return',
 'datafet.jwt_auth']

package_data = \
{'': ['*']}

install_requires = \
['Jinja2>=3.1.2,<4.0.0',
 'PyJWT>=2.4.0,<3.0.0',
 'boto3>=1.24.46,<2.0.0',
 'botocore>=1.27.46,<2.0.0',
 'ecdsa>=0.18.0,<0.19.0',
 'email-validator>=1.2.1,<2.0.0',
 'fastapi>=0.79.0,<0.80.0',
 'mangum>=0.15.0,<0.16.0',
 'mypy-boto3-athena>=1.24.36.post1,<2.0.0',
 'mypy-boto3-s3>=1.24.36.post1,<2.0.0',
 'pydantic>=1.9.1,<2.0.0',
 'python-dateutil>=2.8.2,<3.0.0',
 'pytz>=2022.1,<2023.0',
 'spookyhash>=2.1.0,<3.0.0']

setup_kwargs = {
    'name': 'datafet',
    'version': '0.1.1',
    'description': 'Few libriaries that we need to use in more than one project',
    'long_description': None,
    'author': 'Istvan Szukacs',
    'author_email': 'istvan@datadeft.eu',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
