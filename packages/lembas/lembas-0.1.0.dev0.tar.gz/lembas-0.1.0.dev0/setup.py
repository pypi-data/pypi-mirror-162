# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['lembas']

package_data = \
{'': ['*']}

extras_require = \
{'ci': ['codecov>=2.1.12,<3.0.0']}

setup_kwargs = {
    'name': 'lembas',
    'version': '0.1.0.dev0',
    'description': 'Lifecycle Engineering Model-Based Analysis System',
    'long_description': None,
    'author': 'Matt Kramer',
    'author_email': 'mkramer@anaconda.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'extras_require': extras_require,
    'python_requires': '>=3.9,<3.12',
}


setup(**setup_kwargs)
