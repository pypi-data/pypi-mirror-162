import attr as attrs
from typing import Optional, Any

from .attribute import Kind


def attr(
    type: type,
    *,
    alias: Optional[str] = None,
    kind: Kind = Kind.object,
    computed: bool = False,
    default: Any = attrs.NOTHING,
):
    return attrs.ib(
        default=default,
        metadata={
            "attr": True,
            "alias": alias,
            "type": type,
            "kind": kind,
            "computed": computed,
        },
        kw_only=True,
    )


def arg(*, default: Any = attrs.NOTHING):
    return attrs.ib(default=default, kw_only=True, metadata={"arg": True})


def schema(cls):
    return attrs.define(cls, init=False)


def schema_args(cls):
    return attrs.define(cls)


def configuration(
    maybe_cls=None,
    type: str = "",
    namespace: str = "",
):
    def wrap(cls):
        setattr(cls, "_type", type)
        setattr(cls, "_namespace", namespace)

        return attrs.define(cls, init=False)

    if maybe_cls is None:
        return wrap

    return wrap(maybe_cls)


def provider(
    maybe_cls=None,
    name: str = "",
):
    def wrap(cls):
        setattr(cls, "_name", name)

        return attrs.define(cls, init=False)

    if maybe_cls is None:
        return wrap

    return wrap(maybe_cls)


data = configuration
resource = configuration
