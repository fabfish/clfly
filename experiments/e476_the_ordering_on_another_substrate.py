"""E476 -- the method ordering on another substrate: whether replay-over-penalty travels to the assembly suite.

`e276` read the corpus's largest method contrast off the four forty-replicate `r32` artifacts that carry both the
`replay` and the `ewc-block` arms and found **replay ahead of the penalty by +0.0090 to +0.0618 accuracy at 3.30 to
11.84 sigma**, and it closed on the one thing it could not do: *"no run is made: this is a read of runs the register
already has, and the missing measurement is the one that would say whether the ordering survives a different
substrate -- which is a run, not a re-reading."* `e453` read the same contrast ten times on the card's world and closed
on the same gap from the other side: *"ten rolls of one world (other worlds and `e276`'s other suites are not in it)"*.

**This unit makes that run.** The `r32` line's own command, with the **assembly suite** in place of the overlap
builder and nothing else but the arm list moved: `e140`'s configuration at circuit 800, five hundred updates, the
32-neuron shared head, `lam = 3e-3`, `seed0 = 0`, forty replicates, carrying the three arms the claims need
(`naive`, `ewc-block`, `replay`). The overlap line's three tasks are drawn by `make_overlap_suite` with supports of an
exact overlap; the assembly suite's three are the circuit's own olfactory, central-complex and antennal-lobe tasks
with disjoint supports, which is the substrate the benchmark section calls *implemented*. Four claims, registered
before the new run's reading was opened.

**And the two artifacts are a generation apart**, so their `config`s do not have the same key set -- `e140` predates
the closed-loop block, the sequence builder and `--task-order`, and records neither those keys nor their defaults.
The comparison therefore uses this project's own rule for that case, read from the registry `e172` builds off the
runner's syntax tree: a key the older artifact **lacks**, whose value in the newer artifact equals that flag's
**default**, is inert -- both runs took the flag's default path, and the older one simply did not write it down. A key
both artifacts carry and disagree on is not inert, and `methods` is inert on the strength of `e102`/`e104`'s C0 check
(each arm is trained independently from the same initial body and the same task draws).

- **RA1 -- and the assembly run is one configuration with the register's own except the suite.** Every key both
  artifacts record agrees, and every key `e140` lacks is at its parser default in the new run; `input_overlap` is
  **0.0** in `e140` and **null** in the new artifact, which is the suite moved; the circuit and the read-out draw are
  equal; and each of the three arms carries **forty** replicates. **Falsifier**: any key both artifacts carry
  disagreeing, a key the older one lacks standing away from its default, an equal circuit or read-out draw failing, or
  fewer than forty replicates on an arm.
- **RA2 -- and replay beats the penalty on another substrate.** Paired over the forty replicates the two artifacts
  share, `replay` minus `ewc-block` on the mean diagonal is positive at **two** sigma or more. **Falsifier**: under two
  sigma, or negative.
- **RA3 -- and it does not pay for it in forgetting.** The same contrast on mean forgetting is negative at **two**
  sigma or more, replay forgetting less. **Falsifier**: under two sigma, or positive.
- **RA4 -- and the penalty's own gain over the baseline is still a null.** `ewc-block` minus `naive` on the mean
  diagonal is under **two** sigma in absolute value. **Falsifier**: a contrast that resolves, in either direction.

**What it can do beyond that.** It moves the line's largest number to a second substrate or shows it does not travel,
and it is the first artifact in the corpus that reads a method contrast on the assembly suite at the `r32` line's own
settings.

**What it cannot do.** *One substrate and one setting*: `lam = 3e-3` on a plastic body at five hundred updates, so
`e140`'s frozen-bias configuration and `e153`'s `lam = 1.0` overlap-1.0 one are not run and the two arms `ewc` and
`ewc-block-rand` are absent, so the basis contrast is not in it. *And the suite and the arm list move together*: the
assembly suite carries no overlap knob, so the difference from `e140` is the builder and not a dose. *And the inert
rule is a rule and not a measurement*: it reads the runner's syntax tree and not the code path `e140` ran, so a flag
whose default changed since `e140` would be admitted wrongly. *And forty replicates are not the population*: the sigma
is the paired one over the seeds the two runs share. *And a diagonal is not a mechanism*: what each arm buys and spends
is `e423`'s business on the card's world and not this unit's.
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
from pathlib import Path

from clfly.bench.artifacts import write_json
from experiments.e172_parser_registry import parser_flags

#: the new run on the assembly suite, and the register's own artifact it is matched to
NEW = Path("runs/e476_assembly_r32_methods_40reps.json")
BASE = Path("runs/e140_r32_methods_plastic_40reps.json")
#: the runner whose parser decides what a key the older artifact lacks would have held
RUNNER = Path("experiments/e8_rate_network.py")
BASELINE = "naive"
PENALTY = "ewc-block"
BUFFER = "replay"
ARMS = (BASELINE, PENALTY, BUFFER)
#: the arm list `e140` carries, declared rather than compared
BASE_ARMS = ("naive", "ewc", "ewc-block", "ewc-block-rand", "replay")
#: the suite, which is the manipulation this unit makes, and the run's own bookkeeping
SUITE_FIELD = "input_overlap"
BOOKKEEPING = ("json_out", "save_theta")
#: inert where both artifacts record it: `e102`/`e104`'s C0 check trains each arm independently
INERT_FOR_ALL = ("methods",)
#: the top-level fields that carry the substrate and must be equal where the suite is moved
SHARED = ("circuit", "readout")
MIN_REPS = 40
SIGMA = 2.0
CLAIMS = (
    ("RA1", f"and the assembly run is one configuration with the register's own except the suite, at {MIN_REPS} "
            f"replicates",
     "Every key both artifacts record agrees, and every key e140 lacks is at its parser default in the new run; "
     "input_overlap is 0.0 in e140 and null in the new artifact; the circuit and the read-out draw are equal; and each "
     "of the three arms carries forty replicates",
     "falsifier: any key both artifacts carry disagreeing, a key the older one lacks standing away from its default, "
     "an equal circuit or read-out draw failing, or fewer than forty replicates on an arm"),
    ("RA2", f"and replay beats the penalty on another substrate, at {SIGMA:.0f} sigma",
     "Paired over the forty replicates the two artifacts share, replay minus ewc-block on the mean diagonal is "
     "positive at two sigma or more",
     "falsifier: under two sigma, or negative"),
    ("RA3", f"and it does not pay for it in forgetting, at {SIGMA:.0f} sigma",
     "The same contrast on mean forgetting is negative at two sigma or more, replay forgetting less",
     "falsifier: under two sigma, or positive"),
    ("RA4", f"and the penalty's own gain over the baseline is still a null, under {SIGMA:.0f} sigma",
     "ewc-block minus naive on the mean diagonal is under two sigma in absolute value",
     "falsifier: a contrast that resolves, in either direction"),
)


def _defaults() -> dict:
    """Each flag's default, as the runner's syntax tree states it, with `store_true` read as `False`.

    A flag whose default is not a literal is reported as `None`, which can only make this file **stricter**: a key
    the older artifact lacks is then admitted only if the newer artifact holds `None` for it, and a `None` against a
    `None` is agreement rather than a default.
    """
    try:
        return {k: (False if meta.get("store_true") else meta.get("default"))
                for k, meta in parser_flags(RUNNER).items()}
    except (OSError, ValueError):
        return {}


DEFAULTS = _defaults()


def _inert(key: str, old, new) -> bool:
    """Whether a difference between the two artifacts is one the runner's own code path decides.

    `input_overlap` is the suite and is this unit's manipulation; `json_out` and `save_theta` are bookkeeping; the arm
    list is inert because each arm trains independently; the two spellings of "not frozen" are one value; and a key the
    older artifact lacks, held at its default in the newer one, is a key the older run took the default path on.
    """
    if key == SUITE_FIELD or key in BOOKKEEPING or key in INERT_FOR_ALL:
        return True
    if {old, new} == {None, False}:
        return True
    return old is None and key in DEFAULTS and new == DEFAULTS[key]


def load(path) -> dict | None:
    p = Path(path)
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _paired(a: list, b: list) -> dict:
    d = [x - y for x, y in zip(a, b)]
    n = len(d)
    mean = statistics.fmean(d) if n else 0.0
    sd = statistics.stdev(d) if n > 1 else 0.0
    se = sd / math.sqrt(n) if n else 0.0
    return {"n": n, "mean": mean, "sd": sd, "se": se, "sigma": (mean / se) if se > 0 else 0.0}


def _roll(path: Path, arms) -> dict | None:
    """One artifact's arm readings, replicate by replicate, or None where it cannot supply them."""
    doc = load(path)
    if not doc:
        return None
    methods = doc.get("methods") or {}
    got = {}
    for arm in arms:
        reps = (methods.get(arm) or {}).get("replicates") or []
        if not reps:
            return None
        got[arm] = {"replicates": len(reps),
                    "diagonal": [r["final_accuracy"] for r in reps],
                    "forgetting": [r["mean_forgetting"] for r in reps]}
    return {"artifact": path.name, "arms": got, "n_arms": len(methods),
            "shared": {k: doc.get(k) for k in SHARED},
            "config": dict(doc.get("config") or {})}


