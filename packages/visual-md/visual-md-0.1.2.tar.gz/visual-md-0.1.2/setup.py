# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['visual_md']

package_data = \
{'': ['*']}

install_requires = \
['build>=0.8.0,<0.9.0']

setup_kwargs = {
    'name': 'visual-md',
    'version': '0.1.2',
    'description': '',
    'long_description': None,
    'author': 'lyraxvincent',
    'author_email': 'njongevincent@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
