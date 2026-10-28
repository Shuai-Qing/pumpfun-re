#!/usr/bin/env python3
"""Layout-layer enumerator for pump SBF candidates (T5 / issue #19).

Enumerates deployed-vs-candidate:
  * .rodata path strings (order + size)
  * .data.rel.ro Location records (24-byte) and plain &str slots (16-byte)
  * inline Location constructions in .text (lddw path + stw line + stw/stdw col)
  * residual .data.rel.ro slot count (discriminants / error tables / other)

Maps each record to source (file, line, col) and reports order + size deltas.

Encoding (measured on pump / pump_fees / pump_amm, platform-tools v1.4x):
  A. .data.rel.ro pointer slot stores the .rodata VA in its HIGH 32 bits with a
     zero low dword. Location = (ptr, len, line:u32, col:u32) at 24-byte stride;
     plain &str = (ptr, len) at 16-byte stride.
  B. Inline form (dominant on pump wrappers): lddw carries the .rodata path VA
     in its low 32 bits; a nearby stw stores line; a nearby stw/stdw stores col.

usage:
  python3 tools/relayout.py <deployed.so> <candidate.so>
  python3 tools/relayout.py <deployed.so> <candidate.so> --json out.json
  python3 tools/relayout.py <deployed.so> <candidate.so> --prefix programs/pump/src/
"""
from __future__ import annotations

import argparse
import json
import struct
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sbftool import Prog  # noqa: E402

PATH_ROOTS = (
    b'programs/', b'generated/', b'src/', b'library/', b'core/', b'alloc/',
    b'sdk', b'vendor/', b'interface',
)


def path_strings(p: Prog) -> dict[int, bytes]:
    """Collect every PATH_ROOTS hit. Paths are often packed back-to-back in
    .rodata with no NUL between them, so advance past `.rs` rather than to NUL."""
    out: dict[int, bytes] = {}
    for name in ('.rodata', '.data.rel.ro'):
        sec = p.sec.get(name)
        if not sec:
            continue
        lo, off, size = sec[3], sec[4], sec[5]
        blob = p.b[off:off + size]
        i = 0
        while i < len(blob) - 8:
            if blob.startswith(PATH_ROOTS, i):
                end = blob.find(b'.rs', i)
                if 0 <= end - i < 200:
                    j = blob.find(b'\0', i)
                    raw = blob[i: j if j >= 0 else min(i + 256, len(blob))]
                    out[lo + i] = raw
                    i = end + 3
                    continue
            i += 1
    return out


def pointer_records(p: Prog, paths: dict[int, bytes]) -> tuple[list, list, int]:
    """Return (locations, strings, residual_slot_count) from .data.rel.ro."""
    drr = p.sec.get('.data.rel.ro')
    if not drr:
        return [], [], 0
    addr, off, size = drr[3], drr[4], drr[5]
    slots: dict[int, tuple[str, int]] = {}
    for o in range(0, size - 16, 8):
        v = struct.unpack_from('<Q', p.b, off + o)[0]
        va = v >> 32
        if (v & 0xffffffff) != 0 or va not in paths:
            continue
        raw = paths[va]
        slen = struct.unpack_from('<Q', p.b, off + o + 8)[0]
        end = raw.find(b'.rs')
        if end < 0 or not (0 < slen <= len(raw)):
            continue
        if slen < end + 3:
            continue
        file = raw[: end + 3].decode('latin1', errors='replace')
        slots[addr + o] = (file, slen)

    order = sorted(slots)
    locations, strings = [], []
    claimed: set[int] = set()
    for i, va in enumerate(order):
        nxt = order[i + 1] if i + 1 < len(order) else None
        file, slen = slots[va]
        if nxt is not None and nxt - va == 24:
            o = va - addr
            line, col = struct.unpack_from('<II', p.b, off + o + 16)
            if 0 < line < 100000 and 0 < col < 40000:
                locations.append({
                    'va': va, 'file': file, 'len': slen, 'line': line, 'col': col,
                    'stride': 24, 'order': len(locations), 'encoding': 'data.rel.ro',
                })
                claimed.update((va, va + 8, va + 16))
                continue
        strings.append({
            'va': va, 'file': file, 'len': slen, 'stride': 16,
            'order': len(strings), 'encoding': 'data.rel.ro',
        })
        claimed.update((va, va + 8))

    residual = 0
    for o in range(0, size, 8):
        if addr + o not in claimed:
            residual += 1
    return locations, strings, residual


