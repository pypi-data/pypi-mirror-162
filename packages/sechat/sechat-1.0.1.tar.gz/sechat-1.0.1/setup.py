# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['sechat']

package_data = \
{'': ['*']}

install_requires = \
['bs4>=0.0.1,<0.0.2',
 'requests>=2.27.1,<3.0.0',
 'websocket-client>=1.3.2,<2.0.0']

setup_kwargs = {
    'name': 'sechat',
    'version': '1.0.1',
    'description': 'A BETTER Stack Exchange chat library.',
    'long_description': None,
    'author': 'Ginger',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8.0,<4.0.0',
}


setup(**setup_kwargs)
