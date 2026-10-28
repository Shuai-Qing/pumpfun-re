# T3-prep attribution table

Base measured on the s7p candidate: **802 matched / 161 exact** (1035 original windows, 1012 candidate windows, 233 unmatched, call_consistent 694).
Candidate sha256 `7148f08aef7e8f4a67a62eb70d2967ed1b66f7cd6226fdd6157a3419bc880fd2`.
Symbols sha256 `6db799556477f2f1af2fa4ac0f5dc10ab88f74626f82a6f1946e6b0c1a374722`.

Method: for each unmatched wrapper window on the candidate, pair with the best same-size deployed window (or nearest size on a size gap), then classify every normalized instruction delta as field_offset / opcode_shape / regalloc / other_imm / lddw_content.

## Summary

- `constraint_location_line`: 17 windows
- `size_mismatch_field_or_macro`: 7 windows
- `field_order_or_type`: 7 windows
- `regalloc_noalias`: 1 windows

## Per-wrapper table

| kind | struct | pairing | cand addr | cand size | dep size | norm diffs | cats | cause | proposed construct |
|---|---|---|---|---:|---:|---:|---|---|---|
| try_accounts | `migrate_v2::MigrateV2` | size_gap | `0x17be60` | 22840 | 22520 | - | - | size_mismatch_field_or_macro | Diff field order / field type / constraint blocks until generated size equals deployed; re-check owned AccountInfo for exit offset |
| try_accounts | `create_v2::CreateV2` | same_size | `0x6e500` | 14904 | 14904 | 1 | other_imm:1 | constraint_location_line | Restore source line!()/col!() at the constraint error site (blank-line padding or file layout) so the baked Location immediate matches deployed |
| try_accounts | `distribution::DistributeCreatorFeesV2` | size_gap | `0x1833c8` | 9672 | 9776 | - | - | size_mismatch_field_or_macro | Diff field order / field type / constraint blocks until generated size equals deployed; re-check owned AccountInfo for exit offset |
| try_accounts | `mayhem_virtual_params::SetMayhemVirtualParams` | size_gap | `0x179cc8` | 8600 | 8544 | - | - | size_mismatch_field_or_macro | Diff field order / field type / constraint blocks until generated size equals deployed; re-check owned AccountInfo for exit offset |
| try_accounts | `buy_v2::BuyV2` | same_size | `0x68670` | 8128 | 8128 | 1 | other_imm:1 | constraint_location_line | Restore source line!()/col!() at the constraint error site (blank-line padding or file layout) so the baked Location immediate matches deployed |
| try_accounts | `sell_v2::SellV2` | same_size | `0x9c320` | 8128 | 8128 | 1 | other_imm:1 | constraint_location_line | Restore source line!()/col!() at the constraint error site (blank-line padding or file layout) so the baked Location immediate matches deployed |
| try_accounts | `trade::SellV3` | same_size | `0xb0228` | 8128 | 8128 | 1 | other_imm:1 | constraint_location_line | Restore source line!()/col!() at the constraint error site (blank-line padding or file layout) so the baked Location immediate matches deployed |
| try_accounts | `legacy_buy::LegacyBuy` | same_size | `0x105280` | 8128 | 8128 | 1 | other_imm:1 | constraint_location_line | Restore source line!()/col!() at the constraint error site (blank-line padding or file layout) so the baked Location immediate matches deployed |
| try_accounts | `InitUserVolume` | same_size | `0x1a6fd0` | 7824 | 7824 | 2 | other_imm:2 | constraint_location_line | Restore source line!()/col!() at the constraint error site (blank-line padding or file layout) so the baked Location immediate matches deployed |
| try_accounts | `holder_distribution::DistributeFeeToHolders` | size_gap | `0x7e3f8` | 7312 | 7344 | - | - | size_mismatch_field_or_macro | Diff field order / field type / constraint blocks until generated size equals deployed; re-check owned AccountInfo for exit offset |
| try_accounts | `create::Create` | same_size | `0xfd550` | 6672 | 6672 | 2 | other_imm:2 | constraint_location_line | Restore source line!()/col!() at the constraint error site (blank-line padding or file layout) so the baked Location immediate matches deployed |
| try_accounts | `distribution::DistributeCreatorFees` | size_gap | `0x181a58` | 6512 | 6464 | - | - | size_mismatch_field_or_macro | Diff field order / field type / constraint blocks until generated size equals deployed; re-check owned AccountInfo for exit offset |
| try_accounts | `create_v2::CreateV2` | same_size | `0x71f38` | 6464 | 6464 | 1 | other_imm:1 | constraint_location_line | Restore source line!()/col!() at the constraint error site (blank-line padding or file layout) so the baked Location immediate matches deployed |
| try_accounts | `create::Create` | same_size | `0xfef60` | 6464 | 6464 | 2 | other_imm:2 | constraint_location_line | Restore source line!()/col!() at the constraint error site (blank-line padding or file layout) so the baked Location immediate matches deployed |
| try_accounts | `quote_control::initialize_quote_control` | same_size | `0x8fb58` | 5952 | 5952 | 1 | other_imm:1 | constraint_location_line | Restore source line!()/col!() at the constraint error site (blank-line padding or file layout) so the baked Location immediate matches deployed |
| try_accounts | `global_init::Initialize` | same_size | `0xf8f90` | 5896 | 5896 | 2 | other_imm:2 | constraint_location_line | Restore source line!()/col!() at the constraint error site (blank-line padding or file layout) so the baked Location immediate matches deployed |
| try_accounts | `multi_hop_curve::CurveHop` | same_size | `0x8df80` | 3512 | 3512 | 3 | regalloc:3 | regalloc_noalias | Pass &UncheckedAccount into helpers, or rebind let x: &AccountInfo = x.as_ref() to drop noalias |
| dispatch | `buy` | size_gap | `0xc4500` | 1776 | 1768 | - | - | size_mismatch_field_or_macro | Diff field order / field type / constraint blocks until generated size equals deployed; re-check owned AccountInfo for exit offset |
| dispatch | `buy_exact_sol_in` | size_gap | `0xc4bf0` | 1776 | 1768 | - | - | size_mismatch_field_or_macro | Diff field order / field type / constraint blocks until generated size equals deployed; re-check owned AccountInfo for exit offset |
| dispatch | `distribute_creator_fees_v2` | same_size | `0xcb410` | 1736 | 1736 | 199 | regalloc:7,opcode_shape:175,field_offset:13,other_imm:4 | field_order_or_type | Reorder fields or change Account / InterfaceAccount / UncheckedAccount / owned AccountInfo until load offsets and prologue match |
| dispatch | `distribute_creator_fees` | same_size | `0xcaf50` | 1216 | 1216 | 142 | regalloc:1,opcode_shape:128,field_offset:12,other_imm:1 | field_order_or_type | Reorder fields or change Account / InterfaceAccount / UncheckedAccount / owned AccountInfo until load offsets and prologue match |
| dispatch | `set_mayhem_virtual_params` | same_size | `0xbf6c8` | 1088 | 1088 | 110 | regalloc:9,opcode_shape:93,other_imm:5,field_offset:3 | field_order_or_type | Reorder fields or change Account / InterfaceAccount / UncheckedAccount / owned AccountInfo until load offsets and prologue match |
| try_deserialize | `legacy_sell::LegacyFeeConfig` | same_size | `0xb2628` | 1048 | 1048 | 118 | opcode_shape:105,regalloc:1,field_offset:11,other_imm:1 | field_order_or_type | Reorder fields or change Account / InterfaceAccount / UncheckedAccount / owned AccountInfo until load offsets and prologue match |
| try_deserialize | `multi_hop_curve::RouteFeeConfig` | same_size | `0x14b928` | 1048 | 1048 | 118 | opcode_shape:105,regalloc:1,field_offset:11,other_imm:1 | field_order_or_type | Reorder fields or change Account / InterfaceAccount / UncheckedAccount / owned AccountInfo until load offsets and prologue match |
| try_deserialize | `distribution::SharingConfig` | same_size | `0xb2a40` | 744 | 744 | 2 | other_imm:2 | constraint_location_line | Restore source line!()/col!() at the constraint error site (blank-line padding or file layout) so the baked Location immediate matches deployed |
| try_deserialize | `volume_sync::GlobalVolumeAccumulator` | same_size | `0xac178` | 728 | 728 | 2 | other_imm:2 | constraint_location_line | Restore source line!()/col!() at the constraint error site (blank-line padding or file layout) so the baked Location immediate matches deployed |
| try_deserialize | `__private::__idl` | same_size | `0x10e4e0` | 728 | 728 | 1 | other_imm:1 | constraint_location_line | Restore source line!()/col!() at the constraint error site (blank-line padding or file layout) so the baked Location immediate matches deployed |
| try_deserialize | `Global` | same_size | `0x198ac8` | 728 | 728 | 1 | other_imm:1 | constraint_location_line | Restore source line!()/col!() at the constraint error site (blank-line padding or file layout) so the baked Location immediate matches deployed |
| try_deserialize | `UserVolumeAccumulator` | same_size | `0x1a4e80` | 728 | 728 | 2 | other_imm:2 | constraint_location_line | Restore source line!()/col!() at the constraint error site (blank-line padding or file layout) so the baked Location immediate matches deployed |
| exit | `mayhem_virtual_params::SetMayhemVirtualParams` | same_size | `0x859c8` | 576 | 576 | 1 | other_imm:1 | constraint_location_line | Restore source line!()/col!() at the constraint error site (blank-line padding or file layout) so the baked Location immediate matches deployed |
| dispatch | `migrate_v2` | same_size | `0xc5a78` | 552 | 552 | 60 | field_offset:7,other_imm:1,opcode_shape:51,regalloc:1 | field_order_or_type | Reorder fields or change Account / InterfaceAccount / UncheckedAccount / owned AccountInfo until load offsets and prologue match |
| try_deserialize | `trade_types::BondingCurve` | same_size | `0x5bc50` | 200 | 200 | 22 | opcode_shape:20,regalloc:1,other_imm:1 | field_order_or_type | Reorder fields or change Account / InterfaceAccount / UncheckedAccount / owned AccountInfo until load offsets and prologue match |

