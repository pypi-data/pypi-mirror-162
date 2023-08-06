# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['webcode_tk']

package_data = \
{'': ['*']}

install_requires = \
['MechanicalSoup>=1.1.0,<2.0.0',
 'bs4>=0.0.1,<0.0.2',
 'file-clerk>=1.0.9,<2.0.0',
 'lxml>=4.9.1,<5.0.0',
 'pre-commit>=2.20.0,<3.0.0',
 'requests>=2.28.1,<3.0.0']

setup_kwargs = {
    'name': 'webcode-tk',
    'version': '0.2.2',
    'description': '',
    'long_description': 'webcode-toolkit (webcode-tk)\n============================\n\nA set of tools for inspecting HTML and CSS code for validity and other\nvarious checks, such as semantics or required elements.\n',
    'author': 'hundredvisionsguy',
    'author_email': 'cwinikka@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
