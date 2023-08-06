
# -*- coding: utf-8 -*-
from setuptools import setup

import codecs

with codecs.open('README.md', encoding="utf-8") as fp:
    long_description = fp.read()
INSTALL_REQUIRES = [
    'graia-broadcast<1.0.0,>=0.18',
    'creart~=0.2',
]

setup_kwargs = {
    'name': 'graiax-shortcut',
    'version': '0.1.0',
    'description': 'Utilities for Graia Framework Community.',
    'long_description': long_description,
    'license': 'MIT',
    'author': '',
    'author_email': 'BlueGlassBlock <blueglassblock@outlook.com>',
    'maintainer': None,
    'maintainer_email': None,
    'url': '',
    'packages': [
        'graiax.shortcut',
    ],
    'package_dir': {'': 'src'},
    'package_data': {'': ['*']},
    'long_description_content_type': 'text/markdown',
    'install_requires': INSTALL_REQUIRES,
    'python_requires': '>=3.8,<4.0',

}


setup(**setup_kwargs)
