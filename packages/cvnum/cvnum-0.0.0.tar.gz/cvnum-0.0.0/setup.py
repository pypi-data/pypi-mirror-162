# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['cvnum',
 'cvnum.config',
 'cvnum.config.textify',
 'cvnum.convert',
 'cvnum.convert.integer',
 'cvnum.convert.natural',
 'cvnum.core',
 'cvnum.textify']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'cvnum',
    'version': '0.0.0',
    'description': 'A tool to convert mathematical numbers in several formats.',
    'long_description': 'The Python module `cvnum`\n=========================\n\n> **I beg your pardon for my english...**\n>\n> English is not my native language, so be nice if you notice misunderstandings, misspellings, or grammatical errors in my documents and codes.\n\n\nLast version: 0.0.0\n-------------------\n\nThis version was made on 2022-08-10.\n\n\nAbout `cvnum`\n-------------\n\nHere are the features proposed by `cvnum`.\n\n   1. Conversion of natural integers from one base to another.\n\n   1. Textual version of natural integers in several languages. **Proposing new translations can be done without being a programmer.**\n<!--\n   1. Conversion of textual versions of natural integers to their digital value (the translation can fixed some errors like basic mispellings).\n-->',
    'author': 'Christophe BAL',
    'author_email': None,
    'maintainer': 'Christophe BAL',
    'maintainer_email': None,
    'url': 'https://github.com/math-tools/math-objects/tree/main/cvnum',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
