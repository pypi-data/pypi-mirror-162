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
    'version': '0.1.1',
    'description': 'Calculate your score by one simple command!',
    'long_description': "# calculate-my-score\n\nAll of you students have hard time calculate your final score.\n\nUse this simple script to solve the problem of solving you final grade!\n\n## Installation\n\n```shell\npip install calculate-my-score\n```\n\n## Usage\n\nProvide a pair of GRADE:WEIGHT.\n\nLets say we had a homework which we scored 90 in it, and it's worth 20 points. On our final exam, we scored 100 and it worth 80 points.\n\nWe shall run the next command:\n\n```shell\n❯ calculate-my-score 90:20 80:100\nYour score is 81.67/120\n```\n\n## Thanks\n\nThank you my love for asking me simple calculation questions so I can program them ❤️\n",
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
