# ONLYOFFICE Native Overtype — technical handover and validation report

**Document date:** October 11, 2026.\
**Project release:** `v0.9.0-beta.1` and its source-only RC5/10-second implementation; later documentation/translation updates may be present on `main`.\
**Status:** unofficial functional beta tested on a narrowly specified Linux environment. This is **not** an upstream ONLYOFFICE feature, a comprehensive document-integrity certification, or a claim of general compatibility.

[Back to English README](README.md) · [Magyar dokumentáció](DOKUMENTACIO_HU.md) · [License](LICENSE) · [Release notes](GITHUB_RELEASE_NOTES_EN.md)

## 1. Background and objectives

The project adds a persistent Microsoft Word-style **Insert/Overtype (INS/OVR)** mode to ONLYOFFICE Desktop Editors' word processor. In INS mode, typed text is inserted at the cursor; in OVR mode, typing replaces the next ordinary character when the editor can safely identify one. The user can toggle the mode with the **Insert** key or the Overtype action on the **Plugins** ribbon. The existing **Ctrl+Insert** copy and **Shift+Insert** paste shortcuts should continue to work.

An earlier experimental package, `onlyoffice-overtype-x11`, simulated overtype by generating an external X11 **Delete** event after character insertion. That helper had no understanding of the DOCX structure and failed at paragraph boundaries, empty paragraphs, selected text and Undo. It was replaced with a native implementation inside the ONLYOFFICE SDKJS Word engine. **Do not run or install the legacy X11 helper together with the native beta.**

This behavior cannot be implemented reliably through the supported, ordinary plugin API alone. The native version therefore changes **two installed JavaScript Word bundles** under `/opt/onlyoffice/desktopeditors`. The toolbar plugin is a separate user-level component that invokes the newly introduced engine method.

## 2. Supported system and reproducibility

| Item | Verified requirement |
| --- | --- |
| OS / desktop | Linux Mint **22.3**, Cinnamon, X11 |
| ONLYOFFICE | Desktop Editors **9.4.0-129**, system DEB installation |
| Installation root | `/opt/onlyoffice/desktopeditors` |
| SDKJS Git tag | `v9.4.0.129` |
| SDKJS commit | `75b53d504bfd81bfa35d59bb57dd9e56f7c9235d` |
| SDKJS Word build | `python3 build/build.py --product word --desktop` |
| Tools / permissions | Git, Python 3, Node.js, `dpkg-query`, `sudo`, an internet connection, at least 4 GiB of free space |
| Out of scope | Other editor versions/builds; Snap/Flatpak/AppImage; Wayland; Windows; macOS; other Linux distributions |

The source patch relies on precise internal symbols and source anchors. Other ONLYOFFICE versions can change these anchors and must not be forced through the version checks. The source package contains SHA-256 input checksums; the installer separately records the hashes of the locally produced and installed Word bundles.

## 3. Architecture and behavior

### 3.1. Native editing engine

The patch is built from the pinned SDKJS `word/Editor/Document.js`. It modifies the key-handling and text-entry paths (notably `CDocument.prototype.OnKeyDown` and `CDocument.prototype.EnterText`), the cursor's current-paragraph positioning rules, and the document History integration.

The per-document flag `_ooOvertypeEnabled` determines whether the engine is in INS or OVR mode. During normal text input, `_ooTryOvertypeOne()` checks whether the next position represents a single ordinary character that can safely be replaced. If so, deletion/replacement and character insertion occur within the **same `StartAction` / `FinalizeAction` document-edit operation**.

**Conservative safeguards:** the patch is intended to avoid deleting structural paragraph markers, merging paragraphs, or overwriting an active text selection. It declines replacement in certain uncertain/embedded structures, table, mathematical, form and revision-related states. At document/paragraph end or on complex Unicode grapheme clusters, it may perform normal insertion rather than force a potentially destructive replacement. These checks reduce risk but **do not prove safety for all possible DOCX objects**.

The original X11-based approach did not provide these engine-level guarantees and is explicitly incompatible with the native mode.

### 3.2. Consecutive overwrite Undo/Redo (RC5)

