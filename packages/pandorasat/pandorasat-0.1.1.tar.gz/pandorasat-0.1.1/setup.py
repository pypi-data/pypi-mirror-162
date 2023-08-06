# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['pandorasat']

package_data = \
{'': ['*'], 'pandorasat': ['data/*']}

install_requires = \
['astropy>=5.0.4,<6.0.0',
 'numpy>=1.22.3,<2.0.0',
 'pandas>=1.4.2,<2.0.0',
 'scipy>=1.8.1,<2.0.0',
 'tqdm>=4.64.0,<5.0.0']

setup_kwargs = {
    'name': 'pandorasat',
    'version': '0.1.1',
    'description': '',
    'long_description': None,
    'author': 'Christina Hedges',
    'author_email': 'christina.l.hedges@nasa.gov',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)
