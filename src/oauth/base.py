import datetime
from typing import List, Literal
from .enums import Provider, Service


class BaseOAuth:
    @staticmethod
    def format_credentials(
        email: str,
        uid: str,
        provider: Provider,
        service: Service,
        token: str,
        id: str | None = None,
        refresh_token: str | None = None,
        client_id: str | None = None,
        token_uri: str | None = None,
        client_secret: str | None = None,
        scopes: List[str] | None = None,
        rapt_token: str | None = None,
        universe_domain: str | None = None,
        account: str | None = None,
        expiry: datetime.datetime | None = None,
        extras: dict | None = None,
    ):
        # TODO: Add type here when internal and external are configured
        return {
            "email": email,
            "uid": uid,
            "provider": provider.value,
            "service": service.value,
            "creds": {
                "id": id,
                "token": token,
                "refresh_token": refresh_token,
                "client_id": client_id,
                "token_uri": token_uri,
                "client_secret": client_secret,
                "scopes": scopes,
                "rapt_token": rapt_token,
                "universe_domain": universe_domain,
                "account": account,
                "expiry": expiry,
            },
            "extras": extras or {},
        }

