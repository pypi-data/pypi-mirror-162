from __future__ import annotations

import inspect
import attr as attrs
from abc import ABC, abstractmethod
from typing import (
    Any,
    Dict,
    Generic,
    List,
    Optional,
    TypeVar,
    Union,
    get_args,
    get_origin,
    cast,
)

from pydash import (
    is_boolean,
    is_empty,
    is_float,
    is_integer,
    is_string,
    trim_end,
)

from .argument import Argument
from .attribute import Attribute
from ..ast import AstArgument, AstArray, AstBoolean, AstMap, AstNumber, AstString, Element


def is_optional(typ: Optional[type]) -> bool:
    return get_origin(typ) is Union and type(None) in get_args(typ)


class Out(ABC):
    @abstractmethod
    def expr_(self) -> str:
        ...

    @property
    @abstractmethod
    def parent(self) -> Optional[Schema]:
        ...


@attrs.define
class BaseOut(Out):
    attr: Attribute

    parent: Optional[Schema] = None
    index: Optional[int] = None
    key: Optional[str] = None

    def expr_(self) -> str:
        expr = self.attr.name

        if self.parent:
            expr = f"{self.parent.expr_()}.{expr}"

        if self.index is not None:
            expr = f"{trim_end(expr)}[{self.index}]"

        if self.key:
            expr = f"{trim_end(expr)}[{self.key}]"

        return expr


class StringOut(BaseOut):
    ...


class IntOut(BaseOut):
    ...


class FloatOut(BaseOut):
    ...


class BoolOut(BaseOut):
    ...


class SchemaArgs:
    def __attrs_post_init__(self):
        if not hasattr(self, "_fields"):
            setattr(self, "_fields", [])

        for item in attrs.fields(self.__class__):
            if "arg" in item.metadata and item.metadata["arg"]:
                if hasattr(self, "_fields"):
                    getattr(self, "_fields").append(Argument(item.name))

    @property
    def fields_(self):
        return getattr(self, "_fields") if hasattr(self, "_fields") else None


class Schema(Out):
    def __init__(self, args: Optional[SchemaArgs] = None):
        super(Schema, self).__init__()

        self._args = args
        self._out: Optional[BaseOut] = None
        self._attrs: List[Attribute] = []

        self.__attrs_init__(**self.required_attrs())  # type: ignore

    def __attrs_post_init__(self):
        for item in attrs.fields(self.__class__):
            if "attr" in item.metadata and item.metadata["attr"]:
                self._attrs.append(
                    Attribute(
                        type=item.metadata["type"],
                        key=item.name,
                        kind=item.metadata["kind"],
                        computed=item.metadata["computed"]
                        if "computed" in item.metadata
                        else False,
                    )
                )

    @property
    def parent(self) -> Optional[Schema]:
        return self._out.parent if self._out else None

    @staticmethod
    def label_() -> Optional[str]:
        return None

    @staticmethod
    def op_() -> str:
        return ""

    def out_(self) -> Optional[BaseOut]:
        return self._out

    def set_out_(self, out: BaseOut):
        self._out = out

    def is_out_(self) -> bool:
        return self._out is not None

    def expr_(self) -> str:
        return self._out.expr_() if self._out else ""

    def attrs_(self) -> List[Attribute]:
        return self._attrs

    def args_(self) -> Optional[SchemaArgs]:
        return self._args

    @classmethod
    def required_attrs(cls):
        params: Dict[str, Any] = {}
        for item in attrs.fields(cls):
            if "attr" in item.metadata and item.metadata["attr"]:
                if not is_optional(item.type):
                    params[item.name] = None
        return params

    @classmethod
    def new(cls):
        return cls(**cls.required_attrs())


def unwrap_out(o: Union[Schema, BaseOut]) -> Optional[BaseOut]:
    return o.out_() if isinstance(o, Schema) else o


T = TypeVar("T", Schema, IntOut, StringOut, FloatOut, BoolOut)


