# ONLYOFFICE Native Overtype 0.9.0-beta.1 – javasolt GitHub Release-leírás

> **Nem hivatalos, kísérleti beta.** A kiadási jelölt Névjegy/licencfelülete és Undo/Redo működése a ThinkPad T470s-en ellenőrzött (2026-10-11). A komplex dokumentumok és a 10 másodperces build teljes automatizált regressziója nem igazolt.

Kísérleti, nem hivatalos natív **Insert/Overtype** mód az ONLYOFFICE Desktop Editors Word-szerkesztőhöz. Nem az ONLYOFFICE gyártója által fejlesztett, jóváhagyott vagy támogatott megoldás.

**Célplatform:** Linux Mint 22.3 / X11 / hagyományosan telepített ONLYOFFICE Desktop Editors **9.4.0-129**. Más rendszerekre és verziókra nem alkalmas.

**Fő funkciók:** `Insert` kapcsolás, Plugins/Overtype szalaggomb; bekezdéshatárokat és kijelöléseket óvó karakterfelülírás; legfeljebb 10 másodperces betűközöket egy Undo-egységbe összevonó RC5-kezelés; eredeti Word-bundle-ökről készített root biztonsági mentés és visszaállítás.

**Hitelesített eredmények, 2026-10-11:** korábbi izolált RC5 (1,8 s) **29/29 GUI PASS**; a hordozható 10 s-os forrásbuild egy második Linux Mint gépen sikeresen települt, és **4/4 felhasználói kézi teszt PASS** (alapfelülírás, lassú Undo/Redo, normál beszúrás, DOCX mentés és újranyitás). A 10 s-os kiadáson teljes 29-es automatizált teszt még nem történt.

**Telepítés**: kibontás után, normál felhasználóként:

```bash
bash run.sh --check
bash run.sh --build
bash run.sh --install
bash run.sh --status
```

**Visszaállítás**: az összes ONLYOFFICE-ablak bezárása után `bash run.sh --rollback`. Régi X11-es Overtype-helper mellett ne telepítsd.

**Fontos korlátok:** a telepítő két gyári Word JS-bundle-t cserél; az ONLYOFFICE-frissítés a módosítást felülírhatja. Komplex DOCX-szerkezetek, együttműködés és összetett Unicode-karakterek nem kaptak átfogó tesztelést. Fontos dokumentumokon való éles használatra jelen béta nem minősített.

A teljes magyar műszaki és biztonsági dokumentáció a `DOKUMENTACIO_HU.md` fájlban olvasható.

Eredeti fejlesztő: **Ascensio System SIA / ONLYOFFICE**. SDKJS: GNU AGPLv3 és upstream kiegészítő feltételek. Teljes eredeti licenc: https://github.com/ONLYOFFICE/sdkjs/blob/v9.4.0.129/LICENSE
