# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['podler']

package_data = \
{'': ['*']}

install_requires = \
['feedparser>=6.0.8,<7.0.0', 'fire>=0.4.0,<0.5.0', 'strictyaml>=1.6.1,<2.0.0']

entry_points = \
{'console_scripts': ['podler = podler.app:main']}

setup_kwargs = {
    'name': 'podler',
    'version': '0.2.1',
    'description': 'podcast downloader',
    'long_description': None,
    'author': 'Leo',
    'author_email': 'leetschau@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
