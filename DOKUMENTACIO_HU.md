# ONLYOFFICE Native Overtype – egységes műszaki átadási dokumentáció

**Dokumentumállapot:** 2026. október 11., második gépes teszt után.\
**Vizsgált kiadás:** `0.9.0-beta.1`, RC5/10s natív felülírás; **nem hivatalos ONLYOFFICE-kiegészítés**.\
**Minősítés:** funkcionális beta a lent megnevezett célkörnyezetre. **Nem** általánosan kompatibilis, nem teljes dokumentumbiztonsági tanúsítás, és a nyilvános kiadás jogi felülvizsgálata még hátravan.

## 1. A projekt célja és előzménye

Az ONLYOFFICE Desktop Editors Word-szerkesztőjében Word-szerű, tartósan kapcsolható `Insert`/`Overtype` (INS/OVR) üzemmód bevezetése. INS módban a gépelés beszúr, OVR módban a soron következő, egyszerű karakter felülíródik. A felhasználó az `Insert` billentyűvel vagy a Plugins szalagon látható **Overtype** gombbal kapcsolhatja az üzemmódot. Az `Insert` mellett a `Ctrl+Insert` és `Shift+Insert` meglévő másolás/beillesztés funkcióját meg kell őrizni.

A korábbi `onlyoffice-overtype-x11` megoldás az X11 billentyűeseményekre épült; egy beszúrás után külső `Delete` eseménnyel igyekezett elérni a felülírást. Ez a dokumentumszerkezetet nem ismerte, ezért bekezdés-összevonás, üres bekezdés elvesztése, kijelöléses műveletek és Ctrl+Z során hibázott. A régi segéd **nem működhet együtt** a natív megoldással.

A natív változat ezért az ONLYOFFICE `SDKJS` Word motorjában hajtja végre a karaktercserét, ugyanazon dokumentumszerkesztői műveleten belül. Ez *nem* valósítható meg kizárólag a szokásos, támogatott plugin API-val, ezért a program telepített Word JavaScript-motorjának két fájlját módosítja.

## 2. Pontosan támogatott rendszer

| Paraméter | Támogatott érték |
|---|---|
| Operációs rendszer | Linux Mint 22.3, Cinnamon, X11 |
| ONLYOFFICE | Desktop Editors `9.4.0-129`, DEB, `/opt/onlyoffice/desktopeditors` |
| SDKJS | Git tag `v9.4.0.129` |
| Git commit | `75b53d504bfd81bfa35d59bb57dd9e56f7c9235d` |
| Build mód | `python3 build/build.py --product word --desktop` |
| Futtatási előfeltételek | `python3`, Node.js, Git, `sudo`, `dpkg-query`, X11, szabad tárhely, internet |
| Nem igazolt / elutasított | Eltérő ONLYOFFICE-verzió, más csomagolás (Snap/Flatpak), Wayland, Windows, macOS |

A felépítés a rögzített upstream forrás pontos belső függvény- és szöveghorgonyaira támaszkodik. Egy későbbi ONLYOFFICE-frissítés ezeket megváltoztathatja, ezért **más verzióra nem szabad kézzel ráerőltetni**. A kiadáshoz tartozó SHA-256-összegek a csomagforrásokra vonatkoznak; a célgépen létrejövő bundle-ök hashét a buildmanifest és a telepítő külön rögzíti.

## 3. Architektúra és működés

### 3.1. Word motor

A natív módosítás az `SDKJS` `word/Editor/Document.js` fájlban, illetve az ebből épülő Word bundle-ökben érinti a billentyűkezelést (`CDocument.prototype.OnKeyDown`), a karakterbevitel útvonalát (`CDocument.prototype.EnterText`), az aktuális bekezdés pozíciókezelését és a dokumentum History-ját.

Az `Insert` engedélyezi/letiltja a dokumentumhoz kötött felülíró állapotot (`_ooOvertypeEnabled`). Felülíráskor a `_ooTryOvertypeOne()` ellenőrzi, hogy a kurzor következő pozíciója egyetlen biztonságosan cserélhető, egyszerű karakter-e. A következő karakter kijelölése és törlése a betű tényleges beszúrásával azonos `StartAction`/`FinalizeAction` művelet alatt történik.

