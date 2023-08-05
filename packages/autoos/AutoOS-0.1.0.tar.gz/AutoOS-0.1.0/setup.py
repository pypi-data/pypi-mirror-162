# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['autoos']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'autoos',
    'version': '0.1.0',
    'description': 'Automated Open Science (AutoOS) provides methods for the automated documentation of (autonomously conducted) experiments. These methods build on community-supported and machine-readable standards for expressing quantitative models of brain function and behavior (e.g., the Model Description Format) and corresponding data sets (e.g., the Brain Imaging Data Structure). Our tools are designed to automate the translation of those data sets into the English language and facilitate uploads thereof to the Open Science Framework.',
    'long_description': None,
    'author': 'Sebastian Musslick',
    'author_email': 'sebastian_musslick@brown.edu',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
