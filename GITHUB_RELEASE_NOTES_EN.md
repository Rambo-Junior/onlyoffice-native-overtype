# ONLYOFFICE Native Overtype v0.9.0-beta.1

**Experimental, unofficial beta — NOT affiliated with, endorsed by, or supported by Ascensio System SIA / ONLYOFFICE.**

Adds a native, toggleable **Insert/Overtype** mode to the ONLYOFFICE Desktop Editors Word editor. Unlike older X11 helpers, character replacement is performed inside the SDKJS document engine. The `Insert` key and a Plugins-ribbon button toggle the mode.

### Supported configuration

**Linux Mint 22.3 · Cinnamon / X11 · ONLYOFFICE Desktop Editors 9.4.0-129 (DEB)**. Other versions, packaging methods and operating systems are not supported.

### Highlights

- Conservative overwrite behavior at paragraph and selection boundaries.
- Consecutive overwrites grouped into one Ctrl+Z/Ctrl+Y unit, with a **10-second maximum gap** between typed characters (additional history boundaries still apply).
- Standalone toolbar plugin with About/License attribution.
- Source-only reproducible build from pinned SDKJS `v9.4.0.129` (`75b53d504bfd81bfa35d59bb57dd9e56f7c9235d`).
- Verified factory-backup, installer status and rollback; no dependency on the old X11 Delete hook.

### Install

Extract the release ZIP on a **clean, supported machine**, close ONLYOFFICE, remove/disable the older `onlyoffice-overtype-x11` helper, and execute from the extracted project root:

```bash
bash run.sh --check
bash run.sh --build
bash run.sh --install
bash run.sh --status
```

`--install` requires the explicit word `TELEPITES` and root access for two SDKJS Word-bundle replacements. To revert, close ONLYOFFICE and run `bash run.sh --rollback`. **Do not bypass version checks or delete the factory backup.**

### Testing evidence

The **earlier RC5 1.8-second build** passed **29/29 automated GUI scenarios** and 3/3 targeted Undo tests. The **10-second portable build** was built/installed on a second Linux Mint machine and passed **4/4 manual checks**, including slow Undo/Redo and DOCX save/reopen. A later About/License UI smoke test was also reported as successful. The 29-test automated suite has **not** been rerun on the released 10-second build.

### Known limitations

The modification replaces two installed Word JavaScript bundles, may be overwritten by ONLYOFFICE updates, and has not been comprehensively verified against complex tables, comments, revision tracking, fields, embedded objects, advanced Unicode/IME input or collaborative editing. Use disposable files for initial testing. This release is a **beta, not a document-integrity certification or stable v1.0**.

### Documentation and licensing

- [English README](https://github.com/Rambo-Junior/onlyoffice-native-overtype/blob/main/README.md)
- [English technical documentation](https://github.com/Rambo-Junior/onlyoffice-native-overtype/blob/main/DOKUMENTACIO_EN.md)
- [Magyar dokumentáció](https://github.com/Rambo-Junior/onlyoffice-native-overtype/blob/main/DOKUMENTACIO_HU.md)
- [Full upstream license and supplemental terms](https://github.com/ONLYOFFICE/sdkjs/blob/v9.4.0.129/LICENSE)

Original SDKJS is copyright © 2009–2026 Ascensio System SIA, licensed under the GNU AGPLv3 with applicable supplementary terms. This is an independently maintained, unofficial modification.
