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
    'version': '0.1.1',
    'description': 'Plotting ridgeplots with matplotlib',
    'long_description': '# ridgeplot-py #\n\n[![CI](https://github.com/wckdouglas/ridgeplot-py/actions/workflows/ci.yaml/badge.svg)](https://github.com/wckdouglas/ridgeplot-py/actions/workflows/ci.yaml) [![codecov](https://codecov.io/gh/wckdouglas/ridgeplot-py/branch/main/graph/badge.svg?token=2owCGZa1K4)](https://codecov.io/gh/wckdouglas/ridgeplot-py)\n\n\nA simple module for plotting [ridgeplot](https://clauswilke.com/blog/2017/09/15/goodbye-joyplots/) with the [scipy ecosystem](https://www.scipy.org/about.html).\n\n## Install ##\n\n```\ngit clone git@github.com:wckdouglas/ridgeplot-py.git\ncd ridgeplot-py\npython setup.py install \n```\n\n\n## Example ##\n\nA [notebook](https://github.com/wckdouglas/ridgeplot-py/blob/main/Example.ipynb) showing quick howto is included in this repo!',
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
