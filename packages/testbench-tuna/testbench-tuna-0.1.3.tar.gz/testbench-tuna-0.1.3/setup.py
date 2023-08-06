# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['testbench_tuna']

package_data = \
{'': ['*']}

install_requires = \
['fastapi>=0.78.0,<0.79.0']

setup_kwargs = {
    'name': 'testbench-tuna',
    'version': '0.1.3',
    'description': '',
    'long_description': None,
    'author': 'Tim Schwenke',
    'author_email': 'tim.schwenke@trallnag.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
