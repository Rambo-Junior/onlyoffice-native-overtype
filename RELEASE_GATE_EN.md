# Beta release gate — verified status and outstanding limitations

**Current public release:** [`v0.9.0-beta.1`](https://github.com/Rambo-Junior/onlyoffice-native-overtype/releases/tag/v0.9.0-beta.1), October 11, 2026. The repository is public; the release is explicitly marked **prerelease**. Do not describe it as a stable or generally certified build.

## Checks completed for beta.1

- Upstream SDKJS pinned to tag `v9.4.0.129` / commit `75b53d504bfd81bfa35d59bb57dd9e56f7c9235d`.
- Complete upstream `LICENSE` included and verified against Git blob `53bc62cde3c705aa2d03b895b966bd6250f389ae`.
- Source-only ZIP and `SHA256SUMS` produced, with `NOTICE.md` and artwork provenance.
- Portable build, installer and hash-checked backup tested on a second supported Linux Mint machine.
- Original RC5 (1.8-second Undo threshold): **3/3 targeted and 29/29 full automated GUI tests passed**.
- Portable RC5/10-second build: **4/4 manual acceptance tests passed** on the ThinkPad T470s.
- About/License ribbon UI and Overtype/Undo smoke tests reported as passed on the ThinkPad before beta.1 publication.
- GitHub Actions source checks: PASS on commits `e555a7c` and `f093772`.
- Draft created, source ZIP attached, repository switched to public, and beta.1 published as a prerelease.

## Known limitations — do not misstate

- **29/29 was run on the 1.8-second RC5, not on the final 10-second portable build.**
- Complex DOCX tables, fields, comments, tracked changes, collaborative editing, footnotes, large files and complex Unicode/IME input do **not** have comprehensive coverage.
- Changes under `/opt/onlyoffice/desktopeditors` can be overwritten by editor upgrades, and this release does **not** support another editor version or packaging format.
- Only a narrow Linux Mint 22.3 / Cinnamon X11 / ONLYOFFICE 9.4.0-129 DEB configuration has been validated.
- The standalone plugin loads an upstream SDKJS JavaScript helper over HTTPS; offline behavior has not been independently qualified.
- Optional localhost diagnostics are disabled by default. Independent security and privacy audits have not been performed.

## English documentation / bilingual UI follow-up

- Make **English README** the repository landing page, preserve Hungarian as `README_HU.md`.
- Publish `DOKUMENTACIO_EN.md` with the full technical history and known limitations; retain `DOKUMENTACIO_HU.md`.
- Publish `GITHUB_RELEASE_NOTES_EN.md` and use it as the public Release description; retain the Hungarian notes as a separate file.
- The existing beta.1 tag and attached source ZIP are **immutable historical artifacts in this workflow**. Commits to `main` do not silently update them.
- Translating user-visible toolbar/About text affects the plugin UI. Run the targeted About and Overtype/Undo smoke tests again and publish this changed source under a **new beta tag**, rather than silently replacing beta.1 code.
- Re-run `python3 tools/prepare_github_release.py` after any source/document change to refresh `SHA256SUMS` and prepare a fresh source ZIP.

## Criteria before a stable release

Extend the automated GUI/document-integrity suite to the 10-second version; cover complex DOCX structures, selection/navigation interruption conditions, alternate keyboard/IME input, upgrade and rollback failures, and independently reproducible installation on each newly supported ONLYOFFICE version.
