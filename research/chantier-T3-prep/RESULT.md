# chantier-T3-prep: per-wrapper attribution for Anchor wrappers (#17)

Groundwork for T3 Accounts-struct reconstruction. Diffs every unmatched
`try_accounts` / `exit` / `dispatch` / `try_deserialize` window on the current
s7p candidate against the deployed binary, attributes each mismatch to one of
{field order, field type, constraint, macro version}, and records the proposed
construct change. Stock Anchor 0.31.2 derive path is the measured baseline.

Refs #17. Spec: `docs/T3_WRAPPERS.md`, method: `docs/WRAPPER_RECONSTRUCTION.md`.

## Measure

| build | matched | raw (exact) | candidate sha256 |
|---|---:|---:|---|
| s7p base (chain #22-#32) | **802** | **161** | `7148f08aef7e8f4a67a62eb70d2967ed1b66f7cd6226fdd6157a3419bc880fd2` |
| this packet (docs + table) | **802** | **161** | same |

Lost: none. Source and binary unchanged; this packet is the attribution table.

## Findings (32 unmatched wrapper windows)

| cause | count | proposed construct |
|---|---:|---|
| `constraint_location_line` | 17 | blank-line / file-layout restore of `line!()`/`col!()` at constraint error sites |
| `size_mismatch_field_or_macro` | 7 | field order / type / constraint blocks until size equals deployed |
| `field_order_or_type` | 6 | reorder or retarget Account / InterfaceAccount / UncheckedAccount / owned AccountInfo |
| `regalloc_noalias` | 1 | pass `&UncheckedAccount` into helpers |
| `constraint_or_macro_shape` | 1 | match constraint blocks under stock 0.31.2 |

Full table: [`ATTRIBUTION.md`](ATTRIBUTION.md). Machine-readable: [`attribution.json`](attribution.json).

## Representative measurements

- `LegacyBuy` closure `try_accounts` 8128 B (`0x105280` vs deployed `0x172110`): bodies match after normalize except one `stw` Location line immediate (**7** vs **2871**); column 24 matches. Field order and field type already align.
- `CurveHop::try_accounts` 3512 B: 3 regalloc deltas only (same opcodes, frame offsets, immediates) → `&UncheckedAccount` helper-arg fix.
- Size-gap parsers: `MigrateV2` 22840 vs 22520 (+320), `DistributeCreatorFeesV2` 9672 vs 9776 (-104), `SetMayhemVirtualParams` 8600 vs 8544 (+56), `DistributeFeeToHolders` 7312 vs 7344 (-32), `DistributeCreatorFees` 6512 vs 6464 (+48).

## Tricks captured

1. Owned `AccountInfo` shifts exit/parser offsets (already on matched LegacyBuy/Create exits; apply on size-gap structs).
2. `&UncheckedAccount` into helpers removes noalias regalloc divergence (`CurveHop`).

## Follow-on sub-claims (one PR each)

1. Blank-line / path layout for the 17 Location-line near-misses.
2. Field reconstruction for the 5 size-gap `try_accounts` structs.
3. `&UncheckedAccount` helper pass for `CurveHop`.
4. Dispatch / `try_deserialize` field-order windows (`distribute_creator_fees*`, `LegacyFeeConfig`, `BondingCurve`).