def reading(new: Path = NEW, base: Path = BASE) -> dict:
    out = {"ok": True, "reason": None, "runs": {}, "same": {}, "inert": {}, "shared": {}, "suite": {},
           "contrasts": {}, "base_contrasts": {}, "spans": {}}
    got_new = _roll(new, ARMS)
    got_base = _roll(base, ARMS)
    if got_new is None:
        return {**out, "ok": False,
                "reason": f"the assembly run {new} is absent or carries no one of the arms {list(ARMS)}"}
    if got_base is None:
        return {**out, "ok": False,
                "reason": f"the register's artifact {base} is absent or carries no one of the arms {list(ARMS)}"}
    out["runs"] = {"assembly": got_new, "overlap0": got_base}
    ca, cb = got_base["config"], got_new["config"]
    for k in sorted(set(ca) | set(cb)):
        old, new_v = ca.get(k), cb.get(k)
        if old == new_v:
            continue
        (out["inert"] if _inert(k, old, new_v) else out["same"])[k] = [old, new_v]
    for k in SHARED:
        out["shared"][k] = got_new["shared"].get(k) == got_base["shared"].get(k)
    out["suite"] = {"field": SUITE_FIELD, "old": ca.get(SUITE_FIELD), "new": cb.get(SUITE_FIELD)}
    for label, roll in out["runs"].items():
        g = roll["arms"]
        out["contrasts" if label == "assembly" else "base_contrasts"] = {
            "buffer_over_penalty": {"diagonal": _paired(g[BUFFER]["diagonal"], g[PENALTY]["diagonal"]),
                                    "forgetting": _paired(g[BUFFER]["forgetting"], g[PENALTY]["forgetting"])},
            "penalty_over_baseline": {"diagonal": _paired(g[PENALTY]["diagonal"], g[BASELINE]["diagonal"]),
                                      "forgetting": _paired(g[PENALTY]["forgetting"], g[BASELINE]["forgetting"])},
            "buffer_over_baseline": {"diagonal": _paired(g[BUFFER]["diagonal"], g[BASELINE]["diagonal"]),
                                     "forgetting": _paired(g[BUFFER]["forgetting"], g[BASELINE]["forgetting"])},
            "means": {arm: {"diagonal": statistics.fmean(g[arm]["diagonal"]),
                            "forgetting": statistics.fmean(g[arm]["forgetting"])} for arm in ARMS},
        }
    out["spans"] = {
        "arms": list(ARMS), "shared": list(SHARED),
        "same_fields": len(set(ca) | set(cb)), "differ": sorted(out["same"]), "inert": sorted(out["inert"]),
        "n_defaults": len(DEFAULTS),
        "shared_equal": sorted(k for k, v in out["shared"].items() if v),
        "shared_differ": sorted(k for k, v in out["shared"].items() if not v),
        "replicates": {label: sorted({v["replicates"] for v in roll["arms"].values()})
                       for label, roll in out["runs"].items()},
        "n_arms": {label: roll["n_arms"] for label, roll in out["runs"].items()},
        "base_arms": list(BASE_ARMS),
    }
    return out


