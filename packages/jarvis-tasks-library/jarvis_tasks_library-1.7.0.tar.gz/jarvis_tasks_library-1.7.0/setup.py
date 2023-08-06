# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['jarvis_tasks_library']

package_data = \
{'': ['*']}

install_requires = \
['mypy>=0.971,<0.972']

setup_kwargs = {
    'name': 'jarvis-tasks-library',
    'version': '1.7.0',
    'description': '',
    'long_description': None,
    'author': 'Juan Rodriguez',
    'author_email': 'angel.neb@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
