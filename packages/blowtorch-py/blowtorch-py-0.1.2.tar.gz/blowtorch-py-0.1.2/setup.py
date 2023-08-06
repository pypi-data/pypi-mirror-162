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
    'version': '0.1.2',
    'description': 'A framework for creating Rust machine learning models that are trained in Python.',
    'long_description': '# Blowtorch\nBlowtorch is a Python package that allows you to train machine learning models\nand run inference in pure Rust. This is done through a specifying the model\nonce in a JSON file. Blowtorch then exports your specification into Rust and Python \nmodels. You can train the Python model as you prefer, and Blowtorch can be run again\nto share the weights to Rust. \n\nAn example application built with a predecessor of Blowtorch is [ZipNet](https://conzel.github.io/zipnet/), \nwhich is a neural-network based compression algorithm run entirely in the browser.\nWe built Blowtorch as we could not find any easily extensible machine learning frameworks\nthat could be compiled to WebAssembly.\n\nAdvantages over similar packages\n- Inference is in pure Rust, meaning your model can run anywhere that Rust runs. You can for example compile it to WebAssembly.\n- New layers can be implemented very easily, as one just has to write a forward pass in Rust\n- Training is completely in Python, meaning you can use whatever training procedures you like\n- Complex networks can be built by splitting the architecture into simpler modules, which are combined together by some glue code\n\n## Features\n\n- [x] Export and import trained weights\n- [ ] Implementations for the following layers:\n    - [x] Conv\n    - [x] ConvT\n    - [x] ReLU\n    - [ ] GDN\n    - [ ] iGDN\n    - [x] Flatten\n    - [x] Linear\n- [x] Easy-to-use example \n- [x] Possibilities to extend the framework\n- [x] Documentation for Python & Rust\n',
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
