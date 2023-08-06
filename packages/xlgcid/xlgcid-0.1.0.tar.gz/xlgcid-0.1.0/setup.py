# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['xlgcid']
setup_kwargs = {
    'name': 'xlgcid',
    'version': '0.1.0',
    'description': 'XunLei GCID hash algorithm',
    'long_description': "# xlgcid\n\nXunLei GCID hash algorithm, inspired from https://binux.blog/2012/03/hash_algorithm_of_xunlei/.\n\n## Usage\n\n``` python\nfrom xlgcid import get_file_gcid_digest\n\nprint(get_file_gcid_digest('a.txt').hex())\n```\n",
    'author': 'Cologler',
    'author_email': 'skyoflw@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Cologler/xlgcid-python',
    'py_modules': modules,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
