"""E275 -- the suite makes it visible: one of the three configurations that cannot see its own spread, re-run.

`e267` turned the benchmark's own noise block into the suite each configuration would need to see its own spread, and
found **three** where every arm's test-set floor sits at or above that arm's replicate spread -- the configurations
that cannot tell the test set from the training. `e269` then measured what a suite costs, held-out decision by
held-out decision, and found it free next to the training that produces them. **This unit spends that**, on the
configuration whose requirement is the largest of the three.

The configuration is `e140_r32_methods_frozenbias_40reps`: cs 800, `readout_size` 32, `lam` 0.003, `frozen_bias`, five
arms, forty replicates, and a **144**-item suite at which the arms' variance fractions read 2.086, 1.112, 1.293, 1.104
and 1.309 -- every one above 1. The run below has the same configuration and **the same seed sequence**, with the
suite raised to **600** items (three tasks of 200), so the training is nominally identical and only the measurement
moved.

    runs/e140_r32_methods_frozenbias_40reps.json     144 items
    runs/e275_frozenbias_suite600_40reps.json        600 items

Registered before the data landed, all **confirmatory**:

- **Z1 -- the training did not move.** Every arm's per-replicate **training** column (`learned`, the per-task accuracy
  on the training set) is **identical** between the two runs, because the seeds and the configuration are the same and
  only the held-out suite changed. This is the built-in control: if the training columns differ, the two runs are not
  the same experiment and nothing below is a price for the suite. **Falsifier**: any arm whose training column differs.
- **Z2 -- and the floor falls by the ratio of the suites.** The test-set variance scales as `1/n_eval`, so each arm's
  fraction should fall by **144/600**; the check allows a factor of 1.5 either way for the replicate spread's own
  movement. **Falsifier**: any arm outside that band.
- **Z3 -- so the configuration becomes readable.** Every arm's fraction is **below 1** in the new run, where all five
  were at or above 1.10 in the old -- which is what `e267` said the suite would buy and `e269` said it would cost
  nothing to buy. **Falsifier**: any arm at or above 1.

**What it cannot do**: one configuration of the three, chosen because its requirement is the largest, so nothing here
says the other two behave the same way; forty replicates estimate each arm's spread on thirty-nine degrees of freedom,
so a fraction near the boundary of 1 is a factor-of-1.1 statement and not a sharp one; the check in Z2 is a band
because the *replicate spread* is itself a draw between two runs and not only the floor moved; `frozen_bias` removes
most of the training variance, so this is the easiest case in which to see the floor at all; and the run is one seed
sequence, so it is a replicate of the configuration's *visible* spread and not of the configuration's claim.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

from clfly.bench.artifacts import duration_seconds, write_json

#: The configuration at the suite it cannot see itself at, and at the suite it needs.
OLD = "runs/e140_r32_methods_frozenbias_40reps.json"
NEW = "runs/e275_frozenbias_suite600_40reps.json"
METRICS = ("final_accuracy", "mean_forgetting")
#: The training column the control reads, and the suite the new run asks for.
TRAINING = "learned"
WANTED_SUITE = 600
CLAIMS = (
    ("Z1", "the training did not move",
     "Every arm's per-replicate training column is identical between the two runs",
     "falsifier: any arm whose training column differs"),
    ("Z2", "and the floor falls by the ratio of the suites",
     "Each arm's variance fraction falls by the ratio of the suites, within a factor of 1.5",
     "falsifier: any arm outside that band"),
    ("Z3", "so the configuration becomes readable",
     "Every arm's fraction is below one in the new run, where all five were at or above 1.10",
     "falsifier: any arm at or above one"),
)


def load(path):
    p = Path(path)
    if not p.exists():
        return None
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def arms(d: dict) -> list[str]:
    meth = d.get("methods")
    if not isinstance(meth, dict):
        return []
    return sorted(a for a in meth if isinstance(meth[a], dict) and meth[a].get("replicates"))


def fractions(d: dict) -> dict:
    """Each arm's test-set floor as a fraction of its own replicate spread, per metric."""
    ev = d.get("evaluation_noise") or {}
    out = {}
    for a in arms(d):
        for metric in METRICS:
            xs = [r[metric] for r in d["methods"][a]["replicates"]]
            if len(xs) < 2:
                continue
            mean = sum(xs) / len(xs)
            v = sum((x - mean) ** 2 for x in xs) / (len(xs) - 1)
            e = (ev.get(a) or {}).get("binomial_sem")
            if e is None or v <= 0:
                continue
            out[f"{a}/{metric}"] = e ** 2 / v
    return out


