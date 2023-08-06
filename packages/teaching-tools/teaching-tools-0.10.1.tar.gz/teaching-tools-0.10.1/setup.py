# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['teaching_tools', 'teaching_tools.ab_test']

package_data = \
{'': ['*']}

install_requires = \
['ipython>=8.1.1,<9.0.0',
 'ipywidgets>=7.6.5,<8.0.0',
 'matplotlib>=3.4.3,<4.0.0',
 'names>=0.3.0,<0.4.0',
 'numpy>=1.21,<2.0',
 'pandas>=1.4.1,<2.0.0',
 'pymongo>=4.1.1,<5.0.0',
 'randomtimestamp>=2.2,<3.0',
 'sklearn>=0.0,<0.1']

setup_kwargs = {
    'name': 'teaching-tools',
    'version': '0.10.1',
    'description': 'Teaching tools for the WQU Data Science Lab',
    'long_description': None,
    'author': 'Nicholas Cifuentes-Goodbody',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
