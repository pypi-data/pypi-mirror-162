from typing import Optional

from ..lang.decorators import schema, schema_args
from ..lang.provider import Provider as Base
from ..lang.types import SchemaArgs
from ..lang.decorators import arg


@schema
class Provider(Base):
    ...

    @schema_args
    class Args(SchemaArgs):
        """
        Provider alias
        """

        alias: Optional[str] = arg(default=None)

        """
        Provider version
        """
        version: Optional[str] = arg(default=None)
