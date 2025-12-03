import json
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials as GCPOAuthCredentials

from src.oauth.gcp.services import GCPOAuth as BaseGCPOAuth
from src.oauth.enums import Provider as OAuthProvider
from src.oauth.enums import Service as OAuthService


REDIRECT_URL = "http://localhost:8080/oauth/gcp/imap-redirect"
SECRET_FILE_PATH = "gcp_secret.json"


class GCPOAuth(BaseGCPOAuth):

    def setup(self):
        with open(SECRET_FILE_PATH, "r") as f:
            secret_key = json.load(f)

        super().setup(
            gcp_client_secret=json.dumps(secret_key)
        )

    @property
    def imap_auth_redirect_uri(self):
        return REDIRECT_URL

    def get_imap_auth_url(self, imap_flow: InstalledAppFlow):
        """Get GCP OAuth authorization URL."""
        flow = imap_flow
        flow.redirect_uri = self.imap_auth_redirect_uri
        auth_url, state = flow.authorization_url(
            access_type="offline",  # ensures you get a refresh_token
            include_granted_scopes="true",  # if you want incremental auth later
            prompt="consent",
        )

        return auth_url

    def register_imap_credentials(
        self, imap_flow: InstalledAppFlow, creds: GCPOAuthCredentials
    ):
        if creds.id_token:
            id_info = self.decrypt_id_token(imap_flow, creds.id_token)
        else:
            raise ValueError("ID token is required for GCP OAuth credentials.")

        creds_dict = json.loads(creds.to_json())
        formatted_creds = self.format_credentials(
            email=id_info["email"],
            uid=id_info["sub"],
            provider=OAuthProvider.GCP,
            service=OAuthService.IMAP,
            **creds_dict,
            extras={"id_token": creds.id_token},
        )
        # IMP: Store based on the uid
        # db._update_one(
        #     db.oauth_coll,
        #     {"uid": formatted_creds["uid"]},
        #     {"$set": formatted_creds},
        #     upsert=True,
        # )
        with open("debug_gcp_imap_creds.json", "w") as f:
            json.dump(formatted_creds, f, indent=4)
