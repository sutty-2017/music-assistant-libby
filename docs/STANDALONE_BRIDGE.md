# Standalone Libby Bridge — feasibility and implementation plan

## Goal
Run as a separate Home Assistant OS App. Do not modify or replace the official Music Assistant installation.

## Architecture
Libby/OverDrive authenticated loans -> standalone HTTP service -> Open Subsonic API -> Music Assistant's existing Open Subsonic provider -> existing players.

## Verified external compatibility
- Home Assistant OS supports third-party app repositories (https://www.home-assistant.io/common-tasks/os/).
- Music Assistant has an Open Subsonic provider (https://www.music-assistant.io/music-providers/subsonic/).
- MA's Open Subsonic implementation primarily supports artist/album/track/podcast media, **not native audiobook media**. Thus book-as-album/chapters-as-tracks is a compromise, and native book resume is not guaranteed.
- MA warns some variable-bitrate and container formats may not play through Subsonic.
- Official OverDrive APIs require approval and production credentials; Libby private endpoints are undocumented and can change.

## Safety boundaries
- Only authenticated, currently borrowed loans.
- No persistent audio storage, exporting, DRM bypass, or archiving.
- Keep device token and signed stream URLs private.
- App serves LAN-only authenticated API, with configurable credentials.
- Stop/uninstall bridge without changing Music Assistant's installation.
- Personal, unofficial, experimental, AI-assisted project; not affiliated with Libby, OverDrive, libraries, or Music Assistant.

## Build gates
1. Read-only Libby pairing and current audiobook loan listing. Mocked tests first.
2. Open Subsonic ping, getOpenSubsonicExtensions, getArtists, getArtist, getAlbum, getMusicDirectory, getCoverArt, search3, stream; validate against py-opensonic and Music Assistant.
3. Establish authorized *on-demand* playback of one active loan, without storing audio. **Do not ship playback until legal/technical feasibility is confirmed.**
4. Verify seek, end-of-chapter transitions, expiry, and progress limitations.
5. Package Home Assistant OS App with minimal privileges, healthcheck, configuration, logs, and documented rollback.

## Decision
Proceed with a separate bridge prototype, not a Music Assistant fork. Native audiobook UX may be unavailable via Open Subsonic; reassess after a real compatibility test.
