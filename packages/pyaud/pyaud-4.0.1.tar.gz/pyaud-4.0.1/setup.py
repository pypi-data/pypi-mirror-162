# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pyaud']

package_data = \
{'': ['*']}

install_requires = \
['appdirs>=1.4.4,<2.0.0',
 'environs>=9.4.0,<10.0.0',
 'gitspy>=0,<1',
 'lsfiles>=0,<1',
 'object-colors>=2.0.1,<3.0.0',
 'pyaud-plugins>=0.8',
 'spall>=0,<1',
 'tomli-w>=1.0.0,<2.0.0',
 'tomli>=2.0.1,<3.0.0']

entry_points = \
{'console_scripts': ['pyaud = pyaud.__main__:main']}

setup_kwargs = {
    'name': 'pyaud',
    'version': '4.0.1',
    'description': 'Framework for writing Python package audits',
    'long_description': 'pyaud\n=====\n.. image:: https://img.shields.io/badge/License-MIT-yellow.svg\n    :target: https://opensource.org/licenses/MIT\n    :alt: License\n.. image:: https://img.shields.io/pypi/v/pyaud\n    :target: https://img.shields.io/pypi/v/pyaud\n    :alt: pypi\n.. image:: https://github.com/jshwi/pyaud/actions/workflows/ci.yml/badge.svg\n    :target: https://github.com/jshwi/pyaud/actions/workflows/ci.yml\n    :alt: CI\n.. image:: https://github.com/jshwi/pyaud/actions/workflows/codeql-analysis.yml/badge.svg\n    :target: https://github.com/jshwi/pyaud/actions/workflows/codeql-analysis.yml\n    :alt: CodeQL\n.. image:: https://codecov.io/gh/jshwi/pyaud/branch/master/graph/badge.svg\n    :target: https://codecov.io/gh/jshwi/pyaud\n    :alt: codecov.io\n.. image:: https://readthedocs.org/projects/pyaud/badge/?version=latest\n    :target: https://pyaud.readthedocs.io/en/latest/?badge=latest\n    :alt: readthedocs.org\n.. image:: https://img.shields.io/badge/python-3.8-blue.svg\n    :target: https://www.python.org/downloads/release/python-380\n    :alt: python3.8\n.. image:: https://img.shields.io/badge/code%20style-black-000000.svg\n    :target: https://github.com/psf/black\n    :alt: black\n\nFramework for writing Python package audits\n-------------------------------------------\n\nThe ``pyaud`` framework is designed for writing modular audits for Python packages\n\nAudits can be run to fail, such as when using CI, or include a fix\n\nFixes can be written for whole directories or individual files\n\nPlugins can be written for manipulating files\n\nSupports single script plugins\n\nInstallation\n------------\n\nPyPi\n****\n\n``pip install pyaud``\n\nDevelopment\n***********\n\n``poetry install``\n\nUsage\n-----\n\n.. code-block:: console\n\n    usage: pyaud [-h] [-c] [-f] [-n] [-s] [-t] [-v] [--rcfile RCFILE] [--version] MODULE\n\n    positional arguments:\n      MODULE           choice of module: [modules] to list all\n\n    optional arguments:\n      -h, --help       show this help message and exit\n      -c, --clean      clean unversioned files prior to any process\n      -f, --fix        suppress and fix all fixable issues\n      -n, --no-cache   disable file caching\n      -s, --suppress   continue without stopping for errors\n      -t, --timed      track the length of time for each plugin\n      -v, --verbose    incrementally increase logging verbosity\n      --rcfile RCFILE  select file to override config hierarchy\n      --version        show version and exit\n\nPlugins\n-------\n\n``pyaud`` will search for a plugins package in the project root\n\nTo register a plugin package ensure it is importable and prefix the package with ``pyaud_``\n\nThe name ``pyaud_plugins`` is reserved and will be automatically imported\n\nTo view available plugins see ``pyaud-plugins`` `README <https://github.com/jshwi/pyaud-plugins/blob/master/README.rst>`_ or run ``pyaud modules all``\n\nFor writing plugins see `docs <https://jshwi.github.io/pyaud/pyaud.html#pyaud-plugins>`_\n\nConfigure\n---------\n\nConfiguration of settings can be made with the following toml syntax files (overriding in this order):\n\n    | ~/.config/pyaud/pyaud.toml\n    | ~/.pyaudrc\n    | .pyaudrc\n    | pyproject.toml\n\nA config can be generated with `pyaud generate-rcfile`\n\nPrefix each key with ``tool.pyaud`` when using pyproject.toml\n',
    'author': 'jshwi',
    'author_email': 'stephen@jshwisolutions.com',
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
