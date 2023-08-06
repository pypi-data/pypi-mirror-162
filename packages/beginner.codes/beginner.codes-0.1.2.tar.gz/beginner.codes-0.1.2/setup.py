# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['beginnercodes', 'beginnercodes.challenges']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.27.1,<3.0.0']

setup_kwargs = {
    'name': 'beginner.codes',
    'version': '0.1.2',
    'description': 'Official package for the Beginner.Codes Discord community.',
    'long_description': None,
    'author': 'Zech Zimmerman',
    'author_email': 'hi@zech.codes',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
