# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['grokpub', 'grokpub.response', 'grokpub.schema', 'grokpub.utils']

package_data = \
{'': ['*']}

install_requires = \
['orjson>=3.7.11,<4.0.0', 'pydantic>=1.9.1,<2.0.0']

setup_kwargs = {
    'name': 'grokpub',
    'version': '0.1.1',
    'description': '',
    'long_description': None,
    'author': 'Gaoddy',
    'author_email': 'gaoddy@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
