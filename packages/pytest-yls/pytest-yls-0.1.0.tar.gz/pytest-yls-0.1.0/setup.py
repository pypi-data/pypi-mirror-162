# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pytest_yls']

package_data = \
{'': ['*']}

install_requires = \
['pytest>=7.1.2,<8.0.0', 'tenacity>=8.0.1,<9.0.0', 'yls>=1,<2']

entry_points = \
{'pytest11': ['pytest_yls = pytest_yls']}

setup_kwargs = {
    'name': 'pytest-yls',
    'version': '0.1.0',
    'description': 'Pytest plugin to test the YLS as a whole.',
    'long_description': '# pytest-yls\n\nPytest plugin adding primitives for E2E tests.\n',
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
