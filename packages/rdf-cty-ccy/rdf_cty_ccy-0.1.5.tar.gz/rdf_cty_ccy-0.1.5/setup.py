# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['rdf_cty_ccy',
 'rdf_cty_ccy.common',
 'rdf_cty_ccy.graph',
 'rdf_cty_ccy.model',
 'rdf_cty_ccy.query',
 'rdf_cty_ccy.rdfdata']

package_data = \
{'': ['*']}

install_requires = \
['PyMonad>=2.4.0,<3.0.0',
 'rdflib>=6.1.1,<7.0.0',
 'requests>=2.28.1,<3.0.0',
 'simple-memory-cache>=1.0.0,<2.0.0']

entry_points = \
{'console_scripts': ['build_onto = rdf_cty_ccy.common.build_onto:builder']}

setup_kwargs = {
    'name': 'rdf-cty-ccy',
    'version': '0.1.5',
    'description': '',
    'long_description': None,
    'author': 'Col Perks',
    'author_email': 'wild.fauve@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
