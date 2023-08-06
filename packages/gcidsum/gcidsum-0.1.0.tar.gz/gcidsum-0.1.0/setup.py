# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['gcidsum']
install_requires = \
['xlgcid>=0.1.0,<0.2.0']

entry_points = \
{'console_scripts': ['gcidsum = gcidsum:main']}

setup_kwargs = {
    'name': 'gcidsum',
    'version': '0.1.0',
    'description': '',
    'long_description': '# gcidsum\n\nCalculates and verifies XunLei GCID like `sha1sum`.\n\n## Usage\n\nInstall via `pip` or `pipx`, then run `gcidsum --help` for more details.\n',
    'author': 'Cologler',
    'author_email': 'skyoflw@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Cologler/gcidsum-python',
    'py_modules': modules,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