def inline_locations(p: Prog, paths: dict[int, bytes]) -> list[dict]:
    """Encoding B: Location built in .text near an lddw of a path VA."""
    out: list[dict] = []
    for pc, ins in sorted(p.ins.items()):
        if ins.op != 0x18:
            continue
        va = ins.imm & 0xffffffff
        if va not in paths:
            continue
        raw = paths[va]
        end = raw.find(b'.rs')
        if end < 0:
            continue
        file = raw[: end + 3].decode('latin1', errors='replace')
        line = col = None
        line_pc = col_pc = None
        for pc2 in range(pc + 1, pc + 16):
            ins2 = p.ins.get(pc2)
            if not ins2:
                continue
            if ins2.op == 0x62 and line is None:
                v = ins2.imm & 0xffffffff
                if 0 < v < 100000:
                    line = v
                    line_pc = pc2
            elif line is not None and col is None and ins2.op in (0x62, 0x7a):
                v = ins2.imm & 0xffffffff
                if 0 < v < 40000:
                    col = v
                    col_pc = pc2
                    break
        if line is not None and col is not None:
            out.append({
                'pc': pc, 'file': file, 'line': line, 'col': col,
                'line_pc': line_pc, 'col_pc': col_pc, 'path_va': va,
                'encoding': 'inline', 'order': len(out),
            })
    return out


def rodata_paths(paths: dict[int, bytes]) -> list[dict]:
    rows = []
    for va in sorted(paths):
        raw = paths[va]
        end = raw.find(b'.rs')
        if end < 0:
            continue
        rows.append({
            'va': va,
            'file': raw[: end + 3].decode('latin1', errors='replace'),
            'raw_len': len(raw),
            'path_len': end + 3,
            'order': len(rows),
        })
    return rows


def error_name_strings(p: Prog) -> list[dict]:
    """ASCII tokens in .rodata that look like Anchor/program error names."""
    ro = p.sec.get('.rodata')
    if not ro:
        return []
    blob = p.b[ro[4]:ro[4] + ro[5]]
    base = ro[3]
    out = []
    i = 0
    while i < len(blob) - 4:
        if blob[i:i + 1].isalpha() and blob[i:i + 1].isupper():
            j = i
            while j < len(blob) and (blob[j:j + 1].isalnum() or blob[j:j + 1] in b'_'):
                j += 1
            tok = blob[i:j]
            if 6 <= len(tok) <= 64 and b'_' in tok and tok[0:1].isupper():
                # likely Camel_or_Pascal error / event name
                if tok.decode('ascii', errors='ignore') == tok.decode('latin1'):
                    out.append({
                        'va': base + i, 'name': tok.decode('ascii'),
                        'len': len(tok), 'order': len(out),
                    })
            i = j + 1
        else:
            i += 1
    return out


def enumerate_all(p: Prog) -> dict:
    paths = path_strings(p)
    locs, strs, residual = pointer_records(p, paths)
    inline = inline_locations(p, paths)
    ro = p.sec.get('.rodata')
    drr = p.sec.get('.data.rel.ro')
    return {
        'sections': {
            '.rodata': {'va': ro[3], 'size': ro[5]} if ro else None,
            '.data.rel.ro': {'va': drr[3], 'size': drr[5]} if drr else None,
        },
        'paths': rodata_paths(paths),
        'locations_data': locs,
        'strings_data': strs,
        'locations_inline': inline,
        'error_names': error_name_strings(p),
        'residual_slots': residual,
    }


