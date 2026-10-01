# Testing

## First milestone

The initial build is successful when:

1. Music Assistant discovers the Libby provider.
2. Setup accepts an 8-digit Libby setup code.
3. Authentication completes and the provider loads.
4. Library sync exposes currently borrowed MP3 audiobooks.
5. No audio is downloaded or streamed yet.

## HAOS development-provider workflow

Music Assistant currently does not offer a HACS-style install path for arbitrary third-party provider repositories. Music Assistant maintainers recommend testing a development provider with the development server pointed at a branch containing the provider. Home Assistant Advanced Mode must be enabled for the relevant user.

The stable Music Assistant instance may need to be stopped while the development instance runs to avoid discovery/port conflicts.

## Safe diagnostics

When testing, capture the Music Assistant version, the UI error, and relevant log lines around `libby`.

Never post a saved Libby identity token, a still-valid setup code, library-card numbers/PINs, signed audiobook URLs, or complete raw account-sync responses. Redact personal/library-account information before opening an issue.
