# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['blowtorch', 'blowtorch.layers']

package_data = \
{'': ['*'], 'blowtorch': ['schema/*', 'templates/*']}

install_requires = \
['Jinja2>=3.1.1,<4.0.0', 'jsonschema>=4.4.0,<5.0.0', 'torch>=1.11.0,<2.0.0']

entry_points = \
{'console_scripts': ['blowtorch = blowtorch.cli:main']}

setup_kwargs = {
    'name': 'blowtorch-py',
    'version': '0.1.1',
    'description': 'A framework for creating Rust machine learning models that are trained in Python.',
    'long_description': None,
    'author': 'Conzel',
    'author_email': '38732545+Conzel@users.noreply.github.com',
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
