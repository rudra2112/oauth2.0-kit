from enum import StrEnum

class Provider(StrEnum):
    GCP = "gcp"


class Service(StrEnum):
    IMAP = "imap"

    def get_scopes(self, provider: Provider):
        # IMP: Changing Scopes can break existing integrations, ensure revoking authorization of existing users and reauthorization
        if self == Service.IMAP and provider == Provider.GCP:
            return [
                "openid",
                "https://www.googleapis.com/auth/userinfo.email",
                "https://www.googleapis.com/auth/userinfo.profile",
                "https://www.googleapis.com/auth/gmail.labels",
                "https://www.googleapis.com/auth/gmail.metadata",
                "https://www.googleapis.com/auth/gmail.modify",
            ]
        else: 
            raise ValueError(f"Unsupported service {self} for provider {provider}")