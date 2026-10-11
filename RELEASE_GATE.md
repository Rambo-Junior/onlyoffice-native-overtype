# Public release gate — 2026-10-11

**Státusz: KIADÁS ELŐTT MÉG CÉLZOTT GUI-PRÓBA SZÜKSÉGES.** Az eredeti hordozható RC5/10s második gépes tesztje 4/4 PASS volt. A kiadásra előkészített csomagban az alábbi, még nem GUI-tesztelt változások történtek:

- Az ikonokat 2026-10-11-én létrehozott, önálló geometriájú grafikára cseréltük.
- Külön szalaggomb: `Névjegy és licencek` → About-ablak a jogi értesítéssel és az eredeti ONLYOFFICE licenclinkjével.
- A `127.0.0.1:39169` fejlesztői WebSocket diagnosztika alapból kikapcsolva.
- Az új patch-források SPDX-azonosítója `AGPL-3.0-only`; telepítő figyelmeztető szövege javítva.
- CI és teljes upstream LICENSE SHA-ellenőrző előkészítő hozzáadva.

## Kötelező publikálás előtt

1. A ThinkPaden, vagy olyan gépen, ahol az SDKJS pinelt forrása már elérhető: `python3 tools/prepare_github_release.py`; a LICENSE Git blob SHA értéke `53bc62cde3c705aa2d03b895b966bd6250f389ae` legyen.
2. Forráscsomag SHA-256 ellenőrzése és a `LICENSE`, `NOTICE.md`, `PROVENANCE.md` jelenléte.
3. A frissen épített kiadási jelölt külön GUI-próbája Linux Mint 22.3 / ONLYOFFICE 9.4.0-129 rendszerben: **toolbar About panel** megnyílik, szövege és hivatkozása megjelenik; gyors/lassú `xyz`, Ctrl+Z/Ctrl+Y, Insert módváltás, DOCX mentés és újranyitás.
4. A `--rollback` állapotellenőrzése, és a telepítő különálló gyári ONLYOFFICE-on történő használata.
5. Az upstream `plugins.js` HTTPS betöltés hálózati függését README-ben dokumentálni; esetleges CDN-kockázatot elfogadni.
6. GitHub repo a felhasználó fiókjában; **nyilvános publikálás csak újabb, egyértelmű jóváhagyás után.**

A korábbi 29/29 PASS a korábbi RC5 1,8 s-os izolált buildből származik, nem az új GitHub-kiadási jelöltből. A 10 s-os hordozható előző buildet két gépen validáltuk (4/4 kézi eset a második gépen). Nem tesztelt komplex DOCX-ekkel a béta nem tekinthető stabil kiadásnak.
