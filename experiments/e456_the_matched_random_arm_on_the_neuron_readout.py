"""E456 -- the matched-random anchor on the neuron read-out: whether `e455`'s reading holds for the other arm.

`e455` moved the card's world's read-out from the **world's own state** (`--readout-from-world`, the earned label) to the
**circuit's own neurons** and found the arm's one resolved effect gone: `ewc-block`'s newest-task cost reads **-0.0115**
at **0.78** sigma on the neurons against **-0.1177** at **3.71** on the earned label, and its whole-diagonal standing
**+0.0187** at **1.03** against **-0.0302** at **1.77** -- so the card's clauses about that arm are clauses about the
earned-label configuration. `e455` closed with the prediction its own reading implies and did not take: *if the price is
the earned label's rather than the anchoring's, the matched-random arm's price should be the earned label's too*.

**This unit drives that arm on the neuron read-out.** `e455`'s configuration with
`--methods naive,ewc-block-rand,replay` alone differing, at the same twenty replicates, coupled world and neuron read-out,
so the second anchor can be asked the same three questions and the two arms compared under the head that is not the card's.
Five claims, registered before the new run's reading was opened.

- **DC1 -- and the run is one configuration with the arm list moved.** The three arms at **20** replicates, every
  recorded config field agreeing with `e455`'s except `methods`, the output path and the saved weights, the read-out the
  circuit's **32** and not the world's, the task names held, and the new run's `naive` and `replay` replicates
  **bit-identical** to `e455`'s. **Falsifier**: any other field differing, an arm missing or short, a read-out that is
  the world's or another width, or any shared replicate differing.
- **DC2 -- and the matched-random arm's standing is unresolved on the neuron read-out.** Its mean diagonal over the
  baseline is under **two** sigma. **Falsifier**: at or above two sigma in either direction. *This is `e455`'s
  prediction for the second arm.*
- **DC3 -- and its newest-task price does not resolve either.** Its cost at the last-taught task is under **two** sigma.
  **Falsifier**: at or above two sigma.
- **DC4 -- and the two anchors agree under this read-out.** Their mean-diagonal contrasts differ by at most **0.05**.
  **Falsifier**: **0.10** or more apart; **null**: between.
- **DC5 -- and the buffer is ahead of the matched-random anchor here too.** `replay` minus `ewc-block-rand` on the mean
  diagonal is positive at **two** sigma or more. **Falsifier**: not positive, or under two sigma.

**What it can do beyond that.** It turns `e455`'s single arm into a pair. If both anchors lose their only resolved
effect when the head stops reading the world, then the price the card carries is the **read-out's** for the pair and not
for one arm -- which is what a clause about *the anchor* would then have to say, and which `e439`, `e447` and `e451`
found for the pair on the earned label at **0.0042** to **0.0101**. If instead the matched-random arm keeps its price
where the biological one loses it, then the price is the **basis's** after all and `e455`'s reading is one arm's.

**What it cannot do.** *One read-out moved, two things changed*: the circuit's **32** neurons differ from the world's
**8** both in what they read and in width, and `e448`/`e449` measured the width axis on the earned label alone. *And one
cell*: the card's world at twenty replicates, so the other five draws and the three streams are not in the reading. *And
one partition draw*: the matched-random partition is a draw of the same group sizes and not the family of them. *And the
two rolls are two runs*: the pair pairs replicate against replicate by the runner's `seed0 + 100 * r` schedule, which is a
same-seed pairing and not the same run -- and `e455`'s own finding is that the two read-outs differ by more than the ten
earned-label rolls span, so what this pair carries is the read-out and not the seeds.
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
from pathlib import Path

from clfly.bench.artifacts import write_json

#: the matched-random arm on the neuron read-out, and the biological arm's roll at the same read-out
RUNS = {
    "new": Path("runs/e456_earned_label_rand_neurons_20reps.json"),
    "biological": Path("runs/e455_earned_label_neurons_20reps.json"),
}
ARMS = ("naive", "ewc-block", "ewc-block-rand", "replay")
BASELINE = "naive"
BIO = "ewc-block"
RAND = "ewc-block-rand"
BUFFER = "replay"
SHARED_ARMS = ("naive", "replay")
READOUT_FIELD = "readout_from_world"
SHARED = ("circuit", "tasks")
IGNORED = ("json_out", "save_theta", "methods")
N_TASKS = 3
N_ARMS = 3
MIN_REPS = 20
NEURON_READOUT = 32
ALIKE = 0.05
ALIKE_FIRES = 0.10
SIGMA = 2.0
#: the biological arm's readings on this read-out, which `e455` took
BIO_STANDING = 0.0187
BIO_STANDING_SIGMA = 1.03
BIO_PRICE = -0.0115
BIO_PRICE_SIGMA = 0.78
CLAIMS = (
    ("DC1", f"and the run is one configuration with the arm list moved, at {MIN_REPS} replicates",
     "The three arms at twenty replicates, every recorded config field agreeing with e455's except methods, the output "
     "path and the saved weights, the read-out the circuit's 32 and not the world's, the task names held, and the new "
     "run's naive and replay bit-identical to e455's",
     "falsifier: any other field differing, an arm missing or short, a read-out that is the world's or another width, "
     "or any shared replicate differing"),
    ("DC2", f"and the matched-random arm's standing is unresolved here, under {SIGMA:.0f} sigma",
     "Its mean diagonal over the baseline is under two sigma",
     "falsifier: at or above two sigma in either direction"),
    ("DC3", f"and its newest-task price does not resolve either, under {SIGMA:.0f} sigma",
     "Its cost at the last-taught task is under two sigma",
     "falsifier: at or above two sigma"),
    ("DC4", f"and the two anchors agree under this read-out, within {ALIKE:.2f}",
     "Their mean-diagonal contrasts differ by at most 0.05",
     f"falsifier: {ALIKE_FIRES:.2f} or more apart; null: between"),
    ("DC5", f"and the buffer is ahead of the matched-random anchor here too, at {SIGMA:.0f} sigma",
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


def _roll(path: Path) -> dict | None:
    doc = load(path)
    if not doc:
        return None
    methods = doc.get("methods") or {}
    arms = {}
    for arm in ARMS:
        if arm not in methods:
            continue
        got = _arm(methods[arm])
        if got is None:
            return None
        arms[arm] = got
    cfg = doc.get("config") or {}
    return {"artifact": path.name, "arms": arms,
            "task_names": [t.get("name") if isinstance(t, dict) else t for t in (doc.get("tasks") or [])],
            "readouts": [t.get("n_readout") if isinstance(t, dict) else None for t in (doc.get("tasks") or [])],
            "readout_from_world": cfg.get(READOUT_FIELD),
            "shared": {k: doc.get(k) for k in SHARED},
            "config": {k: cfg.get(k) for k in sorted(set(cfg) - set(IGNORED))}}


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
        got = _roll(path)
        if got is None:
            return {**out, "ok": False, "reason": f"roll {label}: {path} is absent or carries no arm"}
        out["runs"][label] = got
    new, bio = out["runs"]["new"], out["runs"]["biological"]
    missing = [a for a in (BASELINE, RAND, BUFFER) if a not in new["arms"]]
    if missing:
        return {**out, "ok": False, "reason": f"the new roll carries no arm for {missing}"}
    if BIO not in bio["arms"] or BASELINE not in bio["arms"]:
        return {**out, "ok": False, "reason": "the biological arm's roll carries no anchor or no baseline"}
    same = {}
    fields = sorted(set(new["config"]) | set(bio["config"]))
    for k in fields:
        same[f"config.{k}"] = new["config"].get(k) == bio["config"].get(k)
    same["circuit"] = new["shared"].get("circuit") == bio["shared"].get("circuit")
    same["task_names"] = new["task_names"] == bio["task_names"]
    out["same"] = same
    out["readouts"] = {"new": {"readouts": new["readouts"], "from_world": new["readout_from_world"]},
                       "biological": {"readouts": bio["readouts"], "from_world": bio["readout_from_world"]}}
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
        "basis_accuracy": _paired(bio["arms"][BIO]["diagonal"], new["arms"][RAND]["diagonal"]),
        "buffer_over_rand": _paired(new["arms"][BUFFER]["diagonal"], new["arms"][RAND]["diagonal"]),
        "buffer_over_bio": _paired(bio["arms"][BUFFER]["diagonal"], bio["arms"][BIO]["diagonal"]),
    }
    out["spans"] = {"replicates": sorted({v["replicates"] for roll in out["runs"].values()
                                         for v in roll["arms"].values()}),
                    "arms": {label: len(roll["arms"]) for label, roll in out["runs"].items()},
                    "same_fields": len(same),
                    "readout": {"new": new["readouts"][0] if new["readouts"] else None,
                                "biological": bio["readouts"][0] if bio["readouts"] else None,
                                "from_world": {"new": new["readout_from_world"],
                                               "biological": bio["readout_from_world"]}},
                    "standing": {"rand": out["contrasts"]["rand_over_naive"]["mean"],
                                 "rand_sigma": out["contrasts"]["rand_over_naive"]["sigma"],
                                 "bio": out["contrasts"]["bio_over_naive"]["mean"],
                                 "bio_sigma": out["contrasts"]["bio_over_naive"]["sigma"]},
                    "last": {"rand": out["contrasts"]["rand_last"]["mean"],
                             "rand_sigma": out["contrasts"]["rand_last"]["sigma"],
                             "bio": out["contrasts"]["bio_last"]["mean"],
                             "bio_sigma": out["contrasts"]["bio_last"]["sigma"]},
                    "buffer_over_rand": out["contrasts"]["buffer_over_rand"],
                    "known": {"bio_standing": BIO_STANDING, "bio_standing_sigma": BIO_STANDING_SIGMA,
                              "bio_price": BIO_PRICE, "bio_price_sigma": BIO_PRICE_SIGMA}}
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
    reads_ok = (ro["new"] == NEURON_READOUT and ro["biological"] == NEURON_READOUT and
                ro["from_world"]["new"] is False and ro["from_world"]["biological"] is False and
                all(x == NEURON_READOUT for x in r["runs"]["new"]["readouts"]))
    j1 = {"id": "DC1",
          "measured": f"the new roll carries {len(r['runs']['new']['arms'])} arms at {r['spans']['replicates']} "
                      f"replicates over {r['spans']['same_fields']} compared fields, the read-out {ro['new']} against "
                      f"the biological roll's {ro['biological']}, from the world "
                      f"{ {k: v for k, v in ro['from_world'].items()} }, the shared arms bit-identical "
                      f"{len(r['identical']) - len(not_identical)} of {len(r['identical'])}",
          "verdict": "MET -- one configuration with the arm list moved on the neuron read-out, and the two shared arms "
                     "reproducing `e455`'s roll" if
                     (not short and not differ and not not_identical and reads_ok and not thin) else
                     f"FALSIFIER FIRED -- differing {differ}, not bit-identical {not_identical}, read-outs {ro}, "
                     f"thin {thin}, short {short}"}
    st = r["spans"]["standing"]
    j2 = {"id": "DC2",
          "measured": f"on the neuron read-out the matched-random arm's mean diagonal over the baseline is "
                      f"{st['rand']:+.4f} at {abs(st['rand_sigma']):.2f} sigma, against the biological arm's "
                      f"{st['bio']:+.4f} at {abs(st['bio_sigma']):.2f}",
          "verdict": f"MET -- the matched-random arm's standing is unresolved here too, "
                     f"{abs(st['rand_sigma']):.2f} sigma" if abs(st["rand_sigma"]) < SIGMA else
                     f"FALSIFIER FIRED -- the standing resolves at {abs(st['rand_sigma']):.2f} sigma"}
    last = r["spans"]["last"]
    j3 = {"id": "DC3",
          "measured": f"on the neuron read-out the matched-random arm's newest-task cost is {last['rand']:+.4f} at "
                      f"{abs(last['rand_sigma']):.2f} sigma, against the biological arm's {last['bio']:+.4f} at "
                      f"{abs(last['bio_sigma']):.2f}",
          "verdict": f"MET -- the matched-random arm's price does not resolve here either, "
                     f"{abs(last['rand_sigma']):.2f} sigma" if abs(last["rand_sigma"]) < SIGMA else
                     f"FALSIFIER FIRED -- the price resolves at {abs(last['rand_sigma']):.2f} sigma"}
    gap = abs(st["rand"] - st["bio"])
    j4 = {"id": "DC4",
          "measured": f"the two anchors' standings are {st['rand']:+.4f} and {st['bio']:+.4f}, {gap:.4f} apart, against "
                      f"`e439`'s as-built pair at {0.0063:.4f}",
          "verdict": f"MET -- the two anchors agree under this read-out, {gap:.4f} apart" if gap <= ALIKE else
                     f"FALSIFIER FIRED -- the gap is {gap:.4f}" if gap >= ALIKE_FIRES else
                     f"NULL -- the gap is {gap:.4f}, between {ALIKE:.2f} and {ALIKE_FIRES:.2f}"}
    b = r["spans"]["buffer_over_rand"]
    j5 = {"id": "DC5",
          "measured": f"on the neuron read-out the buffer is {b['mean']:+.4f} ahead of the matched-random anchor on the "
                      f"mean diagonal at {abs(b['sigma']):.2f} sigma, against {r['contrasts']['buffer_over_bio']['mean']:+.4f} "
                      f"ahead of the biological one",
          "verdict": f"MET -- the buffer is ahead of the matched-random anchor here too, {b['mean']:+.4f} at "
                     f"{abs(b['sigma']):.2f} sigma" if (b["mean"] > 0 and abs(b["sigma"]) >= SIGMA) else
                     f"FALSIFIER FIRED -- {b['mean']:+.4f} at {abs(b['sigma']):.2f} sigma"}
    return [j1, j2, j3, j4, j5]


def report(r: dict) -> int:
    print("== the matched-random anchor on the neuron read-out ==")
    if not r.get("ok"):
        print(f"   REFUSED -- {r.get('reason', 'a roll is absent')}")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)
    print("   the card's world at `cue@0` with the action source, coupled, twenty replicates, the head reading the")
    print("   circuit's own neurons -- and `e455` read the biological arm on the same head")
    print(f"\n   {'roll':>11} {'read-out':>9} {'from world':>11} {'arms':>34}")
    for label, roll in r["runs"].items():
        print(f"   {label:>11} {str(roll['readouts'][0] if roll['readouts'] else None):>9} "
              f"{str(roll['readout_from_world']):>11} {','.join(sorted(roll['arms'])):>34}")
    st, last = r["spans"]["standing"], r["spans"]["last"]
    print(f"\n   the two anchors over the baseline on the mean diagonal: {RAND} {st['rand']:+.4f} at "
          f"{abs(st['rand_sigma']):.2f} sigma, {BIO} {st['bio']:+.4f} at {abs(st['bio_sigma']):.2f}")
    print(f"   their newest-task costs: {RAND} {last['rand']:+.4f} at {abs(last['rand_sigma']):.2f} sigma, {BIO} "
          f"{last['bio']:+.4f} at {abs(last['bio_sigma']):.2f}")
    print(f"   the basis contrast on the mean diagonal: {r['contrasts']['basis_accuracy']['mean']:+.4f} at "
          f"{abs(r['contrasts']['basis_accuracy']['sigma']):.2f} sigma")
    print(f"   the buffer over each anchor: {r['contrasts']['buffer_over_rand']['mean']:+.4f} at "
          f"{abs(r['contrasts']['buffer_over_rand']['sigma']):.2f} sigma against {RAND}, "
          f"{r['contrasts']['buffer_over_bio']['mean']:+.4f} at "
          f"{abs(r['contrasts']['buffer_over_bio']['sigma']):.2f} against {BIO}")
    print(f"   the shared arms against e455's roll: " +
          ", ".join(f"{k} {v['equal']}" for k, v in r["identical"].items()))
    print("\n== the registered claims, DC1-DC5 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e455` found the biological arm's only resolved effect -- its newest-task price -- is the earned")
    print("    label's, and predicted the same of the matched-random arm; this is that prediction's run)")
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