class Collection(Generic[T], Out):
    _item: T

    @property
    def item(self):
        return self._item

    @item.setter
    def item(self, item: T):
        self._item = item

    @property
    def parent(self) -> Optional[Schema]:
        return self._item.parent if self._item else None

    def expr_(self) -> str:
        return self._item.expr_() if self._item else ""


class ArrayOut(Collection[T]):
    def get(self, index: int) -> T:
        out = unwrap_out(self.item)
        if out:
            out.index = index
        return self.item


class MapOut(Collection[T]):
    def get(self, key: str) -> T:
        out = unwrap_out(self.item)
        if out:
            out.key = key
        return self.item


U = TypeVar("U", IntOut, StringOut, FloatOut, BoolOut)


class MapArrayOut(Generic[U]):
    _item: MapOut[U]

    @property
    def item(self):
        return self._item

    @item.setter
    def item(self, item: MapOut[U]):
        self._item = item

    @property
    def parent(self) -> Optional[Schema]:
        return self._item.parent if self._item else None

    def expr_(self) -> str:
        return self._item.expr_() if self._item else ""

    def get(self, index: int) -> MapOut[U]:
        out = cast(BaseOut, self._item.item)
        if out:
            out.index = index
        return self.item


def is_collection(s: Any) -> bool:
    return issubclass(s.__class__, Collection)


def is_schema(s: Any) -> bool:
    return issubclass(s.__class__, Schema)


def is_out(o: Any) -> bool:
    cls = o if inspect.isclass(o) else o.__class__
    if issubclass(cls, Schema):
        return cast(Schema, o).is_out_()

    return issubclass(cls, Out)


def is_schema_array(o: Any) -> bool:
    return isinstance(o, list) and len(o) > 0 and is_schema(o[0])


def is_schema_map(o: Any) -> bool:
    return isinstance(o, dict) and len(o) > 0 and is_schema(next(iter(o.values())))


def parse_schema(value: Schema) -> List[Element]:
    elements: List[Element] = []
    args = value.args_()
    if args is None:
        return []

    fields = args.fields_

    if fields is None or is_empty(fields):
        return elements

    for field in fields:
        v = getattr(args, field.key)
        if v is None:
            continue

        if is_out(v):
            elements.append(AstArgument(field.name, op="=", value=AstString(f"${{{v.expr_()}}}")))

        elif is_schema_array(v):
            elements.extend(parse_array(field.name, v))

        elif is_schema_map(v):
            items = parse_map(v)
            if not is_empty(items):
                elements.append(AstArgument(field.name, op="", value=items))

        elif is_schema(v):
            items = parse_schema(v)
            if not is_empty(items):
                elements.append(AstArgument(field.name, op=v.op_(), value=items, label=v.label_()))

        else:
            item = parse_primitive(v)
            if item:
                elements.append(AstArgument(field.name, op="=", value=item))

    return elements


def parse_array(key: str, value: List[Schema]) -> List[Element]:
    elements: List[Element] = []
    if not value or is_empty(value):
        return elements

    for block in value:
        items = parse_schema(block)
        if not is_empty(items):
            elements.append(AstArgument(key, op="", value=items, label=block.label_()))

    return elements


def parse_map(value: Dict[str, Schema]) -> List[Element]:
    elements: List[Element] = []
    if not value or is_empty(value):
        return elements

    for key, block in value.items():
        items = parse_schema(block)
        if not is_empty(items):
            elements.append(AstArgument(key, op="=", value=items, label=block.label_()))

    return elements


def parse_primitive(value: Any) -> Optional[Element]:
    if is_string(value):
        return AstString(value)

    elif is_integer(value) or is_float(value):
        return AstNumber(value)

    elif is_boolean(value):
        return AstBoolean(value)

    elif isinstance(value, list):
        arr = AstArray()
        for v in value:
            item = parse_primitive(v)
            if item:
                arr.add(item)
        return arr

    elif isinstance(value, dict):
        m = AstMap()
        for k, v in value.items():
            item = parse_primitive(v)
            if item:
                m.set(k, item)
        return m

    return None
