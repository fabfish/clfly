"""E319 -- the penalty dialled four times: does the position effect scale with it, or appear at a threshold?

`e317` found the reversal's position effect carried by the arms that read a penalty; `e318` asked the controlled
version -- one arm, one suite, one seed set -- and found `ewc` at four times the effect with its penalty on than off
(+0.0917 at 2.75 sigma and -0.1083 at 4.33 against -0.0083 at 0.78 and -0.0042 at exactly 1.00). `e318`'s own
limitation names what that leaves: **two penalty strengths, so this is on against off and not a dose-response
curve.** This unit dials the penalty four times.

    lam = 0.0, 0.1, 1.0, 3.0, each trained forwards (the suite's own order) and backwards (its reversal)

Eight runs of one configuration -- the assembly suite, the same circuit, read-out and seeds -- with `naive` riding
along in every one as a constant. Four claims, registered before the reading below was taken:

- **D1 -- the eight runs are one configuration at four penalties.** Each penalty's two orders agree on circuit,
  read-out and seeds and reverse their task lists, and the four settings differ in **`lam` alone**. **Falsifier**: a
  differing circuit, read-out or seed list, or a `config` differing elsewhere.
- **D2 -- and the effect scales with the penalty.** The median sigma of `ewc`'s moved-position contrasts is
  **non-decreasing** across `lam` = 0.0, 0.1, 1.0, 3.0. **Falsifier**: a decrease at any step.
- **D3 -- and it crosses the threshold somewhere inside the range.** At least one penalty has both moved contrasts at
  or above **1 sigma** and at least one has both below. **Falsifier**: every penalty above, or every penalty below.
- **D4 -- and the direction is the position's wherever it resolves.** Every contrast that clears 1 sigma favours the
  run that trains the task first. **Falsifier**: one the other way.

**What it cannot do.** *Four penalties on one suite and five replicates*, so a monotone sequence of four points is an
ordering and not a curve, and adjacent points are not separated: D2 is a sign test on three steps. *`lam = 3.0` is
above everything the corpus has run before*, so the top of the range is a new regime and a drop there would be the
penalty's own cost rather than the effect's end. *The arms are still one arm*: `ewc-block` and `ewc-block-rand` read a
penalty through a partition, and nothing here dials theirs. *And the runs are not the same trained models*, since
`lam` changes the gradients, so a difference across settings is the penalty's effect on the whole trajectory.
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path

from clfly.bench.artifacts import write_json

RUNS = Path("runs")
#: The four penalties, each with its forwards and backwards run -- the whole design.
LAMBDAS = ("0.0", "0.1", "1.0", "3.0")
PATHS = {(lam, order): RUNS / f"e319_lam{lam.replace('.', 'p')}_{order.replace('-', '')}.json"
         for lam in LAMBDAS for order in ("as-built", "reverse")}
#: The arm under test and the constant that rides along, and D3's threshold.
UNDER_TEST = "ewc"
RIDE_ALONG = "naive"
SIGMA = 1.0
#: The `config` keys two settings may differ in without being two configurations.
SETTING_IGNORES = ("lam", "json_out", "task_order")
CLAIMS = (
    ("D1", "the eight runs are one configuration at four penalties",
     "Each penalty's two orders agree on circuit, read-out and seeds and are reversed, and the four settings differ "
     "in `lam` alone",
     "falsifier: a differing circuit, read-out or seed list, or a `config` differing elsewhere"),
    ("D2", "and the effect scales with the penalty",
     "The median sigma of `ewc`'s moved contrasts is non-decreasing across `lam` = 0.0, 0.1, 1.0, 3.0",
     "falsifier: a decrease at any step"),
    ("D3", "and it crosses the threshold somewhere inside the range",
     f"At least one penalty has both moved contrasts at or above {SIGMA} sigma and at least one has both below",
     "falsifier: every penalty above, or every penalty below"),
    ("D4", "and the direction is the position's wherever it resolves",
     f"Every moved contrast clearing {SIGMA} sigma favours the run that trains the task first",
     "falsifier: one the other way"),
)


def load(path) -> dict | None:
    p = Path(path)
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def paired(one: list[float], two: list[float]) -> dict:
    diffs = [a - b for a, b in zip(one, two)]
    if len(diffs) < 2:
        return {"n": len(diffs), "delta": None, "sem": None, "sigma": None}
    mean = statistics.fmean(diffs)
    sem = statistics.stdev(diffs) / (len(diffs) ** 0.5)
    if sem < 1e-12:
        return {"n": len(diffs), "delta": mean, "sem": sem, "sigma": float("inf") if mean else None}
    return {"n": len(diffs), "delta": mean, "sem": sem, "sigma": abs(mean) / sem}


def contrast(run_fwd: dict, run_bwd: dict, arm: str) -> dict:
    names_a = [str(t["name"]) for t in run_fwd["tasks"]]
    names_b = [str(t["name"]) for t in run_bwd["tasks"]]
    ea, eb = run_fwd.get("methods", {}).get(arm), run_bwd.get("methods", {}).get(arm)
    if not isinstance(ea, dict) or not isinstance(eb, dict):
        return {}
    la = [r.get("learned") for r in ea.get("replicates") or []]
    lb = [r.get("learned") for r in eb.get("replicates") or []]
    if not la or not lb or any(x is None for x in la + lb) or len(la) != len(lb):
        return {}
    n = len(la)
    out = {}
    for task in names_a:
        ia, ib = names_a.index(task), names_b.index(task)
        out[task] = {"forward_position": ia, "backward_position": ib, "moved": ia != ib,
                     **paired([la[r][ia] for r in range(n)], [lb[r][ib] for r in range(n)])}
    return out


def reading(root: Path = RUNS, paths: dict = PATHS) -> dict:
    runs = {}
    for key, path in paths.items():
        d = load(path if root == RUNS else Path(root) / Path(path).name)
        if d is None:
            return {"runs": 0, "missing": path.as_posix()}
        runs[key] = d
    settings = {}
    for lam in LAMBDAS:
        a, b = runs[(lam, "as-built")], runs[(lam, "reverse")]
        names_a = [str(t["name"]) for t in a["tasks"]]
        names_b = [str(t["name"]) for t in b["tasks"]]
        rows = contrast(a, b, UNDER_TEST)
        moved = [x for x in rows.values() if x["moved"]]
        still = [x for x in rows.values() if not x["moved"]]
        settings[lam] = {
            "same_circuit": a.get("circuit") == b.get("circuit"),
            "same_readout": a.get("readout", {}).get("subset_sha1") == b.get("readout", {}).get("subset_sha1"),
            "orders": [a.get("config", {}).get("task_order"), b.get("config", {}).get("task_order")],
            "reversed_names": names_b == names_a[::-1] and names_a != names_b,
            "seeds": [[r.get("seed") for r in a["methods"][UNDER_TEST]["replicates"]],
                      [r.get("seed") for r in b["methods"][UNDER_TEST]["replicates"]]],
            "n": len(a["methods"][UNDER_TEST]["replicates"]),
            "tasks": rows, "ride_along": contrast(a, b, RIDE_ALONG),
            "median_sigma": statistics.median([(x["sigma"] or 0) for x in moved]) if moved else None,
            "moved_sigmas": sorted((x["sigma"] or 0) for x in moved),
            "control_smallest": (min((x["sigma"] or 0) for x in still) < min((x["sigma"] or 0) for x in moved))
            if moved and still else None,
            "config": a.get("config") or {},
        }
    cfgs = {lam: settings[lam]["config"] for lam in LAMBDAS}
    keys = set().union(*[set(c) for c in cfgs.values()]) if cfgs else set()
    differing = sorted(k for k in keys
                       if k not in SETTING_IGNORES and len({json.dumps(c.get(k), sort_keys=True)
                                                            for c in cfgs.values()}) > 1)
    return {"runs": 8, "settings": settings, "config_fields_differing_between_settings": differing}


def judge(r: dict) -> list[dict]:
    if not r.get("runs"):
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- the eight runs are not all on disk"}
                for c in CLAIMS]
    s = r["settings"]

    pairs = all(v["same_circuit"] and v["same_readout"] and v["reversed_names"] and v["orders"] == ["as-built", "reverse"]
                and v["seeds"][0] == v["seeds"][1] for v in s.values())
    fields = r["config_fields_differing_between_settings"]
    out = [{"id": "D1", "measured": f"the four settings' configs differ in {fields}; every penalty's two orders "
                                    f"agree on circuit, read-out and seeds and reverse their task lists: {pairs}",
            "verdict": "MET -- one configuration at four penalties, each in two orders" if pairs and not fields else
                       f"FALSIFIER FIRED -- pairs agree {pairs}, fields {fields}"}]

    medians = [s[lam]["median_sigma"] for lam in LAMBDAS]
    drops = [f"{LAMBDAS[i]} to {LAMBDAS[i + 1]}" for i in range(len(medians) - 1)
             if (medians[i + 1] or 0) < (medians[i] or 0)]
    out.append({"id": "D2", "measured": f"the median moved-contrast sigma by penalty: "
                                        + ", ".join(f"{lam} {m:.2f}" for lam, m in zip(LAMBDAS, medians))
                                        + f"; {len(drops)} step(s) fall",
                "verdict": "MET -- the effect does not shrink as the penalty grows" if not drops else
                           f"FALSIFIER FIRED -- falls at {drops}"})

    above = [lam for lam in LAMBDAS if s[lam]["moved_sigmas"] and min(s[lam]["moved_sigmas"]) >= SIGMA]
    below = [lam for lam in LAMBDAS if s[lam]["moved_sigmas"] and max(s[lam]["moved_sigmas"]) < SIGMA]
    out.append({"id": "D3", "measured": f"penalties with both moved contrasts clearing {SIGMA} sigma: "
                                        f"{above or 'none'}; with both below it: {below or 'none'}",
                "verdict": "MET -- the range contains both sides of the line" if above and below else
                           f"FALSIFIER FIRED -- above {above}, below {below}"})

    cleared = [(lam, t, x) for lam in LAMBDAS for t, x in s[lam]["tasks"].items()
               if x["moved"] and (x["sigma"] or 0) >= SIGMA]
    wrong = [(lam, t) for lam, t, x in cleared
             if (x["forward_position"] == 0 and (x["delta"] or 0) <= 0)
             or (x["backward_position"] == 0 and (x["delta"] or 0) >= 0)]
    out.append({"id": "D4", "measured": f"{len(cleared) - len(wrong)} of {len(cleared)} contrasts clearing {SIGMA} "
                                        f"sigma favour the run that trains the task first: "
                                        + "; ".join(f"lam {lam}/{t} {x['delta']:+.4f} at {x['sigma']:.2f}"
                                                    for lam, t, x in cleared),
                "verdict": "MET -- wherever the effect resolves it points the position's way" if cleared and
                not wrong else f"FALSIFIER FIRED -- {wrong}"})
    return out


def report(r: dict) -> int:
    print("== the position effect at four penalty strengths ==")
    print(f"   the settings' configs differ in {r['config_fields_differing_between_settings']}")
    print(f"\n   {'lam':6} {'median sigma':>13} {'moved sigmas':>20} {'control':>9}  contrasts")
    for lam in LAMBDAS:
        v = r["settings"][lam]
        sigs = ", ".join(f"{x:+.2f}" for x in v["moved_sigmas"])
        print(f"   {lam:6} {v['median_sigma']:13.2f} {sigs:>20} {str(v['control_smallest']):>9}  "
              + "; ".join(f"{t} {x['delta']:+.4f} at {x['sigma']:.2f}"
                          for t, x in sorted(v["tasks"].items()) if x["moved"]))
    print(f"\n   `{RIDE_ALONG}`'s moved sigmas by penalty: "
          + ", ".join(f"{lam} " + ",".join(f"{x['sigma']:.2f}" for x in r["settings"][lam]["ride_along"].values()
                                           if x["moved"]) for lam in LAMBDAS))

    print("\n== the registered claims, D1-D4 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e318` compared the penalty on against off on one arm and named the gap: that is not a")
    print("    dose-response; four settings on the same suite and seeds is what that takes)")
    return sum("REFUSED" in row["verdict"] for row in j)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--runs", type=Path, default=RUNS)
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args(argv)
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")

    r = reading(args.runs)
    r["claims"] = judge(r)
    if args.json_out:
        write_json(args.json_out, r)
        print(f"wrote {args.json_out}")
    return report(r)


if __name__ == "__main__":
    sys.exit(main())
