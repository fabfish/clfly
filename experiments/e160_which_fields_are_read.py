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
from experiments.e103_reproducibility_audit import arm_matches, environment_key, load_artifacts, signature

#: fields whose value *identifies* the artifact rather than describing the run
IGNORED = ("json_out", "seed0", "repeats", "methods")
#: the synthetic field name for a difference in what the numbers were measured *in*. The environment is not part
#: of `config` and is therefore invisible to this join, which is how `e102_rate_fb8_omp1` and `..._omp4` came to
#: be read as single-field evidence about `fisher_batches` when the field that actually differed was the thread
#: count. **The identity is `e103.environment_key`**, i.e. the environment *minus* its timing: a first attempt at
#: this refinement keyed on the whole environment block and lost `replay`'s clean `lam` verdict, because the
#: block carries `calibration_matmul_s` and two runs of one command never share it. Removing the timing is what
#: makes the refinement work, and that is the reason the field is imported rather than re-derived here.
ENVIRONMENT_FIELD = "environment"
#: the synthetic field for a pair whose environments are **not both recorded**. Two runs of one command whose
#: environment nobody wrote down cannot be evidence about a `config` field, and -- the part that matters -- they
#: must not be read as "the environments were equal" either, because that is the defect this file's first
#: environment attempt had one level down. The pair is marked with a difference it cannot resolve, so it drops
#: out of single-field evidence while the *marker itself* gets a row: **`environment:unrecorded` is the field
#: that differs between two runs that do not know what they were**, and its verdict is a statement about the
#: corpus rather than about any method.
UNIDENTIFIABLE = "environment:unrecorded"
UNREAD, READ, MAYBE, CONFLICT, UNTESTED = "unread", "read", "possibly read", "CONFLICTING", "untested"


def effective(config: dict) -> dict:
    """A `config` as a statement about what the run was *asked* for, with the default entries dropped.

    The dump is `vars(args)`, so a key's **absence** means the parser had no such flag yet and its stored
    **`None` or `False`** means the flag existed and was not given: for the question this table asks -- did the
    run differ in this field -- those are the same statement, and comparing them as values makes a *schema epoch*
    look like an intervention. Measured: `e104_frozen_r32_plastic` (which predates `frozen_bias`) against
    `e164_fb8_today_a` was read as a single-field difference in `frozen_bias` while the two arms were
    bit-identical, which turned `frozen_bias x naive` **CONFLICTING**.

    `is None` and `is False` rather than `in (None, False)`: `0` is equal to `False` in Python and
    `pool_below = 0`/`readout_size = 0` are real settings.
    """
    return {k: v for k, v in config.items() if k != "json_out" and v is not None and v is not False}


def pairs_for_arm(artifacts: list[dict], arm: str, environment_field: bool = True) -> list[dict]:
    """Every comparable pair of artifacts that share ``arm``, with the fields that differ and the verdict.

    With ``environment_field``, a difference in the environment (minus its timing) is reported as a difference in
    a field, so that a pair whose arms move because the *machine* differed cannot be counted as evidence about a
    `config` field.
    """
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
        ea, eb = effective(a["config"]), effective(b["config"])
        fields = {k for k in set(ea) | set(eb) if k not in IGNORED and ea.get(k) != eb.get(k)}
        if environment_field:
            env_a, env_b = a["payload"].get("environment"), b["payload"].get("environment")
            if not isinstance(env_a, dict) or not isinstance(env_b, dict):
                fields.add(UNIDENTIFIABLE)
            elif environment_key(a["payload"]) != environment_key(b["payload"]):
                fields.add(ENVIRONMENT_FIELD)
        differing = sorted(fields)
        same_signature = signature(a["config"]) == signature(b["config"])
        out.append({"a": a["name"], "b": b["name"], "n": na, "differing": differing,
                    "same_signature": same_signature,
                    "identical": bool(arm_matches([a, b], arm).get("exact"))})
    return out


