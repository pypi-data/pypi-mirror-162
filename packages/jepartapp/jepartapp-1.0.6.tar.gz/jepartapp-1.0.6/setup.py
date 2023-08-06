# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['jepartapp']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'jepartapp',
    'version': '1.0.6',
    'description': 'Criado para envio e atualiçaõ de informações de loja fisica para servidor online.',
    'long_description': None,
    'author': 'Jean Carlos',
    'author_email': 'jeancarlosjc210995@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
