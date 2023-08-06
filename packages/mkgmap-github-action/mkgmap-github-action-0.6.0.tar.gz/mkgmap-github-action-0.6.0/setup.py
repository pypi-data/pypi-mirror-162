# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['mkgmap_github_action']
install_requires = \
['Jinja2>=3.1.2,<4.0.0', 'requests>=2.28.1,<3.0.0']

entry_points = \
{'console_scripts': ['mkgmap-github-action = mkgmap_github_action:main']}

setup_kwargs = {
    'name': 'mkgmap-github-action',
    'version': '0.6.0',
    'description': '',
    'long_description': None,
    'author': 'Dick Marinus',
    'author_email': 'dick@mrns.nl',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'py_modules': modules,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)