def judge(r: dict) -> list[dict]:
    if not r.get("ok"):
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- an artifact is absent or lacks an arm"}
                for c in CLAIMS]
    s = r["spans"]
    a = r["contrasts"]
    differ = s["differ"]
    thin = {label: reps for label, reps in s["replicates"].items() if any(n < MIN_REPS for n in reps)}
    suite = r["suite"]
    j1 = {"id": "RA1",
          "measured": f"{s['same_fields']} keys compared against {r['runs']['overlap0']['artifact']}, "
                      f"**{len(differ)}** differing past the inert rule and {len(s['inert'])} admitted by it "
                      f"(differing {differ}; inert {s['inert']}); the suite {suite['field']} is "
                      f"**{suite['old']}** there against **{suite['new']}** here; the circuit and the read-out draw "
                      f"equal on {s['shared_equal']}; replicates {s['replicates']} over arm lists of three against "
                      f"{r['runs']['overlap0']['n_arms']}",
          "verdict": "MET -- one configuration with the suite moved, and the assembly suite's own three tasks read at "
                     "the r32 line's settings" if (not differ and not s["shared_differ"] and not thin
                                                    and suite["old"] != suite["new"])
                     else f"FALSIFIER FIRED -- differing {differ}, shared differing {s['shared_differ']}, thin "
                          f"{thin}, suite {suite}"}
    c2 = a["buffer_over_penalty"]["diagonal"]
    j2 = {"id": "RA2",
          "measured": f"replay minus ewc-block on the mean diagonal in the assembly suite is **{c2['mean']:+.4f}** at "
                      f"**{c2['sigma']:+.2f}** sigma over {c2['n']} replicates (the register's overlap-0.0 run reads "
                      f"**{r['base_contrasts']['buffer_over_penalty']['diagonal']['mean']:+.4f}** at "
                      f"**{r['base_contrasts']['buffer_over_penalty']['diagonal']['sigma']:+.2f}**)",
          "verdict": f"MET -- the ordering travels: replay leads the penalty by {c2['mean']:+.4f} at "
                     f"{c2['sigma']:+.2f} sigma on a second substrate" if c2["sigma"] >= SIGMA else
                     f"FALSIFIER FIRED -- the ordering does not travel: {c2['mean']:+.4f} at {c2['sigma']:+.2f} sigma"}
    c3 = a["buffer_over_penalty"]["forgetting"]
    j3 = {"id": "RA3",
          "measured": f"the same contrast on mean forgetting is **{c3['mean']:+.4f}** at **{c3['sigma']:+.2f}** sigma "
                      f"(the register reads **{r['base_contrasts']['buffer_over_penalty']['forgetting']['mean']:+.4f}** "
                      f"at **{r['base_contrasts']['buffer_over_penalty']['forgetting']['sigma']:+.2f}**; negative is "
                      f"better)",
          "verdict": f"MET -- replay forgets less by {abs(c3['mean']):.4f} at {abs(c3['sigma']):.2f} sigma" if
                     c3["sigma"] <= -SIGMA else
                     f"FALSIFIER FIRED -- the buffer pays for the lead in forgetting: {c3['mean']:+.4f} at "
                     f"{c3['sigma']:+.2f} sigma"
                     if c3["sigma"] >= SIGMA else
                     f"FALSIFIER FIRED -- the forgetting contrast does not resolve: {c3['mean']:+.4f} at "
                     f"{c3['sigma']:+.2f} sigma"}
    c4 = a["penalty_over_baseline"]["diagonal"]
    j4 = {"id": "RA4",
          "measured": f"ewc-block minus naive on the mean diagonal is **{c4['mean']:+.4f}** at **{c4['sigma']:+.2f}** "
                      f"sigma (the register reads "
                      f"**{r['base_contrasts']['penalty_over_baseline']['diagonal']['mean']:+.4f}** at "
                      f"**{r['base_contrasts']['penalty_over_baseline']['diagonal']['sigma']:+.2f}**)",
          "verdict": f"MET -- the penalty's own gain over the baseline is still a null at {c4['sigma']:+.2f} sigma" if
                     abs(c4["sigma"]) < SIGMA else
                     f"FALSIFIER FIRED -- the penalty's gain resolves here: {c4['mean']:+.4f} at {c4['sigma']:+.2f} "
                     f"sigma"}
    return [j1, j2, j3, j4]


