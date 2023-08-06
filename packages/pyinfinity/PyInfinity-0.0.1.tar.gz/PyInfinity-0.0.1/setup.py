# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['README']
setup_kwargs = {
    'name': 'pyinfinity',
    'version': '0.0.1',
    'description': 'Typed interactions with the Pexip Infinity API(s)',
    'long_description': None,
    'author': 'Pexip AS',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'py_modules': modules,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
