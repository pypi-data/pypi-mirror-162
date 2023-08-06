# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['volosti_server_sanic', 'volosti_server_sanic.wui']

package_data = \
{'': ['*']}

install_requires = \
['sanic>=22.6.1,<23.0.0']

extras_require = \
{'all': ['gunicorn>=20.1.0,<21.0.0', 'uvicorn>=0.18.2'],
 'gunicorn': ['gunicorn>=20.1.0,<21.0.0'],
 'uvicorn': ['uvicorn>=0.18.2']}

setup_kwargs = {
    'name': 'volosti-server-sanic',
    'version': '0.1.dev0',
    'description': 'Разрабатываемая реализация сервера Волостей на веб-фреймворке Sanic',
    'long_description': 'volosti-server-sanic\n====================\nРазрабатываемая реализация сервера Волостей на веб-фреймворке Sanic\n',
    'author': 'Ruslan Ilyasovich Gilfanov',
    'author_email': 'ri.gilfanov@yandex.ru',
    'maintainer': 'Ruslan Ilyasovich Gilfanov',
    'maintainer_email': 'ri.gilfanov@yandex.ru',
    'url': 'https://pypi.org/project/volosti-server-sanic',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
