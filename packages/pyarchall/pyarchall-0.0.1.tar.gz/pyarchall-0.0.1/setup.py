# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pyarchall']

package_data = \
{'': ['*']}

install_requires = \
['BeautifulSoup4', 'fire', 'requests', 'tqdm']

entry_points = \
{'console_scripts': ['pyarchall = pyarchall:main.main']}

setup_kwargs = {
    'name': 'pyarchall',
    'version': '0.0.1',
    'description': 'PYthon package to ARCHive ALL versions of single python packge',
    'long_description': None,
    'author': 'Alon David',
    'author_email': 'alondavid13@gmail.com',
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
