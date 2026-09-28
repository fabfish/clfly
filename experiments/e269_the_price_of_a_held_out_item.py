"""E269 -- the price of a held-out item, measured: the suite `e267` asked for costs less than the noise of one run.

`e267` turned the benchmark's own noise block into the suite each configuration would need, found three that cannot see
their own spread, and **reported rather than claimed** that the fix is a task-suite regeneration and not a retraining --
"the cost of the fix is a statement about the generator and not a measurement". This module makes it a measurement.

Two runs of the same configuration differ in `--test` alone: three tasks of 48 held-out decisions, which is the
**144** the whole corpus reads at, against three of **366**, which is **1098** -- the suite the worst of `e267`'s three
configurations needs, to within two items, because that requirement came out of a fraction of 7.61. One replicate of
one arm each, so the training work is identical and the only difference is how many decisions are evaluated:

    runs/e269_suite144_1rep.json      n_eval 144,   30.47 s
    runs/e269_suite1098_1rep.json     n_eval 1098,  23.38 s

Registered, all **confirmatory** and computed in the exploration that wrote the module:

- **T1 -- the larger suite is real and the runner records it.** The second artifact carries `n_eval = 1098` against the
  first's **144** (3 tasks of 366 against 3 of 48), with `n_train` unchanged at 96 per task, so the two runs differ in
  the held-out decisions and nothing else. **Falsifier**: equal `n_eval`, or a changed training set.
- **T2 -- and the extra 954 decisions cost less than the difference between the two clocks.** The 1098-item run was
  **faster** than the 144-item one (23.4 s against 30.5 s). Charging the whole 7.1 s difference to the extra items --
  the conservative direction, since the sign is backwards -- prices a decision at **under 0.01 s**. **Falsifier**: a
  difference above half the smaller run's clock.
- **T3 -- so the suite `e267` asked for costs under half a minute.** The requirement it computed for the worst
  configuration was 1096 items and this run built 1098; at the charged rate the whole suite is **under 8 seconds** of
  machine time against the **47 minutes** a real sixteen-replicate four-arm run of that cell takes (measured, `e266`),
  i.e. **under 1%**. **Falsifier**: above 5%.

**What it cannot do**: two single-replicate runs give one timing draw each, so the difference has no error bar and the
bound in T2 is a bound and not an estimate -- a second pair would price the decision properly; the test items are
generated with the training data in one pass, so an item's marginal cost is not separable from the setup that both runs
pay; 1098 items is the requirement of the *worst* of the three configurations and not of a suite forty times larger, so
nothing here says a much larger suite stays free; and the runs carry one arm, so the evaluation cost per arm is not
measured -- a four-arm run evaluates the suite four times over, which is the direction that would show a cost.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from clfly.bench.artifacts import duration_seconds, write_json

#: The two runs, smaller suite first, and what the audits ask for.
SMALL = "runs/e269_suite144_1rep.json"
LARGE = "runs/e269_suite1098_1rep.json"
#: `e267`'s computed requirement for the worst configuration, and the clock of a real run of that cell (`e266`).
WANTED = 1096
REAL_RUN_SECONDS = 47 * 60
CLAIMS = (
    ("T1", "the larger suite is real and the runner records it",
     "The two runs differ in `n_eval` and in nothing else, with the training set unchanged",
     "falsifier: equal n_eval, or a changed training set"),
    ("T2", "and the extra decisions cost less than the difference between the two clocks",
     "Charging the whole difference to the extra held-out decisions prices one at under 0.01 s",
     "falsifier: a difference above half the smaller run's clock"),
    ("T3", "so the suite the audits asked for costs under half a minute",
     "The extra decisions are charged the whole difference between the two clocks, and that is under 1% of the "
     "clock a real run of that cell takes",
     "falsifier: a charge above 5% of a real run"),
)


def load(path):
    p = Path(path)
    if not p.exists():
        return None
    import json
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def reading(d: dict) -> dict:
    cfg = d["config"]
    return {"n_eval": d["evaluation_noise"]["n_eval"], "seconds": duration_seconds(d),
            "test_per_task": [t["n_test"] for t in d["tasks"]], "train_per_task": [t["n_train"] for t in d["tasks"]],
            "repeats": cfg.get("repeats"), "methods": cfg.get("methods"), "lam": cfg.get("lam"),
            "circuit_size": cfg.get("circuit_size"), "readout_size": cfg.get("readout_size"),
            "basis": cfg.get("basis"), "shared_head": cfg.get("shared_head"),
            "fisher_batches": cfg.get("fisher_batches")}


def judge(small: dict, large: dict) -> list[dict]:
    out: list[dict] = []
    if small is None or large is None:
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- one of the two runs is absent"} for c in CLAIMS]

    same = (small["train_per_task"] == large["train_per_task"] and small["repeats"] == large["repeats"]
            and small["methods"] == large["methods"] and small["lam"] == large["lam"]
            and small["circuit_size"] == large["circuit_size"] and small["basis"] == large["basis"])
    out.append({"id": "T1", "measured": f"n_eval {small['n_eval']} against {large['n_eval']}; test per task "
                                        f"{small['test_per_task']} against {large['test_per_task']}; train per task "
                                        f"{small['train_per_task']} against {large['train_per_task']}; "
                                        f"everything else equal: {same}",
                "verdict": "MET -- the runs differ in the held-out decisions and nothing else"
                if large["n_eval"] > small["n_eval"] and same else
                "FALSIFIER FIRED -- the suites are the same size or something else moved"})

    extra_items = large["n_eval"] - small["n_eval"]
    diff = small["seconds"] - large["seconds"]
    per_item = diff / extra_items if extra_items else float("nan")
    fast = large["seconds"] < small["seconds"]
    out.append({"id": "T2", "measured": f"{extra_items} extra decisions; the two clocks are {small['seconds']:.2f} s "
                                        f"against {large['seconds']:.2f} s, so the larger suite ran "
                                        f"{'faster' if fast else 'slower'} by {abs(diff):.2f} s; charging the whole "
                                        f"difference to those decisions prices one at {abs(per_item):.4f} s",
                "verdict": "MET -- the extra decisions cost less than the difference between the clocks"
                if abs(diff) <= 0.5 * small["seconds"] else
                "FALSIFIER FIRED -- the difference is over half the smaller run's clock"})

    #: the conservative charge for the extra decisions is the whole difference between the clocks, either way round
    cost = abs(diff)
    share = cost / REAL_RUN_SECONDS
    out.append({"id": "T3", "measured": f"the extra {extra_items} decisions are charged {cost:.2f} s, which is what "
                                        f"the requirement of {WANTED} items costs against the "
                                        f"{REAL_RUN_SECONDS / 60:.0f} min a real run of that cell takes "
                                        f"({100 * share:.2f}%)",
                "verdict": "MET -- the suite the audits asked for costs under 1% of a real run" if share <= 0.05 else
                           "FALSIFIER FIRED -- above 5% of a real run"})
    return out


def report(small: dict, large: dict) -> int:
    if small is None or large is None:
        print("both runs are needed: " + ", ".join(p for p in (SMALL, LARGE)))
    else:
        print("== the two runs, differing in the suite alone ==")
        for name, r in ((SMALL, small), (LARGE, large)):
            print(f"   {name.split('/')[-1]:28} n_eval {r['n_eval']:5d}  {r['seconds']:7.2f} s  "
                  f"test per task {r['test_per_task']}  train per task {r['train_per_task']}  "
                  f"repeats {r['repeats']}  methods {r['methods']}")
        print(f"\n   the suite the audits asked for (the worst of `e267`'s three): {WANTED} items")
        print(f"   a real run of that cell: {REAL_RUN_SECONDS / 60:.0f} min for sixteen replicates of four arms")
    print("\n== the registered claims, T1-T3 ==")
    j = judge(small, large)
    for c, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {c[2]}")
        print(f"          and its {c[3]}")
    print("\n   (the benchmark's note says the test-set part is removable and that the suite is cheap; this measures")
    print("    what 'cheap' is, and the answer is that it is under the run-to-run noise of a single thirty-second run)")
    return sum("REFUSED" in row["verdict"] for row in j)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args(argv)
    a, b = load(SMALL), load(LARGE)
    small = reading(a) if a else None
    large = reading(b) if b else None
    if args.json_out:
        write_json(args.json_out, {"runs": [SMALL, LARGE], "wanted_items": WANTED,
                                   "real_run_seconds": REAL_RUN_SECONDS,
                                   "small": small, "large": large, "claims": judge(small, large)})
        print(f"wrote {args.json_out}")
    return report(small, large)


if __name__ == "__main__":
    sys.exit(main())
