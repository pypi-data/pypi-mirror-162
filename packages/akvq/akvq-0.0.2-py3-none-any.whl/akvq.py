import os
from pathlib import Path

from azure.core.exceptions import ClientAuthenticationError
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient


__doc__ = """

get all secrets and only set ENV on keys that start with "akvq-"
use alwyas UPPERCASE for ENV
SWAP dash to underscores, akv only allow (link to spec)

See :manpage:`bash#name`

akvq-HASS -> HASS (as env)
hello -> (skip)

For now I am skipping to implemt auth cache because we are saveing it to disk
https://github.com/Azure/azure-sdk-for-python/issues/11134

source ~/.akvq.sh
Follow for bash: https://stackoverflow.com/q/10735574

Uess the same as for ssh keys

:doc:`azure.keyvault.secrets`

:doc:`azure-keyvault-secrets:index`
"""


def main():
    """
    .. todo::

        - save secrets to file
        - clear file
        - add config list like poetry
        - env for vault_url
        - support to add to vault

    :class:`azure.identity.DefaultAzureCredential`

    :class:`azure.identity.TokenCachePersistenceOptions`

    `azure-identity logging
    <https://azuresdkdocs.blob.core.windows.net/$web/python/azure-identity/latest/index.html#logging>`_

    """
    # cache_options = TokenCachePersistenceOptions()

    # # From: https://stackoverflow.com/a/65893640
    # azure_identity_logger = logging.getLogger("azure.identity")

    # # Critical is to hide the error from azure
    # azure_identity_logger.setLevel(logging.CRITICAL)

    from . import logger
    log = logger.config("akvq")

    try:
        credential = DefaultAzureCredential(
            # cache_persistence_options=cache_options,
            exclude_interactive_browser_credential=False,
            logging_enable=True,
        )

        secret_client = SecretClient(
            vault_url=os.environ.get("AKVQ_VAULT_URI"),
            credential=credential,
        )

        # secret = secret_client.get_secret("hello")

        # print(f"secret value from keyvault is: '{secret.value}'")

        aprefix = "akvq-"
        secrets = []
        secret_properties = secret_client.list_properties_of_secrets()
        for secret_property in secret_properties:
            # the list doesn't include values or versions of the secrets
            if secret_property.name.startswith(aprefix):
                secrets.append(secret_property.name)

        akfilename = Path.home() / ".akvq.sh"

        with open(akfilename, "w") as akfile:
            # Will override oldfile
            for secret in secrets:
                real_secret_name = secret.split(aprefix)[1]
                log.info(f"adding: {real_secret_name}")
                secret_value = secret_client.get_secret(secret).value
                akfile.write(f"export {real_secret_name}={secret_value}\n")

    except ClientAuthenticationError:
        pass

    # # specify a cache name to isolate the cache from other applications
    # TokenCachePersistenceOptions(name="akvq")


if __name__ == "__main__":
    main()
