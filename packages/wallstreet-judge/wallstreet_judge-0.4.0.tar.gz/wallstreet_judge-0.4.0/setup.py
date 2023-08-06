# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['wallstreet_judge']

package_data = \
{'': ['*'], 'wallstreet_judge': ['data/*']}

install_requires = \
['colorama>=0.4.5,<0.5.0',
 'pydantic>=1.9.1,<2.0.0',
 'requests>=2.28.1,<3.0.0',
 'typer>=0.6.1,<0.7.0']

entry_points = \
{'console_scripts': ['wallstreet_judge = wallstreet_judge.main:app']}

setup_kwargs = {
    'name': 'wallstreet-judge',
    'version': '0.4.0',
    'description': '',
    'long_description': None,
    'author': 'Kushal Chordiya',
    'author_email': 'kushal.chordiya@trilogy.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
