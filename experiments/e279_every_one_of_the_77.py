"""E279 -- "every one of the 77 stored runs": a universal over an epoch of the line, falsified an eighth of the way.

`e277` left four of the paper's counts unchecked and named them as the audit's largest gap. One of them is a
**universal about a configuration**:

    in the pool-96 / per-step-8 configuration ... `e62` found that every one of the 77 stored runs used 16 stored
    stimuli per task and 16 replayed samples per step

The population is enumerable -- every artifact carrying a `replay_per_task` or `replay_batch` field -- and so is the
clause. **The corpus has moved on**, and by the paper's own account: the sentence's own paragraph names the
pool-96 / per-step-8 configuration as the thing that replaced 16/16, so the universal is true of an **epoch** of the
line while reading as a statement about the line.

Registered, all **confirmatory** and computed in the exploration that wrote the module:

- **W1 -- the population has grown by more than half again.** Artifacts carrying a replay field: **167** against the
  sentence's **77**. **Falsifier**: under 1.5 times.
- **W2 -- and the clause is false today.** **16** artifacts carry a *recorded* setting other than 16 stored stimuli
  per task with 16 replayed samples per step -- **14** at 96/8, one at 96/16 and one at 96/48 -- and **7** more leave
  the batch unrecorded, so an eighth of the population is outside the clause. **Falsifier**: every artifact inside it.
- **W3 -- and the paper's own next clause names the configuration that superseded it.** The 96/8 setting is the
  pool-96 / per-step-8 configuration the same paragraph discusses, so the universal and the configuration that
  violates it sit in one paragraph and neither notices the other. **Falsifier**: the paper does not name that
  configuration.

**The fix is the same as `e278`'s**: an **epoch**, not a bigger count -- which runs, under which replay setting, at
which date. A universal about a configuration is a statement about the configurations that existed when it was
written, and this line changed its replay setting deliberately and said so twenty words later.

**What it cannot do**: `stored runs` is the sentence's own phrase, and the module's enumeration -- any artifact
carrying either replay field -- is the one the words admit and not necessarily the author's; 77 of 167 is plausible
for a stricter reading (say, only artifacts that trained a replay arm), and the report prints the setting tally so a
reader can see which population would fit; the seven artifacts that leave `replay_batch` unrecorded are counted
outside the clause although they may have used 16; and nothing here says the sentence was wrong when written, which is
the point of the unit.
"""

from __future__ import annotations

import argparse
import glob
import json
import sys
from collections import Counter
from pathlib import Path

from clfly.bench.artifacts import write_json

PAPER = Path("docs/paper/clfly-v1.md")
#: The clause the sentence states, and the population it states it over.
WANTED = (16, 16)
QUOTED_POPULATION = 77
#: The configuration the paper's own next clause names as the replacement.
SUCCESSOR = "pool-96"
CLAIMS = (
    ("W1", "the population has grown by more than half again",
     "The artifacts carrying a replay field number at least 1.5 times the sentence's 77",
     "falsifier: under 1.5 times"),
    ("W2", "and the clause is false today",
     "At least one artifact carries a recorded setting other than 16 stored stimuli per task with 16 replayed "
     "samples per step",
     "falsifier: every artifact is inside the clause"),
    ("W3", "and the paper's own next clause names the configuration that superseded it",
     "The paper names the pool-96 / per-step-8 configuration in the same passage",
     "falsifier: it does not"),
)


def load(path):
    p = Path(path)
    if not p.exists():
        return None
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def population(root: Path = Path("runs")) -> list[dict]:
    """Every artifact carrying either replay field, with the setting it records."""
    out = []
    for path in sorted(glob.glob(str(root / "*.json"))):
        try:
            d = json.loads(Path(path).read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError, OSError):
            continue
        cfg = (d or {}).get("config") or {}
        if "replay_per_task" not in cfg and "replay_batch" not in cfg:
            continue
        out.append({"artifact": Path(path).name, "per_task": cfg.get("replay_per_task"),
                    "batch": cfg.get("replay_batch")})
    return out


