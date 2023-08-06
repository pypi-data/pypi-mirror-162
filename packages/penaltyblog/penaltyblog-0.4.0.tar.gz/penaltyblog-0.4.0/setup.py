# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['penaltyblog',
 'penaltyblog.fpl',
 'penaltyblog.implied',
 'penaltyblog.metrics',
 'penaltyblog.models',
 'penaltyblog.ratings',
 'penaltyblog.scrapers']

package_data = \
{'': ['*']}

install_requires = \
['PuLP>=2.6.0,<3.0.0',
 'cssselect>=1.1.0,<2.0.0',
 'lxml>=4.9.1,<5.0.0',
 'numpy>=1.23.1,<2.0.0',
 'pandas>=1.4.3,<2.0.0',
 'scipy>=1.9.0,<2.0.0',
 'selenium>=4.3.0,<5.0.0',
 'webdriver-manager>=3.8.3,<4.0.0']

setup_kwargs = {
    'name': 'penaltyblog',
    'version': '0.4.0',
    'description': 'Library from http://pena.lt/y/blog for scraping and modelling football (soccer) data',
    'long_description': '# Penalty Blog\n\n<div align="center">\n\n  <a href="">[![Python Version](https://img.shields.io/pypi/pyversions/penaltyblog)](https://pypi.org/project/penaltyblog/)</a>\n  <a href="">[![Coverage Status](https://coveralls.io/repos/github/martineastwood/penaltyblog/badge.svg?branch=master&service=github)](https://coveralls.io/repos/github/martineastwood/penaltyblog/badge.svg?branch=master&service=github)</a>\n  <a href="">[![PyPI](https://img.shields.io/pypi/v/penaltyblog.svg)](https://pypi.org/project/penaltyblog/)</a>\n  <a href="">[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)</a>\n  <a href="">[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)</a>\n  <a href="">[![Code style: pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)</a>\n\n</div>\n\n\nThe **penaltyblog** Python package contains lots of useful code from [pena.lt/y/blog](http://pena.lt/y/blog.html) for working with football (soccer) data.\n\n**penaltyblog** includes functions for:\n\n- Scraping football data from sources such as football-data.co.uk, ESPN, Club Elo, Understat and Fantasy Premier League\n- Modelling of football matches using Poisson-based models, such as Dixon and Coles\n- Predicting probabilities for many betting markets, e.g. Asian handicaps, over/under, total goals etc\n- Modelling football team\'s abilities using Massey ratings and Colley ratings\n- Estimating the implied odds from bookmaker\'s odds by removing the overround using multiple different methods\n- Mathematically optimising your fantasy football team\n\n## Installation\n\n`pip install penaltyblog`\n\n\n## Documentation\n\nTo learn how to use penaltyblog, you can read the [documentation](https://penaltyblog.readthedocs.io/en/latest/) and look at the\nexamples for:\n\n- [Scraping football data](https://penaltyblog.readthedocs.io/en/latest/scrapers/index.html)\n- [Predicting football matches and betting markets](https://penaltyblog.readthedocs.io/en/latest/models/index.html)\n- [Estimating the implied odds from bookmakers odds](https://penaltyblog.readthedocs.io/en/latest/implied/index.html)\n- [Calculate Massey and Colley ratings](https://penaltyblog.readthedocs.io/en/latest/ratings/index.html)\n\n## References\n\n- Mark J. Dixon and Stuart G. Coles (1997) Modelling Association Football Scores and Inefficiencies in the Football Betting Market.\n- Håvard Rue and Øyvind Salvesen (1999) Prediction and Retrospective Analysis of Soccer Matches in a League.\n- Anthony C. Constantinou and Norman E. Fenton (2012) Solving the problem of inadequate scoring rules for assessing probabilistic football forecast models\n- Hyun Song Shin (1992) Prices of State Contingent Claims with Insider Traders, and the Favourite-Longshot Bias\n- Hyun Song Shin (1993) Measuring the Incidence of Insider Trading in a Market for State-Contingent Claims\n- Joseph Buchdahl (2015) The Wisdom of the Crowd\n',
    'author': 'Martin Eastwood',
    'author_email': 'martin.eastwood@gmx.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/martineastwood/penaltyblog',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.12',
}


setup(**setup_kwargs)
