from pydantic import BaseModel
from src.oauth.enums import Provider as OAuthProvider, Service as OAuthService

class OAuthRequest(BaseModel):
    provider: OAuthProvider
    service: OAuthService

class OAuthResponse(BaseModel):
    authorization_url: str