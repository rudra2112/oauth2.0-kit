from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2 import id_token as IDToken
from google.oauth2.credentials import Credentials as GCPOAuthCredentials
from ..enums import Provider, Service

import google.auth.exceptions
import json
from ..base import BaseOAuth


class GCPOAuth(BaseOAuth):
    def setup(self, gcp_client_secret: str):
        gcp_client_secret_dict = json.loads(gcp_client_secret)
        self.__CLIENT_SECRET = gcp_client_secret_dict

    def get_imap_flow(self, redirect_uri: str = None):
        return InstalledAppFlow.from_client_config(
            self.__CLIENT_SECRET,
            Service.IMAP.get_scopes(Provider.GCP),
            redirect_uri=redirect_uri,
        )

    def get_creds_from_dict(self, creds_dict: dict):
        creds = GCPOAuthCredentials.from_authorized_user_info(creds_dict)
        if creds_dict.get("extras") and creds_dict["extras"].get("id_token"):
            creds.id_token = creds_dict["extras"]["id_token"]

        return creds

    def decrypt_id_token(self, imap_flow: InstalledAppFlow, id_token: str):
        decrypted_data = IDToken.verify_oauth2_token(
            id_token,  # the raw JWT
            Request(),  # HTTP transport
            imap_flow.client_config["client_id"],
        )
        return decrypted_data
