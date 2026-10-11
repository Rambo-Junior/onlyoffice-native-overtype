# ONLYOFFICE Native Overtype – portable beta 0.9.0-beta.1

**Kísérleti, nem hivatalos módosítás** az ONLYOFFICE Desktop Editors alkalmazáshoz. Nem ONLYOFFICE által támogatott funkció.

**Egyetlen támogatott célplatform:** Linux Mint 22.3, X11 (Cinnamon), ONLYOFFICE Desktop Editors **9.4.0-129**, hagyományos DEB telepítés. Más verzióval, Flatpak/Snap alatt, Waylanden vagy Windows/macOS rendszeren **nem telepíthető**.

Az `Insert` kapcsolja az INS/OVR módot. Felülíráskor az aktuális bekezdés következő egyszerű karakterét helyettesíti, a dokumentum szerkezeti határait védve. A folyamatos gépelést legfeljebb **10 másodperces** betűközökig egy Ctrl+Z-egységbe csoportosítja; a navigáció, mentés és kijelölés külön művelet. A szalag **Overtype** gombja is kapcsol.

## Mi van a csomagban?

A forrásalapú patchszkriptek, natív Overtype plugin, telepítő, ellenőrzések és visszaállító. **NINCS benne előre módosított ONLYOFFICE-motor vagy teljes alkalmazás.** A builder a hivatalos SDKJS rögzített `v9.4.0.129` Git-tagből (`75b53d504bfd81bfa35d59bb57dd9e56f7c9235d`) épít. Az eredeti, módosítás nélküli forrást a GitHubról tölti le; szükséges az internet, `git`, `node`, `python3`, `sudo`, és legalább 4 GiB szabad hely.

A builder nem módosítja a `/opt/onlyoffice` telepítést. Az élesítés csak külön parancsra, interaktív `TELEPITES` jóváhagyással történik. Ezt a csomagot **ne telepítsd a már natív RC5-tel módosított első gépre**; ott a korábbi, működő verzió maradjon.

## Második, gyári ONLYOFFICE-os gép: telepítési lépések

Zárd be az ONLYOFFICE-ot, ellenőrizd a verziót: `dpkg-query -W -f='${Version}\n' onlyoffice-desktopeditors`.

Az első **olvasási ellenőrzés**:

```bash
bash run.sh --check
```

Egyedi, csak felhasználói mappában történő forrásletöltés és build:

```bash
bash run.sh --build
```

Ezt követően az éles rendszerfájlok telepítése, **csak ha a build PASS**:

```bash
bash run.sh --install
```

A sikeres telepítés után:

```bash
bash run.sh --status
```

**Visszaállítás:**

```bash
bash run.sh --rollback
```

A gyári két SDKJS-fájlról a rendszer `/var/lib/onlyoffice-overtype-native-portable-940129` könyvtárban készül root-only mentés. A friss Overtype plugin a felhasználói ONLYOFFICE pluginmappában jön létre; korábbi, azonos GUID-jú plugin esetén a telepítő **nem írja felül**.

A telepítő **elutasítja** a már módosított Overtype-motort, a foglalt X11-segédportot, az aktív korábbi Overtype automatikus indítást, a nyitott ONLYOFFICE-ot és a nem megfelelő verziót. Nincs automatikus régi hídleállítás.

## Kézi ellenőrzés a második gépen

Csak eldobható DOCX-ben: `ABCDE` → kurzor az A után → `Insert` → `xyz` → `AxyzE`; egy `Ctrl+Z` → `ABCDE`; `Ctrl+Y` → `AxyzE`. Ismételd meg **2–3 másodperces karakterközökkel**. Kapcsold vissza az INS módot, mentsd DOCX-ként, zárd be és nyisd meg újra. Ha bármelyik eltér, **rollback**.

A korábbi izolált RC5 (1,8 s) build 29/29 GUI-tesztet teljesített. A 10 másodperces változat az első gépen kézzel működött. A jelen forráscsomagból a ThinkPad T470s gépen külön lefordított és telepített változat a **négyből négy kézi füsttesztet teljesítette**: felülírás, lassú gépelés Undo/Redo, normál beszúrás, DOCX mentés és újranyitás (2026-10-11; felhasználó által közölt eredmény). Az eredeti, 1,8 másodperces RC5 build **29/29** automatizált GUI-tesztet teljesített egy másik gépen. A 10 másodperces hordozható buildhez **nem történt új 29 esetes automatizált futtatás**. A kiadás ezért továbbra is **beta**, nem stabil v1.0.0.

## Jelenlegi ismert korlátok

A szerkesztőmotor rendszerszintű módosítása nem szabványos, nem támogatott ONLYOFFICE plugin API. Az ONLYOFFICE-frissítés felülírhatja a patchelt fájlokat. A táblázatok, lábjegyzetek, megjegyzések, követett változások, védett mezők, összetett Unicode-gráfémák és más komplex DOCX-funkciók nincsenek átfogóan tesztelve. Fontos dokumentumokon ne használd éles munkára a beta változatot.

## Licenc, eredet és nyilvános kiadás

A módosított ONLYOFFICE SDKJS-forrás **AGPLv3-only**, és az eredeti Ascensio System SIA további feltételei is alkalmazandók. A teljes, változatlan upstream `LICENSE` hozzáadása kötelező a **publikált** archívumhoz, illetve a repositoryhoz; csak URL nem elegendő. Az ikonok új, saját grafikai elemek (lásd `plugin/resources/PROVENANCE.md`). A bővítmény az ONLYOFFICE szalagon külön **Névjegy és licencek** gombbal jeleníti meg a módosításról és az eredeti szoftverről szóló tájékoztatást, valamint a licenclinket. A fejlesztői WebSocket-diagnosztika a nyilvános változatban alapértelmezés szerint tiltott.

**Kiadási licenc előkészítése (azon a gépen, ahol `--build` már sikeres):**

```bash
python3 tools/prepare_github_release.py
```

A program a helyi, rögzített SDKJS Git-commit **változatlan teljes licencfájlját** másolja a `LICENSE` fájlba, ellenőrzi annak Git SHA-ját, újraszámolja a `SHA256SUMS` fájlt és előállítja a publikálható forrás-ZIP-et. Ha nincs meg a teljes licenc, a GitHub Actions licencekapu hibával leáll.

**Kiadási korlát:** az About ablak és az alapból letiltott diagnosztika új kódmódosítás, így a korábbi 4/4 kézi és 29/29 automatikus siker **nem igazolja automatikusan ezt az új csomagot**. A kiadási jelölt Névjegy/licencpanelje és natív felülírás/Undo/Redo funkciója a ThinkPad T470s-en 2026-10-11-én kézi GUI-tesztben PASS. A DOCX mentés/újranyitás a pluginfrissítés előtti RC5/10s változaton PASS. A teljes rollback éles próbája és a 10 s-os build 29-es automata regressziója még hiányzik. A 29/29 QA a régebbi 1,8 másodperces RC5 build eredménye.

A részletes dokumentáció: [`DOKUMENTACIO_HU.md`](DOKUMENTACIO_HU.md), a kiadás korlátai: [`RELEASE_GATE.md`](RELEASE_GATE.md).
