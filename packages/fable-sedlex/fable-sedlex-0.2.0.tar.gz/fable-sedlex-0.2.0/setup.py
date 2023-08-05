# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['fable_sedlex',
 'fable_sedlex.fable_modules',
 'fable_sedlex.fable_modules.fable_library']

package_data = \
{'': ['*'], 'fable_sedlex.fable_modules': ['fable_library/fable_modules/*']}

setup_kwargs = {
    'name': 'fable-sedlex',
    'version': '0.2.0',
    'description': 'language agnostic lexer generator via Fable and OCaml Sedlex',
    'long_description': None,
    'author': 'thautwarm',
    'author_email': 'twshere@outlook.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
