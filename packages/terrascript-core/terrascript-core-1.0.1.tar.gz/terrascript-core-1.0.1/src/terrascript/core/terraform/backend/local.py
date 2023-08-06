from typing import Optional

from ...lang.decorators import schema, schema_args
from ...lang.types import Schema, SchemaArgs
from ...lang.decorators import arg


@schema
class Local(Schema):
    def __init__(
        self,
        *,
        path: Optional[str] = None,
        workspace_dir: Optional[str] = None,
    ):
        super().__init__(
            Local.Args(
                path=path,
                workspace_dir=workspace_dir,
            )
        )

    @staticmethod
    def label_() -> Optional[str]:
        return "local"

    @schema_args
    class Args(SchemaArgs):
        """
        The path to the tfstate file. This defaults to "terraform.tfstate" relative to
        the root module by default.
        """

        path: Optional[str] = arg(default=None)

        """
        The path to the tfstate file. This defaults to "terraform.tfstate" relative to
        the root module by default.
        """
        workspace_dir: Optional[str] = arg(default=None)
