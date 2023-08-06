# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['quart_uploads']

package_data = \
{'': ['*']}

install_requires = \
['aiofiles>=0.8.0,<0.9.0', 'quart>=0.18.0,<0.19.0']

setup_kwargs = {
    'name': 'quart-uploads',
    'version': '0.0.1',
    'description': '',
    'long_description': 'Quart Uploads\n=============\n\n![Quart Uploads Logo](logos/logo.png)\n\nQuart-Uploads allows your application to flexibly and efficiently handle file\nuploading and serving the uploaded files.\n\nYou can create different sets of uploads - one for document attachments, one\nfor photos, etc. - and the application can be configured to save them all in\ndifferent places and to generate different URLs for them.\n\nFor more information on Quart, [visit here](https://quart.palletsprojects.com/en/latest/)\n\nQuart-Uploads is based on [Flask-Uploads](https://github.com/maxcountryman/flask-uploads>) by maxcountryman. ',
    'author': 'Chris Rood',
    'author_email': 'quart.addons@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Quart-Addons/quart-uploads',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
