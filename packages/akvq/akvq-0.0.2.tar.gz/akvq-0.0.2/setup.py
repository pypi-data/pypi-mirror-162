# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

modules = \
['akvq']
install_requires = \
['azure-identity>=1.10.0,<2.0.0', 'azure-keyvault-secrets>=4.4.0,<5.0.0']

entry_points = \
{'console_scripts': ['akvq = src.akvq:main']}

setup_kwargs = {
    'name': 'akvq',
    'version': '0.0.2',
    'description': 'Get secrets from azure key vaults quick and easy',
    'long_description': None,
    'author': 'Viktor Freiman',
    'author_email': 'freiman.viktor@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'py_modules': modules,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6.2,<4.0.0',
}


setup(**setup_kwargs)
