# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['qctrlpyquil']

package_data = \
{'': ['*']}

install_requires = \
['numpy>=1.16,<2.0',
 'pyquil>=2.9,<3.0',
 'qctrl-open-controls>=9.1.1,<10.0.0',
 'scipy>=1.3,<2.0',
 'toml>=0.10.0,<0.11.0']

setup_kwargs = {
    'name': 'qctrl-pyquil',
    'version': '0.0.6',
    'description': 'Q-CTRL Python PyQuil',
    'long_description': '# Q-CTRL Python PyQuil\n\nThe aim of the Q-CTRL pyQuil Adapter package is to provide export functions allowing\nusers to deploy established error-robust quantum control protocols from the\nopen literature and defined in Q-CTRL Open Controls on Rigetti quantum hardware\nand simulators.\n\nAnyone interested in quantum control is welcome to contribute to this project.',
    'author': 'Q-CTRL',
    'author_email': 'support@q-ctrl.com',
    'maintainer': 'Q-CTRL',
    'maintainer_email': 'support@q-ctrl.com',
    'url': 'https://q-ctrl.com',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.2,<3.9',
}


setup(**setup_kwargs)
