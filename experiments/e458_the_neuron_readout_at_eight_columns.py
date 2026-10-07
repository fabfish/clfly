"""E458 -- the neuron read-out at eight columns: what the read-out's identity does once its width is held.

`e455` moved the card's world's head from the **world's own state** to the **circuit's own neurons** and found the
biological anchor's one resolved effect gone -- its newest-task cost **-0.0115** at **0.78** sigma against **-0.1177** at
**3.71**. `e457` then wrote both read-outs into the card's eleventh revision and named the gap it could not close: the two
differ in **what they read** *and* in **width**, **8** columns against **32**, so the difference is not separated from
`e448`'s and `e449`'s width axis. **On the earned label the two cannot be separated at all** -- `--readout-from-world`
makes the head's input the world's own state, so `--readout-size` is inert and the read-out's width *is* the world's
dimension.

**This unit holds the width and moves the source.** `e438`'s configuration with the read-out off the world **and its
width set to the world's own eight** -- `--readout-from-world` omitted and `--readout-size 8` instead of 32 -- at the same
three arms and twenty replicates, so this roll is **eight columns like the card's** and differs from it in **what it
reads** alone. Five claims, registered before the new run's reading was opened.

- **DE1 -- and the run is one configuration with the source moved at the card's width.** The three arms at **20**
  replicates, every recorded config field agreeing with `e438`'s except `readout_from_world`, `readout_size`, the output
  path and the saved weights, the three task names equal, and each task's own read-out **8** -- the width the card's head
  also reads at. **Falsifier**: any other config field differing, an arm missing or short, a task name differing, or a
  read-out that is not **8**.
- **DE2 -- and with the width held, the anchor's newest-task price does not resolve.** Its cost at the last-taught task is
  under **two** sigma. **Falsifier**: at or above two sigma. *`e457`'s gap: the earned label reads **-0.1177** at
  **3.71** and the neurons at **32** columns **-0.0115** at **0.78**. If the price is the head's source this stays
  unresolved; if it is the sixteen columns the neurons gave up, it returns here.*
- **DE3 -- and its standing does not resolve either.** Its mean diagonal over the baseline is under **two** sigma.
  **Falsifier**: at or above two sigma in either direction.
- **DE4 -- and the buffer's own ledger holds at this width.** `replay` minus `naive` at the first position is at least
  **+0.05** and at the last position at most **zero**. **Falsifier**: the first at or below **zero** (null between) or the
  last above **+0.05**.
- **DE5 -- and the buffer is ahead of the anchor here too.** `replay` minus `ewc-block` on the mean diagonal is positive
  at **two** sigma or more. **Falsifier**: not positive, or under two sigma.

**What it can do beyond that.** It closes the gap `e457` named, from the side that is open. With the card's roll
(**world's state, 8**), `e455`'s (**neurons, 32**) and this one (**neurons, 8**) the source is moved twice at two
widths and the width once at a fixed source, so the price's dependence on the two dials can be told apart: if it is
unresolved at **both** eight-column rolls and absent again at sixteen, the price is the **source's**; if it returns here,
it was the **width** the neurons gave up and `e455`'s reading is `e448`'s axis arriving through a different door.

**What it cannot do.** *One side of the corner*: **world's state at 32 columns** is not constructible, because
`--readout-from-world` makes the head's input the world's state and a 32-column world state is a different task rather
than the same one read differently. *And one cell each*: the card's world at twenty replicates, so the other five draws
and the three streams are not in the reading. *And a decoder's width is not its subset*: `--readout-seed` and
`--readout-size` are two of the three draws `e339` found in `--seed0`, and this unit moves the second. *And an arm is not
a mechanism*: `e440`'s two parameters are read on the earned label and not on this head.
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
from pathlib import Path

from clfly.bench.artifacts import write_json

#: the neuron read-out narrowed to the card's width, and the two rolls it is read against
RUNS = {
    "new": Path("runs/e458_earned_label_neurons8_20reps.json"),
    "card": Path("runs/e438_earned_label_three_arms_20reps.json"),
    "wide": Path("runs/e455_earned_label_neurons_20reps.json"),
}
ARMS = ("naive", "ewc-block", "replay")
BASELINE = "naive"
ANCHOR = "ewc-block"
BUFFER = "replay"
SHARED = ("circuit", "tasks")
IGNORED = ("json_out", "save_theta", "methods", "readout_from_world", "readout_size")
N_TASKS = 3
N_ARMS = 3
MIN_REPS = 20
CARD_WIDTH = 8
WIDE_WIDTH = 32
SIGMA = 2.0
FIRST_BAR = 0.05
FIRST_FLOOR = 0.0
LAST_BAR = 0.0
LAST_FIRES = 0.05
#: what the two rolls already read, which DE2 is the test of
CARD_PRICE = -0.1177
CARD_PRICE_SIGMA = 3.71
WIDE_PRICE = -0.0115
WIDE_PRICE_SIGMA = 0.78
CLAIMS = (
    ("DE1", f"and the run is one configuration with the source moved at the card's width, at {MIN_REPS} replicates",
     "The three arms at twenty replicates, every recorded config field agreeing with e438's except readout_from_world, "
     "readout_size, the output path and the saved weights, the three task names equal, and each task's own read-out 8",
     "falsifier: any other config field differing, an arm missing or short, a task name differing, or a read-out that is "
     "not 8"),
    ("DE2", f"and with the width held, the anchor's newest-task price does not resolve, under {SIGMA:.0f} sigma",
     "Its cost at the last-taught task is under two sigma",
     "falsifier: at or above two sigma"),
    ("DE3", f"and its standing does not resolve either, under {SIGMA:.0f} sigma",
     "Its mean diagonal over the baseline is under two sigma",
     "falsifier: at or above two sigma in either direction"),
    ("DE4", f"and the buffer's own ledger holds at this width, first at least {FIRST_BAR:+.2f} and last at most {LAST_BAR:+.2f}",
     "replay minus naive at the first position is at least +0.05 and at the last position at most zero",
     f"falsifier: the first at or below {FIRST_FLOOR:+.2f} (null between) or the last above {LAST_FIRES:+.2f}"),
    ("DE5", f"and the buffer is ahead of the anchor here too, at {SIGMA:.0f} sigma",
     "replay minus ewc-block on the mean diagonal is positive at two sigma or more",
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


def _roll(path: Path) -> dict | None:
    doc = load(path)
    if not doc:
        return None
    methods = doc.get("methods") or {}
    arms = {}
    for arm in ARMS:
        if arm not in methods:
            continue
        reps = (methods.get(arm) or {}).get("replicates") or []
        if not reps:
            return None
        arms[arm] = {"replicates": len(reps),
                     "final": [statistics.fmean([r["final_per_task"][k] for r in reps]) for k in range(N_TASKS)],
                     "diagonal": [statistics.fmean(r["final_per_task"]) for r in reps],
                     "last": [r["final_per_task"][-1] for r in reps],
                     "forgetting": statistics.fmean([r["mean_forgetting"] for r in reps])}
    cfg = doc.get("config") or {}
    tasks = doc.get("tasks") or []
    return {"artifact": path.name, "arms": arms,
            "task_names": [t.get("name") if isinstance(t, dict) else t for t in tasks],
            "readouts": [t.get("n_readout") if isinstance(t, dict) else None for t in tasks],
            "from_world": cfg.get("readout_from_world"), "readout_size": cfg.get("readout_size"),
            "shared": {k: doc.get(k) for k in SHARED},
            "config": {k: cfg.get(k) for k in sorted(set(cfg) - set(IGNORED))}}


def _paired(a: list, b: list) -> dict:
    d = [x - y for x, y in zip(a, b)]
    n = len(d)
    mean = statistics.fmean(d) if n else 0.0
    sd = statistics.stdev(d) if n > 1 else 0.0
    se = sd / math.sqrt(n) if n else 0.0
    return {"n": n, "mean": mean, "sd": sd, "se": se, "sigma": (mean / se) if se > 0 else 0.0}


def reading(runs: dict = RUNS) -> dict:
    out = {"ok": True, "reason": None, "runs": {}, "same": {}, "readouts": {}, "contrasts": {}, "spans": {}}
    for label, path in runs.items():
        got = _roll(path)
        if got is None:
            return {**out, "ok": False, "reason": f"roll {label}: {path} is absent or carries no arm"}
        out["runs"][label] = got
    new, card, wide = out["runs"]["new"], out["runs"]["card"], out["runs"]["wide"]
    missing = [a for a in ARMS if a not in new["arms"]]
    if missing:
        return {**out, "ok": False, "reason": f"the new roll carries no arm for {missing}"}
    same = {}
    fields = sorted(set(new["config"]) | set(card["config"]))
    for k in fields:
        same[f"config.{k}"] = new["config"].get(k) == card["config"].get(k)
    same["circuit"] = new["shared"].get("circuit") == card["shared"].get("circuit")
    same["task_names"] = new["task_names"] == card["task_names"]
    out["same"] = same
    out["readouts"] = {label: {"readouts": roll["readouts"], "from_world": roll["from_world"],
                               "readout_size": roll["readout_size"]}
                       for label, roll in out["runs"].items()}
    for label, roll in out["runs"].items():
        out["contrasts"][label] = {
            "anchor_diagonal": _paired(roll["arms"][ANCHOR]["diagonal"], roll["arms"][BASELINE]["diagonal"]),
            "anchor_last": _paired(roll["arms"][ANCHOR]["last"], roll["arms"][BASELINE]["last"]),
            "buffer_gain": [roll["arms"][BUFFER]["final"][k] - roll["arms"][BASELINE]["final"][k]
                            for k in range(N_TASKS)],
            "buffer_diagonal": _paired(roll["arms"][BUFFER]["diagonal"], roll["arms"][BASELINE]["diagonal"]),
            "buffer_over_anchor": _paired(roll["arms"][BUFFER]["diagonal"], roll["arms"][ANCHOR]["diagonal"]),
            "forgetting": {a: roll["arms"][a]["forgetting"] for a in roll["arms"]}}
    n = out["contrasts"]["new"]
    out["spans"] = {"replicates": sorted({v["replicates"] for roll in out["runs"].values()
                                         for v in roll["arms"].values()}),
                    "arms": {label: len(roll["arms"]) for label, roll in out["runs"].items()},
                    "same_fields": len(same),
                    "readout": {"new": new["readouts"][0] if new["readouts"] else None,
                                "card": card["readouts"][0] if card["readouts"] else None,
                                "wide": wide["readouts"][0] if wide["readouts"] else None,
                                "from_world": {l: out["runs"][l]["from_world"] for l in out["runs"]}},
                    "anchor": {"standing": n["anchor_diagonal"]["mean"],
                               "standing_sigma": n["anchor_diagonal"]["sigma"],
                               "price": n["anchor_last"]["mean"], "price_sigma": n["anchor_last"]["sigma"]},
                    "buffer": {"first": n["buffer_gain"][0], "last": n["buffer_gain"][-1],
                               "over_anchor": n["buffer_over_anchor"]["mean"],
                               "over_anchor_sigma": n["buffer_over_anchor"]["sigma"]},
                    "known": {"card_price": CARD_PRICE, "card_price_sigma": CARD_PRICE_SIGMA,
                              "wide_price": WIDE_PRICE, "wide_price_sigma": WIDE_PRICE_SIGMA}}
    return out


def judge(r: dict) -> list[dict]:
    if not r.get("ok"):
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- a roll is absent or carries no arm"} for c in CLAIMS]
    differ = sorted(k for k, v in r["same"].items() if not v)
    thin = {f"{lbl}.{a}": v["replicates"] for lbl, roll in r["runs"].items() for a, v in roll["arms"].items()
            if v["replicates"] < MIN_REPS}
    short = {} if len(r["runs"]["new"]["arms"]) >= N_ARMS else {"new": sorted(r["runs"]["new"]["arms"])}
    ro = r["spans"]["readout"]
    reads_ok = (ro["new"] == CARD_WIDTH and ro["card"] == CARD_WIDTH and
                all(x == CARD_WIDTH for x in r["runs"]["new"]["readouts"]) and
                ro["from_world"]["new"] is False and ro["from_world"]["card"] is True)
    j1 = {"id": "DE1",
          "measured": f"the new roll carries {len(r['runs']['new']['arms'])} arms at {r['spans']['replicates']} "
                      f"replicates over {r['spans']['same_fields']} compared fields, its read-out {ro['new']} against "
                      f"the card's {ro['card']} and the wide roll's {ro['wide']}, from the world "
                      f"{ {l: v for l, v in ro['from_world'].items()} }",
          "verdict": "MET -- one configuration with the read-out off the world at the card's own eight columns, the task "
                     "names held, and every task's read-out eight" if
                     (not short and not differ and not thin and reads_ok) else
                     f"FALSIFIER FIRED -- differing {differ}, thin {thin}, short {short}, read-outs {ro}"}
    a = r["spans"]["anchor"]
    j2 = {"id": "DE2",
          "measured": f"at eight neuron columns the anchor's newest-task cost is {a['price']:+.4f} at "
                      f"{abs(a['price_sigma']):.2f} sigma, against the earned label's {CARD_PRICE:+.4f} at "
                      f"{CARD_PRICE_SIGMA:.2f} and the thirty-two column roll's {WIDE_PRICE:+.4f} at "
                      f"{WIDE_PRICE_SIGMA:.2f}",
          "verdict": f"MET -- with the width held the price does not resolve, {abs(a['price_sigma']):.2f} sigma" if
                     abs(a["price_sigma"]) < SIGMA else
                     f"FALSIFIER FIRED -- the price returns at {abs(a['price_sigma']):.2f} sigma"}
    j3 = {"id": "DE3",
          "measured": f"at eight neuron columns the anchor's mean diagonal over the baseline is {a['standing']:+.4f} at "
                      f"{abs(a['standing_sigma']):.2f} sigma",
          "verdict": f"MET -- its standing does not resolve here either, {abs(a['standing_sigma']):.2f} sigma" if
                     abs(a["standing_sigma"]) < SIGMA else
                     f"FALSIFIER FIRED -- the standing resolves at {abs(a['standing_sigma']):.2f} sigma"}
    b = r["spans"]["buffer"]
    first_ok = b["first"] >= FIRST_BAR
    last_ok = b["last"] <= LAST_BAR
    j4 = {"id": "DE4",
          "measured": f"at eight neuron columns the buffer over naive reads {b['first']:+.4f} at the first position and "
                      f"{b['last']:+.4f} at the last, against the card's +0.2896 and -0.0604",
          "verdict": f"MET -- the buffer's ledger holds at this width, {b['first']:+.4f} and {b['last']:+.4f}" if
                     (first_ok and last_ok) else
                     f"FALSIFIER FIRED -- the first is {b['first']:+.4f} and the last {b['last']:+.4f}" if
                     (b["first"] <= FIRST_FLOOR or b["last"] > LAST_FIRES) else
                     f"NULL -- the first is {b['first']:+.4f} and the last {b['last']:+.4f}"}
    j5 = {"id": "DE5",
          "measured": f"at eight neuron columns the buffer is {b['over_anchor']:+.4f} ahead of the anchor on the mean "
                      f"diagonal at {abs(b['over_anchor_sigma']):.2f} sigma",
          "verdict": f"MET -- the buffer is ahead of the anchor here too, {b['over_anchor']:+.4f} at "
                     f"{abs(b['over_anchor_sigma']):.2f} sigma" if
                     (b["over_anchor"] > 0 and abs(b["over_anchor_sigma"]) >= SIGMA) else
                     f"FALSIFIER FIRED -- {b['over_anchor']:+.4f} at {abs(b['over_anchor_sigma']):.2f} sigma"}
    return [j1, j2, j3, j4, j5]


def report(r: dict) -> int:
    print("== the neuron read-out at eight columns ==")
    if not r.get("ok"):
        print(f"   REFUSED -- {r.get('reason', 'a roll is absent')}")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)
    print("   the card's world at `cue@0` with the action source, coupled, twenty replicates -- three heads of the same")
    print("   world: the world's own state at eight columns, the circuit's neurons at thirty-two, and the neurons at eight")
    print(f"\n   {'roll':>6} {'read-out':>9} {'from world':>11} {'readout_size':>13} {'tasks':>50}")
    for label, roll in r["runs"].items():
        print(f"   {label:>6} {str(roll['readouts'][0] if roll['readouts'] else None):>9} "
              f"{str(roll['from_world']):>11} {str(roll['readout_size']):>13} "
              f"{'>'.join(roll['task_names'])[:50]:>50}")
    a, b = r["spans"]["anchor"], r["spans"]["buffer"]
    print(f"\n   the anchor over the baseline: standing {a['standing']:+.4f} at {abs(a['standing_sigma']):.2f} sigma, "
          f"newest task {a['price']:+.4f} at {abs(a['price_sigma']):.2f}")
    print(f"   the buffer over the baseline by position: " +
          " ".join(f"{x:+.4f}" for x in r["contrasts"]["new"]["buffer_gain"]))
    print(f"   the buffer over the anchor: {b['over_anchor']:+.4f} at {abs(b['over_anchor_sigma']):.2f} sigma")
    print("\n   the three heads against each other:")
    for label in ("card", "wide", "new"):
        c = r["contrasts"][label]
        print(f"      {label:>5} anchor {c['anchor_diagonal']['mean']:+.4f} ({abs(c['anchor_diagonal']['sigma']):.2f}s) "
              f"standing, {c['anchor_last']['mean']:+.4f} ({abs(c['anchor_last']['sigma']):.2f}s) price; buffer over "
              f"anchor {c['buffer_over_anchor']['mean']:+.4f} ({abs(c['buffer_over_anchor']['sigma']):.2f}s)")
    print("\n== the registered claims, DE1-DE5 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e457` named the gap: the two read-outs differ in what they read and in width, and on the earned label")
    print("    the two cannot be separated -- this roll holds the width and moves the source)")
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
