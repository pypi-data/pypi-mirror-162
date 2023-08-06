import attr as attrs
from enum import Enum
from typing import Optional
from functools import cached_property


class Kind(str, Enum):
    object = "object"
    array = "array"
    map = "map"
    map_array = "map_array"


@attrs.define
class Attribute:
    type: type = attrs.ib(kw_only=True)
    key: str = attrs.ib(kw_only=True)
    kind: Kind = attrs.ib(kw_only=True, default=Kind.object)
    computed: bool = attrs.ib(kw_only=True, default=False)
    alias: Optional[str] = attrs.ib(kw_only=True, default=None)

    @property
    def name(self):
        return self.alias if self.alias else self.key

    @cached_property
    def is_optional(self) -> bool:
        from .types import is_optional

        return is_optional(self.type)

    @property
    def is_collection(self):
        return self.kind in (Kind.map, Kind.array)
