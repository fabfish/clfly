"""E460 -- the matched-random anchor at eight neuron columns: whether the width moves the other arm's price too.

`e458` held the card's world's width and moved its source and the biological anchor's newest-task price came back --
**-0.0615** at **4.48** sigma at eight neuron columns against **-0.0115** at **0.78** at thirty-two -- so the price is
the head's **width**'s and not its source's, and the card's twelfth revision carries that. **But the width story is about
one arm**: `e456` drove the matched-random anchor on the same thirty-two column head and found its price **resolves**
there too, **-0.0323** at **2.77** sigma, and on the earned label's eight columns it reads **-0.1135** at **4.49**. So
the two arms' prices across the three heads read

  * `ewc-block`: **-0.1177** (3.71) at the world's eight, **-0.0115** (0.78) at the neurons' thirty-two, **-0.0615**
    (4.48) at the neurons' eight;
  * `ewc-block-rand`: **-0.1135** (4.49) at the world's eight, **-0.0323** (2.77) at the neurons' thirty-two, and
    **nothing at the neurons' eight**,

and the width that removes the biological arm's price leaves the matched-random arm's resolved. **This unit drives the
fifth cell.** `e458`'s configuration with `--methods naive,ewc-block-rand,replay` alone differing, at the same twenty
replicates, coupled world and eight-column neuron head, so the pair can be read at the head where the width story was
found and the two shared arms checked against `e458`'s roll. Five claims, registered before the new run's reading was
opened.

- **DG1 -- and the run is one configuration with the arm list moved.** The three arms at **20** replicates, every
  recorded config field agreeing with `e458`'s except `methods`, the output path and the saved weights, the read-out **8**
  and not the world's, the task names held, and the new run's `naive` and `replay` replicates **bit-identical** to
  `e458`'s. **Falsifier**: any other field differing, an arm missing or short, a read-out that is the world's or another
  width, or any shared replicate differing.
- **DG2 -- and the matched-random arm's price resolves at eight neuron columns too.** Its cost at the last-taught task is
  negative at **two** sigma or more. **Falsifier**: not negative, or under two sigma. *It reads **-0.0323** at **2.77**
  sigma at thirty-two columns and **-0.1135** at **4.49** on the earned label's eight.*
- **DG3 -- and its standing is unresolved here.** Its mean diagonal over the baseline is under **two** sigma.
  **Falsifier**: at or above two sigma in either direction.
- **DG4 -- and the two arms' standings agree at this head.** Their mean-diagonal contrasts differ by at most **0.05**.
  **Falsifier**: **0.10** or more apart; **null**: between. *The fifth cell of the pair, after the earned label and the
  neurons at thirty-two.*
- **DG5 -- and the buffer is ahead of the matched-random anchor here too.** `replay` minus `ewc-block-rand` on the mean
  diagonal is positive at **two** sigma or more. **Falsifier**: not positive, or under two sigma.

**What it can do beyond that.** It closes the pair at the head where the width story was found and says whether that
story is the arm's or the pair's. If the matched-random arm's price resolves here as it does at thirty-two columns, then
**the width removes one arm's price and not the other's** -- the two arms have separated at every head this line has put
them on except the earned label's eight -- and the card's `head` clause should carry the pair rather than the biological
arm alone. If it does not resolve here either, then both prices are the width's after all and the thirty-two column
reading of the matched-random arm is the one that needs explaining.

**What it cannot do.** *One head of the three the pair has* and it is the arm list that moved, so the fifth cell is one
roll. *And one cell each*: the card's world at twenty replicates, so a price at **2.77** sigma is what a redraw could put
under the bar. *And one partition draw*: the matched-random partition is a draw of the same group sizes and not the family
of them. *And two arms are not a mechanism*: `e440`'s two parameters are read on the earned label and not on this head,
so that the two prices part company here does not say which parameter moves them.
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
from pathlib import Path

from clfly.bench.artifacts import write_json

#: the matched-random arm at eight neuron columns, and the two rolls it is read against
RUNS = {
    "new": Path("runs/e460_earned_label_rand_neurons8_20reps.json"),
    "biological": Path("runs/e458_earned_label_neurons8_20reps.json"),
    "wide": Path("runs/e456_earned_label_rand_neurons_20reps.json"),
}
ARMS = ("naive", "ewc-block", "ewc-block-rand", "replay")
BASELINE = "naive"
BIO = "ewc-block"
RAND = "ewc-block-rand"
BUFFER = "replay"
SHARED_ARMS = ("naive", "replay")
SHARED = ("circuit", "tasks")
IGNORED = ("json_out", "save_theta", "methods")
N_TASKS = 3
N_ARMS = 3
MIN_REPS = 20
NARROW = 8
SIGMA = 2.0
ALIKE = 0.05
ALIKE_FIRES = 0.10
#: what the other four cells already read, which DG2 is the test of
BIO_NARROW_PRICE = -0.0615
BIO_NARROW_PRICE_SIGMA = 4.48
RAND_WIDE_PRICE = -0.0323
RAND_WIDE_PRICE_SIGMA = 2.77
RAND_LABEL_PRICE = -0.1135
RAND_LABEL_PRICE_SIGMA = 4.49
CLAIMS = (
    ("DG1", f"and the run is one configuration with the arm list moved, at {MIN_REPS} replicates",
     "The three arms at twenty replicates, every recorded config field agreeing with e458's except methods, the output "
     "path and the saved weights, the read-out 8 and not the world's, the task names held, and the new run's naive and "
     "replay bit-identical to e458's",
     "falsifier: any other field differing, an arm missing or short, a read-out that is the world's or another width, "
     "or any shared replicate differing"),
    ("DG2", f"and the matched-random arm's price resolves at eight neuron columns too, at {SIGMA:.0f} sigma",
     "Its cost at the last-taught task is negative at two sigma or more",
     "falsifier: not negative, or under two sigma"),
    ("DG3", f"and its standing is unresolved here, under {SIGMA:.0f} sigma",
     "Its mean diagonal over the baseline is under two sigma",
     "falsifier: at or above two sigma in either direction"),
    ("DG4", f"and the two arms' standings agree at this head, within {ALIKE:.2f}",
     "Their mean-diagonal contrasts differ by at most 0.05",
     f"falsifier: {ALIKE_FIRES:.2f} or more apart; null: between"),
    ("DG5", f"and the buffer is ahead of the matched-random anchor here too, at {SIGMA:.0f} sigma",
     "replay minus ewc-block-rand on the mean diagonal is positive at two sigma or more",
     "falsifier: not positive, or under two sigma"),
)


def load(path) -> dict | None:
    p = Path(path)
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _arm(got: dict) -> dict | None:
    reps = (got or {}).get("replicates") or []
    if not reps:
        return None
    return {"replicates": len(reps),
            "final": [statistics.fmean([r["final_per_task"][k] for r in reps]) for k in range(N_TASKS)],
            "diagonal": [statistics.fmean(r["final_per_task"]) for r in reps],
            "last": [r["final_per_task"][-1] for r in reps],
            "forgetting": statistics.fmean([r["mean_forgetting"] for r in reps]),
            "records": [{"final_per_task": list(r["final_per_task"]),
                         "mean_forgetting": r["mean_forgetting"]} for r in reps]}


def _roll(path: Path, anchor: str) -> dict | None:
    doc = load(path)
    if not doc:
        return None
    methods = doc.get("methods") or {}
    arms = {}
    for arm in (BASELINE, anchor, BUFFER):
        if arm not in methods:
            return None
        got = _arm(methods[arm])
        if got is None:
            return None
        arms[arm] = got
    return {"artifact": path.name, "anchor": anchor, "arms": arms,
            "readouts": [t.get("n_readout") if isinstance(t, dict) else None for t in (doc.get("tasks") or [])],
            "from_world": (doc.get("config") or {}).get("readout_from_world"),
            "shared": {k: doc.get(k) for k in SHARED},
            "config": {k: (doc.get("config") or {}).get(k)
                       for k in sorted(set(doc.get("config") or {}) - set(IGNORED))}}


def _identical(a: list, b: list) -> dict:
    out = {"equal": True, "n": min(len(a), len(b)), "first_differing": None, "fields": []}
    if len(a) != len(b):
        out["equal"] = False
        return out
    for i, (x, y) in enumerate(zip(a, b)):
        if x == y:
            continue
        out["equal"] = False
        out["first_differing"] = i
        out["fields"] = sorted(k for k in set(x) | set(y) if x.get(k) != y.get(k))
        break
    return out


def _paired(a: list, b: list) -> dict:
    d = [x - y for x, y in zip(a, b)]
    n = len(d)
    mean = statistics.fmean(d) if n else 0.0
    sd = statistics.stdev(d) if n > 1 else 0.0
    se = sd / math.sqrt(n) if n else 0.0
    return {"n": n, "mean": mean, "sd": sd, "se": se, "sigma": (mean / se) if se > 0 else 0.0}


def reading(runs: dict = RUNS) -> dict:
    out = {"ok": True, "reason": None, "runs": {}, "same": {}, "identical": {}, "readouts": {}, "contrasts": {},
           "spans": {}}
    for label, path in runs.items():
        anchor = {k: v for k, v in (("new", RAND), ("biological", BIO), ("wide", RAND))}[label]
        got = _roll(path, anchor)
        if got is None:
            return {**out, "ok": False, "reason": f"roll {label}: {path} is absent or carries no {anchor} arm"}
        out["runs"][label] = got
    new, bio, wide = out["runs"]["new"], out["runs"]["biological"], out["runs"]["wide"]
    missing = [a for a in (BASELINE, RAND, BUFFER) if a not in new["arms"]]
    if missing:
        return {**out, "ok": False, "reason": f"the new roll carries no arm for {missing}"}
    same = {}
    fields = sorted(set(new["config"]) | set(bio["config"]))
    for k in fields:
        same[f"config.{k}"] = new["config"].get(k) == bio["config"].get(k)
    same["circuit"] = new["shared"].get("circuit") == bio["shared"].get("circuit")
    same["tasks"] = new["shared"].get("tasks") == bio["shared"].get("tasks")
    out["same"] = same
    out["readouts"] = {label: {"readouts": roll["readouts"], "from_world": roll["from_world"]}
                       for label, roll in out["runs"].items()}
    for arm in SHARED_ARMS:
        if arm not in bio["arms"]:
            out["identical"][f"new/biological:{arm}"] = {"equal": False, "n": 0, "first_differing": None, "fields": []}
            continue
        out["identical"][f"new/biological:{arm}"] = _identical(new["arms"][arm]["records"],
                                                               bio["arms"][arm]["records"])
    out["contrasts"] = {
        "rand_over_naive": _paired(new["arms"][RAND]["diagonal"], new["arms"][BASELINE]["diagonal"]),
        "rand_last": _paired(new["arms"][RAND]["last"], new["arms"][BASELINE]["last"]),
        "bio_over_naive": _paired(bio["arms"][BIO]["diagonal"], bio["arms"][BASELINE]["diagonal"]),
        "bio_last": _paired(bio["arms"][BIO]["last"], bio["arms"][BASELINE]["last"]),
        "buffer_over_rand": _paired(new["arms"][BUFFER]["diagonal"], new["arms"][RAND]["diagonal"]),
        "buffer_over_bio": _paired(bio["arms"][BUFFER]["diagonal"], bio["arms"][BIO]["diagonal"]),
        "wide_rand_last": _paired(wide["arms"][RAND]["last"], wide["arms"][BASELINE]["last"]),
    }
    out["spans"] = {"replicates": sorted({v["replicates"] for roll in out["runs"].values()
                                         for v in roll["arms"].values()}),
                    "arms": {label: len(roll["arms"]) for label, roll in out["runs"].items()},
                    "same_fields": len(same),
                    "readout": {"new": new["readouts"][0] if new["readouts"] else None,
                                "biological": bio["readouts"][0] if bio["readouts"] else None,
                                "wide": wide["readouts"][0] if wide["readouts"] else None,
                                "from_world": {l: out["runs"][l]["from_world"] for l in out["runs"]}},
                    "standing": {"rand": out["contrasts"]["rand_over_naive"]["mean"],
                                 "rand_sigma": out["contrasts"]["rand_over_naive"]["sigma"],
                                 "bio": out["contrasts"]["bio_over_naive"]["mean"],
                                 "bio_sigma": out["contrasts"]["bio_over_naive"]["sigma"]},
                    "price": {"rand": out["contrasts"]["rand_last"]["mean"],
                              "rand_sigma": out["contrasts"]["rand_last"]["sigma"],
                              "bio": out["contrasts"]["bio_last"]["mean"],
                              "bio_sigma": out["contrasts"]["bio_last"]["sigma"]},
                    "buffer_over_rand": out["contrasts"]["buffer_over_rand"],
                    "known": {"bio_narrow_price": BIO_NARROW_PRICE, "bio_narrow_price_sigma": BIO_NARROW_PRICE_SIGMA,
                              "rand_wide_price": RAND_WIDE_PRICE, "rand_wide_price_sigma": RAND_WIDE_PRICE_SIGMA,
                              "rand_label_price": RAND_LABEL_PRICE,
                              "rand_label_price_sigma": RAND_LABEL_PRICE_SIGMA}}
    return out


def judge(r: dict) -> list[dict]:
    if not r.get("ok"):
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- a roll is absent or carries no arm"} for c in CLAIMS]
    differ = sorted(k for k, v in r["same"].items() if not v)
    not_identical = sorted(k for k, v in r["identical"].items() if not v["equal"])
    thin = {f"{lbl}.{a}": v["replicates"] for lbl, roll in r["runs"].items() for a, v in roll["arms"].items()
            if v["replicates"] < MIN_REPS}
    short = {} if len(r["runs"]["new"]["arms"]) >= N_ARMS else {"new": sorted(r["runs"]["new"]["arms"])}
    ro = r["spans"]["readout"]
    reads_ok = (ro["new"] == NARROW and ro["biological"] == NARROW and
                ro["from_world"]["new"] is False and ro["from_world"]["biological"] is False and
                all(x == NARROW for x in r["runs"]["new"]["readouts"]))
    j1 = {"id": "DG1",
          "measured": f"the new roll carries {len(r['runs']['new']['arms'])} arms at {r['spans']['replicates']} "
                      f"replicates over {r['spans']['same_fields']} compared fields, the read-out {ro['new']} against "
                      f"the biological roll's {ro['biological']} and the wide roll's {ro['wide']}, from the world "
                      f"{ {l: v for l, v in ro['from_world'].items()} }, the shared arms bit-identical "
                      f"{len(r['identical']) - len(not_identical)} of {len(r['identical'])}",
          "verdict": "MET -- one configuration with the arm list moved at eight neuron columns, and the two shared arms "
                     "reproducing `e458`'s roll" if
                     (not short and not differ and not not_identical and reads_ok and not thin) else
                     f"FALSIFIER FIRED -- differing {differ}, not bit-identical {not_identical}, read-outs {ro}, "
                     f"thin {thin}, short {short}"}
    p = r["spans"]["price"]
    j2 = {"id": "DG2",
          "measured": f"at eight neuron columns the matched-random arm's newest-task cost is {p['rand']:+.4f} at "
                      f"{abs(p['rand_sigma']):.2f} sigma, against its {RAND_WIDE_PRICE:+.4f} at "
                      f"{RAND_WIDE_PRICE_SIGMA:.2f} at thirty-two columns and {RAND_LABEL_PRICE:+.4f} at "
                      f"{RAND_LABEL_PRICE_SIGMA:.2f} on the earned label's eight",
          "verdict": f"MET -- its price resolves here too, {p['rand']:+.4f} at {abs(p['rand_sigma']):.2f} sigma" if
                     (p["rand"] < 0 and abs(p["rand_sigma"]) >= SIGMA) else
                     f"FALSIFIER FIRED -- {p['rand']:+.4f} at {abs(p['rand_sigma']):.2f} sigma"}
    st = r["spans"]["standing"]
    j3 = {"id": "DG3",
          "measured": f"at eight neuron columns the matched-random arm's mean diagonal over the baseline is "
                      f"{st['rand']:+.4f} at {abs(st['rand_sigma']):.2f} sigma, against the biological arm's "
                      f"{st['bio']:+.4f} at {abs(st['bio_sigma']):.2f}",
          "verdict": f"MET -- its standing is unresolved here, {abs(st['rand_sigma']):.2f} sigma" if
                     abs(st["rand_sigma"]) < SIGMA else
                     f"FALSIFIER FIRED -- the standing resolves at {abs(st['rand_sigma']):.2f} sigma"}
    gap = abs(st["rand"] - st["bio"])
    j4 = {"id": "DG4",
          "measured": f"the two anchors' standings at eight neuron columns are {st['rand']:+.4f} and {st['bio']:+.4f}, "
                      f"{gap:.4f} apart",
          "verdict": f"MET -- the two anchors' standings agree at this head, {gap:.4f} apart" if gap <= ALIKE else
                     f"FALSIFIER FIRED -- the gap is {gap:.4f}" if gap >= ALIKE_FIRES else
                     f"NULL -- the gap is {gap:.4f}, between {ALIKE:.2f} and {ALIKE_FIRES:.2f}"}
    b = r["spans"]["buffer_over_rand"]
    j5 = {"id": "DG5",
          "measured": f"at eight neuron columns the buffer is {b['mean']:+.4f} ahead of the matched-random anchor on the "
                      f"mean diagonal at {abs(b['sigma']):.2f} sigma, against {r['contrasts']['buffer_over_bio']['mean']:+.4f} "
                      f"ahead of the biological one",
          "verdict": f"MET -- the buffer is ahead of the matched-random anchor here too, {b['mean']:+.4f} at "
                     f"{abs(b['sigma']):.2f} sigma" if (b["mean"] > 0 and abs(b["sigma"]) >= SIGMA) else
                     f"FALSIFIER FIRED -- {b['mean']:+.4f} at {abs(b['sigma']):.2f} sigma"}
    return [j1, j2, j3, j4, j5]


def report(r: dict) -> int:
    print("== the matched-random anchor at eight neuron columns ==")
    if not r.get("ok"):
        print(f"   REFUSED -- {r.get('reason', 'a roll is absent')}")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)
    print("   the card's world at `cue@0` with the action source, coupled, twenty replicates, the head reading the")
    print("   circuit's own neurons at eight columns -- `e458` read the other anchor on the same head")
    print(f"\n   {'roll':>11} {'read-out':>9} {'from world':>11} {'anchor':>15} {'arms':>34}")
    for label, roll in r["runs"].items():
        print(f"   {label:>11} {str(roll['readouts'][0] if roll['readouts'] else None):>9} "
              f"{str(roll['from_world']):>11} {roll['anchor']:>15} {','.join(sorted(roll['arms'])):>34}")
    st, p = r["spans"]["standing"], r["spans"]["price"]
    print(f"\n   the two anchors over the baseline on the mean diagonal: {RAND} {st['rand']:+.4f} at "
          f"{abs(st['rand_sigma']):.2f} sigma, {BIO} {st['bio']:+.4f} at {abs(st['bio_sigma']):.2f}")
    print(f"   their newest-task costs: {RAND} {p['rand']:+.4f} at {abs(p['rand_sigma']):.2f} sigma, {BIO} "
          f"{p['bio']:+.4f} at {abs(p['bio_sigma']):.2f}")
    print("\n   the two arms' prices across the heads this line has put them on:")
    print(f"      {BIO:>15}  the world's eight {BIO_NARROW_PRICE:+.4f} ({BIO_NARROW_PRICE_SIGMA:.2f}s);  "
          f"the neurons' eight {p['bio']:+.4f} ({abs(p['bio_sigma']):.2f}s)")
    print(f"      {RAND:>15}  the world's eight {RAND_LABEL_PRICE:+.4f} ({RAND_LABEL_PRICE_SIGMA:.2f}s);  "
          f"the neurons' thirty-two {RAND_WIDE_PRICE:+.4f} ({RAND_WIDE_PRICE_SIGMA:.2f}s);  "
          f"the neurons' eight {p['rand']:+.4f} ({abs(p['rand_sigma']):.2f}s)")
    print(f"\n   the buffer over each anchor: {r['contrasts']['buffer_over_rand']['mean']:+.4f} at "
          f"{abs(r['contrasts']['buffer_over_rand']['sigma']):.2f} sigma against {RAND}, "
          f"{r['contrasts']['buffer_over_bio']['mean']:+.4f} at "
          f"{abs(r['contrasts']['buffer_over_bio']['sigma']):.2f} against {BIO}")
    print(f"   the shared arms against e458's roll: " +
          ", ".join(f"{k} {v['equal']}" for k, v in r["identical"].items()))
    print("\n== the registered claims, DG1-DG5 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e458` found the width removes the biological arm's price; this asks the fifth cell -- the same head")
    print("    for the matched-random arm, whose price resolved at thirty-two columns)")
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
