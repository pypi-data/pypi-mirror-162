# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['aiop4']

package_data = \
{'': ['*']}

install_requires = \
['googleapis-common-protos==1.54.0',
 'grpcio==1.46.3',
 'p4runtime==1.4.0rc5',
 'protobuf==3.18.1']

setup_kwargs = {
    'name': 'aiop4',
    'version': '0.1.0',
    'description': 'asyncio P4Runtime Python client',
    'long_description': '<div align="center">\n  <h1><code>aiop4</code></h1>\n\n  <strong>asyncio P4Runtime Python client</strong>\n</div>\n',
    'author': 'Vinicius Arcanjo',
    'author_email': 'viniarck@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/viniarck/aiop4',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
