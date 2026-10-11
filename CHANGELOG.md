# Changelog

## 0.9.0-beta.1 — 2026-10-11

- Source-only portable installer for Linux Mint 22.3/X11 and ONLYOFFICE Desktop Editors 9.4.0-129.
- Pinned SDKJS tag/commit and checked source Git blob.
- Native Insert/Overtype and toolbar plugin, without the legacy X11 Delete hook.
- RC5 WeakMap-based Undo grouping; 10-second typing continuity threshold.
- Self-contained standalone plugin; no previous RC directories, tokens, localhost service, or personal test reports.
- Root-only factory backup, preflight, installer, status and rollback.
- Unit/fixture tests only on release tooling. **A ThinkPad T470s-en 4/4 valós kézi teszt PASS (2026-10-11). A teljes 29-es regresszió a korábbi 1,8 s-os RC5 builden volt PASS.**

## Release preparation 2026-10-11

- Replaced unverified resource icons with independently generated OVR artwork.
- Added a clearly accessible About & Licenses toolbar action and offline notice content.
- Disabled optional localhost diagnostics by default; it requires explicit developer opt-in.
- Corrected source SPDX identifiers and obsolete install warning; preserved native OVR behavior.
- Added pinned upstream-license packaging gate and unit CI checks.

GUI re-verification required for these new changes before first public beta release.
