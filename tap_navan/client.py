"""HTTP API client (REST or GraphQL), including NavanStream base class."""

from __future__ import annotations

from functools import cached_property
from typing import Any

import requests
from hotglue_singer_sdk.authenticators import APIAuthenticatorBase
from hotglue_singer_sdk.streams import RESTStream
from typing_extensions import override


class NavanStream(RESTStream):
    """Navan stream class."""

    records_jsonpath = "$.content[*]"

    @override
    @property
    def url_base(self) -> str:
        """Return the API URL root, configurable via the ``api_url`` tap setting."""
        return self.config.get("api_url", "https://api.navan.com/v1")

    @override
    @cached_property
    def authenticator(self) -> APIAuthenticatorBase:
        """Return a new authenticator object.

        Returns:
            An authenticator instance.
        """
        authenticator_cls, auth_endpoint = self._tap.access_token_support(self._tap)
        return authenticator_cls(
            stream=self,
            auth_endpoint=auth_endpoint,
        )

    @override
    @property
    def http_headers(self) -> dict:
        """Return the http headers needed.

        Returns:
            A dictionary of HTTP headers.
        """
        return {}

    @override
    def get_next_page_token(
        self,
        response: requests.Response,
        previous_token: Any | None,
    ) -> Any | None:
        """Return ``next_cursor`` when ``has_next`` is true."""
        body = response.json()
        if not body.get("has_next"):
            return None
        return body["next_cursor"]

    @override
    def get_url_params(
        self,
        context: dict | None,
        next_page_token: Any | None,
    ) -> dict[str, Any]:
        """Return a dictionary of values to be used in URL parameterization.

        Args:
            context: The stream context.
            next_page_token: Cursor from the previous response's ``next_cursor``.

        Returns:
            A dictionary of URL query parameters.
        """
        params: dict[str, Any] = {}
        if next_page_token is not None:
            params["cursor"] = next_page_token
        return params
