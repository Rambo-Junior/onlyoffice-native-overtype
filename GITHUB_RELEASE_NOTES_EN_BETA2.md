# ONLYOFFICE Native Overtype v0.9.0-beta.2

**Experimental, unofficial beta — NOT developed, endorsed or supported by ONLYOFFICE / Ascensio System SIA.**

## What's new

- **English-first project documentation** with the full technical guide, installation instructions, FAQ-like limitations and release checklist.
- **Hungarian documentation retained** (`README_HU.md`, `DOKUMENTACIO_HU.md`).
- **Bilingual About & Licenses panel** on the Plugins ribbon, including the original developer attribution and upstream AGPLv3 terms link.
- Plugin version updated to `0.9.0-beta.2`; source ZIP is packaged from the beta.2 release commit.

## Functionality and scope

The native Insert/Overtype algorithm and RC5 **10-second Undo grouping have not changed**. Press `Insert` or use the Overtype ribbon button. The source-only installer builds from pinned SDKJS `v9.4.0.129` (commit `75b53d504bfd81bfa35d59bb57dd9e56f7c9235d`). It backs up and replaces two vendor Word JavaScript bundles and provides a rollback command.

**Supported platform only:** Linux Mint 22.3, Cinnamon/X11, ONLYOFFICE Desktop Editors **9.4.0-129** installed from DEB. Other versions, Snap/Flatpak, Wayland, Windows and macOS are not validated.

## Install (on a clean supported system)

Download the attached `onlyoffice-native-overtype-v0.9.0-beta.2-source.zip`, extract it, then from the extracted directory:

```bash
bash run.sh --check
bash run.sh --build
bash run.sh --install
bash run.sh --status
```

To undo the modification after closing ONLYOFFICE: `bash run.sh --rollback`. Do **not** install over an already patched editor, or while the legacy X11 overtype helper is active. The user must confirm `TELEPITES` before installation.

## Testing and limitations

The original RC5 build with 1.8-second Undo grouping passed **29/29 isolated GUI tests**. The 10-second portable build passed **4/4 manual smoke tests** on a second Linux Mint machine, including DOCX save/reopen, and the updated bilingual toolbar was checked separately by the user. The beta.2 package has **not** undergone a new 29-test automated GUI run. Complex DOCX structures (tables, tracked changes, comments, protected forms, advanced Unicode and collaborative editing) are not comprehensively verified. **Back up documents and avoid critical/irreplaceable files.**

Documentation: [English README](https://github.com/Rambo-Junior/onlyoffice-native-overtype/blob/v0.9.0-beta.2/README.md) · [English technical guide](https://github.com/Rambo-Junior/onlyoffice-native-overtype/blob/v0.9.0-beta.2/DOKUMENTACIO_EN.md) · [Magyar](https://github.com/Rambo-Junior/onlyoffice-native-overtype/blob/v0.9.0-beta.2/DOKUMENTACIO_HU.md).

Upstream original developer: Ascensio System SIA. License: AGPLv3 and original additional terms, included in the source package. Independent, unofficial project.
