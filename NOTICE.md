# NOTICE – Unofficial modified ONLYOFFICE SDKJS extension

This project is **not affiliated with, endorsed by, or supported by Ascensio System SIA / ONLYOFFICE**. It modifies the ONLYOFFICE SDKJS Word editor to add optional keyboard overtyping and groups consecutive character overwrites for Undo/Redo. The original software is Copyright © 2009–2026 Ascensio System SIA.

The official SDKJS repository is https://github.com/ONLYOFFICE/sdkjs ; the exact upstream source for this beta is tagged `v9.4.0.129` at commit `75b53d504bfd81bfa35d59bb57dd9e56f7c9235d`.

The upstream SDKJS is under the GNU Affero General Public License version 3, with supplementary terms in its LICENSE; see https://github.com/ONLYOFFICE/sdkjs/blob/v9.4.0.129/LICENSE . The license requires attribution, modification notices, and appropriate legal notices in modified user interfaces. Trademark rights are not granted. The patch was developed in October 2026. This project remains a **beta**. Installation and four manual acceptance cases were verified on a second Linux Mint machine on 2026-10-11; a public-release licensing review is still required.

The build scripts do not redistribute compiled ONLYOFFICE bundles. They download the pinned upstream source into the user's own machine, apply changes, and build user-owned modified JS files. Any subsequent distribution of modified compiled files must also comply with the upstream license and other applicable terms. Do not remove upstream copyright and license notices.

## Beta release changes (2026-10-11)

A separate **About & Licenses** button displays the original developer, the modified nature of this SDKJS build, and links to the pinned full upstream license and source. The OVR icons were created for this release; see `plugin/resources/PROVENANCE.md`. The optional localhost WebSocket diagnostics are disabled unless a developer enables `doc._ooOvertypeDebug` explicitly. The original upstream `LICENSE` must be copied unchanged from the pinned commit before public release. Original SDKJS copyright and attribution must remain intact.
