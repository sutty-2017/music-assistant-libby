"""Libby audiobook provider for Music Assistant."""

from __future__ import annotations

from collections.abc import AsyncGenerator
from typing import TYPE_CHECKING, Any, cast

from music_assistant_models.enums import ImageType, MediaType, ProviderFeature
from music_assistant_models.errors import LoginFailed, MediaNotFoundError
from music_assistant_models.media_items import (
    Audiobook,
    MediaItemImage,
    ProviderMapping,
    UniqueList,
)

from music_assistant.constants import CONF_ENTRY_UNOFFICIAL_PROVIDER
from music_assistant.models.music_provider import MusicProvider

from .client import LibbyAuthenticationError, LibbyClient, LibbyClientError
from .constants import CONF_IDENTITY_TOKEN

if TYPE_CHECKING:
    from music_assistant_models.config_entries import ConfigEntry, ProviderConfig
    from music_assistant_models.provider import ProviderManifest

    from music_assistant.mass import MusicAssistant
    from music_assistant.models import ProviderInstanceType


SUPPORTED_FEATURES = {ProviderFeature.LIBRARY_AUDIOBOOKS}


async def setup(
    mass: MusicAssistant, manifest: ProviderManifest, config: ProviderConfig
) -> ProviderInstanceType:
    """Initialize a Libby provider instance."""
    return LibbyProvider(mass, manifest, config, SUPPORTED_FEATURES)


class LibbyProvider(MusicProvider):
    """Music Assistant provider for a user's current Libby audiobook loans."""

    _client: LibbyClient

    async def get_config_entries(self) -> tuple[ConfigEntry, ...]:
        """Return runtime provider options."""
        return (CONF_ENTRY_UNOFFICIAL_PROVIDER,)

    async def handle_async_init(self) -> None:
        """Validate the saved Libby identity when the provider loads."""
        token = cast("str | None", self.get_setup_value(CONF_IDENTITY_TOKEN))
        if not token:
            raise LoginFailed("Libby identity token is missing. Re-authenticate the provider.")

        self._client = LibbyClient(self.mass.http_session, token)
        try:
            state = await self._client.sync()
        except (LibbyAuthenticationError, LibbyClientError) as err:
            raise LoginFailed(f"Unable to authenticate with Libby: {err}") from err

        self.logger.info(
            "Connected to Libby with %s library card(s) and %s active loan(s).",
            len(state.get("cards", [])),
            len(state.get("loans", [])),
        )

    @property
    def is_streaming_provider(self) -> bool:
        """Return True because Libby is a remote streaming source."""
        return True

    @property
    def supported_media_types(self) -> set[MediaType]:
        """Return the media types exposed by this provider."""
        return {MediaType.AUDIOBOOK}

    async def get_library_audiobooks(self) -> AsyncGenerator[Audiobook]:
        """Yield the user's currently borrowed Libby audiobooks."""
        try:
            loans = await self._client.audiobook_loans()
        except LibbyClientError as err:
            self.logger.warning("Unable to refresh Libby audiobook loans: %s", err)
            return

        for loan in loans:
            try:
                yield self._parse_audiobook(loan)
            except (KeyError, TypeError, ValueError) as err:
                self.report_skipped_sync_item(
                    MediaType.AUDIOBOOK,
                    str(loan.get("id") or "") or None,
                    err,
                )

    async def get_audiobook(self, prov_audiobook_id: str) -> Audiobook:
        """Return an active Libby audiobook loan by provider ID."""
        for loan in await self._client.audiobook_loans():
            if str(loan.get("id")) == prov_audiobook_id:
                return self._parse_audiobook(loan)
        raise MediaNotFoundError(
            f"Libby audiobook {prov_audiobook_id} is not an active loan."
        )

    def _parse_audiobook(self, loan: dict[str, Any]) -> Audiobook:
        """Convert a Libby loan record to a Music Assistant audiobook."""
        item_id = str(loan["id"])
        title = str(loan.get("title") or "Unknown title")
        author = str(loan.get("firstCreatorName") or "Unknown author")

        book = Audiobook(
            item_id=item_id,
            provider=self.instance_id,
            name=title,
            duration=0,
            provider_mappings={
                ProviderMapping(
                    item_id=item_id,
                    provider_domain=self.domain,
                    provider_instance=self.instance_id,
                    available=True,
                )
            },
            publisher=_publisher_name(loan),
            authors=UniqueList([author]),
            narrators=UniqueList(),
        )

        if subtitle := loan.get("subtitle"):
            book.metadata.description = str(subtitle)
        if cover_url := _best_cover_url(loan):
            book.metadata.images = UniqueList(
                [
                    MediaItemImage(
                        type=ImageType.THUMB,
                        path=cover_url,
                        provider=self.instance_id,
                        remotely_accessible=True,
                    )
                ]
            )
        subjects = loan.get("subjects") or []
        book.metadata.genres = {
            str(subject.get("name") or subject.get("id"))
            for subject in subjects
            if isinstance(subject, dict) and (subject.get("name") or subject.get("id"))
        }
        return book


def _best_cover_url(loan: dict[str, Any]) -> str | None:
    """Return the highest-resolution cover URL present on a Libby loan."""
    covers = loan.get("covers")
    if not isinstance(covers, dict):
        return None
    candidates = [cover for cover in covers.values() if isinstance(cover, dict)]
    candidates.sort(key=lambda cover: int(cover.get("width") or 0), reverse=True)
    if not candidates:
        return None
    href = candidates[0].get("href")
    return str(href) if href else None


def _publisher_name(loan: dict[str, Any]) -> str | None:
    """Extract a displayable publisher name from a Libby loan."""
    publisher = loan.get("publisherAccount")
    if isinstance(publisher, dict):
        value = publisher.get("name")
        return str(value) if value else None
    return str(publisher) if publisher else None
