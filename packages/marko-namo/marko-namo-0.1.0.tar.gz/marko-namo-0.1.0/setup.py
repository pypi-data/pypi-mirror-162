# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

modules = \
['marko_namo']
install_requires = \
['PyYAML>=6.0,<7.0', 'requests>=2.28.1,<3.0.0']

setup_kwargs = {
    'name': 'marko-namo',
    'version': '0.1.0',
    'description': 'Markov chain project name generator',
    'long_description': None,
    'author': 'Yass Eltahir',
    'author_email': '15998949+diabolical-ninja@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'py_modules': modules,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