def report(r: dict) -> int:
    print("== the method ordering on another substrate ==")
    if not r.get("ok"):
        print(f"   REFUSED -- {r.get('reason', 'an artifact is absent')}")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)
    print("   the r32 line's own command at circuit 800, five hundred updates, the 32-neuron shared head and")
    print("   lam = 3e-3, with the assembly suite in place of the overlap builder and nothing else but the arm list")
    for label in ("overlap0", "assembly"):
        roll = r["runs"][label]
        c = r["base_contrasts"] if label == "overlap0" else r["contrasts"]
        print(f"\n   {label} ({roll['artifact']}):")
        for arm in ARMS:
            print(f"      {arm:<10} diagonal {c['means'][arm]['diagonal']:.4f}  forgetting "
                  f"{c['means'][arm]['forgetting']:+.4f}")
        for name, tag in (("buffer_over_penalty", "replay - ewc-block"),
                          ("penalty_over_baseline", "ewc-block - naive"),
                          ("buffer_over_baseline", "replay - naive")):
            print(f"      {tag:<20} diagonal {c[name]['diagonal']['mean']:+.4f} "
                  f"({c[name]['diagonal']['sigma']:+.2f}s)  forgetting {c[name]['forgetting']['mean']:+.4f} "
                  f"({c[name]['forgetting']['sigma']:+.2f}s)")
    print(f"\n   the suite moved: {r['suite']['field']} {r['suite']['old']} -> {r['suite']['new']}")
    print(f"   keys compared {r['spans']['same_fields']}; differing past the inert rule {r['spans']['differ']};")
    print(f"   admitted by it {r['spans']['inert']}; shared fields equal {r['spans']['shared_equal']}")
    print("\n== the registered claims, RA1-RA4 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e276` read the ordering off the overlap line and named the missing measurement as a run on")
    print("    another substrate; `e453` named the same gap from the card's world)")
    return sum("REFUSED" in row["verdict"] for row in j)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args(argv)
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")

    r = reading()
    r["claims"] = judge(r)
    if args.json_out:
        write_json(args.json_out, r)
        print(f"wrote {args.json_out}")
    return report(r)


if __name__ == "__main__":
    sys.exit(main())
