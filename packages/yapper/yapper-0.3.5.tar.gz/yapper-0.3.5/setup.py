
# -*- coding: utf-8 -*-
from setuptools import setup

import codecs

with codecs.open('README.md', encoding="utf-8") as fp:
    long_description = fp.read()
INSTALL_REQUIRES = [
    'docstring-parser<1.0,>=0.13',
    'dominate<3.0.0,>=2.6.0',
    'python-slugify<7.0.0,>=6.1.1',
    'Markdown<4.0.0,>=3.3.6',
    'toml>=0.10.2',
]
ENTRY_POINTS = {
    'console_scripts': [
        'yapper = yapper.cli:parse_cli',
    ],
}

setup_kwargs = {
    'name': 'yapper',
    'version': '0.3.5',
    'description': 'Parser for converting python docstrings to .astro files for the Astro static site generator.',
    'long_description': long_description,
    'license': 'MIT',
    'author': '',
    'author_email': 'Gareth Simons <info@benchmarkurbanism.com>',
    'maintainer': '',
    'maintainer_email': 'Gareth Simons <info@benchmarkurbanism.com>',
    'url': 'https://github.com/benchmark-urbanism/yapper',
    'packages': [
        'yapper',
    ],
    'package_data': {'': ['*']},
    'long_description_content_type': 'text/markdown',
    'keywords': ['python', 'static-site-generator', 'astro', 'parser', 'documentation', 'docstrings'],
    'classifiers': [
        'Programming Language :: Python',
    ],
    'install_requires': INSTALL_REQUIRES,
    'python_requires': '>=3.8,<4.0',
    'entry_points': ENTRY_POINTS,

}


setup(**setup_kwargs)
