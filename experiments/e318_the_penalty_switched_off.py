"""E318 -- the penalty switched off: the same arm, the same suite, the same seeds, with and without its penalty.

`e317` found the reversal's position effect carried by the three arms that read a penalty and absent from the two
that do not, and named what it left open: *no arm is compared with itself*, so "carried by the penalty arms" is a
statement about which arms move and not about the penalty. **This is that comparison.** Four runs of one
configuration, the assembly suite at the same circuit, read-out and seeds:

    runs/e318_lam0_as_built.json    lam = 0.0, the suite's own order
    runs/e318_lam0_reverse.json     lam = 0.0, its full reversal
    runs/e318_lam1_as_built.json    lam = 1.0, the suite's own order
    runs/e318_lam1_reverse.json     lam = 1.0, its full reversal

`ewc` is the arm under test and `naive` rides along in every run as the internal control, so the question *does the
position effect need the penalty* is asked of **one arm at two penalty strengths on one suite** rather than of two
arms.

Four claims, registered before the reading below was taken:

- **S1 -- the four runs are one configuration at two settings.** Every pair of orders at one penalty records the same
  circuit, the same read-out subset, the same seeds and reversed task lists, and the two penalties differ in `lam`
  and in nothing else. **Falsifier**: a differing circuit, read-out or seed list, or a `config` that differs in
  another field.
- **S2 -- and with the penalty off the position does not matter.** At `lam = 0.0`, `ewc`'s two moved-position
  contrasts are both below **1 sigma**. **Falsifier**: one of them clears it.
- **S3 -- and with the penalty on it does.** At `lam = 1.0`, both of `ewc`'s moved-position contrasts clear
  **1 sigma** and favour the run that trains the task first. **Falsifier**: one that does not.
- **S4 -- and the control separates the two settings.** The unchanged-position task is the smallest of `ewc`'s three
  contrasts at `lam = 1.0` and is not at `lam = 0.0`. **Falsifier**: neither, or both.

**What it cannot do.** *Two penalty strengths on one suite and five replicates*, so a contrast near the threshold is
one this run does not resolve and nothing here is a dose-response curve: the claim is on against off. *`lam = 0.0` is
not the same code path as `naive`*: the arm still computes a Fisher and multiplies it by zero, so "the penalty off"
means the penalty term is zero and not that the run is `naive`. *The four runs are not the same trained models*, since
both the penalty and the order change the gradients, and `ewc` at the two settings shares its suite and its seeds and
not its trajectory. *And `naive` is present only as a constant across the four*, so nothing here re-measures what
`e317` measured about it.
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path

from clfly.bench.artifacts import write_json

RUNS = Path("runs")
#: The four runs, by penalty and order, which is the whole design.
RUNS_BY_SETTING = {
    ("0.0", "as-built"): RUNS / "e318_lam0_as_built.json",
    ("0.0", "reverse"): RUNS / "e318_lam0_reverse.json",
    ("1.0", "as-built"): RUNS / "e318_lam1_as_built.json",
    ("1.0", "reverse"): RUNS / "e318_lam1_reverse.json",
}
#: The arm under test and the internal control, and S2's and S3's threshold.
UNDER_TEST = "ewc"
RIDE_ALONG = "naive"
SIGMA = 1.0
#: The `config` keys two runs of one setting may differ in: the order, and the output path.
SETTING_IGNORES = ("task_order", "json_out")
CLAIMS = (
    ("S1", "the four runs are one configuration at two settings",
     "At each penalty the orders agree on circuit, read-out and seeds and are reversed, and the two penalties differ "
     "in `lam` alone",
     "falsifier: a differing circuit, read-out or seed list, or a `config` differing elsewhere"),
    ("S2", "and with the penalty off the position does not matter",
     f"At `lam = 0.0` both of `{UNDER_TEST}`'s moved-position contrasts are below {SIGMA} sigma",
     "falsifier: one of them clears it"),
    ("S3", "and with the penalty on it does",
     f"At `lam = 1.0` both of `{UNDER_TEST}`'s moved-position contrasts clear {SIGMA} sigma and favour the run that "
     f"trains the task first",
     "falsifier: one that does not"),
    ("S4", "and the control separates the two settings",
     f"The unchanged-position task is the smallest of `{UNDER_TEST}`'s three contrasts at `lam = 1.0` and is not at "
     f"`lam = 0.0`",
     "falsifier: neither, or both"),
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
    """The arm's per-task paired contrast between the two orders, keyed by task in the forwards run's order."""
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


def reading(root: Path = RUNS, map_: dict = RUNS_BY_SETTING) -> dict:
    runs = {}
    for (lam, order), path in map_.items():
        d = load(path if root == RUNS else Path(root) / Path(path).name)
        if d is None:
            return {"runs": 0, "missing": path.as_posix()}
        runs[(lam, order)] = d
    settings = {}
    for lam in sorted({k[0] for k in runs}, key=float):
        a, b = runs[(lam, "as-built")], runs[(lam, "reverse")]
        names_a = [str(t["name"]) for t in a["tasks"]]
        names_b = [str(t["name"]) for t in b["tasks"]]
        rows = contrast(a, b, UNDER_TEST)
        ride = contrast(a, b, RIDE_ALONG)
        moved = [x for x in rows.values() if x["moved"]]
        still = [x for x in rows.values() if not x["moved"]]
        settings[lam] = {
            "circuit": [a.get("circuit"), b.get("circuit")],
            "same_circuit": a.get("circuit") == b.get("circuit"),
            "readout": [a.get("readout", {}).get("subset_sha1"), b.get("readout", {}).get("subset_sha1")],
            "orders": [a.get("config", {}).get("task_order"), b.get("config", {}).get("task_order")],
            "reversed_names": names_b == names_a[::-1] and names_a != names_b,
            "seeds": [[r.get("seed") for r in a["methods"][UNDER_TEST]["replicates"]],
                      [r.get("seed") for r in b["methods"][UNDER_TEST]["replicates"]]],
            "n": len(a["methods"][UNDER_TEST]["replicates"]),
            "tasks": rows, "ride_along": ride,
            "control_smallest": (min((x["sigma"] or 0) for x in still) < min((x["sigma"] or 0) for x in moved))
            if moved and still else None,
        }
    settings["1.0"]["same_readout"] = settings["1.0"]["readout"][0] == settings["1.0"]["readout"][1]
    settings["0.0"]["same_readout"] = settings["0.0"]["readout"][0] == settings["0.0"]["readout"][1]
    #: the two settings' configs, to check that `lam` is the only field that differs between them
    cfgs = {lam: runs[(lam, "as-built")].get("config") or {} for lam in settings if lam != "1.0" or True}
    differing = []
    if "0.0" in cfgs and "1.0" in cfgs:
        keys = set(cfgs["0.0"]) | set(cfgs["1.0"])
        #: A field two settings may differ in without being two configurations: the output path is where the
        #: runner was told to write, and `SETTING_IGNORES` says so -- the first version of this line compared
        #: it and reported `json_out` as a configuration difference, which is the defect `e185` recorded.
        differing = sorted(k for k in keys
                           if k not in SETTING_IGNORES and cfgs["0.0"].get(k) != cfgs["1.0"].get(k))
    return {"runs": 4, "settings": {k: v for k, v in settings.items() if k in ("0.0", "1.0")},
            "config_fields_differing_between_settings": differing}


def judge(r: dict) -> list[dict]:
    if not r.get("runs"):
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- the four runs are not all on disk"}
                for c in CLAIMS]
    s = r["settings"]
    off, on = s.get("0.0"), s.get("1.0")
    if not off or not on:
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- one of the two settings could not be read"}
                for c in CLAIMS]

    ok_pairs = all(v["same_circuit"] and v["same_readout"] and v["reversed_names"] and v["orders"][0] == "as-built"
                   and v["orders"][1] == "reverse" and v["seeds"][0] == v["seeds"][1] for v in (off, on))
    fields = r["config_fields_differing_between_settings"]
    out = [{"id": "S1", "measured": f"the settings' configs differ in {fields}; each penalty's two orders agree on "
                                    f"circuit, read-out and seeds and reverse their task lists: {ok_pairs}",
            "verdict": "MET -- one configuration at two penalty strengths, each in two orders"
            if ok_pairs and fields == ["lam"] else
            f"FALSIFIER FIRED -- pairs agree {ok_pairs}, fields {fields}"}]

    def moved(v):
        return [x for x in v["tasks"].values() if x["moved"]]

    off_sig = [(x["sigma"] or 0) for x in moved(off)]
    on_sig = [(x["sigma"] or 0) for x in moved(on)]
    out.append({"id": "S2", "measured": f"at `lam = 0.0` `{UNDER_TEST}`'s moved contrasts are "
                                        + ", ".join(f"{x['delta']:+.4f} at {x['sigma']:.2f} sigma" for x in moved(off)),
                "verdict": "MET -- with the penalty off the position does not move the arm" if off_sig and
                max(off_sig) < SIGMA else f"FALSIFIER FIRED -- {off_sig}"})

    favoured = [x for x in moved(on)
                if (x["forward_position"] == 0 and (x["delta"] or 0) > 0)
                or (x["backward_position"] == 0 and (x["delta"] or 0) < 0)]
    out.append({"id": "S3", "measured": f"at `lam = 1.0` `{UNDER_TEST}`'s moved contrasts are "
                                        + ", ".join(f"{x['delta']:+.4f} at {x['sigma']:.2f} sigma" for x in moved(on))
                                        + f"; {len(favoured)} of {len(moved(on))} favour the run that trains the task "
                                          f"first",
                "verdict": "MET -- with the penalty on the position moves the arm, in the position's direction"
                if on_sig and min(on_sig) >= SIGMA and len(favoured) == len(moved(on)) else
                f"FALSIFIER FIRED -- {on_sig}, favoured {len(favoured)} of {len(moved(on))}"})

    out.append({"id": "S4", "measured": f"the control is the smallest of `{UNDER_TEST}`'s three contrasts at "
                                        f"`lam = 1.0`: {on['control_smallest']}; at `lam = 0.0`: "
                                        f"{off['control_smallest']}",
                "verdict": "MET -- the control separates the two settings" if on["control_smallest"] is True and
                off["control_smallest"] is False else
                f"FALSIFIER FIRED -- on {on['control_smallest']}, off {off['control_smallest']}"})
    return out


def report(r: dict) -> int:
    print("== `ewc` with its penalty off and on, each in two orders ==")
    print(f"   the settings' configs differ in {r['config_fields_differing_between_settings']}")
    for lam, label in (("0.0", "penalty off"), ("1.0", "penalty on")):
        v = r["settings"].get(lam)
        if not v:
            continue
        print(f"\n   lam = {lam} ({label}): circuits {v['circuit']}, read-out {v['readout']}, orders {v['orders']}, "
              f"reversed {v['reversed_names']}, same seeds {v['seeds'][0] == v['seeds'][1]}")
        print(f"   {'arm':8} {'task':18} {'pos fwd':>8} {'pos bwd':>8} {'delta fwd-bwd':>14} {'sigma':>7}")
        for arm, rows in ((UNDER_TEST, v["tasks"]), (RIDE_ALONG, v["ride_along"])):
            for t, row in sorted(rows.items()):
                print(f"   {arm:8} {t:18} {row['forward_position']:8} {row['backward_position']:8} "
                      f"{row['delta']:+14.4f} {row['sigma']:7.2f}{'' if row['moved'] else '  <- control'}")
        print(f"   {'':8} ({v['n']} replicates; control smallest for `{UNDER_TEST}`: {v['control_smallest']})")

    print("\n== the registered claims, S1-S4 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e317` found the effect in the arms that read a penalty and named what it lacked: no arm was")
    print("    compared with itself -- this is one arm, one suite, one seed set, with the penalty dialled)")
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
