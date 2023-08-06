from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Generic, Hashable, Iterator, TypeVar

T = TypeVar("T")
S = TypeVar("S")
Key = TypeVar("Key", bound=Hashable)


@dataclass(frozen=True)
class RichSet(Generic[T]):
    records: list[T]

    @classmethod
    def from_list(cls, lst: list[T]) -> RichSet[T]:
        return cls(records=lst[:])

    def __iter__(self) -> Iterator[T]:
        return iter(self.records)

    def to_list(self) -> list[T]:
        return self.records[:]

    def get_first(self) -> T | None:
        if self.records:
            return self.records[0]
        return None

    def first(self) -> T:
        if self.records:
            return self.records[0]
        raise IndexError("RichSet is empty")

    def is_empty(self) -> bool:
        return not self.records

    def to_dict(self, key: Callable[[T], Key]) -> dict[Key, T]:
        return {key(r): r for r in self.records}

    def unique(self, key: Callable[[T], Key]) -> RichSet[T]:
        new_records = []
        seen = set()
        for r in self.records:
            key_ = key(r)
            if key_ not in seen:
                new_records.append(r)
                seen.add(key_)
        return RichSet.from_list(new_records)

    def map(self, f: Callable[[T], S]) -> RichSet[S]:
        return RichSet.from_list(list(map(f, self.records)))
