# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['quantready', 'quantready.templates']

package_data = \
{'': ['*']}

install_requires = \
['colorama>=0.4.5,<0.5.0',
 'rich>=12.5.1,<13.0.0',
 'shellingham>=1.5.0,<2.0.0',
 'tabulate>=0.8.10,<0.9.0',
 'termcolor>=1.1.0,<2.0.0',
 'tomlkit>=0.11.3,<0.12.0',
 'typer>=0.6.1,<0.7.0']

setup_kwargs = {
    'name': 'quantready',
    'version': '0.1.0',
    'description': 'A cli to configure your entire quantitative investing stack, from building signals to managing SMAs',
    'long_description': None,
    'author': 'Sean Kruzel',
    'author_email': 'skruzel@astrocyte.io',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
