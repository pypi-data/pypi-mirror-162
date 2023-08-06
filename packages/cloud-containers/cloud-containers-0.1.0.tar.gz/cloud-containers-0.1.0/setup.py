# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['cloud_containers']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'cloud-containers',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Ryan Moos',
    'author_email': 'ryan@moos.engineering',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
