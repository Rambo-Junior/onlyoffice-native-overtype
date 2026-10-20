# v1.0.0-rc.1 — release-candidate validation and publication gate

**NOT a stable, fully certified document-integrity release.** This release candidate keeps the **same native RC5/10-second overtype code** as public `v0.9.0-beta.2`. It adds pinned SDKJS build verification, additional static release gates, and separate English/Hungarian release guidance.

## Verified to date

- SDKJS source pinned to `v9.4.0.129` (`75b53d504bfd81bfa35d59bb57dd9e56f7c9235d`).
- 29/29 automated GUI scenarios on the **earlier 1.8-second RC5**, **not** the 10-second candidate.
- 4/4 manual acceptance checks on the 10-second portable installation on ThinkPad T470s, including DOCX save/reopen; updated bilingual toolbar UI passed a targeted smoke test.
- Portable install, status and rollback behaviors are covered by scripted fixture tests. A complete fresh-machine, failed-upgrade and rollback real-hardware matrix has **not** been performed.
- New GitHub Actions checks the exact SDKJS source/build and synthesized patched JS. A green build is **not** a substitute for opening, editing and saving DOCX in a real desktop editor.

## Required before stable `v1.0.0`

1. Run the complete GUI + saved DOCX 29-case suite against the **exact 10-second RC** on a disposable isolated editor, and publish its machine-readable results.
2. Extend integrity checks to tables, tracked changes, comments, headers, footers, footnotes/endnotes, protected regions, fields, emoji, combining Unicode/IME input, and existing formatting.
3. Test backup, interrupted install, rollback and editor restart **on a separate noncritical machine**, and check behavior after ONLYOFFICE upgrades.
4. Have independent users reproduce the installer and report full build/version context.
5. Keep the source-only artifact, full upstream LICENSE, legal notices and artwork attribution together; confirm the immutable release tag matches the ZIP content.

## Supported system

Only Linux Mint 22.3 / Cinnamon X11 with the system-DEB installation of ONLYOFFICE Desktop Editors 9.4.0-129. Not for Flatpak/Snap/AppImage, Wayland, Windows, macOS or other ONLYOFFICE versions.

## Source and installer

Normal user, **never root**, on an unmodified supported machine:

```bash
bash run.sh --check
bash run.sh --build
bash run.sh --install
bash run.sh --status
# To return to factory bundles after closing ONLYOFFICE:
bash run.sh --rollback
```

Use only disposable documents for the first test. This is an unofficial SDKJS modification, not an official ONLYOFFICE plugin API. License: GNU AGPLv3 and the original Ascensio/ONLYOFFICE supplemental terms in `LICENSE`.
