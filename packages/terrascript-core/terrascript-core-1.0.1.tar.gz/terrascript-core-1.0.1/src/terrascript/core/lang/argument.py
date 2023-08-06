import attr as attrs
from typing import Optional


@attrs.define
class Argument:
    key: str
    alias: Optional[str] = attrs.ib(default=None, kw_only=True)

    @property
    def name(self):
        return self.alias if self.alias else self.key