**Védelmi elvek:** a kód nem kísérel meg felülírást aktív kijelölésen vagy bizonytalan beágyazott szerkezeten; elutasítja a dokumentumvég vagy bekezdésvége átlépését, és bizonyos összetett objektum-, táblázat-, képlet-, űrlap- vagy változáskövetési állapotokat. Több kódpontból álló Unicode-gráfémáknál biztonságosnak ítélt csere helyett normál beszúrás következhet. **A szigorú visszautasítás nem jelenti minden összetett DOCX-eset bizonyított biztonságát.**

### 3.2. Undo/Redo (RC5)

Egy felülírt karakter önálló History-művelet. A Word-szerű folyamatos gépeléshez ezeket egyetlen Ctrl+Z-egységbe kell csoportosítani. Az RC2–RC4 megoldások hibásak voltak, mert az összetartozási metaadatot a History-pont `Additional` mezőjébe tették, miközben az ONLYOFFICE `CHistory.prototype.ClearAdditional()` azt új művelet létrehozásakor üríti.

Az RC5 a folytatásjelölőket külön `WeakMap`-ben, a History-pont objektumazonosságához rendelve kezeli. A szerkesztő megfelelő ellenőrzések után egyesíti az egymást követő változáspontok `Items` tömbjét, meghagyva a visszavonás szempontjából szükséges sorrendet és kezdeti állapotot. Egyesítés csak megszakítatlan, ugyanazon műveletsorozatba tartozó karakterfelülírások között történhet. Navigáció, kiválasztás, egérművelet és mentési határ megszakíthatja a csoportot.

Az eredeti RC5 két felülírás között **1 800 ms** maximális szünetet engedett; kézi, lassabb gépelésnél emiatt két Ctrl+Z kellett. A végső hordozható változatban a küszöb **10 000 ms**. Ez **csoportosítási időablak, nem minden gépelési művelet maximális végrehajtási ideje**. A 10 másodpercnél hosszabb szünet után külön Undo-egység jöhet létre. A csoportba vonás további szerkezeti és előzményfeltételektől is függ.

A kódban megmaradt egy *opcionális*, kizárólag `ws://127.0.0.1:39169/` címre próbálkozó diagnosztikai kapcsolat, amely History-metaadatokat közölhet, **nem dokumentumszöveget**. A program rendes használatához nem kell helyi diagnosztikai szerver; a kapcsolat sikertelenségét elnyeli. Publikus kiadás előtti adatvédelmi és kódtisztasági auditnál javasolt külön átgondolni ennek teljes eltávolítását vagy kikapcsolását.

### 3.3. Toolbar plugin

Az önálló plugin a felhasználó `~/.local/share/onlyoffice/desktopeditors/sdkjs-plugins/{A360C0D9-711B-4C90-BFB4-58AC023074E6}` mappájába kerül. `config.json`, `index.html`, `quick_action.js` és két ikonkép tartozik hozzá. A szalaggomb a módosított motor által felvett belső `OOOvertypeToggle` metódust hívja. Ez csak a megfelelő natív Word-bundle-lel működik.

A plugin HTML-fájlja jelenleg a `https://onlyoffice.github.io/sdkjs-plugins/v1/plugins.js` külső scriptet tölti be. A reprodukálhatóság és offline működés szempontjából ennek viselkedését és eredetét publikálás előtt külön dokumentálni kell. Nem X11-hídon és nem localhost-szolgáltatáson keresztül módosítja a dokumentumot.

## 4. Forráscsomag, könyvtárstruktúra

| Fájl / könyvtár | Szerep |
|---|---|
| `run.sh` | Normál felhasználói parancssori belépési pont |
| `portable.py` | Verzió- és környezetellenőrzés, build, telepítés, státusz, rollback, SHA-256, root mentés |
| `patches.py` | Pontos horgonyokra épülő RC1–RC5/10s bináris build-patch reprodukálása |
| `src/patch_sdkjs.py` | Rögzített upstream `Document.js` forrás patch-elése |
| `src/native_logic.js` és kísérő fájljai | Natív karaktercserélő logika |
| `src/undo_runtime.js`, `rc3_runtime.js`, `rc4_runtime.js`, `rc5_runtime.js` | Undo-fejlesztés technikai állomásainak és végső RC5-nek a forrásai |
| `plugin/` | Önálló szalaggomb és ikonok |
| `tests/` | Telepítő, patchhorgony és 10s Undo-időzítés lokális ellenőrzése |
| `README.md`, `NOTICE.md`, `CHANGELOG.md` | Rövid használati, eredet- és változásinformációk |
| `SHA256SUMS` | A ZIP forrásfájljainak SHA-256 ellenőrzőösszegei |

