# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['testcontainer_python_minio']

package_data = \
{'': ['*']}

install_requires = \
['testcontainers>=3.0.0,<4.0.0']

setup_kwargs = {
    'name': 'testcontainer-python-minio',
    'version': '0.4.0',
    'description': '',
    'long_description': None,
    'author': 'Max Fröhlich',
    'author_email': 'max.froehlich@serviceware.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
