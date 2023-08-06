"""Module with functions for 'config' subpackage."""

from __future__ import annotations
from typing import Any, TypeVar, Union
from copy import deepcopy
import argparse
import sys
from dataclasses import dataclass
from typing import Generic

from typeguard import check_type
from typing_extensions import get_args, get_type_hints, Literal  # pylint: disable=unused-import

from ..property import MyProperty, MyPropertyClass  # pylint: disable=unused-import
from .. import misc
from .. import types

module_globals = globals()

ConfigType = TypeVar("ConfigType", bound="Config")


class ConfigMeta(type):
    """Config metaclass changing config init function.

    Main reason is for being able to define own __init__ but
    still has functionality from parent __init__ that is necessary. With this meta, there is no need
    to use super().__init__ by user.

    As user, you probably will not need it.
    """

    def __init__(cls, name, bases, dct) -> None:
        """Wrap subclass object __init__ to provide Config functionality."""
        type.__init__(cls, name, bases, dct)

        # Avoid base classes here and wrap only user class init
        if name == "Config" and not bases:
            return

        def add_parent__init__(
            self: Config,
            frozen=None,
            *a,
            **kw,
        ):

            self.config_fields = ConfigFields(
                base_config_map={},
                myproperties_list=[],
                vars=[],
                properties_list=[],
                subconfigs=[],
                types=types.get_type_hints(type(self), globalns=module_globals),
            )
            self.do = ConfigDo()
            self.do.setup(config=self)

            # Call user defined init
            cls._original__init__(self, *a, **kw)

            self.do.internal_propagate_config()

            if frozen is None:
                self.config_fields.frozen = True
            else:
                self.config_fields.frozen = frozen

        cls._original__init__ = cls.__init__
        cls.__init__ = add_parent__init__  # type: ignore

    def __getitem__(cls, key):
        """To be able to access attributes also on class for example for documentation."""
        return getattr(cls, key)


