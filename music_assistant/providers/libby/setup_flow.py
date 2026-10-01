"""Interactive setup flow for the Libby Music Assistant provider."""

from __future__ import annotations

from typing import TYPE_CHECKING

from music_assistant_models.config_entries import ConfigEntry
from music_assistant_models.enums import ConfigEntryType
from music_assistant_models.errors import LoginFailed, SetupFlowError

from .client import LibbyAuthenticationError, LibbyClient, LibbyClientError
from .constants import CONF_IDENTITY_TOKEN

if TYPE_CHECKING:
    from music_assistant.models.setup_flow import SetupSession

CONF_SETUP_CODE = "setup_code"


async def run_setup(session: SetupSession) -> None:
    """Authenticate a Libby account using its temporary 8-digit setup code."""
    errors: dict[str, str | SetupFlowError] | None = None

    while True:
        values = await session.form(
            [
                ConfigEntry(
                    key="instructions",
                    type=ConfigEntryType.LABEL,
                    label=(
                        "In Libby, generate an 8-digit setup code for another device, "
                        "then enter it below. The setup code is temporary and is not stored."
                    ),
                ),
                ConfigEntry(
                    key=CONF_SETUP_CODE,
                    type=ConfigEntryType.STRING,
                    label="Libby setup code",
                    required=True,
                ),
            ],
            step_id="authenticate",
            last_step=True,
            errors=errors,
        )
        code = str(values[CONF_SETUP_CODE]).strip()

        if not LibbyClient.valid_setup_code(code):
            errors = {"base": "The Libby setup code must contain exactly 8 digits."}
            continue

        client = LibbyClient(session.mass.http_session)
        try:
            token, _state = await client.authenticate_with_setup_code(code)
        except (LibbyAuthenticationError, LibbyClientError) as err:
            errors = {"base": str(err)}
            continue
        except Exception:
            errors = {
                "base": (
                    "Libby authentication failed unexpectedly. Generate a fresh setup "
                    "code and try again."
                )
            }
            continue

        try:
            await session.finish({CONF_IDENTITY_TOKEN: token})
        except (SetupFlowError, LoginFailed) as err:
            errors = {"base": err}
            continue
        return