Each single-character overwrite naturally creates a History action. For word-processor-like Undo, consecutive uninterrupted overwrites must form a single Undo unit.

The intermediate RC2–RC4 attempts stored continuity markers in the previous History point's `Additional` property. However, ONLYOFFICE's `CHistory.prototype.ClearAdditional()` clears that property when a new point is created. The result was that a three-character overwrite `ABCDE` → `AxyzE` required multiple Undo operations, despite passing simplified model tests.

RC5 instead holds History-point continuity markers in a dedicated **`WeakMap` keyed by History-point object identity**. After structural checks, it merges consecutive point `Items` in the correct order while preserving the initial Undo state. Navigation, selections, mouse activity, saving and other history boundaries can interrupt the group. The finalized action is not a simulated series of Ctrl+Z presses; it is a real editor History grouping.

RC5 initially allowed a maximum **1,800 ms** between characters. This passed rapid automated typing but not slower manual typing. The portable source version uses **10,000 ms** between consecutive keystrokes. This is a *gap threshold*; it does **not** make unrelated edits a single Undo transaction. A gap beyond ten seconds or a structural boundary may create a new Undo unit.

Optional developer telemetry can target `ws://127.0.0.1:39169/`. In the published release candidate, this is **disabled by default** and must not be required for editing. Its intended data consists of History metadata rather than document text; the project has not undergone an independent privacy audit.

### 3.3. Toolbar plugin and legal notices

The plugin is installed per user at:

```text
~/.local/share/onlyoffice/desktopeditors/sdkjs-plugins/{A360C0D9-711B-4C90-BFB4-58AC023074E6}/
```

`plugin/config.json`, `index.html`, `quick_action.js`, `about.html`, and `resources/icon*.png` supply the toolbar actions. The Overtype action calls the native `OOOvertypeToggle` engine method; it **requires the patched Word bundle**. An **About & Licenses** action provides upstream copyright information, the modification notice and links to the applicable full license. Updated bilingual UI wording is a separate UI-only change and should receive targeted GUI verification before being tagged in a later beta.

The plugin HTML currently loads the upstream SDKJS plugin helper from `https://onlyoffice.github.io/sdkjs-plugins/v1/plugins.js`, introducing an HTTPS/CDN dependency. It is not the legacy X11 bridge and the normal editing path does not rely on a localhost server.

## 4. Repository contents and build artifacts

| Path | Purpose |
| --- | --- |
| `run.sh` | Entry point for all supported user commands |
| `portable.py` | Environment checks, source build, installation, integrity verification, status and rollback |
| `patches.py` | Reproduces the RC5/10-second patch against expected source anchors |
| `src/patch_sdkjs.py` | Applies the pinned SDKJS source patch |
| `src/native_logic*.js` | Native text replacement logic and surrounding hooks |
| `src/undo_runtime.js`, `src/rc3_runtime.js`, `src/rc4_runtime.js`, `src/rc5_runtime.js` | Evolution and final implementation of Undo logic |
| `plugin/` | Standalone toolbar plugin, legal notice, resources |
| `tests/` | Python installer/patch tests and Node.js runtime/UI checks |
| `tools/prepare_github_release.py` | Copies and checks the exact upstream license, regenerates checksums and creates the release ZIP |
| `LICENSE`, `NOTICE.md` | Complete unchanged upstream license, attribution and modification notices |
| `SHA256SUMS` | Per-source-file SHA-256 manifest for the repository/release |
| `README.md`, `DOKUMENTACIO_EN.md` | English entry point and technical report |
| `README_HU.md`, `DOKUMENTACIO_HU.md` | Hungarian documentation |

No complete upstream SDKJS checkout, prebuilt modified Word bundles, private test documents or personal logs are distributed in this source-only repository. The builder clones the upstream source into the user's cache, verifies the pinned commit and applies only expected source patches.

## 5. Clean-machine installation

**Prerequisites:** an unmodified compatible ONLYOFFICE installation; an X11 session; no open editor process; no running legacy X11 overtype bridge or its autostart; no conflicting Overtype plugin under the target GUID.

