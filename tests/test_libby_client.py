"""Unit tests for Libby client helpers that do not require a real account."""

from music_assistant.providers.libby.client import LibbyClient


def test_valid_setup_code() -> None:
    assert LibbyClient.valid_setup_code("12345678")
    assert not LibbyClient.valid_setup_code("1234567")
    assert not LibbyClient.valid_setup_code("abcdefgh")
    assert not LibbyClient.valid_setup_code("1234 678")
