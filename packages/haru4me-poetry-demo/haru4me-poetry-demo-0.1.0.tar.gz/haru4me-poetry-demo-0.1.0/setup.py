# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['haru4me_poetry_demo']

package_data = \
{'': ['*']}

install_requires = \
['numpy>=1.23.1,<2.0.0']

setup_kwargs = {
    'name': 'haru4me-poetry-demo',
    'version': '0.1.0',
    'description': 'Poetry demo package',
    'long_description': None,
    'author': 'Haru4me',
    'author_email': 'durdaev2010@yandex.ru',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