Extract the release ZIP. In the extracted project directory, as a **normal non-root user**, execute:

```bash
bash run.sh --check
bash run.sh --build
bash run.sh --install
bash run.sh --status
```

- **`--check`** is a read-only preflight; version/session/conflict checks can fail fast. A preflight against already-patched vendor files can intentionally refuse further installation.
- **`--build`** uses `~/.cache/onlyoffice-overtype-native-940129/` and writes the candidate bundles and manifest without altering `/opt`.
- **`--install`** requires interactive confirmation with `TELEPITES`, then uses privileged operations only when needed; it first stores and verifies factory backups before replacing the bundles and installing the user plugin. Do **not** run the whole script under `sudo`.
- **`--status`** checks the installed native bundles, privileged backup, plugin and user state after installation.

The exact two system files replaced are:

```text
/opt/onlyoffice/desktopeditors/editors/sdkjs/word/sdk-all.js
/opt/onlyoffice/desktopeditors/editors/sdkjs/word/sdk-all-min.js
```

The standard installation locations for state and backups are:

```text
/var/lib/onlyoffice-overtype-native-portable-940129/                      # root-only factory backup
~/.local/state/onlyoffice-overtype-native-940129/                         # user state
~/.local/share/onlyoffice/desktopeditors/sdkjs-plugins/{A360C0D9-711B-4C90-BFB4-58AC023074E6}/
```

File replacement is safeguarded by hashes and a backup-first transaction; if deployment fails, the installer attempts restoration. Do not bypass checks or manually substitute modified bundles from another release. The portable installer does **not** silently remove the old `onlyoffice-overtype-x11` package.

### 5.1. Expected post-install test

Use a disposable DOCX. Type `ABCDE`, place the cursor after `A`, toggle OVR, and enter `xyz`. Expected result: `AxyzE`. One Ctrl+Z should restore `ABCDE`; Ctrl+Y should restore `AxyzE`. Repeat with 2–3-second pauses, toggle back to insertion mode, and save/reopen the DOCX. Open the plugin's About panel and check that the original developer/license notice is accessible. Stop and roll back if any step fails.

## 6. Rollback and recovery

Close **all** ONLYOFFICE windows. Keep the extracted source directory and the candidate build manifest available until rollback is no longer needed. From the same project root:

```bash
bash run.sh --rollback
```

The rollback uses the original root-only backups and validates the factory file hashes, then removes the standalone plugin and user state created by this installer. An unexpected external modification can cause a safe stop rather than a forced overwrite. **Never manually delete backups to work around such an error.** After a successful `ROLLBACK PASS`, verify that the native plugin is absent and stock ONLYOFFICE opens normally.

**Two different installation generations were tested:** the original ThinkCentre M900 used the earlier RC5 developer installer with its own backup/rollback path. The ThinkPad T470s used this independent portable installer. Their backup layouts must **not** be interchanged. For the older developer installation, use its original `ONLYOFFICE_Overtype_Native_Final_9_4_0_129/install.sh --rollback` procedure.

## 7. Validation history and evidence

| Stage | Recorded result | Interpretation |
| --- | --- | --- |
| Legacy X11 helper, 29 scenarios | **23 PASS / 6 FAIL** | External Delete events were unsafe for paragraph structure, selection and Undo |
| Early native RC1.6 | **27 PASS / 1 FAIL / 1 save verification blocked** | Basic editing worked; grouped multi-character Undo did not |
| RC2–RC4 targeted Undo tests | The three-character Undo test repeatedly failed | History points were not merged correctly |
| RC4 diagnostics | `previous-point-is-not-overwrite` | `ClearAdditional()` invalidated continuity metadata |
| RC5 WeakMap, isolated editor | **3/3 Undo PASS; 29/29 full GUI PASS** | Verified on the original **1.8-second-threshold** build, including saved DOCX contents |
| First machine, installed RC5 | `INSTALL PASS`, both native bundles recognized | System-wide engine installation verified |
| First machine, manual slow typing | One Ctrl+Z insufficient, fast typing passed | 1,800 ms threshold was too restrictive |
| First machine, 10-second patch | `PATCH PASS` and functional manual follow-up | Improvement reported; not a new 29-test full automated run |
| ThinkPad T470s portable build/install | `CHECK PASS`, `BUILD PASS`, `INSTALL PASS`, both bundles verified | Reproducible source-based deployment demonstrated on a second machine |
| ThinkPad T470s manual acceptance | **4/4 PASS** | Basic OVR, slow Undo/Redo, INS mode, DOCX save/reopen |
| Publication UI smoke test | **About & Licenses PASS; OVR and Undo/Redo PASS** | New notice/toolbar UI reported working on ThinkPad |
| GitHub Actions | **Source checks PASS** for initial and documentation commits | Unit/source validation, not comprehensive end-to-end document testing |

