# mypythontools

Some tools/functions/snippets/files used across projects.

[![Python versions](https://img.shields.io/pypi/pyversions/mypythontools.svg)](https://pypi.python.org/pypi/mypythontools/) [![PyPI version](https://badge.fury.io/py/mypythontools.svg)](https://badge.fury.io/py/mypythontools) [![Downloads](https://pepy.tech/badge/mypythontools)](https://pepy.tech/project/mypythontools) [![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/Malachov/mypythontools.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/Malachov/mypythontools/context:python) [![Documentation Status](https://readthedocs.org/projects/mypythontools/badge/?version=latest)](https://mypythontools.readthedocs.io/en/latest/?badge=latest) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) [![codecov](https://codecov.io/gh/Malachov/mypythontools/branch/master/graph/badge.svg)](https://codecov.io/gh/Malachov/mypythontools)

It's called mypythontools, but it's also made for you...

Many projects - one codebase.

There is also some extra stuff, that is not bundled via PyPI (CSS for readthedocs etc.),
such a content is under the `Tools` topic.


## Links

Official documentation - [readthedocs](https://mypythontools.readthedocs.io/)

Official repo - [GitHub](https://github.com/Malachov/mypythontools)


## Installation

Python >=3.6 (Python 2 is not supported).

Install with

```console
pip install mypythontools
```

There can be some extras, that not everybody need. Install it like

```console
pip install mypythontools[plots]
```

Available extras are ["all", "plots"]

Python library
==============

**subpackages**

- config
- misc
- paths
- property
- system
- types

Subpackages names are self describing, and you can find documentation in subpackages docstrings.


## Tools

There are some extra tools not included in python library (installable via pip), but still on GitHub repository.


### requirements

Install many libraries at once (no need for Anaconda). Download `requirements.txt` file from (GitHub)[https://github.com/Malachov/mypythontools/tree/master/tools/requirements] and in that folder use

```
pip install -r requirements.txt
```

It's good for python libraries that other users with different versions of libraries will use. If not standalone application where freezing into virtual env is good idea - here is possible to use these requirements with using --upgrade from time to time to be sure that your library will be working for up-to-date version of dependencies.

### sphinx-alabaster-css

It's a good idea to generate documentation from code. If you are using sphinx and alabaster theme, you can use this CSS file for formatting.

Tested on readthedocs hosting (recommended).

CSS are served from GitHub, and it's possible to change on one place and edit how all projects docs look like at once.

Just add this to sphinx conf.py

```
html_css_files = [
    "https://malachov.github.io/readthedocs-sphinx-alabaster-css/custom.css",
]
```

Also, of course if you want, you can download it and use locally from the project if you need.

The result should look like this

<div align="center"><img src="docs/source/_static/sphinx-alabaster-css.png" width="620" alt="sphinx-alabaster-css"/></div>

## Other projects

There are many other projects, that are in separate repository

### mypythontools_cicd

Module with functionality around Continuous Integration and Continuous Delivery. Locally run tests, regenerate docs,
deploy app or package.

https://github.com/Malachov/mypythontools_cicd

### mylogging

Logging in a very simple way.

https://github.com/Malachov/mylogging

### Docs

Documentation - snippets for various topics.

https://github.com/Malachov/DOCS

### pyvueeel

Application microframework. Develop application really fast.

https://github.com/Malachov/pyvueeel

### project-starter-cookiecutter

Cookiecutter template. Based on type (python package, python / js application) create empty project.

https://github.com/Malachov/project-starter-cookiecutter

### Software-settings

Various settings stored, so can be reused. E.g. starting scripts after fresh operation system install.

https://github.com/Malachov/Software-settings
