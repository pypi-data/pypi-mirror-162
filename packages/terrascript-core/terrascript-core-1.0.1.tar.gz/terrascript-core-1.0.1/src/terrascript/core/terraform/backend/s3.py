from typing import Optional, List, Dict

from ...lang.decorators import schema, schema_args
from ...lang.types import Schema, SchemaArgs
from ...lang.decorators import arg


@schema
class S3(Schema):
    def __init__(
        self,
        *,
        region: str,
        access_key: Optional[str] = None,
        secret_key: Optional[str] = None,
        iam_endpoint: Optional[str] = None,
        max_retries: Optional[int] = None,
        profile: Optional[str] = None,
        share_credentials_file: Optional[str] = None,
        skip_credentials_validation: Optional[bool] = None,
        skip_region_validation: Optional[bool] = None,
        skip_metadata_api_check: Optional[bool] = None,
        sts_endpoint: Optional[str] = None,
        token: Optional[str] = None,
        assume_role_duration_seconds: Optional[int] = None,
        assume_role_policy: Optional[str] = None,
        assume_role_policy_arns: Optional[List[str]] = None,
        assume_role_tags: Optional[Dict[str, str]] = None,
        assume_role_transitive_tag_keys: Optional[List[str]] = None,
        external_id: Optional[str] = None,
        role_arn: Optional[str] = None,
        session_name: Optional[str] = None,
        bucket: str,
        key: str,
        acl: Optional[str] = None,
        encrypt: Optional[bool] = None,
        endpoint: Optional[str] = None,
        force_path_style: Optional[bool] = None,
        kms_key_id: Optional[str] = None,
        sse_customer_key: Optional[str] = None,
        workspace_key_prefix: Optional[str] = None,
        dynamo_db_endpoint: Optional[str] = None,
        dynamo_db_table: Optional[str] = None,
    ):
        super().__init__(
            S3.Args(
                region=region,
                access_key=access_key,
                secret_key=secret_key,
                iam_endpoint=iam_endpoint,
                max_retries=max_retries,
                profile=profile,
                share_credentials_file=share_credentials_file,
                skip_credentials_validation=skip_credentials_validation,
                skip_region_validation=skip_region_validation,
                skip_metadata_api_check=skip_metadata_api_check,
                sts_endpoint=sts_endpoint,
                token=token,
                assume_role_duration_seconds=assume_role_duration_seconds,
                assume_role_policy=assume_role_policy,
                assume_role_policy_arns=assume_role_policy_arns,
                assume_role_tags=assume_role_tags,
                assume_role_transitive_tag_keys=assume_role_transitive_tag_keys,
                external_id=external_id,
                role_arn=role_arn,
                session_name=session_name,
                bucket=bucket,
                key=key,
                acl=acl,
                encrypt=encrypt,
                endpoint=endpoint,
                force_path_style=force_path_style,
                kms_key_id=kms_key_id,
                sse_customer_key=sse_customer_key,
                workspace_key_prefix=workspace_key_prefix,
                dynamo_db_endpoint=dynamo_db_endpoint,
                dynamo_db_table=dynamo_db_table,
            )
        )

    @staticmethod
    def label_() -> Optional[str]:
        return "s3"

    @schema_args
    class Args(SchemaArgs):
        """
        AWS Region of the S3 Bucket.
        """

        region: str = arg()

        """
        AWS access key. If configured, must also configure secret_key.
        """
        access_key: Optional[str] = arg(default=None)

        """
        AWS secret key. If configured, must also configure secret_key.
        """
        secret_key: Optional[str] = arg(default=None)

        """
        Custom endpoint for the AWS Identity and Access Management (IAM) API.
        """
        iam_endpoint: Optional[str] = arg(default=None)

        """
        The maximum number of times an AWS API request is retried on retryable failure.
        Defaults to 5.
        """
        max_retries: Optional[int] = arg(default=None)

        """
        Name of AWS profile in AWS shared credentials file (e.g. ~/.aws/credentials)
        or AWS shared configuration file (e.g. ~/.aws/config) to use for credentials and/or
        configuration.
        """
        profile: Optional[str] = arg(default=None)

        """
        Path to the AWS shared credentials file. Defaults to ~/.aws/credentials.
        """
        share_credentials_file: Optional[str] = arg(default=None)

        """
        Skip credentials validation via the STS API.
        """
        skip_credentials_validation: Optional[bool] = arg(default=None)

        """
        Skip validation of provided region name.
        """
        skip_region_validation: Optional[bool] = arg(default=None)

        """
        Skip usage of EC2 Metadata API.
        """
        skip_metadata_api_check: Optional[bool] = arg(default=None)

        """
        Custom endpoint for the AWS Security Token Service (STS) API. This can also be sourced
        from the AWS_STS_ENDPOINT environment variable.
        """
        sts_endpoint: Optional[str] = arg(default=None)

        """
        Multi-Factor Authentication (MFA) token.
        """
        token: Optional[str] = arg(default=None)

        """
        Number of seconds to restrict the assume role session duration.
        """
        assume_role_duration_seconds: Optional[int] = arg(default=None)

        """
        IAM Policy JSON describing further restricting permissions for the IAM Role being assumed.
        """
        assume_role_policy: Optional[str] = arg(default=None)

        """
        Set of Amazon Resource Names (ARNs) of IAM Policies describing further restricting
        permissions for the IAM Role being assumed.
        """
        assume_role_policy_arns: Optional[List[str]] = arg(default=None)

        """
        Map of assume role session tags.
        """
        assume_role_tags: Optional[Dict[str, str]] = arg(default=None)

        """
        Set of assume role session tag keys to pass to any subsequent sessions.
        """
        assume_role_transitive_tag_keys: Optional[List[str]] = arg(default=None)

        """
        External identifier to use when assuming the role.
        """
        external_id: Optional[str] = arg(default=None)

        """
        Amazon Resource Name (ARN) of the IAM Role to assume.
        """
        role_arn: Optional[str] = arg(default=None)

        """
        Session name to use when assuming the role.
        """
        session_name: Optional[str] = arg(default=None)

        """
        Name of the S3 Bucket.
        """
        bucket: str = arg()

        """
        Path to the state file inside the S3 Bucket. When using a non-default workspace, the state
        path will be /workspace_key_prefix/workspace_name/key (see also the workspace_key_prefix configuration).
        """
        key: str = arg()

        """
        Canned ACL to be applied to the state file.
        """
        acl: Optional[str] = arg(default=None)

        """
        Enable server side encryption of the state file.
        """
        encrypt: Optional[bool] = arg(default=None)

        """
        Custom endpoint for the AWS S3 API. This can also be sourced from the AWS_S3_ENDPOINT environment
        variable.
        """
        endpoint: Optional[str] = arg(default=None)

        """
        Enable path-style S3 URLs (https://<HOST>/<BUCKET> instead of https://<BUCKET>.<HOST>).
        """
        force_path_style: Optional[bool] = arg(default=None)

        """
        Amazon Resource Name (ARN) of a Key Management Service (KMS) Key to use for encrypting
        the state.
        """
        kms_key_id: Optional[str] = arg(default=None)

        """
        The key to use for encrypting state with Server-Side Encryption with Customer-Provided
        Keys (SSE-C). This is the base64-encoded value of the key, which must decode to 256 bits.
        """
        sse_customer_key: Optional[str] = arg(default=None)

        """
        Prefix applied to the state path inside the bucket. This is only relevant when using a
        non-default workspace. Defaults to env:.
        """
        workspace_key_prefix: Optional[str] = arg(default=None)

        """
        Custom endpoint for the AWS DynamoDB API.
        """
        dynamo_db_endpoint: Optional[str] = arg(default=None)

        """
        Name of DynamoDB Table to use for state locking and consistency. The table must have a primary
        key named LockID with type of string. If not configured, state locking will be disabled.
        """
        dynamo_db_table: Optional[str] = arg(default=None)
