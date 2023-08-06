# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['portablemc']

package_data = \
{'': ['*']}

entry_points = \
{'console_scripts': ['portablemc = portablemc.cli:main']}

setup_kwargs = {
    'name': 'portablemc',
    'version': '3.1.0',
    'description': 'PortableMC is a module that provides both an API for development of your custom launcher and an executable script to run PortableMC CLI.',
    'long_description': "# PortableMC core module\nGo to repository [README](/README.md) or to [documentations' directory](/doc).\n",
    'author': 'Théo Rozier',
    'author_email': 'contact@theorozier.fr',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/mindstorm38/portablemc',
    'packages': packages,
    'package_data': package_data,
    'entry_points': entry_points,
    'python_requires': '>=3.6',
}


setup(**setup_kwargs)
