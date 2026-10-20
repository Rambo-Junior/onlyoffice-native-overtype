# ONLYOFFICE Native Overtype v1.0.0-rc.1

**Unofficial release candidate — experimental and not supported by ONLYOFFICE. Not a stable v1.0.0 release.**

The native Insert/Overtype and 10-second Undo grouping engine are unchanged from v0.9.0-beta.2. This candidate improves reproducibility and release engineering:

- Builds pinned ONLYOFFICE SDKJS 9.4.0-129 source in a separate GitHub Actions job; checks the generated patched JavaScript.
- Includes source-integrity checks, new release-specific tests, signed-upstream-license provenance and bilingual release documentation.
- Retains the reversible system-DEB installer, root factory backup, plugin and `--rollback`.

**Test limits:** 29/29 full automated GUI tests belonged to the earlier 1.8s RC5; the 10s build passed 4/4 manual second-machine tests. The exact current release candidate has **not** been cleared for complex DOCX, collaboration, tracked changes, footnotes or IME usage. See [release gate](RELEASE_CANDIDATE_V1_EN.md).

Supported **only** on Linux Mint 22.3 / Cinnamon X11 / ONLYOFFICE Desktop Editors **9.4.0-129** installed as a DEB package. Download the source ZIP, extract and run `bash run.sh --check`, `bash run.sh --build`, `bash run.sh --install`, then `bash run.sh --status`. To revert: `bash run.sh --rollback`. Close the editor before installing or restoring; never run with the old X11 overtype helper.

Original ONLYOFFICE SDKJS by Ascensio System SIA; GNU AGPLv3 and supplemental terms. This project is independent of ONLYOFFICE.
