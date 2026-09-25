"""E188 -- the question the overlap suite was built to ask, answered on the corpus's own matched pairs.

`clfly/network/tasks.py`'s `make_overlap_suite` exists for one question, and its docstring states it: *"does raising
input overlap raise forgetting?"* -- with `overlap = 0` giving fully disjoint supports and `overlap = 1` giving every
task the same inputs. `e187` measured that this builder is what the corpus has overwhelmingly run (120 artifacts,
2439 replicates, against the assembly suite's 25 and 107). **This reads the overlap axis itself**: every pair of
payloads that differ in `input_overlap` and, for the method being compared, in nothing that matters.

Each comparison declares **why** it is a pair, and the declaration is checked rather than trusted:

- **exact** -- every `config` field but `input_overlap` and `json_out` is equal;
- **near** -- the differing fields are named, and each is *inert for the compared method* by the runner's own code
  path: `fisher_batches` and `lam` are read only by the Fisher/penalty arms, so they cannot touch `naive` or
  `replay`; `frozen_bias: None` and `frozen_bias: False` are the same state.

The script prints each pair's differing fields beside its two levels, so a reader can reject a pair rather than
take the pooled number on trust. The contrast is **paired by seed** through `e151`'s `load_arm` and `paired`, since
both members of every pair start at `seed0 = 0` with the same replicate count and the replicates are in seed order.

    python -m experiments.e188_overlap_contrast
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from clfly.bench.artifacts import write_json
from experiments.e151_pertask_contrast_audit import load_arm, paired

RUNS = Path("runs")

#: (label, method, overlap-0 artifact, overlap-1 artifact, expectation). The expectation is `"pair"` or
#: `"rejected: <why>"`, and the exit code is the number of declarations the corpus contradicts -- so the one entry
#: below that is *meant* to be refused is a check on the admission rules rather than noise in the reject list.
PAIRS = (
    ("naive, disjoint vs identical inputs", "naive",
     "e116_r32_40reps.json", "e142_r32_overlap1.json", "pair"),
    ("naive, second overlap-0 arm of the same configuration", "naive",
     "e125_r32_plastic.json", "e142_r32_overlap1.json", "pair"),
    ("naive, third overlap-0 arm", "naive",
     "e140_r32_methods_plastic_40reps.json", "e142_r32_overlap1.json", "pair"),
    ("ewc-block (biological side partition)", "ewc-block",
     "e140_r32_methods_plastic_40reps.json", "e144_r32_overlap1_methods_40reps.json", "pair"),
    ("replay", "replay",
     "e140_r32_methods_plastic_40reps.json", "e148_r32_overlap1_replay.json", "pair"),
    ("ewc-block, overlap-1 arm at lambda one", "ewc-block",
     "e140_r32_methods_plastic_40reps.json", "e153_r32_overlap1_methods_40reps.json",
     "rejected: lam is read by the penalised arm"),
    ("ewc-block-rand, draw 1", "ewc-block-rand",
     "e140_r32_rand_draw1.json", "e144_r32_overlap1_rand_draw1.json", "pair"),
    ("ewc-block-rand, draw 2", "ewc-block-rand",
     "e140_r32_rand_draw2.json", "e144_r32_overlap1_rand_draw2.json", "pair"),
    ("ewc + frozen bias, lambda 3e-3", "ewc",
     "e147_r32_frozenbias_ewc_lam3e-3.json", "e150_r32_overlap1_frozenbias_ewc_lam3e-3.json", "pair"),
    ("ewc + frozen bias, lambda 3e-4", "ewc",
     "e147_r32_frozenbias_ewc_lam3e-4.json", "e150_r32_overlap1_frozenbias_ewc_lam3e-4.json", "pair"),
)

#: fields a comparison is allowed to differ in, per method, with the reason -- the runner's own code path decides,
#: not this file's taste. A field absent from a method's set makes the pair "exact" or fails the check.
#:
#: `methods` is here for every method on the strength of a measurement this project already has: each method's arm
#: is trained independently from the same initial body and the same task draws, so a payload that also ran `replay`
#: does not change its `naive` arm -- which is what `e102`/`e104`'s C0 checks assert to the digit ("each run's
#: `naive` row is per-replicate identical to `e116`'s"). The fields that *define* the compared arm are never inert:
#: `lam` and `frozen_*` for the penalised arms, `pool_buckets` and `partition_seed` for the block arms.
INERT_FOR = {
    "naive": {"methods", "fisher_batches", "lam", "replay_per_task", "replay_batch"},
    "replay": {"methods", "fisher_batches", "lam"},
    "ewc": {"methods", "fisher_batches", "replay_per_task", "replay_batch", "pool_buckets", "partition_seed"},
    "ewc-block": {"methods", "fisher_batches", "replay_per_task", "replay_batch"},
    "ewc-block-rand": {"methods", "fisher_batches", "replay_per_task", "replay_batch"},
}
#: the two spellings of "not frozen"
EQUIVALENT = {("frozen_bias", None, False), ("frozen_bias", False, None)}


def differing_fields(a: dict, b: dict) -> dict:
    out = {}
    for k in set(a) | set(b):
        if k in ("json_out", "input_overlap"):
            continue
        if a.get(k) != b.get(k) and (k, a.get(k), b.get(k)) not in EQUIVALENT:
            out[k] = (a.get(k), b.get(k))
    return out


def load(path: Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


#: The bars the level-by-level read checks, taken from the registered design of the intermediate levels rather
#: than restated: on `naive` the 0 -> 1 forgetting rise is +0.0318 (2.99 sigma) and the registered P1 says the
#: value at achieved 0.3333 is closer to the 1.0 end than to the 0.0 end, i.e. more than half of that.
DOSE_HALF_DONE = 0.0159


#: Rule 42's price, carried here for the same reason `ACHIEVED_OVERLAP` is: `e191` imports this file, so a shared
#: helper would be a cycle. A contrast measured `sigma` sems from zero at n = 40 needs 40 * (3 / sigma)**2 seeds at
#: 3 sigma, which reproduces rule 42's own published prices (4 for 9.35 sigma, 169 for 1.46 sigma) exactly.
def seeds_for_three_sigma(sigma: float) -> float | None:
    return 360.0 / sigma ** 2 if sigma else None
#: What a target `--input-overlap` achieves as a Jaccard overlap. Carried here as well as in `e191` because both
#: reads print it beside a level and a reader should not have to know which file holds the table. **It is arithmetic
#: and not a property of the circuit** -- see `e191`'s comment on the same table, and the test that binds both to
#: `overlap_controlled_supports`: the construction makes the per-size overlap exactly the target, so the Jaccard is
#: ``o / (2 - o)`` for any circuit, support size, task count or seed.
ACHIEVED_OVERLAP = {0.0: 0.0000, 0.25: 0.1429, 0.5: 0.3333, 0.75: 0.6000, 1.0: 1.0000}


def admitting_baseline(level_config: dict, method: str, candidates: list[Path]) -> tuple[Path | None, list[str]]:
    """The first candidate baseline whose config diff from the level is INERT for this ARM, with the refusals.

    The dose read was written without this and the omission cost a real catch: the three launched level commands
    inherited the runner's default `--lam 1.0` while `e140` runs `--lam 3e-3`, and `lam` is inert for `naive` and is
    the penalty strength for the block arms. Without the rule the read pairs them all against `e140` and reports a
    333x penalty step as an overlap effect.
    """
    refusals = []
    for cand in candidates:
        if not Path(cand).is_file():
            refusals.append(f"{Path(cand).name}: absent")
            continue
        payload = load(cand)
        if method not in (payload.get("methods") or {}):
            refusals.append(f"{Path(cand).name}: does not carry the {method} arm")
            continue
        diff = sorted(differing_fields(payload["config"], level_config))
        bad = [k for k in diff if k not in INERT_FOR.get(method, set())]
        if bad:
            refusals.append(f"{Path(cand).name}: differs in {bad}, which {method} reads")
            continue
        return cand, refusals
    return None, refusals


def dose_read(levels: list[Path], baseline: Path = Path("runs/e140_r32_methods_plastic_40reps.json"),
              candidates: list[Path] | None = None,
              overlap1: Path = Path("runs/e144_r32_overlap1_methods_40reps.json")) -> dict:
    """Each intermediate level against the disjoint baseline, arm by arm, on the accuracy drop AND the accuracy.

    The same design `e191` reads on the interference account, on the two quantities `e188`'s two-point contrast was
    measured with -- so the dose-response can be read on whichever account the question is asked in, and the two can
    disagree without either being a mistake (they are different quantities with different sems).

    Each quantity also gets a **progress fraction** -- its change at this level over its own 0 -> 1 change -- and an
    **overshoot** against the overlap-1.0 anchor, because the fraction is not bounded by 100% and the account where it
    exceeds it is the one where the sentence needs a sem: `naive`'s accuracy cost at the registered midpoint is
    1.77x its own 0 -> 1 endpoint change, and the overshoot's sem is the *paired* level-against-anchor contrast and
    not two sems in quadrature (the two deltas share `e116`, so they are correlated).
    """
    base = load(baseline) if Path(baseline).is_file() else None
    rows = []
    for level in levels:
        if not Path(level).is_file():
            rows.append({"level": Path(level).name, "status": "not written yet"})
            continue
        d = load(level)
        target = (d.get("config") or {}).get("input_overlap")
        out = {"level": Path(level).name, "target_overlap": target,
               "achieved_overlap": ACHIEVED_OVERLAP.get(target), "arms": {}}
        if base is None:
            out["status"] = "baseline missing"
            rows.append(out)
            continue
        pool: set[str] = set()
        for cand in (candidates or [baseline]):
            if Path(cand).is_file():
                pool |= set((load(cand).get("methods") or {}))
        for method in sorted(pool & set(d.get("methods", {}))):
            use, refusals = admitting_baseline(d.get("config") or {}, method,
                                              candidates or [Path("runs/e116_r32_40reps.json"), baseline,
                                              Path("runs/e153_r32_overlap1_methods_40reps.json")])
            if use is None:
                out.setdefault("refused_arms", {})[method] = refusals
                continue
            a, b = load_arm(use, method), load_arm(level, method)
            if a is None or b is None or a["n"] != b["n"]:
                continue
            entry = {"n": a["n"], "baseline": Path(use).name,
                     "baseline_overlap": (load(use)["config"] or {}).get("input_overlap"), "refusals": refusals,
                     "differs_in": sorted(differing_fields(load(use)["config"], d["config"]))}
            pf = paired(b["forgetting"], a["forgetting"])
            entry["forgetting"] = {"change": pf["change"], "sem": pf["sem"],
                                   "sigma": abs(pf["change"]) / pf["sem"] if pf["sem"] else None}
            acc_key = "final_accuracy"
            af = np.array([r[acc_key] for r in load(use)["methods"][method]["replicates"]], dtype=float)
            bf = np.array([r[acc_key] for r in d["methods"][method]["replicates"]], dtype=float)
            pa = paired(bf, af)
            entry["accuracy"] = {"change": pa["change"], "sem": pa["sem"],
                                 "sigma": abs(pa["change"]) / pa["sem"] if pa["sem"] else None}
            entry["half_done"] = (entry["forgetting"]["change"] > DOSE_HALF_DONE
                                  if method == "naive" else None)
            # The progress fractions and the overshoots. The denominator is each quantity's own 0 -> 1 change, so it
            # exists only when this arm's admitted baseline sits at overlap 0.0 AND the anchor is at 1.0 -- the same
            # condition `e191` applies, and for the same reason: for the block arms the admitted baseline is `e153`,
            # which is itself at overlap 1.0, and the "rise" would be a `lam` difference between two runs at the same
            # overlap. The anchor pairing is admitted by the same inert-fields rule rather than assumed.
            anchor = load(overlap1) if Path(overlap1).is_file() else None
            anchor_overlap = (anchor.get("config") or {}).get("input_overlap") if anchor else None
            if anchor is not None and method in (anchor.get("methods") or {}):
                bad = [k for k in differing_fields(d["config"], anchor["config"]) if k not in INERT_FOR[method]]
                if entry["baseline_overlap"] != 0.0 or anchor_overlap != 1.0:
                    entry["progress_refused"] = (
                        f"not a 0 -> 1 change: this arm's admitted baseline is at overlap "
                        f"{entry['baseline_overlap']} and the anchor at {anchor_overlap}")
                elif bad:
                    entry["progress_refused"] = f"anchor not admitted for {method}: differs in {bad}"
                else:
                    anchor_reps = anchor["methods"][method]["replicates"]
                    entry["full_change"] = {
                        "forgetting": paired([r["mean_forgetting"] for r in anchor_reps], a["forgetting"]),
                        "accuracy": paired([r[acc_key] for r in anchor_reps], af)}
                    entry["progress_fraction"] = {
                        q: entry[q]["change"] / entry["full_change"][q]["change"]
                        for q in ("forgetting", "accuracy") if entry["full_change"][q]["change"]}
                    # the level against the anchor itself, which is what an overshoot beyond 100% has to be tested
                    # with: the two deltas share the baseline, so subtracting their sems in quadrature overstates
                    # it. BOTH quantities are oriented level-minus-anchor so a positive value means the level's
                    # quantity is larger -- the accuracy one is a COST, so its overshoot is negative when the cost is
                    # worse, and the first version had the forgetting one the other way round.
                    entry["overshoot_vs_anchor"] = {
                        "forgetting": paired(b["forgetting"], [r["mean_forgetting"] for r in anchor_reps]),
                        "accuracy": paired(bf, [r[acc_key] for r in anchor_reps])}
                    entry["anchor"] = Path(overlap1).name
            out["arms"][method] = entry
        rows.append(out)
    return {"baseline": Path(baseline).name, "levels": rows}


def report_dose(res: dict) -> int:
    print("   == the accuracy dose-response: each level against the baseline each ARM admits ==")
    missing = 0
    for row in res["levels"]:
        if row.get("status"):
            print(f"        {row['level']}: {row['status']}")
            missing += 1
            continue
        print(f"        {row['level']}: target {row['target_overlap']} -> achieved Jaccard "
              f"{row['achieved_overlap']}")
        for method, e in row["arms"].items():
            f, a = e["forgetting"], e["accuracy"]
            # the registered bar is a statement about achieved 0.3333, so it is checked only there (the first
            # version tagged every level, claiming something the registration does not say)
            at_midpoint = abs((row["achieved_overlap"] or 0) - 0.3333) < 1e-9
            tag = ""
            if method == "naive" and at_midpoint:
                tag = ("   P1's bar (> +0.0159, half the 0->1 rise) " +
                       ("MET" if f["change"] > DOSE_HALF_DONE else "NOT met"))
            elif method == "naive":
                tag = "   (P1's bar applies at achieved 0.3333, not here)"
            pair = f"{e.get('baseline_overlap')} -> {row['target_overlap']}"
            print(f"             {method:16} {pair:14} vs {e.get('baseline', '?')[:22]:24} forgetting {f['change']:+.4f}+/-{f['sem']:.4f}"
                  f"({f['sigma']:.1f}s)  accuracy {a['change']:+.4f}+/-{a['sem']:.4f}({a['sigma']:.1f}s)"
                  f"  n {e['n']}{tag}")
            if e.get("refusals"):
                print(f"                  (cleaner candidates refused: {'; '.join(e['refusals'])})")
            if e["differs_in"]:
                print(f"                  (admitted with inert differences in: {', '.join(e['differs_in'])})")
        na = row["arms"].get("naive")
        if na and na.get("forgetting", {}).get("sem"):
            sem = na["forgetting"]["sem"]
            parts = []
            for label, val in (("the change", abs(na["forgetting"]["change"])), ("P1's bar", DOSE_HALF_DONE)):
                sig = val / sem
                parts.append(f"{label} {val:.5f} = {sig:.2f}s ({seeds_for_three_sigma(sig):.0f} seeds at 3s)")
            print(f"             rule 42, at this level's naive forgetting sem {sem:.5f}: " + "; ".join(parts))
            # the shape of both quantities on one account, and the overshoot where the fraction passes 100%
            if na.get("progress_refused"):
                print(f"             progress: refused for this arm -- {na['progress_refused']}")
            elif na.get("progress_fraction"):
                bits = [f"{q} at {100 * v:.0f}% of its own 0->1 change" for q, v in na["progress_fraction"].items()]
                print(f"             progress ({na.get('anchor')} as the overlap-1.0 anchor): " + "; ".join(bits))
                for q, o in (na.get("overshoot_vs_anchor") or {}).items():
                    sig = abs(o["change"]) / o["sem"] if o["sem"] else 0.0
                    print(f"                  this level against that anchor, {q:11}: {o['change']:+.5f} "
                          f"+/-{o['sem']:.5f} = {sig:.2f}s"
                          + ("   <- the overshoot's own sem, which a fraction above 100% needs"
                             if na["progress_fraction"][q] > 1 else ""))
    print("        (the achieved overlaps are a property of mb+cx+al@n1307, 3 tasks of 80, seed 0: recompute them "
          "for any other circuit.)")
    return missing


def audit(runs_dir: Path = RUNS, pairs=PAIRS) -> dict:
    rows, rejects = [], []
    mismatches = []
    for label, method, lo, hi, expect in pairs:
        pa, pb = runs_dir / lo, runs_dir / hi
        if not pa.is_file() or not pb.is_file():
            rejects.append({"label": label, "why": "artifact missing"})
            continue
        da, db = load(pa), load(pb)
        diff = differing_fields(da["config"], db["config"])
        bad = {k: v for k, v in diff.items() if k not in INERT_FOR.get(method, set())}
        if bad:
            rejects.append({"label": label, "why": f"fields that are not inert for {method}: {sorted(bad)}"})
            continue
        A, B = load_arm(pa, method), load_arm(pb, method)
        if A is None or B is None:
            rejects.append({"label": label, "why": f"the {method} arm is absent from one payload"})
            continue
        if A["n"] != B["n"]:
            rejects.append({"label": label, "why": f"replicate counts differ: {A['n']} against {B['n']}"})
            continue
        pr = paired(B["forgetting"], A["forgetting"])          # overlap 1 minus overlap 0
        per_task = [paired(B["terms"][:, k], A["terms"][:, k]) for k in range(B["terms"].shape[1])]
        rows.append({"label": label, "method": method, "overlap0": lo, "overlap1": hi,
                     "differs_in": sorted(diff), "n": A["n"],
                     "level_overlap0": float(A["forgetting"].mean()),
                     "level_overlap1": float(B["forgetting"].mean()),
                     "change": pr["change"], "sem": pr["sem"],
                     "sigma": abs(pr["change"]) / pr["sem"] if pr["sem"] else None,
                     "per_task": [{"change": t["change"], "sem": t["sem"]} for t in per_task]})
    resolved = [r for r in rows if r["sigma"] and r["sigma"] >= 2]
    for row in rows + rejects:
        declared = next(e for lab, _m, _a, _b, e in pairs if lab == row["label"])
        got = "pair" if "change" in row else f"rejected: {row['why']}"
        if declared == "pair" and got != "pair":
            mismatches.append({"label": row["label"], "declared": declared, "got": got})
        if declared != "pair" and got == "pair":
            mismatches.append({"label": row["label"], "declared": declared, "got": got})
    return {"comparisons": rows, "rejected": rejects, "mismatches": mismatches,
            "n_mismatches": len(mismatches),
            "n_comparisons": len(rows), "n_resolved": len(resolved),
            "n_positive": sum(1 for r in rows if r["change"] > 0),
            "n_negative": sum(1 for r in rows if r["change"] < 0),
            "room_vs_effect": {"levels": [r["level_overlap0"] for r in rows],
                               "effects": [r["change"] for r in rows]}}


def report(res: dict) -> int:
    print(f"   comparisons admitted : {res['n_comparisons']}   of which resolved at 2 sigma: {res['n_resolved']}")
    print(f"   direction of the effect (overlap 1 minus overlap 0): {res['n_positive']} positive, "
          f"{res['n_negative']} negative")
    print(f"   {'comparison':52} {'overlap0':>9} {'overlap1':>9} {'change':>9} {'sem':>7} {'sigma':>6}")
    for r in sorted(res["comparisons"], key=lambda r: -r["level_overlap0"]):
        sig = f"{r['sigma']:6.2f}" if r["sigma"] is not None else "   n/a"
        print(f"   {r['label']:52} {r['level_overlap0']:9.4f} {r['level_overlap1']:9.4f} "
              f"{r['change']:+9.4f} {r['sem']:7.4f} {sig}")
        if r["differs_in"]:
            print(f"        (admitted with inert differences in: {', '.join(r['differs_in'])})")
    for r in res["rejected"]:
        print(f"   refused -- {r['label']}: {r['why']}")
    print(f"   declarations the corpus contradicts: {res['n_mismatches']}")
    for m in res["mismatches"]:
        print(f"        {m['label']}: declared {m['declared']}, got {m['got']}")
    print("   what the magnitudes do NOT do, said here so the table is not read as a law: the effect does not order")
    print("   with the overlap-0 level. The largest absolute effect (+0.0419) is not at the largest level (+0.0750,")
    print("   which moves +0.0318), and the largest RELATIVE effect is the arm with almost nothing to lose:")
    for r in sorted(res["comparisons"], key=lambda r: -r["level_overlap0"]):
        rel = (r["change"] / r["level_overlap0"]) if abs(r["level_overlap0"]) > 1e-6 else None
        sig = f"{r['sigma']:.2f} sigma" if r["sigma"] is not None else "sigma undefined (zero scatter)"
        print(f"        overlap-0 level {r['level_overlap0']:+.4f} -> effect {r['change']:+.4f} "
              f"({sig}" + (f", {rel:.1f}x the level)" if rel is not None else ", level at zero)"))
    return res["n_mismatches"]


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--runs", type=Path, default=RUNS)
    p.add_argument("--dose", type=Path, action="append", default=None,
                   help="an artifact at an intermediate overlap level, paired against --baseline; repeatable")
    p.add_argument("--baseline", type=Path, action="append", default=None,
                   help="candidate disjoint baselines, admitted per ARM (repeatable; default e140 then e153)")
    p.add_argument("--json-out", type=Path, default=None)
    args = p.parse_args(argv)

    if args.dose:
        cands = args.baseline or [Path("runs/e116_r32_40reps.json"),
                                  Path("runs/e140_r32_methods_plastic_40reps.json"),
                                  Path("runs/e153_r32_overlap1_methods_40reps.json")]
        dose = dose_read(args.dose, cands[0], candidates=cands)
        n = report_dose(dose)
        if args.json_out:
            write_json(args.json_out, {"dose": dose})
            print(f"wrote {args.json_out}")
        return 0
    res = audit(args.runs)
    n = report(res)
    if args.json_out:
        write_json(args.json_out, res)
        print(f"wrote {args.json_out}")
    return 0 if n == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
