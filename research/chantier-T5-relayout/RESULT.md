# chantier-T5-relayout: `tools/relayout.py` layout-layer skeleton (#19)

Runnable layout-layer tool that enumerates `.rodata` / `.data.rel.ro` records
(Location, plain `&str`, path strings, residual slots) and inline Location
constructions in `.text`, then diffs deployed vs candidate by source order and
size. This is the T5 data/reloc layer named `relayout.py`.

Refs #19. Spec: `docs/CHANTIER.md` T5.

## Tool

`tools/relayout.py <deployed.so> <candidate.so> [--prefix programs/pump/src/] [--json out.json]`

Encodings covered (measured on pump / pump_fees / pump_amm, platform-tools v1.4x):

- **A.** `.data.rel.ro` pointer slot stores the `.rodata` VA in its high 32 bits;
  Location = `(ptr, len, line, col)` at 24-byte stride; plain `&str` at 16-byte stride.
- **B.** Inline form (dominant on pump wrappers): `lddw` path VA + nearby `stw` line
  + `stw`/`stdw` col. Paths are often packed back-to-back in `.rodata` with no NUL
  between them; the scanner advances past each `.rs`.

## Measure

| build | matched | raw (exact) |
|---|---:|---:|
| s7p base | **802** | **161** |
| this packet (tool + report) | **802** | **161** |

Lost: none. Binary unchanged; packet adds the tool and a measured run on the current candidate.

## Run on current s7p candidate vs deployed (`programs/pump/src/` prefix)

| surface | dep | cand | matched | missing | extra |
|---|---:|---:|---:|---:|---:|
| inline Locations | 386 | 407 | 63 | 323 | 344 |
| `.data.rel.ro` Locations | 42 | 87 | 1 | 41 | 86 |
| path strings | 33 | 35 | 23 | 10 | 12 |
| `.data.rel.ro` `&str` | 12 | 14 | 5 | 7 | 9 |

Section sizes:

- `.rodata`: 32031 → 31891 (delta **-140**)
- `.data.rel.ro`: 10352 → 11808 (delta **+1456**)
- residual `.data.rel.ro` slots: 928 → 942

40 source files show inline line/col shifts. Path inventory gaps include deployed
`creator/distribute_creator_fees*.rs` / `pump_quote.rs` / `token_incentives/*`
versus candidate extras `distribution.rs` / `nested_create.rs` / `global_init.rs`
/ `create.rs`. Full JSON: [`relayout-Y42.json`](relayout-Y42.json). Console:
[`relayout-run.txt`](relayout-run.txt).

## Next steps for T5 sub-claims

1. Align path inventory (rename/split source files to the deployed tree).
2. Blank-line pad so inline Location `(file, line, col)` multisets match.
3. Drive `.data.rel.ro` record order from the matched Location table into
   `ordered.ld` data selectors.
