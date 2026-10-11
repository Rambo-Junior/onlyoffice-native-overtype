# Changelog

## 0.9.0-beta.2 — 2026-10-11

- English README, full technical documentation and GitHub Release notes; Hungarian originals retained.
- Bilingual About & Licenses toolbar and legal information panel.
- Same native RC5/10-second overtype and Undo engine; no engine changes from beta.1.
- Source archive and plugin metadata version now match beta.2.
- Original 29/29 automated GUI pass was for RC5 at 1.8 seconds; manual 10-second and updated bilingual UI checks reported on ThinkPad T470s.

## 0.9.0-beta.1 — 2026-10-11

- Source-only portable installer for Linux Mint 22.3/X11 and ONLYOFFICE Desktop Editors 9.4.0-129.
- Pinned SDKJS tag/commit and checked source Git blob.
- Native Insert/Overtype and toolbar plugin, without the legacy X11 Delete hook.
- RC5 WeakMap-based Undo grouping; 10-second typing continuity threshold.
- Self-contained standalone plugin; no previous RC directories, tokens, localhost service, or personal test reports.
- Root-only factory backup, preflight, installer, status and rollback.
- Unit/fixture tests only on release tooling. **4/4 manual smoke tests passed on ThinkPad T470s (2026-10-11); the full 29-case automated regression passed on the earlier 1.8-second RC5 build only.**

## Release preparation 2026-10-11

- Replaced unverified resource icons with independently generated OVR artwork.
- Added a clearly accessible About & Licenses toolbar action and offline notice content.
- Disabled optional localhost diagnostics by default; it requires explicit developer opt-in.
- Corrected source SPDX identifiers and obsolete install warning; preserved native OVR behavior.
- Added pinned upstream-license packaging gate and unit CI checks.

Release-candidate GUI check PASS on ThinkPad T470s (2026-10-11): About & Licenses and native typing/Undo/Redo. Previous portable RC5/10s save/reopen smoke test PASS.

## English documentation and bilingual interface update (after beta.1 publication)

- `README.md` is now English-first; the previous Hungarian page is preserved as `README_HU.md`.
- Added comprehensive `DOKUMENTACIO_EN.md`, English release notes, and an English release checklist.
- Added English-first, bilingual About/License toolbar text (requires targeted UI retesting before the next tagged beta).
- Does not change the native Word editing or 10-second Undo logic.
- The already published beta.1 tag/asset is a historical snapshot and is not silently replaced.
