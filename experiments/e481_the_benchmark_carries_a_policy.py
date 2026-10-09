"""E481 -- the benchmark carries a policy: the agent's own rule becomes something the runner trains.

`e325` closed on *"What is missing is the thing that makes it a game rather than a loop: **a reward and a policy**"*,
`e477` gave `CueActionEnv` the field and trained one outside the runner, `e478` put a policy through a sequence and
`e479`/`e480` read its methods and their strength -- and every one of those units closed on the same sentence: *"the
policy is not the benchmark's: the runner does not carry one."* **The runner carries one now.**

`--loop-policy` gives the loop's agent a **trainable policy**: a `(len(action_neurons), len(action_neurons))` map from
the action population to the world's drive, created **per replicate** at the **identity** -- which is the
environment's own action rule exactly -- set on the environment so the world is driven through it, and handed to the
same optimizer as the body and the head so the **task loss through the loop** trains it. No penalty in this corpus
covers it, which is the status the bias already has.

**This unit reads the first run that carries it.** The card's own neutral roll (`e438`: the earned-label game at
circuit 300, five hundred updates, the 32-neuron head on the world's eight numbers, twenty replicates, `naive`,
`ewc-block` and `replay`) is the policy-off arm, and the new run is that same command with the flag. Four claims,
registered before the new run's reading was opened.

- **QA1 -- and the flag is the only field moved.** Every recorded config field agrees with the card's neutral roll
  except the flag itself and the run's own bookkeeping, and the circuit and the tasks agree. **Falsifier**: any other
  field differing.
- **QA2 -- and the agent's freedom is used.** On every replicate of every arm the policy's distance from the identity
  it was initialized at is above zero, and the new run records it. **Falsifier**: any replicate with no recorded
  movement, or a movement of zero.
- **QA3 -- and the benchmark still learns with a policy on.** The `naive` arm's mean diagonal on the new run is at
  least **0.10** above the four-class chance of **0.25**. **Falsifier**: within **0.05** of chance, which would say
  the policy's freedom broke the task rather than being available to it.
- **QA4 -- and it does not move what the benchmark measures.** On each of the three arms the **diagonal** and the
  **last row** agree with the card's own roll to under **two** sigma, paired over the twenty replicate seeds the two
  runs share. **Falsifier**: any arm resolving on either quantity. *This is the question a new degree of freedom
  raises: whether the benchmark's numbers are a property of the game or of the rule the agent happens to start from.*

**What it can do beyond that.** It is the first artifact in this corpus whose agent chooses its own action **through
something the benchmark trained**, which is the half of `e325`'s sentence the card's `absent` list has been missing,
and it puts a number on whether that freedom is worth anything to the read-out.

**What it cannot do.** *One configuration*: the card's neutral roll at one world, one budget and one seed stream, so
another world or another budget is not in it. *And the policy is linear over one population*: not covered by any
penalty here, so a run that regularizes it is a different unit, and the recurrent weights are not part of it. *And a
comparison against `e438` is a comparison against a run made before the flag existed*: its config lacks the key
entirely, which the inert rule admits and this unit prints. *And a reward is absent*: the policy is trained by the
**task loss**, so the game still has no reward of its own and the card's `absent` list still names one. *And twenty
replicates are one body and one circuit*: every sigma is the paired one over the seeds the two runs share.
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

#: the first run that carries the policy, and the card's own neutral roll it is compared against
NEW = Path("runs/e481_earned_label_policy_20reps.json")
BASE = Path("runs/e438_earned_label_three_arms_20reps.json")
RUNNER = Path("experiments/e8_rate_network.py")
ARMS = ("naive", "ewc-block", "replay")
#: the flag itself, which is this unit's manipulation, and the run's own bookkeeping
FLAG = "loop_policy"
BOOKKEEPING = ("json_out", "save_theta")
SHARED = ("circuit",)
MIN_REPS = 20
SIGMA = 2.0
CHANCE = 0.25
LEARNS = 0.10
FLAT = 0.05
CLAIMS = (
    ("QA1", f"and the flag is the only field moved, at {MIN_REPS} replicates",
     "Every recorded config field agrees with the card's neutral roll except the flag itself, the output path and the "
     "saved weights, and the circuit agrees",
     "falsifier: any other field differing"),
    ("QA2", "and the agent's freedom is used",
     "On every replicate of every arm the policy's distance from the identity it was initialized at is above zero, and "
     "the new run records it",
     "falsifier: any replicate with no recorded movement, or a movement of zero"),
    ("QA3", f"and the benchmark still learns with a policy on, by {LEARNS:.2f}",
     "The naive arm's mean diagonal on the new run is at least 0.10 above the four-class chance of 0.25",
     f"falsifier: within {FLAT:.2f} of chance"),
    ("QA4", f"and it does not move what the benchmark measures, under {SIGMA:.0f} sigma",
     "On each of the three arms the diagonal and the last row agree with the card's own roll to under two sigma, "
     "paired over the twenty replicate seeds the two runs share",
     "falsifier: any arm resolving on either quantity"),
)


def _defaults() -> dict:
    try:
        return {k: (False if meta.get("store_true") else meta.get("default"))
                for k, meta in parser_flags(RUNNER).items()}
    except (OSError, ValueError):
        return {}


DEFAULTS = _defaults()


def _inert(key: str, old, new) -> bool:
    """Whether a difference between the two runs is one the runner's own code path decides.

    The flag is this unit's manipulation, the output path and the saved weights are bookkeeping, and a key the older
    run **lacks**, held at its default in the newer one, is a key the older run took the default path on -- which is
    the rule `e172`'s registry exists to support and `e476` used for the same generation gap.
    """
    if key == FLAG or key in BOOKKEEPING:
        return True
    if {old, new} == {None, False}:
        return True
    return old is None and key in DEFAULTS and new == DEFAULTS[key]


def _paired(a: list, b: list) -> dict:
    d = [x - y for x, y in zip(a, b)]
    n = len(d)
    mean = statistics.fmean(d) if n else 0.0
    sd = statistics.stdev(d) if n > 1 else 0.0
    se = sd / math.sqrt(n) if n else 0.0
    return {"n": n, "mean": mean, "sd": sd, "se": se, "sigma": (mean / se) if se > 0 else 0.0}


def load(path) -> dict | None:
    p = Path(path)
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _roll(path: Path) -> dict | None:
    doc = load(path)
    if not doc:
        return None
    methods = doc.get("methods") or {}
    got = {}
    for arm in ARMS:
        reps = (methods.get(arm) or {}).get("replicates") or []
        if not reps:
            return None
        got[arm] = {"replicates": len(reps),
                    "diagonal": [float(r["learned"][-1]) for r in reps],
                    "last_row": [statistics.fmean(r["final_per_task"]) for r in reps],
                    "moves": [r.get("policy_move") for r in reps]}
    cfg = doc.get("config") or {}
    return {"artifact": path.name, "arms": got, "shared": {k: doc.get(k) for k in SHARED},
            "config": {k: cfg.get(k) for k in sorted(set(cfg) - {FLAG} - set(BOOKKEEPING))},
            "flag": cfg.get(FLAG)}


def reading(new: Path = NEW, base: Path = BASE) -> dict:
    out = {"ok": True, "reason": None, "runs": {}, "same": {}, "inert": {}, "shared": {}, "moves": {},
           "diagonal": {}, "last_row": {}, "spans": {}}
    got_new, got_base = _roll(new), _roll(base)
    if got_new is None:
        return {**out, "ok": False, "reason": f"the policy run {new} is absent or carries no one of the arms {list(ARMS)}"}
    if got_base is None:
        return {**out, "ok": False, "reason": f"the card's neutral roll {base} is absent or carries no one of {list(ARMS)}"}
    out["runs"] = {"policy": got_new, "card": got_base}
    ca, cb = got_base["config"], got_new["config"]
    for k in sorted(set(ca) | set(cb)):
        old, new_v = ca.get(k), cb.get(k)
        if old == new_v:
            continue
        (out["inert"] if _inert(k, old, new_v) else out["same"])[k] = [old, new_v]
    for k in SHARED:
        out["shared"][k] = got_new["shared"].get(k) == got_base["shared"].get(k)
    out["moves"] = {a: got_new["arms"][a]["moves"] for a in ARMS}
    for a in ARMS:
        out["diagonal"][a] = {"policy": got_new["arms"][a]["diagonal"], "card": got_base["arms"][a]["diagonal"],
                              "contrast": _paired(got_new["arms"][a]["diagonal"], got_base["arms"][a]["diagonal"])}
        out["last_row"][a] = {"policy": got_new["arms"][a]["last_row"], "card": got_base["arms"][a]["last_row"],
                              "contrast": _paired(got_new["arms"][a]["last_row"], got_base["arms"][a]["last_row"])}
    moves = [m for a in ARMS for m in out["moves"][a]]
    out["spans"] = {
        "arms": list(ARMS), "shared": list(SHARED), "differ": sorted(out["same"]), "inert": sorted(out["inert"]),
        "same_fields": len(set(ca) | set(cb)), "flags": [got_base["flag"], got_new["flag"]],
        "shared_equal": sorted(k for k, v in out["shared"].items() if v),
        "shared_differ": sorted(k for k, v in out["shared"].items() if not v),
        "replicates": {label: sorted({v["replicates"] for v in roll["arms"].values()})
                       for label, roll in out["runs"].items()},
        "moves_recorded": sum(1 for m in moves if m is not None),
        "moves_total": len(moves), "move_min": min((m for m in moves if m is not None), default=None),
        "move_mean": statistics.fmean([m for m in moves if m is not None]) if any(m is not None for m in moves) else None,
        "chance": CHANCE,
    }
    return out


def judge(r: dict) -> list[dict]:
    if not r.get("ok"):
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- a run is absent or lacks an arm"} for c in CLAIMS]
    s = r["spans"]
    j1 = {"id": "QA1",
          "measured": f"{s['same_fields']} keys compared against {r['runs']['card']['artifact']}, "
                      f"**{len(s['differ'])}** differing past the inert rule and {len(s['inert'])} admitted by it "
                      f"(differing {s['differ']}; inert {s['inert']}); the flag is {s['flags']}; the circuit equal on "
                      f"{s['shared_equal']}; replicates {s['replicates']}",
          "verdict": "MET -- one configuration with the flag moved and nothing else" if
                     (not s["differ"] and not s["shared_differ"] and s["flags"] == [None, True]
                      and all(v == [MIN_REPS] for v in s["replicates"].values())) else
                     f"FALSIFIER FIRED -- differing {s['differ']}, shared differing {s['shared_differ']}, flags "
                     f"{s['flags']}, replicates {s['replicates']}"}
    j2 = {"id": "QA2",
          "measured": f"the policy's distance from the identity is recorded on **{s['moves_recorded']} of "
                      f"{s['moves_total']}** replicates over the three arms, the smallest **{s['move_min']}** and the "
                      f"mean **{s['move_mean']}**",
          "verdict": "MET -- the agent's freedom is used on every replicate" if
                     (s["moves_recorded"] == s["moves_total"] and s["moves_total"] > 0 and s["move_min"] > 0.0) else
                     f"FALSIFIER FIRED -- {s['moves_recorded']} of {s['moves_total']} moved, the smallest "
                     f"{s['move_min']}"}
    d = r["diagonal"]["naive"]
    learn = statistics.fmean(d["policy"]) - CHANCE
    j3 = {"id": "QA3",
          "measured": f"the naive arm's mean diagonal on the policy run is **{statistics.fmean(d['policy']):.4f}** "
                      f"against a chance of **{CHANCE:.2f}**, so **{learn:+.4f}** above it (the card's own roll reads "
                      f"**{statistics.fmean(d['card']):.4f}**)",
          "verdict": f"MET -- the benchmark learns the game with a policy on, {learn:+.4f} above chance" if
                     learn >= LEARNS else
                     f"FALSIFIER FIRED -- {learn:+.4f} above chance, within the {FLAT:.2f} band" if learn <= FLAT else
                     f"NULL -- {learn:+.4f} above chance, between {FLAT:.2f} and {LEARNS:.2f}"}
    bad = sorted(f"{a}/{q}" for a in ARMS for q, tbl in (("diagonal", r["diagonal"]), ("last row", r["last_row"]))
                 if abs(tbl[a]["contrast"]["sigma"]) >= SIGMA)
    widest = max((abs(r["diagonal"][a]["contrast"]["sigma"]) for a in ARMS), default=0.0)
    widest = max(widest, max((abs(r["last_row"][a]["contrast"]["sigma"]) for a in ARMS), default=0.0))
    j4 = {"id": "QA4",
          "measured": f"the policy run minus the card's roll, paired over {MIN_REPS} replicates: the diagonals "
                      f"{ {a: round(r['diagonal'][a]['contrast']['mean'], 4) for a in ARMS} } at "
                      f"{ {a: round(r['diagonal'][a]['contrast']['sigma'], 2) for a in ARMS} } sigma and the last rows "
                      f"{ {a: round(r['last_row'][a]['contrast']['mean'], 4) for a in ARMS} } at "
                      f"{ {a: round(r['last_row'][a]['contrast']['sigma'], 2) for a in ARMS} } sigma, the widest "
                      f"|sigma| being {widest:.2f}",
          "verdict": "MET -- the benchmark's numbers do not move with the policy, on either quantity and any arm" if
                     not bad else f"FALSIFIER FIRED -- {bad}"}
    return [j1, j2, j3, j4]


def report(r: dict) -> int:
    print("== the benchmark carries a policy ==")
    if not r.get("ok"):
        print(f"   REFUSED -- {r.get('reason', 'a run is absent')}")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)
    print("   `e325` named a reward and a policy as what a game has and this loop did not; this is the runner")
    print("   carrying the second: a trainable identity-initialized map from the action population to the world's")
    print("   drive, in the same optimizer as the body and the head, on the card's own earned-label configuration")
    print(f"\n   {'arm':<10} {'diagonal (policy)':>17} {'(card)':>9} {'contrast':>10} {'sigma':>7} "
          f"{'last row (policy)':>18} {'(card)':>9} {'contrast':>10} {'sigma':>7}")
    for a in ARMS:
        d, l = r["diagonal"][a]["contrast"], r["last_row"][a]["contrast"]
        print(f"   {a:<10} {statistics.fmean(r['diagonal'][a]['policy']):>17.4f} "
              f"{statistics.fmean(r['diagonal'][a]['card']):>9.4f} {d['mean']:>+10.4f} {d['sigma']:>7.2f} "
              f"{statistics.fmean(r['last_row'][a]['policy']):>18.4f} "
              f"{statistics.fmean(r['last_row'][a]['card']):>9.4f} {l['mean']:>+10.4f} {l['sigma']:>7.2f}")
    print(f"\n   the policy's distance from the identity: {r['spans']['moves_recorded']} of "
          f"{r['spans']['moves_total']} recorded, smallest {r['spans']['move_min']}, mean {r['spans']['move_mean']}")
    print(f"   keys compared {r['spans']['same_fields']}; differing past the inert rule {r['spans']['differ']};")
    print(f"   admitted by it {r['spans']['inert']}; the flag {r['spans']['flags']}")
    print("\n== the registered claims, QA1-QA4 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e477` to `e480` trained policies outside the runner and every one of them closed on the same")
    print("    sentence: the runner does not carry one. This unit is the first artifact where it does)")
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
