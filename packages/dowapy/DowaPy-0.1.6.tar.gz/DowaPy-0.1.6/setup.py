# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['dowapy',
 'dowapy.Application',
 'dowapy.Application.console',
 'dowapy.Application.console.command',
 'dowapy.Data',
 'dowapy.File',
 'dowapy.Log',
 'dowapy.Maya',
 'dowapy.Process',
 'dowapy.Process.Multiprocess',
 'dowapy.Process.Thread']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'dowapy',
    'version': '0.1.6',
    'description': '',
    'long_description': None,
    'author': 'Dowa',
    'author_email': 'wingkdh@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