def _filt(rows, prefix, key='file'):
    if not prefix:
        return list(rows)
    return [r for r in rows if r.get(key, '').startswith(prefix)]


def diff_key_multiset(dep_rows, cand_rows, keyfn):
    dk = Counter(keyfn(r) for r in dep_rows)
    ck = Counter(keyfn(r) for r in cand_rows)
    matched = sum(min(dk[k], ck[k]) for k in dk if k in ck)
    missing = sum(max(0, dk[k] - ck.get(k, 0)) for k in dk)
    extra = sum(max(0, ck[k] - dk.get(k, 0)) for k in ck)
    missing_keys = sorted([k for k in dk if ck.get(k, 0) < dk[k]])
    extra_keys = sorted([k for k in ck if dk.get(k, 0) < ck[k]])
    return matched, missing, extra, missing_keys, extra_keys


def file_line_shifts(dep_rows, cand_rows):
    dep_by = defaultdict(list)
    cand_by = defaultdict(list)
    for r in dep_rows:
        dep_by[r['file']].append((r['line'], r['col']))
    for r in cand_rows:
        cand_by[r['file']].append((r['line'], r['col']))
    shifts = []
    for f in sorted(set(dep_by) | set(cand_by)):
        d = sorted(dep_by.get(f, []))
        c = sorted(cand_by.get(f, []))
        if d != c:
            shifts.append({
                'file': f,
                'dep_count': len(d),
                'cand_count': len(c),
                'dep_lines': d[:12],
                'cand_lines': c[:12],
            })
    return shifts


