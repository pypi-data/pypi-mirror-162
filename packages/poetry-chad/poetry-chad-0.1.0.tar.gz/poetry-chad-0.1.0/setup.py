# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['poetry_chad', 'poetry_chad.example']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'poetry-chad',
    'version': '0.1.0',
    'description': 'Learn-by-doing python package',
    'long_description': None,
    'author': 'DevonPeroutky',
    'author_email': 'devonperoutky@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
