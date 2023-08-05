# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['calculate_my_score']

package_data = \
{'': ['*']}

install_requires = \
['pytest>=7.1.2,<8.0.0', 'rich>=12.5.1,<13.0.0', 'typer>=0.6.1,<0.7.0']

entry_points = \
{'console_scripts': ['calculate-my-score = calculate_my_score.main:app']}

setup_kwargs = {
    'name': 'calculate-my-score',
    'version': '0.1.0',
    'description': 'Calculate your score by one simple command!',
    'long_description': '# calculate-my-score\n',
    'author': 'Bar Hochman',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
