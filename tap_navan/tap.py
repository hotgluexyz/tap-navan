"""Navan tap class."""

from __future__ import annotations

from typing import Any

from hotglue_singer_sdk import Stream, Tap
from hotglue_singer_sdk import typing as th  # JSON schema typing helpers
from hotglue_singer_sdk.authenticators import OAuthAuthenticator
from typing_extensions import override

from tap_navan.auth import NavanAuthenticator
from tap_navan.streams import (
    TransactionsStream,
)

STREAM_TYPES = [
    TransactionsStream,
]


class TapNavan(Tap):
    """Singer tap for Navan."""

    name = "tap-navan"

    config_jsonschema = th.PropertiesList(
        th.Property(
            "start_date",
            th.DateTimeType,
            description=(
                "Optional earliest date_modified to sync (clamped to Navan's "
                "~2-month lookback). When unset, the stream bookmark is used, "
                "or Navan's max lookback on a first sync."
            ),
        ),
        th.Property(
            "api_url",
            th.StringType,
            description="Base URL for the Navan API",
            default="https://api.navan.com/v1",
        ),
        th.Property(
            "client_id",
            th.StringType,
            required=True,
            description="OAuth client ID for the Navan OAuth app",
        ),
        th.Property(
            "client_secret",
            th.StringType,
            required=True,
            description="OAuth client secret for the Navan OAuth app",
        ),
    ).to_dict()

    @override
    def discover_streams(self) -> list[Stream]:
        """Return a list of discovered streams."""
        return [stream_class(tap=self) for stream_class in STREAM_TYPES]

    @classmethod
    def access_token_support(
        cls,
        connector: Any = None,
    ) -> tuple[type[OAuthAuthenticator], str]:
        """Return the authenticator class and OAuth token endpoint.

        Returns:
            A tuple with the authenticator class and the OAuth token endpoint URL.
        """
        return NavanAuthenticator, "https://app.navan.com/ta-auth/oauth/token"


if __name__ == "__main__":
    TapNavan.cli()
