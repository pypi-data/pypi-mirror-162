import attr as attrs
from typing import (
    Tuple,
    Callable,
    Any,
    TypeVar,
    Union,
    Optional,
)
from .attribute import Kind

_T = TypeVar("_T")

def __dataclass_transform__(
    *,
    eq_default: bool = True,
    order_default: bool = False,
    kw_only_default: bool = False,
    field_descriptors: Tuple[Union[type, Callable[..., Any]], ...] = (()),
) -> Callable[[_T], _T]: ...
def schema(cls): ...
@__dataclass_transform__(field_descriptors=(attrs.attrib, attrs.field))
def schema_args(cls): ...
@__dataclass_transform__(field_descriptors=(attrs.attrib, attrs.field))
def attr(
    type: type,
    *,
    alias: Optional[str] = None,
    kind: Kind = Kind.object,
    computed: bool = False,
    default: Any = attrs.NOTHING,
): ...
@__dataclass_transform__(field_descriptors=(attrs.attrib, attrs.field))
def arg(*, default: Any = attrs.NOTHING): ...
@__dataclass_transform__(field_descriptors=(attrs.attrib, attrs.field))
def configuration(
    maybe_cls=None,
    type: str = "",
    namespace: str = "",
): ...
@__dataclass_transform__(field_descriptors=(attrs.attrib, attrs.field))
def provider(
    maybe_cls=None,
    name: str = "",
): ...

data = configuration
resource = configuration
