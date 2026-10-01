# Music Assistant Libby

An experimental Music Assistant music provider for accessing **currently borrowed Libby/OverDrive audiobooks**.

> [!IMPORTANT]
> This project is intended for **personal, experimental use**. It is unofficial and is not affiliated with, endorsed by, or supported by OverDrive, Libby, Music Assistant, or any library system.

> [!NOTE]
> This project is developed with substantial assistance from **AI (OpenAI/ChatGPT)**. Code is reviewed and tested iteratively, but users should treat early releases as experimental.

## Goals

- Authenticate using Libby's 8-digit setup-code flow.
- Expose currently borrowed audiobooks to Music Assistant.
- Preserve the normal loan/entitlement boundary: only titles currently available to the authenticated Libby account are exposed.
- Stream audio for playback rather than downloading or archiving borrowed books.
- Support cover art, authors, chapters, duration, and resume/progress synchronization where practical.

## Current status

**Early development / proof of concept.**

The initial provider implements the Music Assistant provider skeleton, Libby setup-code authentication, account sync, audiobook-loan discovery, and basic audiobook metadata mapping. Playback is intentionally not enabled yet; the next milestone is a safe multi-part streaming implementation.

## Important deployment note

Music Assistant does not currently provide a HACS-style mechanism for installing arbitrary provider repositories into the standard HAOS app. Development providers are tested using the Music Assistant development server and a branch containing the provider. Exact test instructions are in `docs/TESTING.md`.

## Design principles

This project is deliberately **stream-oriented**. It is not intended to download, export, archive, retain, or remove DRM from library material. Audio URLs remain internal to the Music Assistant server and should only be requested for a currently entitled loan.

The Libby/OverDrive endpoints used by this project are not a documented public API and may change without notice.

## Roadmap

- [x] Music Assistant provider skeleton
- [x] Libby setup-code authentication
- [x] Sync cards and current loans
- [x] Filter audiobook loans
- [x] Basic Music Assistant audiobook mapping
- [ ] Fetch open-book metadata and chapter structure
- [ ] Stream multi-part audiobook audio through Music Assistant
- [ ] Seeking across audiobook parts
- [ ] Resume position
- [ ] Two-way Libby progress synchronization, if practical
- [ ] Error handling, throttling, caching, and retry hardening
- [ ] Automated API-response tests
- [ ] Upstream-readiness review

## Credits

The Libby API work is informed by the open-source reverse-engineering work in [odmpy](https://github.com/ping/odmpy) and its acknowledgement of pylibby. Music Assistant's demo and Audible providers are references for the current provider architecture.

No user credentials, Libby identity tokens, setup codes, signed audio URLs, or private API responses should ever be committed.

## License

MIT. See [LICENSE](LICENSE).

## Disclaimer

Use this software at your own risk and only with library accounts and loans you are authorized to access. Users are responsible for complying with their library's rules and applicable service terms. This project provides no warranty that unofficial Libby/OverDrive API access will remain available.
