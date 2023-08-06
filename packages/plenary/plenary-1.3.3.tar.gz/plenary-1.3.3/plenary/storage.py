# -*- coding: utf-8 -*-
from abc import ABCMeta, abstractmethod
from collections import OrderedDict
from typing import (Any, Generic, Iterable, Iterator, MutableMapping, Optional,
                    TypeVar, Union)

__all__ = [
    'TRegistryEntry',
    'RegistryEntry',
    'Registry'
]


TRegistryEntry = TypeVar('TRegistryEntry', bound='RegistryEntry')


class RegistryEntry(metaclass=ABCMeta):
    """ Interface for classes capable of storage within a Registry. """

    @property
    @abstractmethod
    def registry_key(self) -> Union[str, Iterable[str]]:
        """ Get the unique identifier for this object when placed in a Registry. Must be a valid Python attribute name
        (i.e. no special characters except '_', preferably lower case).

        :return: registry key string
        """
        pass


class Registry(Generic[TRegistryEntry]):
    """ Registry of instantiated classes. """

    def __init__(self, initial: Optional[Iterable[TRegistryEntry]] = None):
        """ Create a new registry, optionally populated with provided objects.

        :param initial: iterable of objects subclassing RegistryEntry for initial population
        """
        object.__init__(self)

        self._registry: MutableMapping[str, TRegistryEntry] = OrderedDict()

        if initial is not None:
            self.register_all(initial)

    def __contains__(self, item: Any) -> bool:
        return self._safe_key(item) in self._registry

    def __getitem__(self, item: Any) -> TRegistryEntry:
        return self._registry[self._safe_key(item)]

    def __setitem__(self, key: Any, value: Any) -> None:
        raise NotImplementedError('Add items to registry using Registry.register() method')

    def __getattr__(self, item: Any) -> TRegistryEntry:
        return self[item]

    def __iter__(self) -> Iterator[TRegistryEntry]:
        return iter(self._registry.values())

    def register(self, item: TRegistryEntry) -> None:
        """ Register an instance with the Registry.

        :param item: object subclassing RegistryEntry
        """
        if not isinstance(item, RegistryEntry):
            raise ValueError()

        key = item.registry_key

        if not isinstance(key, str) and hasattr(key, '__iter__'):
            for key_instance in key:
                self._registry[self._safe_key(key_instance)] = item
        else:
            self._registry[self._safe_key(key)] = item

    def register_all(self, item_iter: Iterable[TRegistryEntry]) -> None:
        """ Register all items in an iterable with the registry.

        :param item_iter: iterable of objects subclassing RegistryEntry
        """
        for item in item_iter:
            self.register(item)

    def sort(self) -> None:
        """ Sort items in registry by key.

        """
        self._registry = OrderedDict(sorted(self._registry.items(), key=lambda x: x[0]))

    @classmethod
    def _safe_key(cls, x: Any) -> str:
        """ Generate a safe key from arbitrary input.

        :param x: input
        :return: Registry compatible key
        """
        return str(x).replace(' ', '_').replace('-', '_').lower()
