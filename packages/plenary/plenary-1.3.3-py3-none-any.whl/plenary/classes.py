# -*- coding: utf-8 -*-
import functools
import sys
from importlib import import_module
from inspect import isabstract
from pkgutil import walk_packages
from types import ModuleType
from typing import Any, List, Mapping, Type, TypeVar, Union

__all__ = [
    'TObject',
    'get_subclasses',
    'reference_from_str',
    'instance_from_dict',
    'resolve_global'
]


TObject = TypeVar('TObject', bound=object)


def _recurse_subclasses(subclass_list: List[Type[TObject]]) -> List[Type[TObject]]:
    return_list = []

    for subclass in subclass_list:
        if len(subclass.__subclasses__()) > 0:
            return_list.extend(_recurse_subclasses(subclass.__subclasses__()))

            if not isabstract(subclass):
                return_list.append(subclass)
        else:
            return_list.append(subclass)

    return return_list


def get_subclasses(class_root: Type[TObject]) -> List[Type[TObject]]:
    """ Get a list of subclasses for a given parent class.

    :param class_root: parent class type
    :return: list
    """
    return _recurse_subclasses([class_root])


def import_submodules(package: Union[str, ModuleType], recursive: bool = True) -> None:
    """ Import all submodules within a given package.

    :param package: base package to begin import from
    :param recursive: if True then import submodules
    """
    if isinstance(package, str):
        package = import_module(package)

    for loader, name, is_pkg in walk_packages(package.__path__):
        full_name = package.__name__ + '.' + name

        import_module(full_name)

        if recursive and is_pkg:
            import_submodules(full_name)


def reference_from_str(name: str, parent: Any) -> Any:
    """ Get a class from a given module given the classes name as a string.

    :param name:
    :param parent:
    :return:
    """
    if type(parent) is str:
        try:
            parent = sys.modules[parent]
        except KeyError:
            raise KeyError(f"Module {parent} is not available")

    return functools.reduce(getattr, name.split('.'), parent)


def instance_from_dict(config: Mapping[str, Any], parent: Any) -> Any:
    """ Instantiate a class from a given module given a dict containing the class name as a value in the dict.

    :param config: Object description as a dict, requires at least a value for 'class'
    :param parent: Parent module of class
    :return: class instance
    """
    # Create mutable copy of configuration
    config = dict(config)

    if 'class' in config:
        class_name = config.pop('class')

        class_type = reference_from_str(class_name, parent)
        return class_type(**config)
    elif 'method' in config:
        method_name = config.pop('method')

        return reference_from_str(method_name, parent)
    else:
        raise KeyError('Configuration dictionary requires either "class" or "method" key')


def resolve_global(name: str) -> Any:
    """ Resolve a global method, class or module name, importing as required.

    :param name:
    :return:
    """
    # Split name
    name_split = name.split('.')

    # Find root object
    obj_name = name_split.pop(0)
    obj = __import__(obj_name)

    while len(name_split) > 0:
        attr_name = name_split.pop(0)
        obj_name = obj_name + '.' + attr_name

        try:
            obj = getattr(obj, attr_name)
        except AttributeError:
            # Attempt to import module if not already imported
            __import__(obj_name)
            obj = getattr(obj, attr_name)

    return obj
