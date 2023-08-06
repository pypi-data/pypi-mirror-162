# -*- coding: utf-8 -*-
from __future__ import annotations

from dataclasses import dataclass
from types import TracebackType
from typing import Any, Iterable, Iterator, List, Optional, Tuple, Type


@dataclass(frozen=True)
class ExceptionWrapper:
    exception: Exception
    traceback: TracebackType
    context: Optional[ExceptionCapture.Context] = None

    def with_traceback(self) -> Exception:
        return self.exception.with_traceback(self.traceback)

    def __str__(self) -> str:
        if self.context is not None:
            return f"{self.exception!s} (context: {self.context!s})"
        else:
            return str(self.exception)

    def __repr__(self) -> str:
        if self.context is not None:
            return f"{self.exception!r} in {self.context!r}"
        else:
            return repr(self.exception)


class MultiExceptionWrapper(Exception):
    """ Exception class for encapsulation of multiple exceptions. """

    def __init__(self, exceptions: Iterable[ExceptionWrapper]):
        """ Create an instance of an exception list.

        :param exceptions: iterable of exceptions to store in the list (internally a tuple)
        """
        self._exception_wrappers: Tuple[ExceptionWrapper, ...] = tuple(exceptions)

        Exception.__init__(self, 'Multi-exception wrapper')

    @property
    def exceptions(self) -> Tuple[Exception, ...]:
        """ Access encapsulated exceptions.

        :return: frozen set of encapsulated exceptions
        """
        return tuple(x.exception for x in self._exception_wrappers)

    @property
    def tracebacks(self) -> Tuple[TracebackType, ...]:
        """ Access tracebacks for encapsulated exceptions.

        :return: frozen set of encapsulated tracebacks
        """
        return tuple(x.traceback for x in self._exception_wrappers)

    def __contains__(self, item: Any) -> bool:
        if isinstance(item, type):
            # Test if type (exception class) is in list
            return any(issubclass(type(x), item) for x in self.exceptions)
        else:
            return item in self.exceptions

    def __getitem__(self, item: int) -> ExceptionWrapper:
        return self._exception_wrappers[item]

    def __iter__(self) -> Iterator[Exception]:
        return iter(self.exceptions)

    def __str__(self) -> str:
        if len(self.exceptions) == 1:
            return str(self.exceptions[0])

        return f"{Exception.__str__(self)} (contents: {', '.join(map(str, self.exceptions))})"

    def __repr__(self) -> str:
        if len(self.exceptions) == 1:
            return repr(self.exceptions[0])

        return f"{self.__class__.__name__}({', '.join(map(repr, self.exceptions))})"


class ExceptionCapture:
    class Context:
        def __init__(self, capture: ExceptionCapture, label: str,
                     exception_filter: Optional[Iterable[Type[Exception]]] = None):
            self._capture = capture
            self._label = label

            self._exception_filter: Optional[Tuple[Type[Exception], ...]] = None

            if exception_filter is not None:
                exception_filter_tuple = tuple(exception_filter)

                if len(exception_filter_tuple) > 0:
                    self._exception_filter = exception_filter_tuple

        @property
        def capture(self) -> ExceptionCapture:
            return self._capture

        @property
        def label(self) -> str:
            return self._label

        @property
        def exception_filter(self) -> Optional[Tuple[Type[Exception], ...]]:
            return self._exception_filter

        def __enter__(self) -> ExceptionCapture.Context:
            return self

        def __exit__(self, exc_type: Type[Exception], exc_val: Exception, exc_tb: TracebackType) -> Optional[bool]:
            if exc_val is not None:
                if self.exception_filter is not None and not issubclass(exc_type, self.exception_filter):
                    # Not in filter, don't capture
                    return None

                # Save exception in capture
                self.capture.add(exc_val, exc_tb, context=self)

                # Exception handled!
                return True

            return None

    def __init__(self, exception_filter: Optional[Iterable[Type[Exception]]] = None):
        """

        :param exception_filter:
        """
        self._exception_filter = tuple(exception_filter) if exception_filter is not None else None

        self._exception_buffer: List[ExceptionWrapper] = []

        # Create a root context for when this object is used as a context manager
        self._root_context = self.Context(self, '<root context>', self.exception_filter)

    def add(self, exception: Exception, traceback: TracebackType, context: Optional[ExceptionCapture.Context] = None,
            append: bool = True) -> None:
        """

        :param exception:
        :param traceback:
        :param context:
        :param append: if True append to the end of the buffer, otherwise prepend to beginning of buffer
        """
        wrapped = ExceptionWrapper(exception, traceback, context)

        if append:
            self._exception_buffer.append(wrapped)
        else:
            self._exception_buffer.insert(0, wrapped)

    @property
    def buffer(self) -> Tuple[ExceptionWrapper, ...]:
        return tuple(self._exception_buffer)

    @property
    def exceptions(self) -> Tuple[Exception, ...]:
        return tuple(x.exception for x in self._exception_buffer)

    @property
    def exception_filter(self) -> Optional[Tuple[Type[Exception], ...]]:
        return self._exception_filter

    def raise_buffered(self) -> None:
        """ Raise buffered exceptions.

        """
        if len(self._exception_buffer) == 1:
            # Raise original exception
            raise self._exception_buffer[0].with_traceback()
        elif len(self._exception_buffer) > 1:
            # Raise all exceptions in an exception list
            raise MultiExceptionWrapper(self._exception_buffer)

    def context(self, label: str, exception_filter: Optional[Iterable[Type[Exception]]] = None,
                inherit_filter: bool = True) -> ExceptionCapture.Context:
        """ Create a new context for capture of exceptions. Allows the same capture object to be used multiple times
        with labelled contexts providing means to sort the resulting exceptions.

        :param label: context label
        :param exception_filter: optional iterable of exception types to capture, otherwise capture all
        :param inherit_filter: if True the context will inherit filters of this ExceptionCapture
        :return: new context object linked to this ExceptionCapture
        """
        exception_filter = list(exception_filter) if exception_filter is not None else []

        if inherit_filter and self.exception_filter is not None:
            exception_filter.extend(self.exception_filter)

        return self.Context(self, label, exception_filter)

    def __call__(self, *args: Any, **kwargs: Any) -> ExceptionCapture.Context:
        # Create context when called
        return self.context(*args, **kwargs)

    def __contains__(self, item: Any) -> bool:
        if isinstance(item, type):
            # Test if type (exception class) is in list
            return any(issubclass(type(x), item) for x in self.exceptions)
        else:
            return item in self.exceptions

    def __enter__(self) -> ExceptionCapture.Context:
        # Use root context manager
        return self._root_context.__enter__()

    def __exit__(self, exc_type: Type[Exception], exc_val: Exception, exc_tb: TracebackType) -> Optional[bool]:
        # Pass to root context manager
        return self._root_context.__exit__(exc_type, exc_val, exc_tb)
