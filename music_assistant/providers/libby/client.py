"""Small async client for the Libby endpoints used by the provider."""

from __future__ import annotations

from typing import Any
from urllib.parse import urljoin

from aiohttp import ClientResponseError, ClientSession

from .constants import (
    LIBBY_API_BASE,
    LIBBY_AUDIOBOOK_FORMAT,
    LIBBY_AUDIOBOOK_TYPE,
    LIBBY_CLIENT_NAME,
    USER_AGENT,
)


class LibbyClientError(Exception):
    """Base exception for Libby client errors."""


class LibbyAuthenticationError(LibbyClientError):
    """Raised when Libby authentication fails."""


class LibbyClient:
    """Async client for the minimum Libby API surface required by Music Assistant."""

    def __init__(self, session: ClientSession, identity_token: str | None = None) -> None:
        self._session = session
        self.identity_token = identity_token

    @staticmethod
    def valid_setup_code(code: str) -> bool:
        """Return whether a setup code has Libby's expected shape."""
        return len(code) == 8 and code.isdigit()

    def _headers(self, authenticated: bool = True) -> dict[str, str]:
        headers = {
            "User-Agent": USER_AGENT,
            "Accept": "application/json",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
        }
        if authenticated and self.identity_token:
            headers["Authorization"] = f"Bearer {self.identity_token}"
        return headers

    async def _request(
        self,
        endpoint: str,
        *,
        method: str = "GET",
        authenticated: bool = True,
        params: dict[str, str] | None = None,
        data: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        url = urljoin(LIBBY_API_BASE, endpoint)
        try:
            async with self._session.request(
                method,
                url,
                headers=self._headers(authenticated),
                params=params,
                data=data,
            ) as response:
                response.raise_for_status()
                payload: dict[str, Any] = await response.json()
                return payload
        except ClientResponseError as err:
            if err.status in (401, 403):
                raise LibbyAuthenticationError(
                    "Libby rejected the current identity."
                ) from err
            raise LibbyClientError(
                f"Libby request failed with HTTP {err.status}."
            ) from err

    async def create_identity(self) -> str:
        """Create a new Libby client identity and return its bearer token."""
        payload = await self._request(
            "chip",
            method="POST",
            authenticated=False,
            params={"client": LIBBY_CLIENT_NAME},
        )
        token = payload.get("identity")
        if not isinstance(token, str) or not token:
            raise LibbyAuthenticationError("Libby did not return an identity token.")
        self.identity_token = token
        return token

    async def clone_from_setup_code(self, code: str) -> None:
        """Link this client identity to an existing Libby account."""
        if not self.valid_setup_code(code):
            raise LibbyAuthenticationError("Libby setup code must contain exactly 8 digits.")
        if not self.identity_token:
            raise LibbyAuthenticationError("A Libby client identity has not been created.")
        await self._request("chip/clone/code", method="POST", data={"code": code})

    async def sync(self) -> dict[str, Any]:
        """Return the synchronized Libby account state."""
        if not self.identity_token:
            raise LibbyAuthenticationError("Libby is not authenticated.")
        payload = await self._request("chip/sync")
        if payload.get("result") != "synchronized":
            raise LibbyAuthenticationError("Libby account did not synchronize successfully.")
        return payload

    async def authenticate_with_setup_code(self, code: str) -> tuple[str, dict[str, Any]]:
        """Create, clone, and verify a Libby identity using a setup code."""
        token = await self.create_identity()
        await self.clone_from_setup_code(code)
        state = await self.sync()
        if not state.get("cards"):
            raise LibbyAuthenticationError(
                "Libby connected, but no registered library cards were found."
            )
        return token, state

    async def audiobook_loans(self) -> list[dict[str, Any]]:
        """Return currently borrowed loans that expose the MP3 audiobook format."""
        state = await self.sync()
        result: list[dict[str, Any]] = []
        for loan in state.get("loans", []):
            if not isinstance(loan, dict):
                continue
            media_type = loan.get("type") or {}
            if media_type.get("id") != LIBBY_AUDIOBOOK_TYPE:
                continue
            formats = loan.get("formats") or []
            if any(
                isinstance(item, dict) and item.get("id") == LIBBY_AUDIOBOOK_FORMAT
                for item in formats
            ):
                result.append(loan)
        return result
