"""E151 -- does the aggregate hide it? The per-task decomposition of every forty-replicate contrast in the record.

`mean_forgetting` is a mean over the first `T - 1` tasks, so **every headline contrast in this project is an
average of two numbers that can disagree** -- and this plan has already named that as a trap twice, once for the
diagonal (which improves task 0 by 3.79 sigma while *worsening* task 1) and once for the anchored arm (whose
last-task cost is invisible to a mean over the first `T - 1`). Both were found by hand, one contrast at a time.
This script is that hand search done once, over every contrast the record quotes at **forty paired replicates**.

For each contrast (A minus B, paired on the forty shared seeds) it reports five numbers and one label:

    aggregate forgetting   the quantity the paper prints                  (mean over tasks 0 and 1)
    task 0 / task 1        the two terms that average to it
    newest-task retention  the final accuracy on the task *no* forgetting term covers, i.e. the half of
                           the eighth trap the aggregate cannot show either way

and the label is a rule rather than a reading:

    fair          the aggregate resolves and both terms resolve with its sign
    one term      the aggregate resolves, exactly one term resolves
    cancelling    the aggregate resolves while the two terms DISAGREE in sign, or neither term does --
                  then the aggregate is a difference between two effects, not a summary of one
    hidden        the aggregate does NOT resolve while a single term does
    null          nothing resolves

**This is an audit and not a run**, in the same family as `e105` and `e127`: it makes a named trap executable
rather than remembered. Its result is whatever the catalogue says -- and the reason to keep the label's
categories apart is that only one of them is a defect: `one term` is a fair summary of a lopsided effect,
`cancelling` and `hidden` are the two shapes in which the printed number is not the effect.

    python -m experiments.e151_pertask_contrast_audit
    python -m experiments.e151_pertask_contrast_audit --json-out runs/e151_pertask_audit.json

ASCII output only.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np

from clfly.bench.artifacts import write_json

#: `T - 1` terms in `mean_forgetting`, so the aggregate is the mean of the first two.
N_TERMS = 2
RESOLVED = 2.0

#: (label, A path, A method, B path, B method) -- every contrast the record quotes at forty paired replicates.
CONTRASTS: tuple[tuple[str, str, str, str, str], ...] = (
    ("e133: ewc - naive", "runs/e133_r32_naive_ewc_40reps.json", "ewc",
     "runs/e133_r32_naive_ewc_40reps.json", "naive"),
    ("e140: ewc - naive", "runs/e140_r32_methods_plastic_40reps.json", "ewc",
     "runs/e140_r32_methods_plastic_40reps.json", "naive"),
    ("e140: block - naive", "runs/e140_r32_methods_plastic_40reps.json", "ewc-block",
     "runs/e140_r32_methods_plastic_40reps.json", "naive"),
    ("e140: block-rand - naive", "runs/e140_r32_methods_plastic_40reps.json", "ewc-block-rand",
     "runs/e140_r32_methods_plastic_40reps.json", "naive"),
    ("e140: replay - naive", "runs/e140_r32_methods_plastic_40reps.json", "replay",
     "runs/e140_r32_methods_plastic_40reps.json", "naive"),
    ("e140: block - block-rand", "runs/e140_r32_methods_plastic_40reps.json", "ewc-block",
     "runs/e140_r32_methods_plastic_40reps.json", "ewc-block-rand"),
    ("e141: lam 3e-4 - naive", "runs/e141_r32_ewc_lam3e-4.json", "ewc",
     "runs/e133_r32_naive_ewc_40reps.json", "naive"),
    ("e141: lam 3e-3 - naive", "runs/e133_r32_naive_ewc_40reps.json", "ewc",
     "runs/e133_r32_naive_ewc_40reps.json", "naive"),
    ("e141: lam 3e-2 - naive", "runs/e141_r32_ewc_lam3e-2.json", "ewc",
     "runs/e133_r32_naive_ewc_40reps.json", "naive"),
    ("e141: lam 3e-1 - naive", "runs/e141_r32_ewc_lam3e-1.json", "ewc",
     "runs/e133_r32_naive_ewc_40reps.json", "naive"),
    ("e141: lam 3e-4 - lam 3e-3", "runs/e141_r32_ewc_lam3e-4.json", "ewc",
     "runs/e133_r32_naive_ewc_40reps.json", "ewc"),
    ("e138: anchored33 - naive", "runs/e138_r32_ewc_anchorbias33.json", "ewc",
     "runs/e133_r32_naive_ewc_40reps.json", "naive"),
    ("e138: anchored1 - naive", "runs/e138_r32_ewc_anchorbias1.json", "ewc",
     "runs/e133_r32_naive_ewc_40reps.json", "naive"),
    ("e138: anchored33 - unanchored", "runs/e138_r32_ewc_anchorbias33.json", "ewc",
     "runs/e133_r32_naive_ewc_40reps.json", "ewc"),
    ("e125: frozen offsets - naive", "runs/e125_r32_frozenbias.json", "naive",
     "runs/e133_r32_naive_ewc_40reps.json", "naive"),
    ("e147: frozen+ewc - frozen", "runs/e147_r32_frozenbias_ewc_lam3e-4.json", "ewc",
     "runs/e125_r32_frozenbias.json", "naive"),
    ("e147: frozen+ewc - naive", "runs/e147_r32_frozenbias_ewc_lam3e-4.json", "ewc",
     "runs/e133_r32_naive_ewc_40reps.json", "naive"),
    ("e142: overlap1 - base", "runs/e142_r32_overlap1.json", "naive",
     "runs/e133_r32_naive_ewc_40reps.json", "naive"),
    ("e143: wiring frozen - wiring naive", "runs/e143_r32_overlap1_frozenbias.json", "naive",
     "runs/e144_r32_overlap1_methods_40reps.json", "naive"),
    ("e144: ewc - naive (wiring)", "runs/e144_r32_overlap1_methods_40reps.json", "ewc",
     "runs/e144_r32_overlap1_methods_40reps.json", "naive"),
    ("e144: block-rand - naive (wiring)", "runs/e144_r32_overlap1_methods_40reps.json", "ewc-block-rand",
     "runs/e144_r32_overlap1_methods_40reps.json", "naive"),
    ("e144: block - block-rand (wiring)", "runs/e144_r32_overlap1_methods_40reps.json", "ewc-block",
     "runs/e144_r32_overlap1_methods_40reps.json", "ewc-block-rand"),
)


def load_arm(path: Path, method: str) -> dict | None:
    """The three per-task series this audit needs, or None when the artifact or the method is absent."""
    if not Path(path).is_file():
        return None
    entry = json.loads(Path(path).read_text(encoding="utf-8")).get("methods", {}).get(method)
    if entry is None:
        return None
    reps = entry["replicates"]
    return {
        "forgetting": np.array([r["mean_forgetting"] for r in reps]),
        "terms": np.array([[r["forgetting_per_task"][k] for k in range(N_TERMS)] for r in reps]),
        # the newest task's final retention: what a mean over the first T-1 tasks can show neither way
        "newest": np.array([r["final_per_task"][-1] for r in reps]),
        "n": len(reps),
    }


def paired(a: np.ndarray, b: np.ndarray) -> dict:
    d = np.asarray(a) - np.asarray(b)
    n = len(d)
    sem = float(d.std(ddof=1) / math.sqrt(n)) if n > 1 else float("nan")
    mean = float(d.mean())
    return {"change": mean, "sem": sem,
            "sigma": (abs(mean) / sem) if sem else (0.0 if mean == 0 else float("nan")),
            "n": n, "negative": int((d < 0).sum())}


def classify(aggregate: dict, terms: list[dict]) -> str:
    """The label, as a rule over sigma and signs -- so the catalogue cannot be read selectively.

    The four resolved classes are kept apart because they are different objects. `fair` is a summary of one
    effect; `one term` is a summary of a lopsided one; `weak pair` resolves only because two sub-threshold terms
    add, so the aggregate is **not** a summary of any single effect; and `cancelling` is a difference between two
    effects whose signs disagree -- the only one of the four in which the printed number and the effect point in
    different directions.
    """
    agg_res = aggregate["sigma"] >= RESOLVED
    term_res = [t["sigma"] >= RESOLVED for t in terms]
    signs = {math.copysign(1, t["change"]) for t in terms if t["change"] != 0}
    if not agg_res:
        return "hidden" if any(term_res) else "null"
    if len(signs) > 1:
        return "cancelling"
    if all(term_res):
        return "fair"
    return "one term" if any(term_res) else "weak pair"


def audit(contrasts=CONTRASTS) -> dict:
    rows, missing = [], []
    for label, a_path, a_method, b_path, b_method in contrasts:
        a, b = load_arm(Path(a_path), a_method), load_arm(Path(b_path), b_method)
        if a is None or b is None:
            missing.append({"label": label, "a": f"{a_path}[{a_method}]", "b": f"{b_path}[{b_method}]",
                            "a_present": a is not None, "b_present": b is not None})
            continue
        aggregate = paired(a["forgetting"], b["forgetting"])
        terms = [paired(a["terms"][:, k], b["terms"][:, k]) for k in range(N_TERMS)]
        newest = paired(a["newest"], b["newest"])
        rows.append({
            "label": label, "a_path": a_path, "a_method": a_method, "b_path": b_path, "b_method": b_method,
            "aggregate": aggregate, "terms": terms, "newest_retention": newest,
            "label_class": classify(aggregate, terms),
            "term_signs_agree": bool(len({math.copysign(1, t["change"]) for t in terms if t["change"] != 0}) <= 1),
        })
    counts: dict[str, int] = {}
    for r in rows:
        counts[r["label_class"]] = counts.get(r["label_class"], 0) + 1
    return {"rows": rows, "missing": missing, "counts": counts, "n_contrasts": len(rows)}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args()

    res = audit()
    print("== every forty-replicate contrast in the record, decomposed by task ==")
    print(f"   contrasts audited {res['n_contrasts']}   missing artifacts {len(res['missing'])}")
    hdr = ("contrast", "aggregate", "sigma", "task0", "sigma", "task1", "sigma", "newest", "sigma", "class")
    print("  " + "".join(f"{h:>11}" for h in hdr))
    for r in res["rows"]:
        agg, t0, t1, nw = r["aggregate"], r["terms"][0], r["terms"][1], r["newest_retention"]
        print(f"  {r['label']:<40}{agg['change']:>+11.4f}{agg['sigma']:>11.2f}"
              f"{t0['change']:>+11.4f}{t0['sigma']:>11.2f}{t1['change']:>+11.4f}{t1['sigma']:>11.2f}"
              f"{nw['change']:>+11.4f}{nw['sigma']:>11.2f}   {r['label_class']}")
    print("\n== the classes ==" + "".join(f"   {k}: {v}" for k, v in sorted(res["counts"].items())))
    for want in ("cancelling", "hidden", "one term"):
        rows = [r for r in res["rows"] if r["label_class"] == want]
        if rows:
            print(f"   {want}: " + "; ".join(r["label"] for r in rows))
    for m in res["missing"]:
        print(f"   MISSING {m['label']}: {m['a']} present={m['a_present']} / {m['b']} present={m['b_present']}")
    if args.json_out:
        write_json(args.json_out, res)
        print(f"\nwrote {args.json_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