def diff_tables(dep: dict, cand: dict, prefix: str | None) -> dict:
    d_inline = _filt(dep['locations_inline'], prefix)
    c_inline = _filt(cand['locations_inline'], prefix)
    d_dloc = _filt(dep['locations_data'], prefix)
    c_dloc = _filt(cand['locations_data'], prefix)
    d_paths = _filt(dep['paths'], prefix)
    c_paths = _filt(cand['paths'], prefix)
    d_strs = _filt(dep['strings_data'], prefix)
    c_strs = _filt(cand['strings_data'], prefix)

    im, imiss, iextra, imiss_k, iextra_k = diff_key_multiset(
        d_inline, c_inline, lambda r: (r['file'], r['line'], r['col']))
    dm, dmiss, dextra, dmiss_k, dextra_k = diff_key_multiset(
        d_dloc, c_dloc, lambda r: (r['file'], r['line'], r['col']))
    pm, pmiss, pextra, pmiss_k, pextra_k = diff_key_multiset(
        d_paths, c_paths, lambda r: r['file'])
    sm, smiss, sextra, smiss_k, sextra_k = diff_key_multiset(
        d_strs, c_strs, lambda r: (r['file'], r['len']))

    # Section size deltas
    sec = {}
    for name in ('.rodata', '.data.rel.ro'):
        ds = (dep['sections'].get(name) or {}).get('size')
        cs = (cand['sections'].get(name) or {}).get('size')
        sec[name] = {
            'dep_size': ds, 'cand_size': cs,
            'delta': (None if ds is None or cs is None else cs - ds),
        }

    return {
        'prefix': prefix,
        'sections': sec,
        'counts': {
            'inline_locations': {
                'dep': len(d_inline), 'cand': len(c_inline),
                'matched': im, 'missing': imiss, 'extra': iextra,
            },
            'data_locations': {
                'dep': len(d_dloc), 'cand': len(c_dloc),
                'matched': dm, 'missing': dmiss, 'extra': dextra,
            },
            'paths': {
                'dep': len(d_paths), 'cand': len(c_paths),
                'matched': pm, 'missing': pmiss, 'extra': pextra,
            },
            'data_strings': {
                'dep': len(d_strs), 'cand': len(c_strs),
                'matched': sm, 'missing': smiss, 'extra': sextra,
            },
            'error_names': {
                'dep': len(dep['error_names']), 'cand': len(cand['error_names']),
            },
            'residual_slots': {
                'dep': dep['residual_slots'], 'cand': cand['residual_slots'],
            },
        },
        'inline_line_shifts': file_line_shifts(d_inline, c_inline),
        'missing_inline': [
            {'file': k[0], 'line': k[1], 'col': k[2]} for k in imiss_k[:40]
        ],
        'extra_inline': [
            {'file': k[0], 'line': k[1], 'col': k[2]} for k in iextra_k[:40]
        ],
        'missing_paths': list(pmiss_k)[:40],
        'extra_paths': list(pextra_k)[:40],
        'missing_data_locations': [
            {'file': k[0], 'line': k[1], 'col': k[2]} for k in dmiss_k[:20]
        ],
        'inventory': {
            'deployed': {
                'n_inline': len(dep['locations_inline']),
                'n_data_loc': len(dep['locations_data']),
                'n_paths': len(dep['paths']),
                'n_error_names': len(dep['error_names']),
            },
            'candidate': {
                'n_inline': len(cand['locations_inline']),
                'n_data_loc': len(cand['locations_data']),
                'n_paths': len(cand['paths']),
                'n_error_names': len(cand['error_names']),
            },
        },
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('deployed')
    ap.add_argument('candidate')
    ap.add_argument('--prefix', default='programs/pump/src/')
    ap.add_argument('--all-prefix', action='store_true')
    ap.add_argument('--json', dest='json_out', default=None)
    args = ap.parse_args()

    dep = enumerate_all(Prog(args.deployed))
    cand = enumerate_all(Prog(args.candidate))
    prefix = None if args.all_prefix else args.prefix
    report = diff_tables(dep, cand, prefix)

    c = report['counts']
    print(f"# relayout.py  prefix={prefix!r}")
    for name, s in report['sections'].items():
        print(f"  {name}: dep={s['dep_size']} cand={s['cand_size']} delta={s['delta']}")
    il = c['inline_locations']
    print(f"inline Locations: dep={il['dep']} cand={il['cand']} "
          f"matched={il['matched']} missing={il['missing']} extra={il['extra']}")
    dl = c['data_locations']
    print(f"data.rel.ro Locations: dep={dl['dep']} cand={dl['cand']} "
          f"matched={dl['matched']} missing={dl['missing']} extra={dl['extra']}")
    pa = c['paths']
    print(f"paths: dep={pa['dep']} cand={pa['cand']} "
          f"matched={pa['matched']} missing={pa['missing']} extra={pa['extra']}")
    print(f"data.rel.ro &str: {c['data_strings']}")
    print(f"error_name tokens: {c['error_names']}")
    print(f"residual .data.rel.ro slots: {c['residual_slots']}")
    print(f"files with inline line/col shifts: {len(report['inline_line_shifts'])}")
    for sh in report['inline_line_shifts'][:20]:
        print(f"  {sh['file']}: dep={sh['dep_count']} cand={sh['cand_count']}")
        print(f"    dep_lines={sh['dep_lines'][:6]}")
        print(f"    cand_lines={sh['cand_lines'][:6]}")
    if report['missing_paths']:
        print('missing paths:')
        for f in report['missing_paths'][:15]:
            print(f"  {f}")
    if report['extra_paths']:
        print('extra paths:')
        for f in report['extra_paths'][:15]:
            print(f"  {f}")
    if report['missing_inline']:
        print('missing inline Location sample:')
        for r in report['missing_inline'][:12]:
            print(f"  {r['file']}:{r['line']}:{r['col']}")

    if args.json_out:
        Path(args.json_out).write_text(json.dumps(report, indent=2))
        print(f'wrote {args.json_out}')


if __name__ == '__main__':
    main()
