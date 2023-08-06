# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['repo_autoindex', 'repo_autoindex._impl']

package_data = \
{'': ['*'], 'repo_autoindex._impl': ['templates/*']}

install_requires = \
['Jinja2>=3.1.2', 'aiohttp>=3.8.1', 'defusedxml>=0.7.1']

entry_points = \
{'console_scripts': ['repo-autoindex = repo_autoindex._impl.cmd:entrypoint']}

setup_kwargs = {
    'name': 'repo-autoindex',
    'version': '0.2.0',
    'description': 'Generic static HTML indexes of various repository types',
    'long_description': None,
    'author': 'Rohan McGovern',
    'author_email': 'rmcgover@redhat.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4',
}


setup(**setup_kwargs)
