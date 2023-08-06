# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['xair_api']

package_data = \
{'': ['*']}

install_requires = \
['python-osc>=1.8.0,<2.0.0']

setup_kwargs = {
    'name': 'xair-api',
    'version': '1.0.0',
    'description': 'Remote control Behringer X-Air | Midas MR mixers through OSC',
    'long_description': None,
    'author': 'onyx-and-iris',
    'author_email': 'code@onyxandiris.online',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.11,<4.0',
}


setup(**setup_kwargs)
