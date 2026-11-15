# ONLYOFFICE Native Overtype – v1.0.0-rc.2 – kiadási jelölt

**Kísérleti, nem hivatalos módosítás** az ONLYOFFICE Desktop Editors alkalmazáshoz. Nem ONLYOFFICE által támogatott funkció.

**Támogatott célplatform:** Linux Mint 22.3, X11 (Cinnamon), ONLYOFFICE Desktop Editors **9.4.0-129** vagy **10.0.0-169**, hagyományos DEB telepítés (lásd [Támogatott buildek](#támogatott-buildek)). Más verzióval, Flatpak/Snap alatt, Waylanden vagy Windows/macOS rendszeren **nem telepíthető**.

Az `Insert` kapcsolja az INS/OVR módot. Felülíráskor az aktuális bekezdés következő egyszerű karakterét helyettesíti, a dokumentum szerkezeti határait védve. A folyamatos gépelést legfeljebb **10 másodperces** betűközökig egy Ctrl+Z-egységbe csoportosítja; a navigáció, mentés és kijelölés külön művelet. A szalag **Overtype** gombja is kapcsol.

### Támogatott buildek

A telepítő a `dpkg` szerinti verziót olvassa, és pontosan egy rögzített **profilhoz** köti magát; minden más build elutasítva. Az állapot-, cache- és mentési útvonalak profilonként külön vannak (`940129` = 9.4.0-129, `1000169` = 10.0.0-169).

| Telepített build | SDKJS tag / commit | További upstream addon | Állapot |
| --- | --- | --- | --- |
| **9.4.0-129** | `v9.4.0.129` / `75b53d504bfd81bfa35d59bb57dd9e56f7c9235d` | nincs (változatlan) | Validált, lásd lent |
| **10.0.0-169** | `v10.0.0.169` / `3679e0375a758d7dc59d31337a45461be3525ed8` | `sdkjs-forms` `v10.0.0.169` / `0148c8ed3f799136431be49d4d83b4064fbafd01` | Forrás/build/telepítő ellenőrizve; fejlesztői szerkesztőteszt; **teljes GUI-regresszió még nincs dokumentálva** |

#### ONLYOFFICE 10.0.0-169

*Ellenőrizve (automatikusan, nem GUI-teszt):* minden forrás-patch horgony pontosan egyszer illeszkedik; a csoportosítás által tükrözött History/Undo kód (`CheckUnionLastPoints`) és a szövegbeviteli út (`CDocument.EnterText`) azonos a 9.4.0.129-cel; mind a 34 motor-API kanári minta jelen van az épített Word-bundle-ben; mindkét lefordított bundle átmegy a `node --check`-en; a hivatalos 10.0.0-169 DEB fájljainak másolatán teljes próbafutás (build -> telepítés -> státusz -> visszaállítás) az eredeti bájtokat állította vissza. Az `sdk-all.bin` (V8 kódgyorsítótár, a 9.4.0-129-ben is megvan) érintetlen marad.

*Kezelt eltérések:* a `v10.0.0.167`-`170` upstream tagek egy commitra mutatnak, ezért a tag-ellenőrzés `git tag --points-at`-et használ `git describe` helyett; a hivatalos 10.0.0-169 bundle tartalmazza a `sdkjs-forms` (OFORM) addont, ezért ez a profil ugyanazzal a rögzített addonnal épít (a 9.4.0-129 profil az eredeti, addon nélküli buildet tartja); a plugin explicit `background` típusú és `autostart`-os (az ONLYOFFICE 10 magától indítja; a korábbi `unvisible` értéket mindkét verzió csendben `background`-nak vette).

*Tesztelési korlát:* a fejlesztő ONLYOFFICE 10 alatti tesztelésről számolt be; a pontos GUI-eredmények és a teljes 29 esetes regresszió nincsenek dokumentálva. A 10.x módosította a `StartAction`/`FinalizeAction` működését (redo-pontok mentése/visszaállítása); az Undo-csoportosítás a `FinalizeAction` után, csak nem üres felülíró műveletnél fut, ütközés nem várható, de éles használat előtt kézzel próbáld ki az Undo/Redo-t (lásd az `ABCDE` tesztet). Ha az `Insert` telepítés után sem csinál semmit: a `--status` mutasson `PORTABLE RC5/10s`-t, indítsd újra teljesen az ONLYOFFICE-ot, nézd meg, hogy az Overtype engedélyezve van-e a Pluginek között; ha így sem működik, `--rollback`, és jelezd - elsődleges gyanú a V8 kódgyorsítótár.

*Másik 10.x build?* `python3 tools/probe_profile.py <dpkg-verzió>` levezeti a pineket, lefuttatja a teljes build-ellenőrzést, és kiír egy `PROFILES` bejegyzést. GUI-tesztet nem helyettesít.

## Mi van a csomagban?

A forrásalapú patchszkriptek, natív Overtype plugin, telepítő, ellenőrzések és visszaállító. **NINCS benne előre módosított ONLYOFFICE-motor vagy teljes alkalmazás.** A builder a hivatalos SDKJS telepített buildhez rögzített Git-tagjéből (lásd Támogatott buildek) épít. Az eredeti, módosítás nélküli forrást a GitHubról tölti le; szükséges az internet, `git`, `node`, `python3`, `sudo`, és legalább 4 GiB szabad hely.

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

A gyári két SDKJS-fájlról a rendszer `/var/lib/onlyoffice-overtype-native-portable-<profil>` könyvtárban (`<profil>`: `940129` vagy `1000169`) készül root-only mentés. A friss Overtype plugin a felhasználói ONLYOFFICE pluginmappában jön létre; korábbi, azonos GUID-jú plugin esetén a telepítő **nem írja felül**.

A telepítő **elutasítja** a már módosított Overtype-motort, a foglalt X11-segédportot, az aktív korábbi Overtype automatikus indítást, a nyitott ONLYOFFICE-ot és a nem megfelelő verziót. Nincs automatikus régi hídleállítás.

## Kézi ellenőrzés a második gépen

Csak eldobható DOCX-ben: `ABCDE` → kurzor az A után → `Insert` → `xyz` → `AxyzE`; egy `Ctrl+Z` → `ABCDE`; `Ctrl+Y` → `AxyzE`. Ismételd meg **2–3 másodperces karakterközökkel**. Kapcsold vissza az INS módot, mentsd DOCX-ként, zárd be és nyisd meg újra. Ha bármelyik eltér, **rollback**.

A korábbi izolált RC5 (1,8 s) build 29/29 GUI-tesztet teljesített. A 10 másodperces változat az első gépen kézzel működött. A jelen forráscsomagból a ThinkPad T470s gépen külön lefordított és telepített változat a **négyből négy kézi füsttesztet teljesítette**: felülírás, lassú gépelés Undo/Redo, normál beszúrás, DOCX mentés és újranyitás (2026-10-11; felhasználó által közölt eredmény). Az eredeti, 1,8 másodperces RC5 build **29/29** automatizált GUI-tesztet teljesített egy másik gépen. A 10 másodperces hordozható buildhez **nem történt új 29 esetes automatizált futtatás**. A kiadás ezért továbbra is **kiadási jelölt**, nem stabil v1.0.0.

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

**0.9.0-beta.2 frissítés:** angol dokumentáció és kétnyelvű Névjegy/licencfelület; a natív Overtype-motor változatlan.