## Known tricks (where they apply)

1. **Owned `AccountInfo`** on fields such as `event_authority` / `creator_vault` shifts generated `exit` and parser frame offsets. Present on the matched LegacyBuy / Create exit windows; apply the same type on size-gap structs whose exit still drifts (`SetMayhemVirtualParams` exit 576 B is a 1-imm Location near-miss after size work).

2. **`&UncheckedAccount` into helpers** removes the noalias regalloc divergence in handler bodies. Measured on `CurveHop::try_accounts` (3512 B): 3 regalloc deltas at identical opcodes, frame offsets, and immediates.

## Constraint Location line pattern (same-size near-misses)

Same-size `try_accounts` / `try_deserialize` / `exit` near-misses share one shape: the normalized bodies match except for 1-2 `stw`/`stdw` immediates that store `line!()` / `col!()` into an Anchor `Location` right after an `lddw` of the source path. Example: `LegacyBuy` closure `try_accounts` 8128 B at candidate `0x105280` vs deployed `0x172110` stores line **7** vs **2871** at the same frame slot; column 24 matches. Field order and field type already align on these windows.

## Size-gap parsers

| struct | cand size | nearest dep size | delta |
|---|---:|---:|---:|
| `migrate_v2::MigrateV2` | 22840 | 22520 | 320 |
| `distribution::DistributeCreatorFeesV2` | 9672 | 9776 | -104 |
| `mayhem_virtual_params::SetMayhemVirtualParams` | 8600 | 8544 | 56 |
| `holder_distribution::DistributeFeeToHolders` | 7312 | 7344 | -32 |
| `distribution::DistributeCreatorFees` | 6512 | 6464 | 48 |
