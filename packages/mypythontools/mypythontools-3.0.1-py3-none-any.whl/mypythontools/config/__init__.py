"""This is not module that configure library mypythontools, but module that help create config
for your project.

What
====

1) Simple and short syntax.
2) Ability to have docstrings on variables (not dynamically, so visible in IDE) and good for sphinx docs.
3) Type checking and Literal checking via MyProperty.
4) Also function evaluation from other config values (not only static value stored).
5) Options hierarchy (nested options).


Examples:
=========

    By default, config are type validated, so if you configure bad type, error will be raised. You can define
    variables as usual, or can use property for using setters for dynamic behavior. It's recommended to use
    'MyProperty' as it's type validated and there is no need for defining getter.
    
    >>> from __future__ import annotations
    >>> from typing_extensions import Literal
    ...
    >>> class SimpleConfig(Config):
    ...
    ...     simple_var: Literal[1, 2, 3] = 1  # Variables are validated including Unions and Literal
    ...     '''You can document it like this'''
    ...
    ...     @MyProperty
    ...     def dynamic_var(self) -> int:  # Type hints are validated.
    ...         '''
    ...         Type:
    ...             int
    ...
    ...         Default:
    ...             123
    ...
    ...         This is docstrings (also visible in IDE, because not defined dynamically).
    ...         Also visible in Sphinx documentation. It's recommended to document a type for sphinx docs.'''
    ...
    ...         return self.simple_var + 10  # This is default value that can be edited.
    ...
    >>> config = SimpleConfig()
    >>> config.simple_var
    1
    >>> config.simple_var = 2
    >>> config.simple_var
    2
    >>> config['simple_var']  # You can also access params as in a dictionary
    2
    >>> config.simple_var = "String is problem"  # doctest: +3.8
    Traceback (most recent call last):
    TypeError: ...
    ...
    >>> config.simple_var = 4  # Literal is also validated  # doctest: +3.8
    Traceback (most recent call last):
    TypeError: ...
    ...
    >>> config.simple_var = 2  # Restoring value as on 3.7 it's no validated, so test would fails
    >>> config.dynamic_var
    12

    You can still setup a function (or lambda expression) as a new value
    and returned value still will be validated

    >>> config.dynamic_var = lambda self: self.simple_var + 100
    >>> config.dynamic_var
    102 
    >>> config.dynamic_var = lambda self: "String is problem"  # doctest: +3.8
    Traceback (most recent call last):
    TypeError: ...

This is how help looks like in VS Code

.. image:: /_static/intellisense.png
    :width: 620
    :alt: intellisense
    :align: center


Hierarchical config
-------------------

It is possible to use another config object as a value in config and thus hierarchical configs can be created.

Note:
    Use unique values for all config variables even if they are in various subconfig!

>>> from mypythontools.config import MyProperty, Config as ConfigBase
...
>>> class Config(ConfigBase):
...     def __init__(self) -> None:
...         self.subconfig1 = self.SubConfiguration1()
...         self.subconfig2 = self.SubConfiguration2()
...
...     class SubConfiguration1(ConfigBase):
...         def __init__(self) -> None:
...             self.subsubconfig = self.SubSubConfiguration()
...
...         class SubSubConfiguration(ConfigBase):
...
...             value1: Literal[0, 1, 2, 3] = 3
...
...             @MyProperty
...             def subconfig_value(self):
...                 return self.value1 + 1
...
...     class SubConfiguration2(ConfigBase):
...         @MyProperty
...         def other_val(self):
...             return self.subconfig_value + 1
...
...     # Also main category can contain values itself
...     value3: int = 3
...
>>> config = Config()
...
>>> config.subconfig1.subsubconfig.subconfig_value
4

You can access value from config as well as from subcategory

>>> config.subconfig_value
4

Copy
----

Sometimes you need more instances of settings and you need copy of existing configuration.
Copy is deepcopy by default.

>>> config2 = config.do.copy()
>>> config2.value3 = 0
>>> config2.value3
0
>>> config.value3
3

Bulk update
-----------

Sometimes you want to update many values with flat dictionary.

>>> config.do.update({'value3': 2, 'value1': 0})
>>> config.value3
2
>>> config.do.update({"not_existing": "Should fail"})
Traceback (most recent call last):
AttributeError: ...

Get flat dictionary
-------------------

There is a function that will export all the values to the flat dictionary (no dynamic anymore, just values).

>>> flattened = config.do.get_dict()
>>> flattened
{'value3': 2, 'value1': 0, 'subconfig_value': 1, 'other_val': 2}

>>> another_config = Config()
>>> another_config.do.update(flattened)
>>> another_config.subconfig1.subsubconfig.value1
0

Convert dict (or JSON) back to config

Reset
-----
You can reset to default values like this

>>> config = Config()
>>> config.value1
3

CLI
---
CLI is provided by argparse. When using `with_argparse` method, it will

1) Create parser and add all arguments with help
2) Parse users' sys args and update config

::

    config.do.with_argparse()

Now you can use in terminal like.

::

    python my_file.py --value1 12


Only basic types like int, float, str, list, dict, set are possible as eval for using type like numpy
array or pandas DataFrame could be security leak if eval would be used.

Lists and tuples put inside brackets so it's not taken as more parameters.

Setter
======

If you need extra logic in setters, use normal property or implement custom descriptors.

Sphinx docs
===========

If you want to have documentation via sphinx, you can add this to conf.py::

    napoleon_custom_sections = [
        ("Types", "returns_style"),
        ("Type", "returns_style"),
        ("Options", "returns_style"),
        ("Default", "returns_style"),
        ("For example", "returns_style"),
    ]

Here is example

.. image:: /_static/config_on_sphinx.png
    :width: 620
    :alt: config_on_sphinx
    :align: center
"""
# Because of doctest
from __future__ import annotations

from mypythontools.config.config_internal import Config
from mypythontools.property import MyProperty

__all__ = ["Config", "MyProperty"]
