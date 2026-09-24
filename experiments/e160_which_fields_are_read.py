"""E160 -- which `config` fields does each method actually read? Derived from the record, not from the code.

Rules 39 and 44 both turn on the same question and neither can be answered from a registration's prose:

  * rule 39: a prediction about a quantity the manipulation cannot move is not a prediction;
  * rule 44: a C0 identity claim must be checked against the two artifacts' `config` fields, not against a
    paraphrased command -- `e153` was registered to reproduce `e144` and ran at `lam = 1.0` against `3e-3`,
    so its claim of per-replicate identity was false when it was written.

**The record can answer the question empirically, and it does so here.** For every pair of artifacts that share
an arm and a seed stream, compare that arm's per-replicate values and record which config fields differ between
the two artifacts:

    the arm is bit-identical and field X differs      ->  X is UNREAD by this method (observed)
    the arm differs and field X differs               ->  X is READ by this method (observed, if X is the only
                                                          field that differs -- otherwise it is "possibly read")
    the arm is bit-identical and no field differs     ->  a true repeat, uninformative about fields

The output is a **table of method x field**, and its intended use is the one `e153` needed: **before writing an
identity claim, look up whether the differing field is read by the arm it is about.** The table is also a
*checkable* claim about the runner -- `lam` must come out read for the three penalty methods and unread for
`naive` and `replay`, which is the correction that cost three artifacts.

    python -m experiments.e160_which_fields_are_read --json-out runs/e160_field_readership.json

Reads only artifacts on disk; runs nothing. ASCII output only.
"""

from __future__ import annotations

import argparse
import itertools
import json
from collections import defaultdict
from pathlib import Path

from clfly.bench.artifacts import write_json
from experiments.e103_reproducibility_audit import arm_matches, load_artifacts, signature

#: fields whose value *identifies* the artifact rather than describing the run
IGNORED = ("json_out", "seed0", "repeats", "methods")
UNREAD, READ, MAYBE, CONFLICT, UNTESTED = "unread", "read", "possibly read", "CONFLICTING", "untested"


def pairs_for_arm(artifacts: list[dict], arm: str) -> list[dict]:
    """Every comparable pair of artifacts that share ``arm``, with the fields that differ and the verdict."""
    members = [a for a in artifacts
               if isinstance(a["payload"].get("methods"), dict) and arm in a["payload"]["methods"]]
    out = []
    for a, b in itertools.combinations(members, 2):
        if (a["config"].get("seed0"), a["config"].get("repeats")) != \
           (b["config"].get("seed0"), b["config"].get("repeats")):
            continue
        na = len((a["payload"]["methods"][arm].get("replicates") or []))
        nb = len((b["payload"]["methods"][arm].get("replicates") or []))
        if na == 0 or na != nb:
            continue
        differing = sorted({k for k in set(a["config"]) | set(b["config"])
                            if k not in IGNORED and a["config"].get(k) != b["config"].get(k)})
        same_signature = signature(a["config"]) == signature(b["config"])
        out.append({"a": a["name"], "b": b["name"], "n": na, "differing": differing,
                    "same_signature": same_signature,
                    "identical": bool(arm_matches([a, b], arm).get("exact"))})
    return out


def readership(artifacts: list[dict], arms: tuple[str, ...]) -> dict:
    """Per arm and field: read, unread, or **conflicting** -- with the evidence counted rather than overwritten.

    The first version of this function assigned a verdict per pair in iteration order, so **an identical pair
    could overwrite a `read`** and the table's answer depended on which pair came last. That is exactly the class
    of defect this project keeps finding in its own readers, and the repair is to count the evidence instead:
    a field with *both* an identical pair and a single-field-differing pair is reported as **CONFLICTING**, and
    the conflicts are then the useful output -- a field whose evidence conflicts is one no identity claim should
    rest on.
    """
    table: dict[str, dict[str, str]] = {}
    evidence: dict[str, dict[str, list[str]]] = {}
    for arm in arms:
        pairs = pairs_for_arm(artifacts, arm)
        verdict: dict[str, str] = {}
        ev: dict[str, list[str]] = defaultdict(list)
        for field in sorted({f for p in pairs for f in p["differing"]}):
            # only SINGLE-field differences are informative about readership, so both the "moved" and the
            # "stayed" evidence are restricted to them; a field varied only alongside others is untested here.
            clean = [p for p in pairs if p["differing"] == [field]]
            moved = [p for p in clean if not p["identical"]]
            stayed = [p for p in clean if p["identical"]]
            multi = [p for p in pairs if field in p["differing"] and len(p["differing"]) > 1]
            if moved and stayed:
                verdict[field] = CONFLICT
            elif moved:
                verdict[field] = READ
            elif stayed:
                verdict[field] = UNREAD
            else:
                verdict[field] = MAYBE if multi else UNTESTED
            ev[field] = ([f"moved   {p['a'][:26]} vs {p['b'][:26]} n={p['n']} (only {field})" for p in moved[:2]]
                         + [f"stayed  {p['a'][:26]} vs {p['b'][:26]} n={p['n']} (only {field})" for p in stayed[:2]]
                         + [f"multi   {p['a'][:26]} vs {p['b'][:26]} n={p['n']} "
                            f"({'+'.join(p['differing'][:3])})" for p in multi[:1]])
        table[arm] = verdict
        evidence[arm] = dict(ev)
    return {"table": table, "evidence": evidence}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args()

    artifacts = load_artifacts(Path("runs"), skip=("e160_field_readership.json",))
    arms = ("naive", "ewc", "ewc-block", "ewc-block-rand", "replay")
    res = readership(artifacts, arms)
    fields = sorted({f for v in res["table"].values() for f in v})
    print(f"== from {len(artifacts)} artifacts: what each method reads, observed ==")
    print(f"   {'field':<20}" + "".join(f"{a:<16}" for a in arms))
    for field in fields:
        print(f"   {field:<20}" + "".join(f"{res['table'][a].get(field, UNTESTED):<16}" for a in arms))

    print("\n== the check this table exists for: `lam` ==")
    for a in arms:
        got = res["table"][a].get("lam", UNTESTED)
        print(f"   {a:<16} lam is {got}")
    lam_read = [a for a in arms if res["table"][a].get("lam") == READ]
    lam_unread = [a for a in arms if res["table"][a].get("lam") == UNREAD]
    print(f"   -> read by {lam_read or '[]'}; unread by {lam_unread or '[]'}")
    print("   (the runner's three penalty methods must be in the first list and `naive`/`replay` in the second:")
    ok = set(lam_read) == {"ewc", "ewc-block", "ewc-block-rand"} and set(lam_unread) == {"naive", "replay"}
    print(f"    {ok})")

    print("\n== and the fields no observed pair has ever varied, which the table cannot speak for ==")
    for a in arms:
        untested = [f for f in fields if res["table"][a].get(f, UNTESTED) == UNTESTED]
        print(f"   {a:<16} {', '.join(untested) if untested else '(none of the listed fields)'}")

    print("\n== reading ==")
    print("   A field marked `read` for an arm means some pair differing ONLY in that field moved that arm:")
    print("   an identity claim across such a difference is false by observation, which is what rule 44 asks")
    print("   a writer to check. `untested` means no comparable pair varied it, so the table is silent -- and")
    print("   the code, not the table, is then the only source.")

    if args.json_out:
        write_json(args.json_out, res)
        print(f"\nwrote {args.json_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
