# ONLYOFFICE Native Overtype v1.0.0-rc.2

Unofficial, experimental prerelease; not a stable release.

- Adds support for ONLYOFFICE Desktop Editors 10.0.0-169, retaining 9.4.0-129.
- Both pinned SDKJS profiles and source/unit tests passed CI on the merged compatibility update.
- Native Insert/Overtype and 10-second Undo grouping remain unchanged.
- Includes pinned sdkjs-forms support, version-specific installation and verified rollback.

The maintainer reports ONLYOFFICE 10 desktop testing; exact GUI results and full 29-case regression on the 10-second engine remain undocumented. The earlier 29/29 result applies to the 1.8-second RC5 only.

Supported: Linux Mint 22.3 / Cinnamon X11 / system DEB. See [README](README.md) for installation, rollback and licensing; [validation gate](RELEASE_CANDIDATE_V1_EN.md) for test limits. Use disposable documents for testing.

Original SDKJS: Ascensio System SIA, GNU AGPLv3 and supplemental terms. Independent of ONLYOFFICE.