The second-machine manual results and deployment logs were provided by the user. There is **no independent full 29-case automated run of the portable 10-second build**, no exhaustive complex-DOCX matrix, and no claimed cross-platform validation. Failed intermediate RC builds remain part of the engineering history.

### 7.1. What the 29-case suite covered

Ordinary insertion versus overwrite; mode toggling; document and paragraph ends; preservation of blank paragraphs; replacing selections; crossing bold/italic runs; spaces; single/multiple Undo and Redo; Hungarian accented characters `ő`, `ű`, `á`, `é`; high-speed and repeated characters; navigation, Backspace and Ctrl+Home; saved DOCX content comparison. This is meaningful coverage but does not guarantee structural safety for every document.

### 7.2. Known missing regression coverage

Complex tables/cells, footnotes/endnotes/headers/footers, comments, tracked changes and concurrent editing, content controls and forms, complex fields and embedded objects, mixed Unicode combining marks/emoji/grapheme boundaries, alternative keyboard layouts and IME, large DOCX files, package upgrades/unexpected vendor changes, and a full 29-case run against the **10-second released source build**.

## 8. Troubleshooting

**`--check` fails:** verify the exact installed package version via `dpkg-query`, the X11 session via `echo "$XDG_SESSION_TYPE"`, that all `DesktopEditors` processes are closed, and that neither the old X11 helper nor another Overtype plugin is active. Legacy bridge conflicts can include port `39167` or an autostart entry.

**`--build` passed but install refuses:** inspect candidate/`manifest.json`, the preflight output and recorded original bundle hashes. Do not skip source pinning or integrity checks.

**Undo requires multiple presses:** check whether any typing gap exceeded **10 seconds** or whether navigation, selection, saving or mode switching interrupted the group. Reproduce only in a disposable document; capture installer `--status` if a continuous 2–3-second typing sequence still fails.

**Feature disappears after an ONLYOFFICE upgrade:** package updates can overwrite modified Word bundles. **Do not copy the old 9.4.0-129 bundles into the upgraded version.** Wait for a separately validated port to that exact version.

**Rollback refuses to continue:** preserve the recorded error, output of `--status`, original root backup and build manifest. A safe stop may indicate unexpected external changes. Do not force file replacement without examining the state.

## 9. Licensing, origin, privacy and publication

