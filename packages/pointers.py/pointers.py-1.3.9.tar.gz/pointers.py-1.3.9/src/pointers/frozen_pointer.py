from .pointer import Pointer
from typing import TypeVar, NoReturn, Any
from .exceptions import IsFrozenError
from _pointers import add_ref

__all__ = ("FrozenPointer", "to_const_ptr")


T = TypeVar("T")


class FrozenPointer(Pointer[T]):
    def assign(self, _: Pointer[T]) -> NoReturn:
        """Point to a different address."""
        raise IsFrozenError("cannot assign to frozen pointer")

    def move(self, _: Pointer[T], __: bool = False) -> NoReturn:
        """Move data from another pointer to this pointer. Very dangerous, use with caution."""  # noqa
        raise IsFrozenError("cannot move data to frozen pointer")

    def set_attr(self, key: str, value: Any) -> NoReturn:
        raise IsFrozenError("cannot set attribute on frozen pointer")


def to_const_ptr(val: T) -> FrozenPointer[T]:
    """Convert a value to a pointer."""
    add_ref(val)
    return FrozenPointer(id(val), type(val))
