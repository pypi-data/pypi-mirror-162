# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ridgeplot']

package_data = \
{'': ['*']}

install_requires = \
['matplotlib==3.1.3',
 'more-itertools>=8.9.0,<9.0.0',
 'numpy==1.21.1',
 'scipy==1.4.1']

setup_kwargs = {
    'name': 'ridgeplot-py',
    'version': '0.1.0',
    'description': 'Plotting ridgeplots with matplotlib',
    'long_description': None,
    'author': 'Douglas Wu',
    'author_email': 'wckdouglas@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
