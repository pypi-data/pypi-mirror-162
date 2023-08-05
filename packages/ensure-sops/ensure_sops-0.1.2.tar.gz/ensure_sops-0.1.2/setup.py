# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ensure_sops']

package_data = \
{'': ['*']}

install_requires = \
['ordered-set>=4.1.0,<5.0.0',
 'python-dotenv>=0.20.0,<0.21.0',
 'ruamel.yaml>=0.17.21,<0.18.0']

entry_points = \
{'console_scripts': ['ensure_sops = ensure_sops.main:main']}

setup_kwargs = {
    'name': 'ensure-sops',
    'version': '0.1.2',
    'description': 'Check if your files are encrypted with Mozilla SOPS or not. Can act as pre-commit hook as well.',
    'long_description': None,
    'author': 'Engineering Team at Tacto Technology GmbH.',
    'author_email': 'engineering@tacto.ai',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<3.11',
}


setup(**setup_kwargs)
