import ast
import base64
import fnmatch
import json
import logging
import textwrap
import warnings
from typing import Union
import boto3
from botocore.exceptions import ClientError

from ..docker import load_secrets

# logger
logger = logging.getLogger(__name__)

# create client for SecretsManager
def generate_client(
    profile_name=None,
    aws_access_key_id=None,
    aws_secret_access_key=None,
    region_name="ap-northeast-2",
    load_docker_secret=True,
):
    """Create boto3 secretsmanager client.

    Priority:
        1. profile_name
        2. aws_access_key_id & secret_access_key
        3. docker secret (/run/secret)
    """

    # session configuration
    session_conf = dict()
    if load_docker_secret:
        load_secrets()
    if region_name is not None:
        session_conf.update({"region_name": region_name})
    if aws_access_key_id is not None:
        if aws_secret_access_key is not None:
            session_conf.update(
                {
                    "aws_access_key_id": aws_access_key_id,
                    "aws_secret_access_key": aws_secret_access_key,
                }
            )
    if profile_name is not None:
        session_conf = {"profile_name": profile_name}

    # return clinet
    session = boto3.session.Session(**session_conf)
    return session.client(service_name="secretsmanager")


# _get_secrets
def _get_secrets(client, secret_name):
    # get secrets
    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
    except ClientError as e:
        code = e.response["Error"]["Code"]
        description = textwrap.dedent(ERROR_DESCRIPTIONS["CODE"]).strip("\n")
        logger.error(code)
        logger.error(description)
        raise e
    else:
        if "SecretString" in get_secret_value_response:
            secrets = get_secret_value_response["SecretString"]
            try:
                secrets = json.loads(secrets)
            except json.JSONDecodeError:
                secrets = ast.literal_eval(secrets)
            except Exception as ex:
                logger.error(f"[CLUTTER] Cannot Decode JSON, {secrets}")
        else:
            secrets = base64.b64decode(get_secret_value_response["SecretBinary"])

    return secrets


# get secrets
def get_secrets(
    secret_name: str,
    profile_name: str = None,
    aws_access_key_id: str = None,
    aws_secret_access_key: str = None,
    region_name: str = "ap-northeast-2",
    load_docker_secret: bool = True,
):
    """Get secrets from AWS SecretsManager.

    Example
    -------
    >>> conf = get_secrets("some/secrets")
    """

    # get client
    client = generate_client(
        profile_name=profile_name,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name=region_name,
        load_docker_secret=load_docker_secret,
    )

    return _get_secrets(client, secret_name)


# list secrets
def list_secrets(
    patterns: Union[str, list] = "*",
    profile_name: str = None,
    aws_access_key_id: str = None,
    aws_secret_access_key: str = None,
    region_name: str = "ap-northeast-2",
    load_docker_secret: bool = True,
):
    """
    (TODO)
      - filter tags
    """
    # correct args
    patterns = patterns if isinstance(patterns, (tuple, list)) else [patterns]

    # get client
    client = generate_client(
        profile_name=profile_name,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name=region_name,
        load_docker_secret=load_docker_secret,
    )

    # get secrets
    opts = {}
    secrets = []
    while True:
        response = client.list_secrets(**opts)
        secrets += response.get("SecretList", [])
        next_token = response.get("NextToken")
        if next_token is None:
            break
        opts.update({"NextToken": next_token})

    for secret in secrets:
        secret_name = secret["Name"]
        if not any([fnmatch.fnmatch(secret_name, f"*{pat.strip('*')}*") for pat in patterns]):
            continue
        body = _get_secrets(client, secret_name)
        print(f"{secret['Name']}")
        if secret.get("Description"):
            print(f"  (DESCRIPTION: {secret['Description']})")
        if isinstance(body, dict):
            for k, v in body.items():
                try:
                    print(f"  - {k}: {v}")
                except Exception as ex:
                    logger.error(f"[ERROR] {ex} - {k}, {v}")
        else:
            print(f"  - {body}")


# [DEPRECATED]
def get_secret(secret_name, region_name="ap-northeast-2"):
    _warn = "'get_secret' will be deprecated soon, use 'get_secrets'!"
    warnings.warn(_warn, FutureWarning)

    return get_secrets(secret_name=secret_name, region_name=region_name)


# errors
ERROR_DESCRIPTIONS = {
    "DecryptionFailureException": """
    Secrets Manager can't decrypt the protected secret text using the provided KMS key.
    Deal with the exception here, and/or rethrow at your discretion.
    """,
    "InternalServiceErrorException": """
    An error occurred on the server side.
    Deal with the exception here, and/or rethrow at your discretion.
    """,
    "InvalidParameterException": """
    You provided an invalid value for a parameter.
    Deal with the exception here, and/or rethrow at your discretion.
    """,
    "InvalidRequestException": """
    You provided a parameter value that is not valid for the current state of the resource.
    Deal with the exception here, and/or rethrow at your discretion.
    """,
    "ResourceNotFoundException": """
    We can't find the resource that you asked for.
    Deal with the exception here, and/or rethrow at your discretion.
    """,
}
