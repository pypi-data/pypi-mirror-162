# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['autome',
 'autome.automatas',
 'autome.automatas.finite_automata',
 'autome.automatas.turing_machine',
 'autome.grammars',
 'autome.regex',
 'autome.regex.blocks',
 'autome.utils']

package_data = \
{'': ['*']}

install_requires = \
['black>=22.3.0,<23.0.0',
 'click>=8.1.3,<9.0.0',
 'ksuid>=1.3,<2.0',
 'tabulate>=0.8.9,<0.9.0']

setup_kwargs = {
    'name': 'autome',
    'version': '0.2.1',
    'description': 'Automata simulation with Python',
    'long_description': None,
    'author': 'João Vitor Maia',
    'author_email': 'maia.tostring@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