A csomagban nincs teljes SDKJS-forrás, előre épített módosított Word-motor vagy személyes helyi tesztdokumentum. Az SDKJS pontos tagjét a `git clone` tölti le a felhasználó gépén. A forrás build során a Git commitot és az eredeti `Document.js` blobot is ellenőrző logika fut; csak ismert, elvárt patchhorgonyokat fogad el.

## 5. Második gépes telepítés, állapotellenőrzés

**Feltételek:** támogatott ONLYOFFICE-verzió, X11, bezárt ONLYOFFICE, nincs aktív régi X11 Overtype-híd, nincs már ugyanazon GUID-jú plugin, nincs már telepített másik natív patch.

A ZIP kibontása után a csomag gyökérkönyvtárából, **normál felhasználóként**:

```bash
bash run.sh --check
bash run.sh --build
bash run.sh --install
bash run.sh --status
```

Az `--check` olvasási vizsgálat. A `--build` a `$HOME/.cache/onlyoffice-overtype-native-940129/` alatt fordít, és a `candidate` almappában létrehozza a két Word-bundle-t és a buildmanifestet; nem írja át a telepített szerkesztőt. A `--install` interaktív **`TELEPITES`** megerősítést kér, majd root-jogosultsággal – **előzetes gyári mentés készítése és ellenőrzése után** – cseréli le a Word-bundle-öket. Az önálló plugin felhasználói mappába kerül. A rendszerfile-ok telepítéséhez nem a teljes scriptet kell `sudo`-val futtatni, hanem maga a script hívja a szükséges, korlátozott root-alparancsokat.

A következő két telepített fájl módosul:

```text
/opt/onlyoffice/desktopeditors/editors/sdkjs/word/sdk-all.js
/opt/onlyoffice/desktopeditors/editors/sdkjs/word/sdk-all-min.js
```

**Gyári mentés és plugin:**

```text
/var/lib/onlyoffice-overtype-native-portable-940129/
~/.local/state/onlyoffice-overtype-native-940129/
~/.local/share/onlyoffice/desktopeditors/sdkjs-plugins/{A360C0D9-711B-4C90-BFB4-58AC023074E6}/
```

A telepítő teljes, ellenőrzött gyári mentést tesz közzé a root-mappában, mielőtt a `/opt` fájlokhoz nyúl. A két bundle változtatása atomi fájlcserére épül, siker után SHA-256-tal ellenőrizhető. Hiba esetén automatikus visszaállítással próbálkozik. A visszaállító az eredeti tartalom hashét is ellenőrzi; ismeretlen külső módosítás esetén biztonsági okból elutasíthatja az automatikus folytatást.

Az `--status` **telepítés után használható**; a `--check` újraindítása telepítés után elvárt módon elutasíthatja a már módosított motort. A régi `onlyoffice-overtype-x11` DEB-csomag eltávolítását a hordozható telepítő nem végzi automatikusan.

## 6. Biztonságos rollback

**Minden ONLYOFFICE-ablak legyen bezárva.** A ZIP-ből indított csomagkönyvtárat és a cache-ben lévő `candidate/manifest.json` fájlt addig meg kell tartani, amíg esetleges visszaállításra szükség lehet.

```bash
bash run.sh --rollback
```

A visszaállító a gyári két Word-fájlt a root-only mentésből helyreállítja, a telepítő által létrehozott standalone plugint és a felhasználói állapotot eltávolítja. A script hibátlan `ROLLBACK PASS` kimenete után célszerű ellenőrizni, hogy a natív plugin már nincs jelen, és az ONLYOFFICE újra elindul. **Ha a visszaállító ismeretlen módosítást talál, ne töröld kézzel a mentést; szakértői ellenőrzés kell.**

