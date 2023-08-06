# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['owl', 'owl.data_types', 'owl.owl_ast', 'owl.resolver', 'owl.tool']

package_data = \
{'': ['*']}

entry_points = \
{'console_scripts': ['owl = owl:main']}

setup_kwargs = {
    'name': 'owl-lang',
    'version': '0.6.3',
    'description': 'The owl 🦉 programming language',
    'long_description': None,
    'author': 'Hieu Tran',
    'author_email': 'hieutran106@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
