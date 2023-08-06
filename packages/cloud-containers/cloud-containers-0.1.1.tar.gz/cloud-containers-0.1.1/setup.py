# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['cloud_containers', 'cloud_containers.build']

package_data = \
{'': ['*']}

install_requires = \
['cdk8s-plus-22>=2.0.0-rc.75,<3.0.0',
 'cdk8s>=2.3.77,<3.0.0',
 'constructs>=10.1.69,<11.0.0',
 'docker>=5.0.3,<6.0.0']

setup_kwargs = {
    'name': 'cloud-containers',
    'version': '0.1.1',
    'description': 'A Python Package for Building and Deploying Containers',
    'long_description': None,
    'author': 'Ryan Moos',
    'author_email': 'ryan@moos.engineering',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
