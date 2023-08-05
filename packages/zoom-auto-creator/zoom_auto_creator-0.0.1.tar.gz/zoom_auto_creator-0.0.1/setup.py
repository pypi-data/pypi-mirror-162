# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['zoom_auto_creator']
install_requires = \
['Pillow>=9.2.0,<10.0.0', 'pyautogui>=0.9.53,<0.10.0']

setup_kwargs = {
    'name': 'zoom-auto-creator',
    'version': '0.0.1',
    'description': 'Creating Zoom Rooms',
    'long_description': None,
    'author': 'Bohdan Salamakha',
    'author_email': 'allen.avanheim@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'py_modules': modules,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
