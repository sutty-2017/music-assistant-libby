# Architecture

## Scope

The provider represents a user's **active Libby audiobook loans** inside Music Assistant. It is not a general OverDrive catalogue client and is not intended to acquire, retain, or export audiobook files.

## Authentication flow

```text
Music Assistant setup flow
        |
        | 8-digit temporary setup code
        v
POST /chip?client=dewey
        |
        | identity bearer token
        v
POST /chip/clone/code
        |
        v
GET /chip/sync
        |
        +--> cards
        +--> active loans
```

Only the resulting identity token is persisted in Music Assistant setup data. The temporary setup code is discarded.

## Library sync

`chip/sync` supplies active loans. The provider filters to media type `audiobook` and format `audiobook-mp3`. Each eligible loan is mapped to a Music Assistant `Audiobook`.

## Planned playback

Libby audiobook playback is multipart. The open-book response supplies a spine containing ordered audio parts and chapter/navigation metadata. The planned provider uses `StreamType.CUSTOM` so Music Assistant can consume the parts as one logical audiobook while audio remains stream-only.

Audio URLs must remain internal to the Music Assistant server. Decoded audio must not be persisted.

## Progress

Music Assistant provides `get_resume_position` and `on_played` hooks. Libby's progress endpoints still need validation before two-way synchronization is implemented. Until then, this project will not guess at undocumented write calls.

## API stability

Libby/OverDrive does not publish these endpoints as a supported third-party API. Endpoint behavior may change at any time. API-specific behavior belongs in `client.py` and future helper modules.
