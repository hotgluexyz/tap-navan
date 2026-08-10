"""Navan Authentication."""

from __future__ import annotations

from hotglue_singer_sdk.authenticators import OAuthAuthenticator, SingletonMeta
from typing_extensions import override


# The SingletonMeta metaclass makes your streams reuse the same authenticator instance.
# If this behaviour interferes with your use-case, you can remove the metaclass.
class NavanAuthenticator(OAuthAuthenticator, metaclass=SingletonMeta):
    """Authenticator class for Navan."""

    @override
    @property
    def oauth_request_body(self) -> dict:
        """Define the OAuth request body for the Navan API.

        Returns:
            A dict with the request body
        """
        return {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }
