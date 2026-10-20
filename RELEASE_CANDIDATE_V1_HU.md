# v1.0.0-rc.1 – kiadás előtti ellenőrzési feltételek

**Ez még NEM stabil, minden DOCX-szerkezetre biztonságosnak minősített kiadás.** A natív RC5/10s felülírási kód megegyezik a `v0.9.0-beta.2` változattal. Az új csomag a forrásból fordítás CI-ellenőrzését, további automata kapukat és részletes angol–magyar kiadási útmutatót ad hozzá.

## Bizonyított működés

- Csak Linux Mint 22.3 / Cinnamon X11 / ONLYOFFICE Desktop Editors 9.4.0-129 (DEB).
- Korábbi, **1,8 másodperces** RC5: **29/29** automatikus GUI-teszt sikeres. Ez **nem** a 10 másodperces végleges motor teszteredménye.
- Hordozható 10 másodperces motor: **4/4** kézi teszt, DOCX mentés/újranyitás a ThinkPad T470s gépen; a kétnyelvű Névjegy gombot célzottan ellenőriztük.
- A root mentés, telepítés és visszaállítás helyi modellezett tesztekkel ellenőrzött; ezek nem helyettesítik a független, hibás telepítést is lefedő valós tesztet.
- Új GitHub CI: a pontos SDKJS-forrásból épít és ellenőrzi a javított JavaScriptet. A zöld CI **nem jelenti**, hogy az összetett DOCX-ek biztonságosak.

## Stabil v1.0.0 előtt még kötelező

1. 29/29 GUI- és mentett DOCX-ellenőrzés **pontosan a 10 s-os kiadási változaton**.
2. Táblázat, fej- és lábléc, lábjegyzet, követett módosítás, megjegyzés, összetett Unicode/IME, védett mezők és formázások regressziós próbái.
3. Telepítés, hibás telepítés, rollback, alkalmazásfrissítés utáni viselkedés független ellenőrzése.
4. Változatlan teljes eredeti licenc és jogi attribúció, külön forrás-ZIP, sértetlen Git-tag.

## Telepítés támogatott, tiszta gépre

```bash
bash run.sh --check
bash run.sh --build
bash run.sh --install
bash run.sh --status
# Gyári visszaállítás bezárt ONLYOFFICE mellett:
bash run.sh --rollback
```

Nem hivatalos SDKJS-módosítás. A fontos dokumentumok helyett a teszthez eldobható DOCX-et használj.
