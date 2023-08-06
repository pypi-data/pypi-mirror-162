from abc import abstractmethod, ABC
from typing import Any, List, Optional

from ..ast import Element
from .types import (
    Attribute,
    BaseOut,
    BoolOut,
    FloatOut,
    IntOut,
    Schema,
    StringOut,
    parse_schema,
    ArrayOut,
    MapArrayOut,
    MapOut,
    SchemaArgs,
)
from .attribute import Kind
from ..context import register_block


class Block(ABC):
    @property
    @abstractmethod
    def namespace_(self):
        ...

    @abstractmethod
    def generate(self) -> str:
        ...


class AbstractBlock(Schema, Block, ABC):
    def __init__(self, *, args: Optional[SchemaArgs] = None):
        super().__init__(args)

        self._ast: List[Element] = []

        register_block(self)

    def parse(self) -> None:
        if self.args_():
            self._ast.extend(parse_schema(self))

    def ast_(self) -> List[Element]:
        return self._ast

    @property
    @abstractmethod
    def namespace_(self) -> str:
        ...

    def __attrs_post_init__(self):
        super().__attrs_post_init__()

        _prepare_attrs(self, self)


class ConfigurationBlock(AbstractBlock, ABC):
    def __init__(self, *, name: str, args: Optional[SchemaArgs] = None):
        super().__init__(args=args)

        self._name = name

    @property
    def name_(self) -> str:
        return self._name

    @property
    def type_(self) -> str:
        return getattr(self.__class__, "_type")

    @property
    def namespace_(self) -> str:
        return getattr(self.__class__, "_namespace")

    def expr_(self) -> str:
        return f"{self.type_}.{self.name_}"


def _prepare_attrs(schema: Schema, parent: Optional[Schema]):
    for attr in schema.attrs_():
        _set_attr(schema, attr, parent)


def _set_attr(schema: Schema, attr: Attribute, parent: Optional[Schema]):
    out: Optional[BaseOut] = None
    item: Any = None

    if attr.type is str:
        out = StringOut(attr)

    elif attr.type is int:
        out = IntOut(attr)

    elif attr.type is float:
        out = FloatOut(attr)

    elif attr.type is bool:
        out = BoolOut(attr)

    else:
        if issubclass(attr.type, Schema):
            item = attr.type.new()
            _prepare_attrs(item, item)
            out = BaseOut(attr)
            item.set_out_(out)

    if not out:
        return

    if parent:
        out.parent = parent

    if attr.kind == Kind.array:
        a = ArrayOut()
        a.item = item if item else out
        prop = a

    elif attr.kind == Kind.map:
        m = MapOut()
        m.item = item if item else out
        prop = m

    elif attr.kind == Kind.map_array:
        a = MapArrayOut()
        m = MapOut()
        m.item = out
        a.item = m
        prop = a

    else:
        if item:
            prop = item
        else:
            prop = out

    if prop:
        setattr(schema, attr.key, prop)


def is_configuration(c: Any) -> bool:
    return issubclass(c.__class__, ConfigurationBlock)
