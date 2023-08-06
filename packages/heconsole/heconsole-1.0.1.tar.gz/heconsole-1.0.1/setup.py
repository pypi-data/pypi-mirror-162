# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['heconsole']
setup_kwargs = {
    'name': 'heconsole',
    'version': '1.0.1',
    'description': 'Perfect pip module to design and display your terminal, great customization & logging',
    'long_description': None,
    'author': 'MishaKorzhik_He1Zen',
    'author_email': 'miguardzecurity@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'py_modules': modules,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