Fontos: az **első**, korábbi fejlesztői RC5/10s gép eltérő éles telepítőt használ; annak visszaállítása továbbra is az eredeti `ONLYOFFICE_Overtype_Native_Final_9_4_0_129/install.sh --rollback` paranccsal történik, nem a hordozható telepítővel. A portable telepítő csak a második, gyári ONLYOFFICE-ról indított gép saját telepítési állapotát kezeli.

## 7. Tesztelési idővonal és igazolt eredmények

| Állomás | Megfigyelés / eredmény | Értelmezés |
|---|---|---|
| Régi X11-segéd teljes QA | 23 PASS / 6 FAIL, 29 eset | A dokumentumszerkezetet nem ismerő `Delete`-megoldás nem megfelelő |
| RC1.6 izolált GUI QA | 27 PASS / 1 FAIL / 1 mentési ellenőrzés blokkolt | Az alapfelülírás és bekezdésvédelem működik; háromkarakteres Undo hibás |
| RC2–RC4 célzott Undo | 19. teszt ismételt FAIL | History-összevonás nem érvényesült |
| RC4 diagnosztika | `previous-point-is-not-overwrite` | `ClearAdditional()` törölte a folytatásjelölőt |
| RC5 WeakMap és izolált teljes QA | **3/3 Undo + 29/29 GUI PASS** | **Az 1,8 s-os RC5** teljes, 29 esetes automatizált próbája sikeres; mentett DOCX-tartalom ellenőrzéssel |
| Első gépes éles RC5 telepítés | `INSTALL PASS`, `--status` két natív bundle | Rendszerszintű telepítés igazolt |
| Első gépes kézi lassú Undo | Egyetlen Ctrl+Z nem volt elég; gyors gépelésnél igen | Az 1,8 s-os csoportosítási korlát túl rövid |
| Első gépes 10 s javítás | `PATCH PASS` és felhasználói működési visszajelzés | Javított időzítés, de nem új 29 esetes automatizált QA |
| ThinkPad T470s portable beta | `CHECK PASS`, `BUILD PASS`, `INSTALL PASS`, mindkét bundle `PORTABLE RC5/10s` | Másik gépre telepíthetőség igazolt |
| ThinkPad T470s kézi QA | **4/4 PASS** | Felülírás, lassú Undo/Redo, INS mód, DOCX mentés és újranyitás sikeres |

A második gépes tesztek a felhasználó által közölt CLI-kimeneten és kézi ellenőrzési visszajelzésen alapulnak. Nem áll rendelkezésre a ThinkPad teljes automatizált 29-es GUI-tesztje vagy az összetett DOCX-eket átfogó tesztkészlet. A fejlesztés utolsó lépései során kapott hibákat és blokkolásokat nem szabad eltüntetni az auditnyomból; a fenti táblázat a főbb fordulópontokat rögzíti.

### 7.1. Regressziókat lefedő témák

Alapfelülírás; `Insert` kapcsolás; normál gépelés; bekezdésvégek és üres bekezdések megőrzése; kijelöléses műveletek; félkövér/dőlt szakasz melletti szöveg; szóköz; Ctrl+Z/Ctrl+Y; magyar `ő`, `ű`, `á`, `é`; gyors és ismétlődő karakterbevitel; navigáció, Backspace, Ctrl+Home; mentett DOCX-fájl tartalmi ellenőrzése. A teljes automata QA korábbi RC5 buildre vonatkozik, nem bizonyítja az összes lehetséges szövegszerkezet helyességét.

### 7.2. Ismert hiányzó tesztek

Táblázatok és összetett cellák; lábjegyzetek, végjegyzetek, fejlécek/láblécek; megjegyzések; változáskövetés és közös szerkesztés; tartalomvezérlők; komplex mezők és beágyazott objektumok; Unicode kombináló jelek, emojik és grapheme cluster határok; különböző billentyűzetkiosztások és IME; nagyméretű DOCX-ek; frissítés utáni sérülés- és rollback-szcenáriók; a 10 s-os build teljes 29-es automata QA-ja.

## 8. Hibaelhárítás

**`CHECK PASS` nem indul:** ellenőrizni kell a pontos ONLYOFFICE-csomagverziót, az X11-munkamenetet (`echo "$XDG_SESSION_TYPE"`), hogy minden `DesktopEditors` folyamat bezárult-e, nincs-e régi X11-bridge automatikus indítás, foglalt 39167-es port vagy régi Overtype plugin.

