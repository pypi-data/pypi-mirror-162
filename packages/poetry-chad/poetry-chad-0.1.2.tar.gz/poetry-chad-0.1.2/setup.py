# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['poetry']
setup_kwargs = {
    'name': 'poetry-chad',
    'version': '0.1.2',
    'description': 'Learn-by-doing python package',
    'long_description': '# Overview\nThis project is an attempt at building a python package\n',
    'author': 'DevonPeroutky',
    'author_email': 'devonperoutky@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'py_modules': modules,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
