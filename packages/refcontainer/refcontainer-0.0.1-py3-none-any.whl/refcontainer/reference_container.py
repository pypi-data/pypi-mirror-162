# std
from dataclasses import dataclass
from typing import Any
# local
from .strong_generic import T, StrongGeneric


class ReadOnlyError(TypeError):
    pass


@dataclass
class Ref(StrongGeneric[T]):
    def __init__(self, value: T = ...):  # type: ignore
        self.__is_read_only = False
        if value is not Ellipsis:
            self.current = value

    @classmethod
    def readonly(cls, value: T):
        x = cls()
        x.engrave(value)
        return x

    @property
    def current(self):
        return self.__v

    @current.setter
    def current(self, value: T):
        if self.__is_read_only:
            raise ReadOnlyError
        self.__check_type(value)
        self.__v = value

    def engrave(self, value: T):
        self.current = value
        self.__is_read_only = True

    def clear(self):
        if self.__is_read_only:
            raise ReadOnlyError
        try:
            del self.__v
        except AttributeError:
            pass

    def __check_type(self, value: T):
        try:
            if not self.__type_ok(value):
                raise TypeError
        except AttributeError:
            self._set_type_constrainst(type(value))

    def __type_ok(self, value: T):
        return self._type_constraints() is Any or isinstance(value, self._type_constraints())
