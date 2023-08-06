# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['volosti']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'volosti',
    'version': '0.1.dev0',
    'description': 'Метапакет запланированного проекта',
    'long_description': '#######\nВолости\n#######\nМетапакет запланированного проекта\n',
    'author': 'Ruslan Ilyasovich Gilfanov',
    'author_email': 'ri.gilfanov@yandex.ru',
    'maintainer': 'Ruslan Ilyasovich Gilfanov',
    'maintainer_email': 'ri.gilfanov@yandex.ru',
    'url': 'https://pypi.org/project/volosti',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
