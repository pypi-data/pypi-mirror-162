# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['docs_helper']
install_requires = \
['sphobjinv>=2.1,<3.0']

entry_points = \
{'console_scripts': ['docs-helper = docs_helper:main']}

setup_kwargs = {
    'name': 'docs-helper',
    'version': '0.0.8',
    'description': 'Simple interactive tool to help with intersphinx',
    'long_description': '# docs-helper\n\nSimple interactive wrapper over sphobjinv and your sphinx conf.py to make it easier to cross-reference with intersphinx.\n\nAll docs are in the docs folder\n',
    'author': 'Viktor Freiman',
    'author_email': 'freiman.viktor@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/viktorfreiman/docs-helper',
    'py_modules': modules,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6.2,<4.0.0',
}


setup(**setup_kwargs)
