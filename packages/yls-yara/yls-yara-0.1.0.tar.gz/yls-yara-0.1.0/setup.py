# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['yls_yara']

package_data = \
{'': ['*']}

install_requires = \
['yara-python>=4.2.0,<5.0.0', 'yls>=1.0.0,<2.0.0']

entry_points = \
{'yls': ['yara = yls_yara']}

setup_kwargs = {
    'name': 'yls-yara',
    'version': '0.1.0',
    'description': 'YLS plugin adding linting using yara-python.',
    'long_description': '# yls-yara\n\nAn YLS plugin adding YARA linting capabilities.\n',
    'author': 'Matej Kastak',
    'author_email': 'matej.kastak@avast.com',
    'maintainer': 'Matej Kašťák',
    'maintainer_email': 'matej.kastak@avast.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
