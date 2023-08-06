# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['sentential', 'sentential.cli', 'sentential.lib', 'sentential.lib.shapes']

package_data = \
{'': ['*'], 'sentential': ['templates/*']}

install_requires = \
['Jinja2>=3.1.2,<4.0.0',
 'boto3>=1.24.31,<2.0.0',
 'pydantic>=1.9.1,<2.0.0',
 'python-on-whales>=0.49,<0.51',
 'tabulate>=0.8.10,<0.9.0',
 'typer>=0.6.1,<0.7.0']

entry_points = \
{'console_scripts': ['sntl = sentential.sntl:main']}

setup_kwargs = {
    'name': 'sentential',
    'version': '0.2.0',
    'description': 'because lambdas are good',
    'long_description': None,
    'author': 'Brendan Keane',
    'author_email': 'btkeane@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
