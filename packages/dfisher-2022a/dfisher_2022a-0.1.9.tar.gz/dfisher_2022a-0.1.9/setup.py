# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'python'}

packages = \
['dfisher_2022a',
 'dfisher_2022a.config',
 'dfisher_2022a.fits',
 'dfisher_2022a.models',
 'dfisher_2022a.models.lmfit',
 'dfisher_2022a.tests']

package_data = \
{'': ['*'], 'dfisher_2022a.tests': ['fixtures/*']}

install_requires = \
['astropy>=5.0.4,<6.0.0',
 'line-profiler>=3.5.1,<4.0.0',
 'lmfit>=1.0.3,<2.0.0',
 'mpdaf>=3.5,<4.0',
 'numpy>=1.8,<2.0',
 'pandas>=1.4.2,<2.0.0',
 'scipy==1.9.0',
 'sympy>=1.10.1,<2.0.0',
 'tables>=3.7.0,<4.0.0',
 'viztracer>=0.15.2,<0.16.0']

extras_require = \
{'docs': ['Sphinx==4.2.0', 'sphinx-rtd-theme==1.0.0']}

setup_kwargs = {
    'name': 'dfisher-2022a',
    'version': '0.1.9',
    'description': 'Spectral analysis code created for the delivery of the DFisher_2022A ADACS MAP project.',
    'long_description': None,
    'author': 'J. Hu',
    'author_email': 'jitinghu@swin.edu.au',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.8,<3.10',
}


setup(**setup_kwargs)
