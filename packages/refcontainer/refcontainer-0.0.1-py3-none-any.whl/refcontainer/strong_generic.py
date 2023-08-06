# type: ignore
from typing import Generic, Type, TypeVar


T = TypeVar('T')


class StrongGeneric(Generic[T]):
    def __class_getitem__(cls, params: Type[T]):
        cls._set_type_constrainst(params)
        return super().__class_getitem__(params)

    @classmethod
    def _type_constraints(cls) -> Type[T]:
        raise AttributeError

    @classmethod
    def _set_type_constrainst(cls, params: Type[T]):
        def f(*a, **kw):
            return params
        cls._type_constraints = f
