

import math
import sys
from types import GenericAlias
from typing import Any, Iterable, Iterator, Sequence, SupportsIndex, TypeVar, Union, overload


T = TypeVar("T", covariant=True)
S = TypeVar("S")
Self = TypeVar("Self")


class EmptyType():
    ...

EMPTY = EmptyType()


class FrozenList(Sequence[T]):

    @overload
    def __init__(self) -> None: ...

    @overload
    def __init__(self, __iterable: Iterable[T]) -> None: ...

    def __init__(self, __iterable: Union[EmptyType, Iterable[T]] = EMPTY) -> None:
        if __iterable is not EMPTY:
            self._list = list(__iterable)
        else:
            self._list = list()

    def copy(self: Self) -> Self:
        return type(self)(self._list)

    def index(self, __value: T, __start: SupportsIndex = 0, __stop: SupportsIndex = math.inf) -> int:
        if __start is EMPTY:
            return self._list.index(__value)
        if __stop is EMPTY:
            return self._list.index(__value, __start)
        return self._list.index(__value, __start, __stop)

    def count(self, __value: T) -> int:
        return self._list.count(__value)

    def __len__(self) -> int:
        return len(self._list)

    def __iter__(self) -> Iterator[T]:
        return iter(self._list)

    def __hash__(self) -> int:
        return sum(hash(elem) for elem in self)

    @overload
    def __getitem__(self: Self, __i: SupportsIndex) -> T: ...
    @overload
    def __getitem__(self: Self, __s: slice) -> Self: ...
    @overload

    def __getitem__(self: Self, __item: Union[SupportsIndex, slice]) -> Union[T, Self]:
        if isinstance(__item, slice):
            return type(self)(self._list[__item])
        else:
            return self._list[__item]

    @overload
    def __add__(self, __x: "Sequence[T]") -> "FrozenList[T]": ...
    @overload
    def __add__(self, __x: "Sequence[S]") -> "FrozenList[Union[S, T]]": ...

    def __add__(self, __x: Union["Sequence[T]", "Sequence[S]"]) -> Union["FrozenList[T]", "FrozenList[Union[S, T]]"]:
        return FrozenList(self._list + list(__x))

    def __mul__(self: Self, __n: SupportsIndex) -> Self:
        return type(self)(self._list * __n)

    def __rmul__(self: Self, __n: SupportsIndex) -> Self:
        return type(self)(self._list * __n)

    def __contains__(self, __o: object) -> bool:
        return __o in self._list

    def __reversed__(self) -> Iterator[T]:
        return reversed(self._list)

    def __gt__(self, __x: list[T]) -> bool: ...
    def __ge__(self, __x: list[T]) -> bool: ...
    def __lt__(self, __x: list[T]) -> bool: ...
    def __le__(self, __x: list[T]) -> bool:


    def __eq__(self, __x: Sequence[T]) -> bool:
        if isinstance(__x, Sequence):
            if len(self) != len(__x):
                return False
            else:
                return all(a == b for a, b in zip(self, __x))
        else:
            return NotImplemented

    if sys.version_info >= (3, 9):

        def __class_getitem__(cls, __item: Any) -> GenericAlias:
            return cls
