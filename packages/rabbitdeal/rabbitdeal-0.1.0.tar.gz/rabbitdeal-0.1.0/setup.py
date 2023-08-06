# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['Receiver', 'Sender']

package_data = \
{'': ['*']}

install_requires = \
['pika>=1.3.0,<2.0.0']

setup_kwargs = {
    'name': 'rabbitdeal',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'germangerken',
    'author_email': 'germangerken@yandex.ru',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/MattiooFR/package_name',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
