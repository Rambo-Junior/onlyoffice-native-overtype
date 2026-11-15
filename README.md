# ONLYOFFICE Native Overtype

> **Latest source candidate: v1.0.0-rc.1.** This is a release candidate, **not a stable v1.0.0**. Native engine unchanged from beta.2. [Validation gate](RELEASE_CANDIDATE_V1_EN.md) · [Magyar](RELEASE_CANDIDATE_V1_HU.md).

**Experimental, unofficial native Insert/Overtype support for ONLYOFFICE Desktop Editors — `v1.0.0-rc.1`.**

**English:** this README · [Technical documentation](DOKUMENTACIO_EN.md) · [Release notes](GITHUB_RELEASE_NOTES_EN.md) · [Release checklist](RELEASE_GATE_EN.md)\
**Magyar:** [README magyarul](README_HU.md) · [Részletes műszaki dokumentáció](DOKUMENTACIO_HU.md) · [Kiadási megjegyzések](GITHUB_RELEASE_NOTES_HU.md)

> **Unofficial modification:** This project is not developed, endorsed or supported by ONLYOFFICE or Ascensio System SIA. It replaces two installed Word-editor JavaScript bundles. This is a **beta**, not a universally safe replacement for the stock editor. Back up important documents and avoid using the patched editor for irreplaceable or complex DOCX files.

## Supported environment

