from typing import Optional, Union, Dict

from ..lang.decorators import schema, schema_args
from ..lang.types import SchemaArgs, Schema
from ..lang.decorators import arg
from ..lang.terraform import Terraform
from .backend.local import Local
from .backend.remote import Remote
from .backend.s3 import S3


@schema
class RequiredProvider(Schema):
    @staticmethod
    def op_() -> str:
        return "="

    def __init__(
        self,
        *,
        version: str,
        source: str,
    ):
        super().__init__(
            RequiredProvider.Args(
                version=version,
                source=source,
            )
        )

    @schema_args
    class Args(SchemaArgs):
        """
        A version constraint specifying which subset of available provider versions
        the module is compatible with.
        """

        version: str = arg()

        """
        The global source address for the provider you intend to use, such as hashicorp/aws.
        """
        source: str = arg()


@schema
class Settings(Terraform):
    def __init__(
        self,
        *,
        required_providers: Dict[str, RequiredProvider],
        required_version: Optional[str] = None,
        backend: Optional[Union[Local, Remote, S3]] = None,
    ):
        super().__init__(
            args=Settings.Args(
                required_providers=required_providers,
                required_version=required_version,
                backend=backend,
            ),
        )

    @schema_args
    class Args(SchemaArgs):
        """
        Specifies all the providers required by the current module, mapping each local provider
        name to a source address and a version constraint.
        """

        required_providers: Dict[str, RequiredProvider] = arg()

        """
        The required_version setting accepts a version constraint string, which specifies
        which versions of Terraform can be used with your configuration.
        """
        required_version: Optional[str] = arg(default=None)

        """
        The local backend configuration block.
        """
        backend: Optional[Union[Local, Remote, S3]] = arg(default=None)
