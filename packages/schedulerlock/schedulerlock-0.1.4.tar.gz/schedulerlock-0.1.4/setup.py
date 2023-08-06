# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['schedulerlock',
 'schedulerlock.jobs',
 'schedulerlock.locks',
 'schedulerlock.migrations']

package_data = \
{'': ['*']}

install_requires = \
['Django==3.2.6', 'django-apscheduler==0.6.2']

setup_kwargs = {
    'name': 'schedulerlock',
    'version': '0.1.4',
    'description': '',
    'long_description': None,
    'author': 'Soham Marik',
    'author_email': 'soham.marik@automationedge.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
