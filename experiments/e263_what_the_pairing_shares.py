"""E263 -- what the pairing shares: the benchmark's own noise decomposition is arm-specific, and the arms are not.

The network benchmark prices its central contrast two ways. `evaluation_noise` splits **each arm's** run-to-run
variance into a test-set part (the binomial noise of `n_eval` held-out decisions, printed as "removable") and a
training part, and the printed sentence tells the reader how much of the spread a bigger test set would take away.
`paired_contrast` then reports the same contrast **paired**, with the arm-to-arm correlation of the sixteen replicates
that licenses it -- the line's own note says the paired sem is the right one "because the two arms share a seed
sequence".

The two blocks are computed in the same run and neither knows about the other, and together they are inconsistent:

    the decomposition gives each arm its OWN test-set and training component, so it predicts a correlation of zero
    between the arms, and a paired sem no tighter than the unpaired one.

**The artifacts report otherwise, and the gap is measurable.** Writing `v`, `b` and `t` for an arm's total, test-set
and training variance, the observed paired variance is `v1 + v2 - 2*cov`, so `cov` is recoverable from the artifact's
own numbers -- and the algebra reproduces the reported `corr` to three decimals in all six readings, which is what
makes the rest of this module a measurement rather than a model.

Registered, all **confirmatory** and computed in the exploration that wrote the module:

- **C1 -- the arms are correlated and the decomposition cannot say so.** Every one of the six paired readings carries
  a positive arm-to-arm correlation (**0.28 to 0.54**), where the artifact's own two components are arm-specific by
  construction. **Falsifier**: any reading at or below 0.10.
- **C2 -- and the test set cannot account for it.** Perfectly shared test-set noise is the **most** any item term can
  contribute, and it predicts correlations of 0.35, 0.18, 0.35, 0.18, 0.23 and 0.11 against the observed 0.54, 0.50,
  0.32, 0.35, 0.32 and 0.28 -- short by more than 0.05 in **five of the six**, so those five require a shared
  *training* component. **Falsifier**: three or fewer readings short by more than 0.05.
- **C3 -- a bigger test set would take most of the pairing's benefit with it.** The advantage is **1.18x to 1.47x**
  today and **0.98x to 1.27x** once the shared item term is removed; it falls in every reading and by more than 0.10
  in five. On `cell_class` on accuracy the surviving advantage is **0.98x**, i.e. that reading's entire pairing
  benefit is the shared test set. **Falsifier**: any reading whose advantage does not fall, or fewer than three
  falling by more than 0.10.
- **C4 -- and the source of the benefit splits by metric.** Forgetting's shared-training correlation has a *lower*
  bound above the shared-item correlation's *upper* bound in **all three** runs, so on forgetting the pairing is not
  the test set at all; on accuracy the same comparison reverses in all three. **Falsifier**: any run where the
  forgetting comparison fails or the accuracy comparison does not reverse.

**What it cannot do**: the shared-item figure is an **upper bound** (it assumes the two arms' test-set noises are
perfectly correlated) and the training figure is a **lower bound**, so C4's forgetting half is a strict statement
while its accuracy half is a bound-versus-bound reading that does not prove items dominate; every reading here is at
the same `n_eval = 144`, so "a bigger test set" is arithmetic under the model and not a run; the decomposition itself
inherits the model's assumption that the held-out decisions are independent, which `e8`'s own print says is a signal
when a fraction exceeds 100%; and only the three artifacts that carry both an `evaluation_noise` block and a
`matched_pair` block can be read this way.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

from clfly.bench.artifacts import write_json

#: The three runs that carry both an `evaluation_noise` block and a `matched_pair` block.
ARTS = ("runs/e60_side_lam0.1_16reps.json", "runs/e46_c2b_powered.json", "runs/e178_rung_side_cs300_144reps.json")
METRICS = ("final_accuracy", "mean_forgetting")
ARMS = ("ewc-block", "ewc-block-rand")
CLAIMS = (
    ("C1", "the arms are correlated and the decomposition cannot say so",
     "Every paired reading carries a positive arm-to-arm correlation of at least 0.10 where the artifact's own "
     "components are arm-specific",
     "falsifier: any reading at or below 0.10"),
    ("C2", "and the test set cannot account for the correlation",
     "Perfectly shared test-set noise fails to reach the observed correlation by more than 0.05 in at least two "
     "thirds of the readings",
     "falsifier: under two thirds of the readings short by more than 0.05"),
    ("C3", "a bigger test set would take most of the pairing's benefit with it",
     "Removing the shared item term lowers the pairing's advantage in every reading and by more than 0.10 in at "
     "least half of them",
     "falsifier: any reading whose advantage does not fall, or under half falling by more than 0.10"),
    ("C4", "the source of the benefit splits by metric",
     "Forgetting's shared-training lower bound exceeds the shared-item upper bound in every run, and the accuracy "
     "comparison reverses in every run",
     "falsifier: any run where either comparison fails"),
)


def load(path) -> dict | None:
    p = Path(path)
    if not p.exists():
        return None
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def variance(xs: list[float]) -> float:
    n = len(xs)
    mean = sum(xs) / n
    return sum((x - mean) ** 2 for x in xs) / (n - 1)


def reading(d: dict, metric: str) -> dict:
    """One artifact's one metric, decomposed from the artifact's own two blocks."""
    ev = d["evaluation_noise"]
    v = {a: variance([r[metric] for r in d["methods"][a]["replicates"]]) for a in ARMS}
    b = {a: ev[a]["binomial_sem"] ** 2 for a in ARMS}
    #: the runner itself clamps its residual at zero, so an arm whose test-set floor exceeds its whole spread
    #: is read with no training part rather than with a negative one
    t = {a: max(v[a] - b[a], 0.0) for a in ARMS}
    mp = d["matched_pair"][metric]
    vd = mp["replicate_sd"] ** 2
    cov = (v[ARMS[0]] + v[ARMS[1]] - vd) / 2.0
    #: the most shared test-set noise can contribute: the two arms' item noises perfectly correlated
    cov_items = math.sqrt(b[ARMS[0]] * b[ARMS[1]])
    cov_train = cov - cov_items
    denom = math.sqrt(v[ARMS[0]] * v[ARMS[1]])
    r = {"metric": metric, "v": v, "b": b, "t": t, "v_difference": vd, "cov": cov, "cov_items": cov_items,
         "cov_train": cov_train, "corr_reported": mp["corr"], "corr_from_cov": cov / denom,
         "corr_items": cov_items / denom,
         "corr_train": cov_train / math.sqrt(t[ARMS[0]] * t[ARMS[1]])
         if t[ARMS[0]] > 0 and t[ARMS[1]] > 0 else float("nan"),
         "advantage": math.sqrt((v[ARMS[0]] + v[ARMS[1]]) / vd) if vd > 0 else float("inf"),
         "n": mp["n"], "sem_paired": mp["sem_paired"], "sem_unpaired": mp["sem_unpaired"]}
    surv_d = t[ARMS[0]] + t[ARMS[1]] - 2 * cov_train
    r["advantage_without_items"] = math.sqrt((t[ARMS[0]] + t[ARMS[1]]) / surv_d) if surv_d > 0 else float("inf")
    #: the share of each arm's variance the arms hold in common
    r["cov_over_var"] = {a: cov / v[a] for a in ARMS}
    return r


def readings() -> dict[str, dict]:
    out = {}
    for path in ARTS:
        d = load(path)
        if d is None or "evaluation_noise" not in d or "matched_pair" not in d:
            continue
        for metric in METRICS:
            out[f"{Path(path).name}/{metric}"] = reading(d, metric)
    return out


def judge(rows: dict[str, dict]) -> list[dict]:
    out: list[dict] = []
    if not rows:
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- no artifact carries both blocks"} for c in CLAIMS]

    cs = {n: r["corr_reported"] for n, r in rows.items()}
    low = [n for n, c in cs.items() if c <= 0.10]
    out.append({"id": "C1", "measured": "; ".join(f"{n} {c:+.3f}" for n, c in sorted(cs.items(), key=lambda kv: kv[1]))
                + f"; the decomposition's own two components are arm-specific, so it predicts 0",
                "verdict": "MET -- every reading correlates the arms" if not low else
                           f"FALSIFIER FIRED -- {low} at or below 0.10"})

    short = {n: r["corr_reported"] - r["corr_items"] for n, r in rows.items()}
    big = [n for n, d in short.items() if d > 0.05]
    need = math.ceil(2 * len(rows) / 3)
    out.append({"id": "C2", "measured": "; ".join(f"{n}: observed {rows[n]['corr_reported']:.3f} against an item "
                                                  f"ceiling of {rows[n]['corr_items']:.3f} ({short[n]:+.3f})"
                                                  for n in sorted(short)),
                "verdict": f"MET -- {len(big)} of {len(rows)} are short by more than 0.05, so those need a shared "
                           f"training component" if len(big) >= need else
                           f"FALSIFIER FIRED -- only {len(big)} of {len(rows)} are short by more than 0.05"})

    falls = {n: r["advantage"] - r["advantage_without_items"] for n, r in rows.items()}
    big_falls = [n for n, f in falls.items() if f > 0.10]
    need_falls = math.ceil(len(rows) / 2)
    out.append({"id": "C3", "measured": "; ".join(f"{n}: {rows[n]['advantage']:.3f}x now, "
                                                 f"{rows[n]['advantage_without_items']:.3f}x without the shared "
                                                 f"items ({falls[n]:+.3f})" for n in sorted(falls)),
                "verdict": f"MET -- every advantage falls and {len(big_falls)} fall by more than 0.10"
                if all(f > 0 for f in falls.values()) and len(big_falls) >= need_falls else
                "FALSIFIER FIRED -- an advantage does not fall, or too few fall far"})

    per_metric = {}
    for n, r in rows.items():
        per_metric.setdefault(r["metric"], []).append(n)
    forbid = [n for n, r in rows.items() if r["metric"] == "mean_forgetting" and not r["corr_train"] > r["corr_items"]]
    acc_bad = [n for n, r in rows.items() if r["metric"] == "final_accuracy" and not r["corr_items"] > r["corr_train"]]
    out.append({"id": "C4", "measured": "; ".join(f"{n}: training lower bound {r['corr_train']:.3f} against item "
                                                  f"upper bound {r['corr_items']:.3f} ({r['metric']})"
                                                  for n, r in sorted(rows.items())),
                "verdict": "MET -- forgetting separates on the strict side in every run, and accuracy reverses in "
                           "every run" if not forbid and not acc_bad else
                           f"FALSIFIER FIRED -- forgetting {forbid}, accuracy {acc_bad}"})
    return out


def report(rows: dict[str, dict]) -> int:
    print("== the two blocks of one artifact, read against each other ==")
    print(f"   {'reading':44} {'v bio':>8} {'v rnd':>8} {'cov':>8} {'corr obs':>9} {'corr items':>11} "
          f"{'corr train':>11} {'now':>7} {'no items':>9}")
    for n in sorted(rows):
        r = rows[n]
        print(f"   {n:44} {r['v'][ARMS[0]]:8.6f} {r['v'][ARMS[1]]:8.6f} {r['cov']:8.6f} "
              f"{r['corr_reported']:9.3f} {r['corr_items']:11.3f} {r['corr_train']:11.3f} "
              f"{r['advantage']:6.3f}x {r['advantage_without_items']:8.3f}x")
    print("\n   the algebra's own correlation against the reported one, per reading:")
    for n in sorted(rows):
        r = rows[n]
        print(f"      {n:44} from the covariance {r['corr_from_cov']:.3f}  reported {r['corr_reported']:.3f}  "
              f"(agrees: {abs(r['corr_from_cov'] - r['corr_reported']) < 5e-4})")

    print("\n== what the arms hold in common, as a share of each arm's own run-to-run variance ==")
    for n in sorted(rows):
        r = rows[n]
        print(f"   {n:44} {r['cov_over_var'][ARMS[0]]:.3f} of the biological arm, "
              f"{r['cov_over_var'][ARMS[1]]:.3f} of its random control")

    print("\n== the registered claims, C1-C4 ==")
    j = judge(rows)
    for c, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {c[2]}")
        print(f"          and its {c[3]}")
    print("\n   (a decomposition is complete only about the components it names: here the test set and the training")
    print("    arm are both per-arm quantities, and the pairing the line relies on needs a third, shared one)")
    return sum("REFUSED" in row["verdict"] for row in j)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args(argv)

    rows = readings()
    if not rows:
        raise SystemExit("need the C2b artifacts -- they are what carry both blocks")
    if args.json_out:
        write_json(args.json_out, {"arms": list(ARMS), "artifacts": list(ARTS),
                                   "readings": {n: {k: (v if not isinstance(v, dict) else v)
                                                    for k, v in r.items()} for n, r in rows.items()},
                                   "claims": judge(rows)})
        print(f"wrote {args.json_out}")
    return report(rows)


if __name__ == "__main__":
    sys.exit(main())
