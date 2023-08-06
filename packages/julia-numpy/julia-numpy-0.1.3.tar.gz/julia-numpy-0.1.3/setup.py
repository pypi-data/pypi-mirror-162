# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['jnumpy', 'jnumpy.tests', 'jnumpy.tests.extension']

package_data = \
{'': ['*'],
 'jnumpy': ['TyPython/Project.toml', 'TyPython/src/*'],
 'jnumpy.tests': ['extension/src/*']}

install_requires = \
['jill>=0.11.1,<0.12.0',
 'numpy>=1.18,<2.0',
 'pydantic>=1.9.1,<2.0.0',
 'toml>=0.10.2,<0.11.0']

setup_kwargs = {
    'name': 'julia-numpy',
    'version': '0.1.3',
    'description': 'Writing Python C extensions in Julia within 5 minutes.',
    'long_description': None,
    'author': 'thautwarm',
    'author_email': 'twshere@outlook.com',
    'maintainer': 'songjhaha',
    'maintainer_email': 'songjh96@foxmail.com',
    'url': 'https://github.com/Suzhou-Tongyuan/jnumpy',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