**`BUILD PASS` után nem telepít:** ellenőrizd a telepítendő `candidate` mappa és a `manifest.json` állapotát, az eredeti gyári bundle-hasheket és a csomag verzióját. Nem szabad kézzel eltávolítani a védelmi hash-ellenőrzéseket.

**Sok Ctrl+Z kell:** vizsgáld meg, eltelt-e több mint 10 s két karakter között, illetve történt-e navigáció, kijelölés, mentés vagy módváltás. Ha 2–3 s-os folytonos gépelés után is hibázik, eldobható dokumentummal reprodukálandó és telepítési státuszt kell ellenőrizni.

**Új ONLYOFFICE-frissítés után eltűnik a funkció:** az új verzióra a régi két JS-fájlt nem szabad átmásolni. Meg kell várni az új, külön ellenőrzött patch/verzió támogatását. Az apt/dpkg frissítés a módosított fájlokat felülírhatja.

**Rollback nem fut:** a mentéseket ne töröld és ne cseréld ki, a képernyőn megjelenő hibát és a `--status` kimenetet kell megőrizni. A telepítéskor létrehozott cache/manifeszt szükséges lehet.

## 9. Licenc, eredet, adatkezelés és közzététel

- **Eredeti fejlesztő:** Ascensio System SIA / ONLYOFFICE. A jelen projekt nem hivatalos, nem kapott ONLYOFFICE támogatást vagy jóváhagyást.
- **Upstream SDKJS:** [ONLYOFFICE/sdkjs, `v9.4.0.129`](https://github.com/ONLYOFFICE/sdkjs/tree/v9.4.0.129), [teljes LICENSE](https://github.com/ONLYOFFICE/sdkjs/blob/v9.4.0.129/LICENSE). A projekt módosított SDKJS-kódra épül; a GNU AGPLv3 és az upstream kiegészítő feltételek alkalmazandók.
- **Kiegészítő feltételek:** eredeti jogi jelölések megőrzése; módosítás és dátum feltüntetése; módosított interaktív felületen elérhető, megfelelő jogi tájékoztatás; védjegyjogok hiánya; egyes nem kódjellegű erőforrások eltérő licencelése.
- **Publikus kiadás előtti hiány:** a csomagban jelenleg nincs az eredeti LICENSE **teljes szövege**, és nem igazolt, hogy az új interaktív plugin felülete megfelel az ONLYOFFICE-féle kiegészítő jogi tájékoztatási előírásnak. Az ikonok eredete/újrafelhasználási joga is ellenőrzendő. Ezeket **nem szabad pusztán README-hivatkozással késznek minősíteni**.
- **SPDX audit:** néhány korábbi patchfájl jelenleg `AGPL-3.0-or-later` jelölést visel, míg az upstream egyes forrásfájlokban `AGPL-3.0-only` használ. A forrásból átvezetett licencjelölést publikálás előtt jogilag és forráshely szerint pontosítani kell; ne írjunk át automatikusan upstream jogosultságot.
- **Adatkezelés:** a normál működéshez nincs felhőfiók vagy jelszóigény; buildkor a program az upstream GitHub-forrást tölti le, a plugin HTML pedig külső ONLYOFFICE scriptet hivatkozik. Az RC5 tartalmaz opcionális `localhost:39169` diagnosztikai WebSocket-próbálkozást; ez a jelenlegi kód szerint előzmény-metaadatot küldhet egy helyben futó szervernek, nem dokumentumszöveget. A végleges nyilvános buildben célszerű az opcionális diagnosztikát eltávolítani vagy kifejezett opt-in kapcsolóra tenni.

### 9.1. Kiadhatósági döntés

**Műszaki állapot:** szűk, rögzített platformon működő, második gépen kipróbált beta.\
**Nyilvános GitHub Release:** a teljes LICENSE, az interaktív jogi tájékoztatás, a képek eredete és a diagnosztikai maradványok ellenőrzése után javasolt.\
**Stabil v1.0.0:** csak lényegesen szélesebb DOCX-regresszió és egyértelmű frissítés-/visszaállítási támogatás után indokolt.

### 9.2. Javasolt GitHub struktúra és publikálási menet

Repo: `onlyoffice-native-overtype` (munkanév). A forrásfájlokból és dokumentációból álló repository-ba ne kerüljön `sdkjs/` clone, `candidate/` fordítási eredmény, mentés, személyes docx, napló, elérési útvonalat tartalmazó tesztjelentés vagy kézzel módosított teljes ONLYOFFICE bundle. A forrásprojekt legyen verziózott. A release címkéje kezdetben például `v0.9.0-beta.1`; a csomag verziója ettől ne térjen el. A GitHub Release notes emeljék ki a támogatott környezetet és a visszaállítási lehetőséget.

A **publikálás előtt** szükséges a végső licenc- és adatvédelmi felülvizsgálat, az eredeti LICENSE pontos másolatának hozzáadása, a release ZIP SHA-256-képzése, a képernyőn megjelenő jogi tájékoztató ellenőrzése és a publikálandó archívum tisztaságának automatikus tesztje. Ha a forráskódon érdemi változtatás történik (például a diagnosztika eltávolítása), legalább a célzott Undo-teszteket és egy valódi DOCX mentés/újranyitás próbát újra kell futtatni.

## 10. A két kipróbált rendszer átadáskori állapota

**Első számítógép – ThinkCentre M900:** a korábbi RC5 éles motor telepítése és állapotellenőrzése sikeres; a 10 másodperces időzítési patch külön, root mentés mellett került fel. A helyi csomagkezelés/rollback útvonala eltér a hordozható változattól.\
**Második számítógép – ThinkPad T470s:** a régi `onlyoffice-overtype-x11 0.5.0` eltávolítva; a friss portábilis forrásból SDKJS-build, telepítés, státusz **PASS**; 4/4 kézi teszt sikeres. A portable root-mentés és pluginállapot jelen van.

**Megőrzendő:** mindkét gép saját telepítőcsomagja, a hozzá tartozó root backup, valamint a gyári fájlok és a módosított fájlok SHA-256-manifesztjei. A forrásmappa vagy a mentések takarítását a visszaállítási próba előtt **nem** javasoljuk.

---

**Átadási összegzés:** az eredeti X11-es eseménytrükk helyett belső, szerkezetkímélő Word-motoros felülírás működik; a korábbi 6 QA-hiba javítása igazolt a 29/29 RC5 automatizált tesztben; a később korrigált 10 s-os Undo-időzítés a ThinkPad T470s-en kézi teszt alapján megfelelő, mentett DOCX újranyitással. A következő érdemi feladat **nem** újabb általános RC-fejlesztés, hanem a nyilvános megjelentetéshez szükséges licenc-/UI-jogi megfelelés és kiadási tisztítás.


## 11. GitHub publikálási előkészítés (2026.10.11.)

A második gépes 4/4 manuális teszt lezárása után a publikálási jelöltbe külön `Névjegy és licencek` szalaggomb és elérhető, jogi tájékoztatóval ellátott pluginablak került; az ikonok saját, egyszerű geometriai grafikával lettek lecserélve (forrás: `tools/generate_icons.py`). A jelen kiadási jelöltben a fejlesztői localhost WebSocket naplózás csak kifejezett diagnosztikai engedélyezéssel aktív; normál gépelésnél kikapcsolt. A működő natív felülírás és Undo-csoportosítás logikáját ezek a módosítások nem kívánják megváltoztatni, viszont az új fordítási artifact hashértékei eltérnek.

A forrásfájlokat az upstream SDKJS `v9.4.0.129` (`75b53d504bfd81bfa35d59bb57dd9e56f7c9235d`) verziójára rögzítettük. A teljes upstream `LICENSE` másolásához a Git SHA-ellenőrzött `tools/prepare_github_release.py` szolgál; sikeres futása **kötelező** a publikálás előtt. A nyilvános kiadás jogi megfelelésének végső mérlegelése és a módosított UI helyszíni ellenőrzése nem helyettesíthető pusztán egységtesztekkel. A fent hivatkozott 29/29 GUI PASS a korábbi 1,8 s-os RC5 ellenőrzött változatára vonatkozik. A 10 s-os változatot második gépen 4/4 kézi esetben ellenőriztük, az új About/diagnosztikai változatot újra kell próbálni.
