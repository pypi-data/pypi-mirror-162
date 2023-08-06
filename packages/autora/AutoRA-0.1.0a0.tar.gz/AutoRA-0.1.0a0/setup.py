# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['autora']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'autora',
    'version': '0.1.0a0',
    'description': 'Autonomous Research Assistant (AutoRA) is a framework for implementing machine learning tools which autonomously and iteratively generate 1) new theories to describe real-world data, and 2) experiments to invalidate those theories and seed a new cycle of theory-making. The experiments will be run online via crowd-sourcing platforms (MTurk, Prolific).',
    'long_description': None,
    'author': 'Sebastian Musslick',
    'author_email': 'sebastian_musslick@brown.edu',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)
