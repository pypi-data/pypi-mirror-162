# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['dacy',
 'dacy.datasets',
 'dacy.datasets.lookup_tables',
 'dacy.hate_speech',
 'dacy.score',
 'dacy.sentiment']

package_data = \
{'': ['*']}

install_requires = \
['pandas>=1.0.0,<2.0.0',
 'protobuf>=3.17.3,<3.18.0',
 'sentencepiece>=0.1.96,<0.2.0',
 'spacy-wrap>=1.0.2,<1.1.0',
 'spacy>=3.2.0,<3.3.0',
 'tqdm>=4.61.2,<5.0.0',
 'wasabi>=0.8.2,<0.10.0']

setup_kwargs = {
    'name': 'dacy',
    'version': '2.0.0',
    'description': 'A Danish pipeline trained in SpaCy that has achieved State-of-the-Art performance on all dependency parsing, NER and POS-tagging for Danish',
    'long_description': None,
    'author': 'KennethEnevoldsen',
    'author_email': 'kennethcenevolsen@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://centre-for-humanities-computing.github.io/DaCy/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
