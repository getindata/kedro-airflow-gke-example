"""
GCP related authorization code
"""
import logging

from cachetools import TTLCache, cached
from mlflow.tracking.request_header.abstract_request_header_provider import (
    RequestHeaderProvider,
)

IAP_CLIENT_ID = "IAP_CLIENT_ID"
DEX_USERNAME = "DEX_USERNAME"
DEX_PASSWORD = "DEX_PASSWORD"


class AuthHandler:
    """
    Utils for handling authorization
    """

    log = logging.getLogger(__name__)

    def obtain_iam_token(self, service_account, client_id):
        from google.cloud import iam_credentials

        self.log.debug(f"Attempt to get IAM token for {service_account}")
        client = iam_credentials.IAMCredentialsClient()
        return client.generate_id_token(
            name=f"projects/-/serviceAccounts/{service_account}",
            audience=client_id,
            include_email=True,
        ).token


class MLFlowGoogleIAMRequestHeaderProvider(RequestHeaderProvider):
    __instance__ = None

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "__instance__") or not isinstance(cls.__instance__, cls):
            cls.__instance__ = object.__new__(cls)
        return cls.__instance__

    required_params = ("client_id", "service_account")
    get_token = AuthHandler().obtain_iam_token

    def __init__(self, kedro_context, client_id, service_account):
        self.kedro_context = kedro_context
        self.client_id = client_id
        self.service_account = service_account

    def in_context(self):
        return True

    @cached(TTLCache(1, ttl=59 * 60))
    def request_headers(self):
        get_token_kwargs = {
            "client_id": self.client_id,
            "service_account": self.service_account,
        }
        token = self.get_token(**get_token_kwargs)
        return {"Authorization": f"Bearer {token}"}
###############

# import logging
# import os
# from functools import lru_cache

# from cachetools import cached, TTLCache
# from kedro.config import ConfigLoader
# from kedro.framework.context import KedroContext
# from mlflow.tracking.request_header.abstract_request_header_provider import (
#     RequestHeaderProvider,
# )

# # OAUTH_CLIENT_ID # mlflow config

# logger = logging.getLogger(__name__)


# #@cached(TTLCache(1, ttl=59 * 60))  # 59 minutes, as tokens have 1h expiration time
# def generate_google_id_token(config_loader: ConfigLoader):
#     try:
#         from google.cloud import iam_credentials

#         if OAUTH_CLIENT_ID in os.environ:
#             client_id = os.environ[OAUTH_CLIENT_ID]
#             sa = resolve_service_account_email()
#         else:
#             kedro_credentials = config_loader.get("credentials*", "cloud/credentials*")

#             iap = kedro_credentials["identity-aware-proxy"]
#             sa = iap["service_account"]
#             client_id = iap["client_id"]

#         client = iam_credentials.IAMCredentialsClient()

#         logger.info(f"Obtaining token using service account: {sa}")

#         token = client.generate_id_token(
#             name=f"projects/-/serviceAccounts/{sa}",
#             audience=client_id,
#             include_email=True,
#         ).token
#         return token
#     except:
#         logger.error("Could not obtain Google IAP token", exc_info=True)
#         raise


# #@lru_cache(1)
# def resolve_service_account_email():
#     from google.auth import default

#     creds, _ = default()
#     if hasattr(creds, "service_account_email"):
#         email = creds.service_account_email
#         if email == "default":
#             # Default compute engine account
#             from google.auth.compute_engine import _metadata as metadata
#             from google.auth import transport

#             sa_info = metadata.get_service_account_info(
#                 request=transport._http_client.Request()
#             )

#             sa = sa_info["email"]
#         else:
#             # Explicit service account
#             sa = email

#     else:
#         raise ValueError(
#             "Invalid configuration - if OAUTH_CLIENT_ID environment variable is specified"
#             " then the code needs to run under a service account."
#             " Unset the OAUTH_CLIENT_ID env and use the credentials.yml in conf otherwise."
#         )
#     return sa


# class MLFlowRequestHeaderProvider(RequestHeaderProvider):
#     def __init__(self, ctx: KedroContext):
#         self.kedro_context: KedroContext = ctx

#     @lru_cache
#     def get_mlflow_tracking_uri(self):
#         cfg = self.kedro_context.config_loader.get("mlflow")
#         return (
#             cfg["server"]["mlflow_tracking_uri"]
#             or os.environ.get("MLFLOW_TRACKING_URI")
#         ).lower()

#     def in_context(self):
#         mlflow_uri = self.get_mlflow_tracking_uri()
#         return any(domain in mlflow_uri for domain in (".appspot.com", ".run.app"))

#     def request_headers(self):
#         return {
#             "Authorization": f"Bearer {generate_google_id_token(self.kedro_context.config_loader)}"
#         }