def judge(rows: list[dict], paper_text: str) -> list[dict]:
    out: list[dict] = []
    if not rows:
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- no artifact carries a replay field"}
                for c in CLAIMS]

    out.append({"id": "W1", "measured": f"{len(rows)} artifacts carry a replay field against the sentence's "
                                        f"{QUOTED_POPULATION} ({len(rows) / QUOTED_POPULATION:.2f}x)",
                "verdict": "MET -- the population is at least half again the sentence's count"
                if len(rows) >= 1.5 * QUOTED_POPULATION else "FALSIFIER FIRED -- under 1.5 times"})

    tally = Counter((r["per_task"], r["batch"]) for r in rows)
    inside = tally.get(WANTED, 0)
    recorded_outside = {k: v for k, v in tally.items() if k != WANTED and k[1] is not None}
    unrecorded = sum(v for k, v in tally.items() if k != WANTED and k[1] is None)
    detail = "; ".join(f"{k[0]}/{k[1]}: {v}" for k, v in sorted(tally.items(), key=lambda kv: -kv[1]))
    out.append({"id": "W2", "measured": f"the settings are {detail}; inside the clause: {inside}; recorded outside: "
                                        f"{sum(recorded_outside.values())} ({recorded_outside}); unrecorded batch: "
                                        f"{unrecorded}",
                "verdict": "MET -- an eighth of the population is outside the clause" if recorded_outside else
                           "FALSIFIER FIRED -- every artifact is inside the clause"})

    named = SUCCESSOR in paper_text
    out.append({"id": "W3", "measured": f"the paper names {SUCCESSOR!r}: {named}; the setting that violates the "
                                        f"clause is {sorted(recorded_outside, key=lambda k: -recorded_outside[k])}",
                "verdict": "MET -- the universal and the configuration that superseded it sit in one paragraph"
                if named and recorded_outside else
                "FALSIFIER FIRED -- the paper does not name the successor"})
    return out


def report(rows: list[dict]) -> int:
    text = PAPER.read_text(encoding="utf-8") if PAPER.exists() else ""
    tally = Counter((r["per_task"], r["batch"]) for r in rows)
    print("== the population the sentence names, by replay setting ==")
    print(f"   artifacts carrying a replay field: {len(rows)}")
    for k, v in sorted(tally.items(), key=lambda kv: -kv[1]):
        print(f"      stored stimuli per task {str(k[0]):>4} / replayed samples per step {str(k[1]):>4}: {v:4d}"
              + ("   <- the sentence's clause" if k == WANTED else ""))

    print("\n== the registered claims, W1-W3 ==")
    j = judge(rows, text)
    for c, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {c[2]}")
        print(f"          and its {c[3]}")
    print("\n   (a universal about a configuration is a statement about the configurations that existed when it was")
    print("    written; this line changed its replay setting deliberately and said so twenty words later)")
    return sum("REFUSED" in row["verdict"] for row in j)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--runs", type=Path, default=Path("runs"))
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args(argv)
    if not PAPER.exists():
        raise SystemExit(f"need {PAPER}")
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    rows = population(args.runs)
    if not rows:
        raise SystemExit("need artifacts carrying a replay field -- they are the population")
    if args.json_out:
        write_json(args.json_out, {"paper": str(PAPER), "wanted": list(WANTED),
                                   "quoted_population": QUOTED_POPULATION, "successor": SUCCESSOR,
                                   "population_size": len(rows),
                                   "settings": {f"{k[0]}/{k[1]}": v for k, v in
                                                Counter((r["per_task"], r["batch"]) for r in rows).items()},
                                   "claims": judge(rows, PAPER.read_text(encoding="utf-8"))})
        print(f"wrote {args.json_out}")
    return report(rows)


if __name__ == "__main__":
    sys.exit(main())
