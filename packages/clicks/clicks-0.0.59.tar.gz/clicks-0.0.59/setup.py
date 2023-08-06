# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['clicks']

package_data = \
{'': ['*']}

install_requires = \
['argcomplete>=2.0.0,<3.0.0', 'rich>=11.2.0,<12.0.0']

setup_kwargs = {
    'name': 'clicks',
    'version': '0.0.59',
    'description': 'Tools for a metamodern terminal environment',
    'long_description': '# clicks\n\nTools for a metamodern terminal environment\n',
    'author': 'Angelo Gladding',
    'author_email': 'angelo@ragt.ag',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://ragt.ag/code/clicks',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<3.11',
}


setup(**setup_kwargs)
