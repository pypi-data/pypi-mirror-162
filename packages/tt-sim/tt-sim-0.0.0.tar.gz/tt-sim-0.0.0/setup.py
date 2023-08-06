# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['tt_sim', 'tt_sim.core']

package_data = \
{'': ['*']}

install_requires = \
['geographiclib>=1.52,<2.0', 'pandas>=1.3.3,<2.0.0', 'scipy>=1.7.1,<2.0.0']

setup_kwargs = {
    'name': 'tt-sim',
    'version': '0.0.0',
    'description': 'Time Trial Simulator',
    'long_description': None,
    'author': 'Jim Parr',
    'author_email': 'jimparr19@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.1,<3.10',
}


setup(**setup_kwargs)
