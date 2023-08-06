# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['volosti']

package_data = \
{'': ['*']}

extras_require = \
{'all': ['gunicorn>=20.1.0,<21.0.0',
         'uvicorn>=0.18.2',
         'volosti-server-sanic>=0,<1',
         'volosti-server-starlette>=0,<1']}

setup_kwargs = {
    'name': 'volosti',
    'version': '0.1.dev1',
    'description': 'Метапакет разрабатываемого проекта',
    'long_description': '#######\nВолости\n#######\nМетапакет разрабатываемого проекта\n',
    'author': 'Ruslan Ilyasovich Gilfanov',
    'author_email': 'ri.gilfanov@yandex.ru',
    'maintainer': 'Ruslan Ilyasovich Gilfanov',
    'maintainer_email': 'ri.gilfanov@yandex.ru',
    'url': 'https://pypi.org/project/volosti',
    'packages': packages,
    'package_data': package_data,
    'extras_require': extras_require,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