| Component | Required version / configuration |
| --- | --- |
| Operating system | **Linux Mint 22.3**, Cinnamon, **X11** |
| Office suite | **ONLYOFFICE Desktop Editors 9.4.0-129** or **10.0.0-169**, system-installed DEB (see [Supported builds](#supported-builds)) |
| Installation location | `/opt/onlyoffice/desktopeditors` |
| SDKJS upstream | Pinned per build, see [Supported builds](#supported-builds) |
| Build dependencies | Python 3, Git, Node.js, internet access, `sudo`, at least 4 GiB free disk space |

**Not supported/tested:** other ONLYOFFICE builds, Flatpak/Snap/AppImage, Wayland, Windows, macOS, or other Linux distributions. The installer must reject unsupported installations; do not bypass its version or hash checks.

### Supported builds

The installer reads the installed `dpkg` version and binds to exactly one pinned **profile**; every other build is refused. State, cache and backup paths are separate per profile (`940129` = 9.4.0-129, `1000169` = 10.0.0-169).

| Installed build | SDKJS tag / commit | Extra upstream addon | Status |
| --- | --- | --- | --- |
| **9.4.0-129** | `v9.4.0.129` / `75b53d504bfd81bfa35d59bb57dd9e56f7c9235d` | none (unchanged from beta/rc.1) | Validated, see below |
| **10.0.0-169** | `v10.0.0.169` / `3679e0375a758d7dc59d31337a45461be3525ed8` | `sdkjs-forms` `v10.0.0.169` / `0148c8ed3f799136431be49d4d83b4064fbafd01` | Source/build/installer verified; **GUI regression pending** |

#### ONLYOFFICE 10.0.0-169

*Verified (automated, not a GUI test):* every source-patch anchor still matches exactly once; the History/Undo code the grouping mirrors (`CheckUnionLastPoints`) and the text-entry path (`CDocument.EnterText`) are identical to 9.4.0.129; all 34 engine-API canary patterns are present in the built Word bundle; both compiled bundles pass `node --check`; and a full dry run against copies of the files of the official 10.0.0-169 DEB (build -> install -> status -> rollback) restored the original bytes exactly. `sdk-all.bin` (V8 code cache, also shipped in 9.4.0-129) is never touched.

*Handled differences:* upstream tags `v10.0.0.167` to `170` share one commit, so the tag check uses `git tag --points-at` instead of `git describe`; the official 10.0.0-169 bundles contain the `sdkjs-forms` (OFORM) addon, so this profile builds with the same pinned addon (the 9.4.0-129 profile keeps its original, addon-free build); the plugin is now declared as an explicit `background` plugin with `autostart` (ONLYOFFICE 10 starts it automatically; the old `unvisible` value was silently treated as `background` by both versions).

*Not done:* no run on a real 10.0.0-169 editor and no 29-case regression. 10.x changed `StartAction`/`FinalizeAction` (redo-point save/restore); the Undo grouping runs after `FinalizeAction` and only on non-empty overwrite actions, so no conflict is expected, but check Undo/Redo by hand (`ABCDE` test below) before relying on it. If `Insert` does nothing after installing, confirm `--status` shows `PORTABLE RC5/10s`, restart ONLYOFFICE completely, check that Overtype is enabled under Plugins; otherwise run `--rollback` and report - the V8 code cache is the first suspect.

*Another 10.x build?* `python3 tools/probe_profile.py <dpkg-version>` derives the pins and runs the full build verification, then prints a `PROFILES` entry. It is no substitute for a GUI test.

## Features

- Toggle **Insert (INS)** versus **Overtype (OVR)** using the `Insert` key or the **Overtype** button on the Plugins ribbon.
- In OVR mode, replace the next ordinary character instead of inserting before it, with conservative paragraph-boundary and selection handling. Unsupported document structures may fall back to ordinary insertion.
- Group consecutive overwrites into one Undo unit when each typing gap is **at most 10 seconds**, subject to additional editing/history boundary checks. `Ctrl+Z` restores the prior text; `Ctrl+Y` reapplies it.
- Preserve the conventional `Ctrl+Insert` (Copy) and `Shift+Insert` (Paste) shortcuts.
- Replace the old X11 `Delete`-event trick with changes inside the Word editing engine. **Do not run the legacy `onlyoffice-overtype-x11` helper at the same time.**
- Provide separate **About & Licenses / Névjegy és licencek** information and a reversible installation.

## What the download contains

The source-only ZIP includes SDKJS patch scripts, a standalone toolbar plugin, tests, a portable installer, original-license notices, and rollback support. It **does not ship a compiled ONLYOFFICE application or patched Word bundles**. `--build` fetches the exact pinned upstream SDKJS source and creates the patched bundles locally.

**Beta.2 includes the English technical documentation and bilingual About & Licenses UI.** The original beta.1 release remains available as a historical snapshot; do not assume that beta.1 contains these later improvements.

## Installation on a clean, supported machine

Download the source ZIP from [GitHub Releases](https://github.com/Rambo-Junior/onlyoffice-native-overtype/releases) and extract it. Run the following **from the extracted project root** as your normal user (not via `sudo`):

```bash
bash run.sh --check
bash run.sh --build
bash run.sh --install
bash run.sh --status
```

`--check` validates the installed version, X11 session, closed editor, absence of conflicting legacy helpers/plugins, and clean vendor files. `--build` downloads and builds under `~/.cache/onlyoffice-overtype-native-<profile>/` **without modifying `/opt`**. Only run `--install` after `BUILD PASS`; it requires the explicit confirmation word `TELEPITES` (the current CLI confirmation has not yet been localized). The installer then requests the necessary root permissions, makes verified factory backups, replaces the two Word JS bundles, and installs the standalone plugin into your user account.

**Never install over an already-patched editor, or alongside the legacy X11 Overtype helper.** Remove/disable the legacy package or service first, and confirm that the editor is closed. Keep the extracted installer, its build cache/manifests, and backups until you no longer need rollback.

### Changed files and backups

```text
/opt/onlyoffice/desktopeditors/editors/sdkjs/word/sdk-all.js
/opt/onlyoffice/desktopeditors/editors/sdkjs/word/sdk-all-min.js
/var/lib/onlyoffice-overtype-native-portable-<profile>/                # privileged factory backup (<profile>: 940129 or 1000169)
~/.local/state/onlyoffice-overtype-native-<profile>/                   # user installation state
~/.local/share/onlyoffice/desktopeditors/sdkjs-plugins/{A360C0D9-711B-4C90-BFB4-58AC023074E6}/
```

### Rollback

Close every ONLYOFFICE window, then run from the same extracted project directory:

```bash
bash run.sh --rollback
```

The rollback restores the original bundled files from a hash-checked factory backup and removes the plugin/state created by this installer. **Do not delete backup files or force rollback over unrecognized changes.** The earlier ThinkCentre M900 developer installation has a *different* rollback mechanism; do not run the portable rollback there.

## Smoke test

Use only a disposable DOCX document:

1. Type `ABCDE`, position the cursor immediately after `A`, then press `Insert` to enable OVR.
2. Type `xyz`. Expected: `AxyzE`.
3. Press `Ctrl+Z` once. Expected: `ABCDE`; press `Ctrl+Y` once. Expected: `AxyzE`.
4. Repeat with 2–3-second pauses between characters. One Undo should still restore the original text.
5. Press `Insert` again and check ordinary **insertion** mode.
6. Save to DOCX, close the editor, reopen the document and verify the saved text.
7. Open **About & Licenses** on the Plugins ribbon to review the legal notice.

If any behavior differs, stop using the patched editor and use the documented rollback.

## Verified results and limitations

- **RC5 at the original 1.8-second grouping threshold:** 3/3 targeted Undo tests and **29/29 isolated automated GUI tests**, including saved DOCX content verification.
- **Portable RC5 with a 10-second threshold:** built and installed successfully on a second Linux Mint machine (ThinkPad T470s); **4/4 manual acceptance tests** passed (basic overwrite, slow Undo/Redo, insertion, save and reopen).
- **Bilingual/About beta UI:** targeted toolbar/About and overtype/Undo tests were reported as passed on the ThinkPad before public beta.1 publication.
- **CI:** repository source/unit checks passed on commits `e555a7c` and `f093772`.
- **Not claimed:** the 29-case automated suite was **not rerun on the released 10-second build**, and complex DOCX content, tables, comments, tracked changes, footnotes, IME/grapheme clusters and collaborative editing are not comprehensively covered.

An ONLYOFFICE update may overwrite the patched bundles. Never copy bundles built for one editor build into another editor build.

## Licensing, attribution and privacy

Original SDKJS is © 2009–2026 **Ascensio System SIA** and governed by the **GNU AGPLv3 and the additional ONLYOFFICE terms** included in the full, unmodified repository [`LICENSE`](LICENSE). See [`NOTICE.md`](NOTICE.md), [the pinned upstream source](https://github.com/ONLYOFFICE/sdkjs/tree/v9.4.0.129) and [artwork provenance](plugin/resources/PROVENANCE.md). This project is an unofficial modification; ONLYOFFICE's trademarks are not licensed by the AGPL.

The ordinary editing path does not require a cloud account or a separately running X11 bridge. SDKJS is downloaded from GitHub during the build. The plugin currently references an HTTPS-hosted ONLYOFFICE `plugins.js` helper. Optional local developer telemetry at `127.0.0.1:39169` is disabled by default and is not required for editing.

For troubleshooting, architecture, precise validation history and supported rollback behavior, read the [English technical documentation](DOKUMENTACIO_EN.md).