def readership(artifacts: list[dict], arms: tuple[str, ...], environment_field: bool = True) -> dict:
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
        pairs = pairs_for_arm(artifacts, arm, environment_field=environment_field)
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

    print("\n== the refinement this table needed, and what it resolves ==")
    bare = readership(artifacts, arms, environment_field=False)
    all_fields = sorted({x for v in res["table"].values() for x in v})
    changed = [(f, a, bare["table"][a].get(f, UNTESTED), res["table"][a].get(f, UNTESTED))
               for a in arms for f in all_fields
               if bare["table"][a].get(f, UNTESTED) != res["table"][a].get(f, UNTESTED)]
    print(f"   treating the environment (minus its timing) as a field changes {len(changed)} cell(s):")
    for f, a, was, now in changed:
        print(f"      {f:<16}{a:<16}{was:<16}-> {now}")
    same_lam = all(bare["table"][a].get("lam") == res["table"][a].get("lam") for a in arms)
    print("   and the cells it must NOT change: `lam` is "
          + ", ".join(f"{a}={res['table'][a].get('lam')}" for a in arms)
          + f" -- {'unchanged' if same_lam else 'CHANGED'}, which is what the first attempt at this broke")
    print("   (that attempt keyed on the WHOLE environment block, and since two runs of one command never share")
    print("    a `calibration_matmul_s`, every pair became multi-field and the clean verdicts went with it)")

    residual = [(a, f) for a in arms for f in all_fields
                if res["table"][a].get(f) == CONFLICT and f != ENVIRONMENT_FIELD]
    print(f"\n== the {len(residual)} conflict(s) the refinement cannot reach, and why ==")
    for a, f in residual:
        named = [line for line in res["evidence"][a].get(f, []) if line.startswith("moved")]
        print(f"   {f} x {a}: " + ("; ".join(named) if named else "(no moved pair listed)"))
    print("   -> a conflict needs a moved pair whose only differing `config` field is this one, and where the")
    print("      environment is UNRECORDED the refinement has nothing to separate it with: the environment is")
    print("      only a field where an artifact says what it was.")

    print("\n== what the SHARPER rule would additionally decide, and the assumption it needs ==")
    sharper = readership(artifacts, arms, environment_field=False)
    decide = {READ, UNREAD}
    gained = [(a, f, sharper["table"][a].get(f, UNTESTED)) for a in arms for f in all_fields
              if sharper["table"][a].get(f, UNTESTED) != res["table"][a].get(f, UNTESTED)]
    extra = [(a, f, v) for a, f, v in gained if v in decide and res["table"][a].get(f) not in decide]
    lost = [(a, f, v) for a, f, v in gained if v not in decide and res["table"][a].get(f) in decide]
    print(f"   {len(extra)} cell(s) are decided by the sharper rule and only `possibly read` here:")
    for a, f, v in extra[:10]:
        print(f"      {f:<22}{a:<16}{v}")
    if len(extra) > 10:
        print(f"      ... and {len(extra) - 10} more")
    print(f"   ({len(lost)} go the OTHER way, which is the rule earning its keep rather than costing anything:")
    for a, f, v in lost:
        print(f"      {f:<22}{a:<16}the sharper rule says {v}, this one decides "
              f"{res['table'][a].get(f)} on evidence that survives it:")
        for line in res["evidence"][a].get(f, [])[:2]:
            print(f"         {line}")
    if not lost:
        print("      (none)")
    print("   -> each of the cells above is evidence from a pair with a pre-2026-09-23-19:06 artifact in it, so")
    print("      the sharper rule is not wrong about them: it refuses to attribute a movement to a field when the")
    print("      record does not say what the run was measured in. What the sharper column needs is the")
    print("      assumption that an unrecorded environment was the default one -- true for most of those")
    print("      artifacts and false for `_omp1`/`_omp4`, two of the seven `e163` found.")

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