- **Original developer:** Ascensio System SIA / ONLYOFFICE. This project is not affiliated with or endorsed by the original developer.
- **Upstream:** [ONLYOFFICE SDKJS tag `v9.4.0.129`](https://github.com/ONLYOFFICE/sdkjs/tree/v9.4.0.129) and its [full licensing text](https://github.com/ONLYOFFICE/sdkjs/blob/v9.4.0.129/LICENSE).
- **License:** upstream SDKJS is subject to the GNU **AGPLv3** plus ONLYOFFICE's supplementary terms in the full `LICENSE`. These include retaining attribution and copyright notices, clearly indicating modifications and dates, suitable accessible notices in modified user interfaces, and no automatic trademark license. Non-code upstream assets may have separate conditions.
- **Distribution:** the source-only release archives include the unchanged upstream `LICENSE`, `NOTICE.md` and generated icon provenance. They do not redistribute entire compiled patched ONLYOFFICE bundles. Other distribution forms still require a fresh licensing review.
- **Network and data:** SDKJS is downloaded from GitHub when building. The plugin references an HTTPS-hosted ONLYOFFICE helper script. Ordinary text editing does not require an account or a separate local bridge. Optional development-only WebSocket diagnostics at `127.0.0.1:39169` are disabled by default and intended to handle History metadata, not document text; no independent security/privacy audit has been conducted.
- **Source/package consistency:** use `python3 tools/prepare_github_release.py` on a machine containing the pinned SDKJS Git checkout. The script verifies the upstream license blob SHA `53bc62cde3c705aa2d03b895b966bd6250f389ae`, updates `SHA256SUMS`, and builds the source ZIP.

The software is openly distributed as a beta, without a claim of comprehensive legal review or broad safety certification. Test modified UI and licensing notices after any source change. An updated `README.md`, documentation or plugin UI committed to `main` **does not retroactively change previously published tag assets**; subsequent code/UI changes should receive a new beta tag and release asset.

### 9.1. Release criteria

For a supported-system beta: pinned upstream and license, source checksum gate, clean installer/rollback, successful CI, targeted interface/Undo/DOCX smoke tests, and clear warnings about unsupported scenarios. The current state meets the historical **beta.1** publication milestone, but subsequent localization/UI updates must be verified and released separately.

A stable `v1.0.0` should require a substantially broader DOCX regression suite, update/rollback scenarios and independently reproducible results.

### 9.2. Repository hygiene

Keep personal files, logs, terminal credentials, cache directories, SDKJS clones, built `candidate/` bundles and root backups **out** of Git. Prefer reproducible source patches, tag/commit pinning, intact license notices and a documented rollback. GitHub Actions source tests are evidence of source integrity, not a substitute for GUI or document-integrity testing.

## 10. State of the two validation systems

**ThinkCentre M900:** older RC5 Word engine was installed system-wide; a separately backed-up 10-second threshold adjustment was applied. Its rollback and backup layout belong to the original RC5 developer installer, *not* to `portable.py`.

**ThinkPad T470s:** previous `onlyoffice-overtype-x11 0.5.0` was removed. A fresh pinned SDKJS checkout was built via the portable installer; installation and hash-based status checks passed; four manual functional/saved-DOCX cases passed, as did targeted About/Undo UI checks.

Preserve each machine's own installer files, privileged factory backups and candidate manifests. Do not perform cleanup or try to share root backup files between systems until rollback has been examined.

## 11. GitHub release history and handover

The source was pushed to [`Rambo-Junior/onlyoffice-native-overtype`](https://github.com/Rambo-Junior/onlyoffice-native-overtype). The initial source commit was `e555a7c`, followed by documentation corrections at `f093772`. GitHub Actions source checks passed for both. On October 11, 2026 the repository was made **public**, and [`v0.9.0-beta.1`](https://github.com/Rambo-Junior/onlyoffice-native-overtype/releases/tag/v0.9.0-beta.1) was published as a **prerelease** with its source ZIP attached.

The legal notice/toolbar and generated icons were tested on the ThinkPad before that release; however, the native engine and 10-second Undo threshold remain restricted to the pinned supported environment. The next practical priorities are accessible English-language documentation and UI, full 10-second-build GUI regression, broader complex-DOCX testing and eventual version-port work.

---

**Summary:** The structural risks of the old X11 Delete technique were addressed by moving the replacement into the Word engine. The initial RC5 fixed the observed test-suite failures in the **29/29 pass** isolated run. The subsequent **10-second** Undo improvement was deployed and manually verified on a second machine with DOCX save/reopen. The public source beta is useful for controlled experimentation on the specified platform, but should not be presented as a universally safe, officially supported or stable ONLYOFFICE feature.

## v0.9.0-beta.2 — English documentation and bilingual interface

The `beta.2` release adds an English-first README and technical documentation, preserves the original Hungarian documents, and introduces English/Hungarian About & Licenses text. The core RC5/10-second editor patch is unchanged. The previously reported 29-case automated GUI regression refers to the original 1.8-second RC5 build, not beta.2. The 10-second portable build and bilingual About panel were independently checked manually on ThinkPad T470s. The full automated suite and complex document-safety cases remain outstanding.