class ConfigDo(Generic[ConfigType]):
    def __init__(self) -> None:
        self.config: ConfigType

    def setup(self, config: ConfigType) -> None:
        self.config: ConfigType = config

    def internal_propagate_config(self) -> None:
        """Provide transferring arguments from base or from sub configs.

        Config class has subconfigs. It is possible to access subconfigs attributes from main config or from
        any other level because of this recursive function.
        """
        frozen = self.config.config_fields.frozen
        self.config.config_fields.frozen = False

        for i, j in vars(self.config).items():
            if i.startswith("_") or (not isinstance(j, Config) and callable(j)):
                continue

            # i is iterated subconfig and self.config is higher level config
            if isinstance(j, Config):
                self.config.config_fields.subconfigs.append(j)
                self.config.config_fields.base_config_map.update(j.config_fields.base_config_map)
                j.config_fields.base_config_map = self.config.config_fields.base_config_map

        for i, j in vars(type(self.config)).items():
            if i.startswith("_"):
                continue

            if isinstance(j, property):
                if isinstance(j, MyPropertyClass):
                    self.config.config_fields.myproperties_list.append(i)
                    # Create private variables (e.g. _variable) with content
                    setattr(
                        self.config,
                        j.private_name,
                        j.init_function,
                    )
                else:
                    self.config.config_fields.properties_list.append(i)

            if i not in ["config_fields", "do"] and not callable(i) and not isinstance(j, type):
                self.config.config_fields.vars.append(i)
                self.config.config_fields.base_config_map[i] = self.config

        self.config.config_fields.frozen = frozen

    def copy(self) -> ConfigType:
        """Create deep copy of config and all it's attributes.

        Returns:
            ConfigType: Deep copy.
        """
        frozen = self.config.config_fields.frozen
        copy = deepcopy(self.config)
        self.config.config_fields.frozen = frozen
        return copy

    def update(self, content: dict) -> None:
        """Bulk update with dict values.

        Args:
            content (dict): E.g {"arg_1": "value"}

        Raises:
            AttributeError: If some arg not found in config.
        """
        for i, j in content.items():
            setattr(self.config, i, j)

    def get_dict(self, recursively: bool = True) -> dict:
        """Get flat dictionary with it's values.

        Args:
            recursively (bool, optional): If True, then values from subconfigurations will be also in result.

        Returns:
            dict: Flat config dict.
        """

        dict_of_values = {
            # Values from vars
            **{key: getattr(self.config, key) for key in self.config.config_fields.vars},
            # Values from myproperties
            **{key: getattr(self.config, key) for key in self.config.config_fields.myproperties_list},
            # Values from properties
            **{key: getattr(self.config, key) for key in self.config.config_fields.properties_list},
        }

        if recursively:
            # From sub configs
            for i in self.config.config_fields.subconfigs:
                dict_of_values.update(i.do.get_dict())

        return dict_of_values

    def with_argparse(self, about: str | None = None) -> None:
        """Parse sys.argv flags and update the config.

        For using with CLI. When using `with_argparse` method.

        1) Create parser and add all arguments with help
        2) Parse users' sys args and update config ::

            config.do.with_argparse()

        Now you can use in terminal like. ::

            python my_file.py --config_arg config_value

        Only basic types like int, float, str, list, dict, set are possible as eval for using type like numpy
        array or pandas DataFrame could be security leak.

        Args:
            about (str, optional): Description used in --help. Defaults to None.

        Raises:
            SystemExit: If arg that do not exists in config.

        Note:
            If using boolean, you must specify the value. Just occurrence, e.g. `--my_arg` is not True. so you
            need to use `--my_arg True`.
        """
        if len(sys.argv) <= 1 or misc.GLOBAL_VARS.jupyter:
            return

        # Add settings from command line if used
        parser = argparse.ArgumentParser(usage=about)

        config_dict = self.get_dict()

        for i in config_dict.keys():
            try:
                help_str = type(self.config)[i].__doc__
            except AttributeError:
                help_str = type(self.config.config_fields.base_config_map[i])[i].__doc__

            parser.add_argument(f"--{i}", help=help_str)

        try:
            parsed_args = parser.parse_known_args()
        except SystemExit as err:
            if err.code == 0:
                sys.exit(0)

            raise SystemExit(
                f"Config args parsing failed. Used args {sys.argv}. Check if args and values are correct "
                "format. Each argument must have just one value. Use double quotes if spaces in string. "
                "For dict e.g. \"{'key': 666}\". If using bool, there has to be True or False."
            ) from err

        if parsed_args[1]:
            raise RuntimeError(
                f"Config args parsing failed on unknown args: {parsed_args[1]}."
                "It may happen if variable not exists in config."
            )

        # Non empty command line args
        parser_args_dict = {}

        # All variables are parsed as strings
        # If it should not be string, infer type
        for i, j in parsed_args[0].__dict__.items():

            if j is None:
                continue

            try:
                used_type = type(self.config)[i].allowed_types
            except AttributeError:
                used_type = type(self.config.config_fields.base_config_map[i])[i].allowed_types

            if used_type is not str:
                try:
                    # May fail if for example Litera["string1", "string2"]
                    parser_args_dict[i] = types.str_to_infer_type(j)
                except ValueError:
                    parser_args_dict[i] = j
                except Exception as err:
                    union_types = [type(Union[str, float])]
                    try:
                        from types import UnionType

                        union_types.append(UnionType)
                    except ImportError:
                        pass

                    # UnionType stands for new Union | syntax
                    if type(used_type) in union_types and str in get_args(used_type):
                        parser_args_dict[i] = j
                    else:
                        raise RuntimeError(
                            f"Type not inferred error. Config option {i} type was not inferred and it cannot "
                            "be a string. Only literal_eval is used in type inferring from CLI parsing. "
                            "If you need more complex types like numpy array, try to use it directly from "
                            "python."
                        ) from err
            else:
                parser_args_dict[i] = j

        self.update(parser_args_dict)


