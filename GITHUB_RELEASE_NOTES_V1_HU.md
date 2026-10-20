# ONLYOFFICE Native Overtype v1.0.0-rc.1

**Nem hivatalos, kísérleti kiadási jelölt; NEM stabil v1.0.0.**

A natív Insert/Overtype és a 10 másodperces Undo-motor a `v0.9.0-beta.2` verzióval megegyezik. Az új csomag a rögzített upstream SDKJS-ből végzett GitHub Actions buildet, ellenőrző teszteket és angol–magyar kiadási dokumentációt tartalmazza.

**Korlát:** a korábbi 29/29 GUI-teszt az 1,8 másodperces RC5-re vonatkozik. A hordozható, 10 másodperces változat 4/4 kézi próbát teljesített a második gépen; az összetett DOCX-tesztek és a 10 s-os teljes GUI-regresszió még hiányoznak.

**Kizárólag:** Linux Mint 22.3 + Cinnamon X11 + ONLYOFFICE Desktop Editors 9.4.0-129 DEB. Telepítés: `bash run.sh --check`, `--build`, `--install`, `--status`; visszaállítás: `--rollback`. Előbb zárd be az ONLYOFFICE-ot, és távolítsd el a régi X11-es segédet. Fontos dokumentummal egyelőre ne tesztelj.

Az eredeti ONLYOFFICE SDKJS szerzője: Ascensio System SIA. Licenc: AGPLv3 és az eredeti további feltételek.