def training_rows(d: dict, arm: str) -> list:
    return [r.get(TRAINING) for r in d["methods"][arm]["replicates"]]


def reading(d: dict) -> dict:
    return {"n_eval": (d.get("evaluation_noise") or {}).get("n_eval"), "n": len(d["methods"][arms(d)[0]]["replicates"]),
            "arms": arms(d), "fractions": fractions(d), "seconds": duration_seconds(d),
            "training": {a: training_rows(d, a) for a in arms(d)},
            "metrics": {m: {a: [r[m] for r in d["methods"][a]["replicates"]] for a in arms(d)} for m in METRICS}}


def judge(old: dict, new: dict) -> list[dict]:
    out: list[dict] = []
    if old is None or new is None:
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- one of the two runs is absent"} for c in CLAIMS]

    differ = [a for a in old["arms"] if a in new["training"] and old["training"][a] != new["training"][a]]
    same_arms = [a for a in old["arms"] if a in new["training"]]
    out.append({"id": "Z1", "measured": f"{len(same_arms)} arms compared on the training column; identical: "
                                        f"{len(same_arms) - len(differ)}; differing: {differ}",
                "verdict": "MET -- the same seeds and the same training, so only the measurement moved"
                if same_arms and not differ else
                "FALSIFIER FIRED -- the training column differs, so the two runs are not the same experiment"})

    band, lines, ok = 1.5, [], True
    for key, f_old in sorted(old["fractions"].items()):
        if key not in new["fractions"]:
            ok = False
            lines.append(f"{key}: absent in the new run")
            continue
        expected = f_old * old["n_eval"] / new["n_eval"]
        got = new["fractions"][key]
        ratio = got / expected if expected > 0 else float("inf")
        if not (1 / band <= ratio <= band):
            ok = False
        lines.append(f"{key}: {f_old:.2f} to {got:.2f} against an expected {expected:.2f} (x{ratio:.2f})")
    out.append({"id": "Z2", "measured": "; ".join(lines),
                "verdict": "MET -- every arm's floor fell by the ratio of the suites" if ok else
                           "FALSIFIER FIRED -- an arm is outside the band"})

    above = {k: v for k, v in new["fractions"].items() if v >= 1.0}
    worst_old = max(old["fractions"].values()) if old["fractions"] else float("nan")
    out.append({"id": "Z3", "measured": f"the new suite is {new['n_eval']} items against {old['n_eval']}; the largest "
                                        f"fraction falls from {worst_old:.2f} to "
                                        f"{max(new['fractions'].values()):.2f}; arms still at or above one: "
                                        f"{above or 'none'}",
                "verdict": "MET -- the configuration can see its own spread now" if new["fractions"] and not above
                else f"FALSIFIER FIRED -- {above}"})
    return out


def report(old: dict, new: dict) -> int:
    if old is None or new is None:
        print("both runs are needed: " + ", ".join(p for p in (OLD, NEW)))
    else:
        print("== the same configuration at two suites ==")
        for name, r in ((OLD, old), (NEW, new)):
            print(f"\n   {name.split('/')[-1]}  n_eval {r['n_eval']}  {r['n']} replicates  "
                  f"{r['seconds'] / 3600 if r['seconds'] else float('nan'):.2f} h")
            for key, f in sorted(r["fractions"].items()):
                print(f"      {key:34} fraction {f:6.2f}")
        print("\n   the training column, arm by arm: "
              + ", ".join(f"{a} {'identical' if old['training'].get(a) == new['training'].get(a) else 'DIFFERS'}"
                          for a in old["arms"]))
    print("\n== the registered claims, Z1-Z3 ==")
    j = judge(old, new)
    for c, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {c[2]}")
        print(f"          and its {c[3]}")
    print("\n   (a configuration whose whole run-to-run spread sat inside its test set's own noise, bought a "
          "four-times-larger")
    print("    suite for the price e269 measured, with the training held identical so the comparison is the suite's)")
    return sum("REFUSED" in row["verdict"] for row in j)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args(argv)
    a, b = load(OLD), load(NEW)
    old = reading(a) if a else None
    new = reading(b) if b else None
    if args.json_out:
        write_json(args.json_out, {"old": OLD, "new": NEW, "wanted_suite": WANTED_SUITE,
                                   "old_n_eval": old["n_eval"] if old else None,
                                   "new_n_eval": new["n_eval"] if new else None,
                                   "fractions_old": old["fractions"] if old else None,
                                   "fractions_new": new["fractions"] if new else None,
                                   "claims": judge(old, new)})
        print(f"wrote {args.json_out}")
    return report(old, new)


if __name__ == "__main__":
    sys.exit(main())
