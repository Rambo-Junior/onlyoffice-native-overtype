# 29-case original GUI regression matrix (historical baseline)

**Scope:** These are the 29 scenarios from the earlier RC1.6 isolated QA harness. **29/29 PASS applies to the 1.8-second RC5 baseline**, not a fresh run against the v1.0.0-rc.1 10-second source build. This matrix is published to make the original coverage and missing new evidence explicit. These are not runnable automatically from this Markdown file.

Use disposable documents only. Each test begins from a fresh document with the named fixture content; save as DOCX and verify both displayed text and saved OOXML content.

| # | Group | Scenario | Original fixture | Expected paragraphs |
|---:|---|---|---|---|
| 01 | 00 GUI-előteszt | Normál gépelés, mentés és fókusz | `plain.docx` | `('qABCDE',)` |
| 02 | 01 Alapfelülírás | A után 1 karakter | `plain.docx` | `('AxCDE',)` |
| 03 | 01 Alapfelülírás | B után 1 karakter | `plain.docx` | `('ABxDE',)` |
| 04 | 01 Alapfelülírás | 3 egymás utáni karakter | `plain.docx` | `('AxyzE',)` |
| 05 | 01 Alapfelülírás | Normál beszúrás Insert nélkül | `plain.docx` | `('AxBCDE',)` |
| 06 | 01 Alapfelülírás | Insert kétszer: normál beszúrás | `plain.docx` | `('AxBCDE',)` |
| 07 | 02 Bekezdésvégek | Első bekezdés utolsó karakterénél | `paragraph.docx` | `('Ax', 'CD')` |
| 08 | 02 Bekezdésvégek | Két bekezdés között | `paragraph.docx` | `('ABx', 'CD')` |
| 09 | 02 Bekezdésvégek | Üres bekezdés megőrzése | `emptypara.docx` | `('ABx', '', 'CD')` |
| 10 | 02 Bekezdésvégek | Dokumentum végén | `plain.docx` | `('ABCDEx',)` |
| 11 | 03 Kijelölések | Két karakter kijelölése | `plain.docx` | `('AxDE',)` |
| 12 | 03 Kijelölések | Egy karakter kijelölése | `plain.docx` | `('AxCDE',)` |
| 13 | 03 Kijelölések | Teljes szó kijelölése | `plain.docx` | `('x',)` |
| 14 | 04 Formázások | Félkövér szakasz átlépése | `formatted.docx` | `('AxCDE',)` |
| 15 | 04 Formázások | Dőlt szakasz átlépése | `formatted.docx` | `('ABxDE',)` |
| 16 | 04 Formázások | Szóköz felülírása | `spaces.docx` | `('AxBC',)` |
| 17 | 05 Undo / Redo | Egyetlen Ctrl+Z | `plain.docx` | `('ABCDE',)` |
| 18 | 05 Undo / Redo | Ctrl+Z után Ctrl+Y | `plain.docx` | `('AxCDE',)` |
| 19 | 05 Undo / Redo | 3 karakter és visszavonás | `plain.docx` | `('ABCDE',)` |
| 20 | 06 Magyar karakterek | ő felülírás | `plain.docx` | `('AőCDE',)` |
| 21 | 06 Magyar karakterek | ű felülírás | `plain.docx` | `('AűCDE',)` |
| 22 | 06 Magyar karakterek | á és é felülírás | `plain.docx` | `('AáéDE',)` |
| 23 | 07 Gyors gépelés | Gyors xyz (10 ms) | `long.docx` | `('xyzDEFGHIJKL',)` |
| 24 | 07 Gyors gépelés | Gyors 8 karakter | `long.docx` | `('12345678IJKL',)` |
| 25 | 07 Gyors gépelés | Ismétlődő betűk | `long.docx` | `('aaaaEFGHIJKL',)` |
| 26 | 08 Integráció | Navigáció közben az OVR mód megmarad | `plain.docx` | `('AxCDE',)` |
| 27 | 08 Integráció | Backspace után az OVR mód megmarad | `plain.docx` | `('xCDE',)` |
| 28 | 08 Integráció | Ctrl+Home után az OVR mód megmarad | `plain.docx` | `('xBCDE',)` |
| 29 | 08 Integráció | Módváltás kattintás nélkül | `plain.docx` | `('AxCDE',)` |

## Candidate acceptance gates

- Re-run these 29 tests against **exactly v1.0.0-rc.1, 10-second Undo threshold** using an isolated desktop installation and disposable files.
- Verify saved DOCX content, not only the clipboard/UI.
- Add slow typing (2–3-second pauses), Ctrl+Z and Ctrl+Y as separate 10-second-specific tests.
- Before calling a release stable, add real DOCX cases for tables, comments, revisions, footnotes, protected fields and complex Unicode/IME input.
- Preserve machine-readable reports, editor version and patched bundle SHA-256 values as CI/release attachments.
