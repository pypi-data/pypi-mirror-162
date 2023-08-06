# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['cruz']

package_data = \
{'': ['*']}

install_requires = \
['pandas>=1.4.3,<2.0.0', 'pyarrow>=9.0.0,<10.0.0', 'requests>=2.28.1,<3.0.0']

setup_kwargs = {
    'name': 'cruz',
    'version': '1.0.0',
    'description': '',
    'long_description': None,
    'author': 'Kyle Kelley',
    'author_email': 'rgbkrk@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
