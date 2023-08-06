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
    'version': '0.1.2',
    'description': 'Plotting ridgeplots with matplotlib',
    'long_description': '# ridgeplot-py #\n\n[![CI](https://github.com/wckdouglas/ridgeplot-py/actions/workflows/ci.yaml/badge.svg)](https://github.com/wckdouglas/ridgeplot-py/actions/workflows/ci.yaml) [![codecov](https://codecov.io/gh/wckdouglas/ridgeplot-py/branch/main/graph/badge.svg?token=2owCGZa1K4)](https://codecov.io/gh/wckdouglas/ridgeplot-py)\n\n\nThis is a simple module for plotting [ridgeplot](https://clauswilke.com/blog/2017/09/15/goodbye-joyplots/) with the [scipy ecosystem](https://www.scipy.org/about.html).\n\nRidgeplot is a great data visualization technique to compare distributions from multiple groups at the same time, and was first introduced in 2017 as joy plot:\n\n<blockquote class="twitter-tweet"><p lang="en" dir="ltr">I hereby propose that we call these &quot;joy plots&quot; <a href="https://twitter.com/hashtag/rstats?src=hash&amp;ref_src=twsrc%5Etfw">#rstats</a> <a href="https://t.co/uuLGpQLAwY">https://t.co/uuLGpQLAwY</a></p>&mdash; Jenny Bryan (@JennyBryan) <a href="https://twitter.com/JennyBryan/status/856674638981550080?ref_src=twsrc%5Etfw">April 25, 2017</a></blockquote> \n\n[ridgeplot-py](https://pypi.org/project/ridgeplot-py/) provides a simple API to produce matplotlib-compatible ridgeplots, as well as a handy [ColorEncoder](https://github.com/wckdouglas/ridgeplot-py/blob/0198628ce0622e2e7f4f4e9284165d5d09324ca9/ridgeplot/colors.py#L117) class with scikit-learn syntax for manipulating color annotations in a consistent way [through out manuscripts or presentations].\n\n## Install ##\n\n```bash\ngit clone git@github.com:wckdouglas/ridgeplot-py.git\ncd ridgeplot-py\npython setup.py install \n```\n\n## Usage ##\n\n```python\nfrom ridgeplot import ridgeplot\nfrom ridgeplot.colors import ColorEncoder, ColorPalette\nimport numpy as np\nimport matplotlib.pyplot as plt\n\n# mocking some data\n# the input data should be a dict of\n# - keys: group names for the distributions\n# - values: list of values \ndata = {}\nfor i in range(8):\n    data[\'data_{}\'.format(i)] = np.random.randn(100) * (i+1)\n\n# make the plot\nfig = plt.figure()\nax = fig.add_subplot(111)\nridgeplot(\n    ax, \n    data, \n    xlim=(-20,20), \n    label_size=15\n)\n```\n\n![img](https://raw.githubusercontent.com/wckdouglas/ridgeplot-py/main/img/ridgeplot.png)\n\n\n## Example ##\n\nA [notebook](https://github.com/wckdouglas/ridgeplot-py/blob/main/Example.ipynb) showing quick howto is included in this repo!',
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