@dataclass
class ConfigFields:
    """Attributes of config class. The reason why it is separated is, that usually config values are the most
    important for user. This would make namespace big and intellisense would not worked as expected.
    """

    frozen = False
    """Usually this config is created from someone else that user using this config. Therefore new attributes
    should not be created. It is possible to force it (raise error). It is possible to set frozen to False
    to enable creating new attributes.
    """

    base_config_map: dict
    """You can access attribute from subconfig as well as from main config object, there is proxy mapping
    config dict. If attribute not found on defined object, it will search through this proxy. It's
    populated automatically in metaclass during init.
    """

    types: dict
    """Attribute types used for type validations."""

    vars: list
    """Simple variables."""

    myproperties_list: list
    """List of all custom properties"""

    properties_list: list
    """List of all properties (variables, that can have some getters and setters)."""

    subconfigs: list
    """List of subconfigurations."""


class Config(metaclass=ConfigMeta):  # type: ignore
    """Main config class.

    You can find working examples in module docstrings.
    """

    config_fields: ConfigFields

    def __init_subclass__(cls) -> None:
        # It would be better to define do on instance level and not class as class variable, but this is the
        # only way I found to have type hints in do methods. It is necessary to pass instance with do.setup
        cls.do: ConfigDo[cls]

    def __new__(cls, *args, **kwargs):
        """Just control that class is subclassed and not instantiated."""
        if cls is Config:
            raise TypeError("Config is not supposed to be instantiated only to be subclassed.")
        return object.__new__(cls, *args, **kwargs)

    def __deepcopy__(self, memo):
        """Provide copy functionality."""
        cls = self.__class__
        result = cls.__new__(cls)
        # result.do.setup(result)
        memo[id(self)] = result
        for i, j in self.__dict__.items():
            if isinstance(j, staticmethod):
                atr = j.__func__
            else:
                atr = j
            object.__setattr__(result, i, deepcopy(atr, memo))
        return result

    def __getattr__(self, name: str):
        """Control logic if attribute from other subconfig is used."""
        try:
            return getattr(self.config_fields.base_config_map[name], name)

        except KeyError:

            if name not in [
                "_pytestfixturefunction",
                "__wrapped__",
                "pytest_mock_example_attribute_that_shouldnt_exist",
                "__bases__",
                "__test__",
            ]:

                raise AttributeError(f"Variable '{name}' not found in config.") from None

    def __setattr__(self, name: str, value: Any) -> None:
        """Setup new config values. Define logic when setting attributes from other subconfig class."""
        if (
            name == "config_fields"
            or not self.config_fields.frozen
            or name
            in [
                *self.config_fields.vars,
                *self.config_fields.myproperties_list,
                *self.config_fields.properties_list,
            ]
        ):
            if name != "config_fields" and name in self.config_fields.types:
                check_type(expected_type=self.config_fields.types[name], value=value, argname=name)

            object.__setattr__(self, name, value)

        elif name in self.config_fields.base_config_map:
            setattr(
                self.config_fields.base_config_map[name],
                name,
                value,
            )

        else:
            raise AttributeError(
                f"Object {str(self)} is frozen. New attributes cannot be set and attribute '{name}' "
                "not found. Maybe you misspelled name. If you really need to change the value, set "
                "attribute frozen to false."
            )

    def __getitem__(self, key):
        """To be able to be able to use same syntax as if using dictionary."""
        return getattr(self, key)

    def __setitem__(self, key, value):
        """To be able to be able to use same syntax as if using dictionary."""
        setattr(self, key, value)

    def __call__(self, *args: Any, **kwds) -> None:
        """Just to be sure to not be used in unexpected way."""
        raise TypeError("Class is not supposed to be called. Just inherit it to create custom config.")
