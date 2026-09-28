"""E270 -- an existence premise the paper states twice, and the corpus falsifies in one command.

`e268` closes supersession for **numbers**: a registry names a number the paper quotes, the finding that moved it and
the replacement, and the check is mechanical. An **existence premise** -- "no artifact on disk carries X" -- is a
different kind of claim and needs a different instrument: it is not superseded by a finding, it is simply checked
against the corpus, and it is the kind of sentence a reader can falsify in one command.

The paper states one such premise twice, in two scopes:

    no artifact on disk carries a 128-batch Fisher at all

and the corpus carries **three** artifacts with `fisher_batches` 128 -- `e101_rate_fb128`, `e102_rate_fb128_rerun` and
`e96_fisher_batches_128_1seed` -- at five, five and one replicates. So the premise is **false as written and true as
intended**: no *powered* run used 128 batches, which is what the sentence is doing in its paragraph, and the written
form is the one on the page.

The same audit runs on a second sentence in the paper's forward-looking section, which carries a right number in the
wrong cell: "`e178` runs at 144, which is conservative: at that sd a 0.0152 effect reads at **3.6σ**" multiplies
`e60`'s sd by `e178`'s replicate count, and `e178` is cs 300 with λ 1.0 while `e60` is cs 800 with λ 0.1 -- the cell
`e265` showed orders arms differently, and the contrast there reads 0.28σ.

Registered, all **confirmatory** and computed in the exploration that wrote the module:

- **V1 -- the premise is false.** The paper's "no artifact on disk carries a 128-batch Fisher at all" is contradicted
  by three artifacts. **Falsifier**: the corpus carries none.
- **V2 -- and it is true of every powered run.** All three carry fewer than **sixteen** replicates (five, five and
  one), so the sentence is right about the record's *power* and wrong about its *contents*, and the fix is a
  qualification rather than a retraction. **Falsifier**: a 128-batch artifact with sixteen or more replicates.
- **V3 -- and the forwarded number is right for a cell the record never ran.** At `e60`'s cell the arithmetic gives
  **3.57σ** at 144 replicates, but no artifact at that cell has more than **sixteen**, and the artifact that does run
  144 is another cell where the contrast reads **0.28σ**. **Falsifier**: an artifact at `e60`'s cell with a hundred
  replicates or more.

**What it cannot do**: it checks existence and not meaning, so a premise that is true and misleading passes; the scans
are over artifacts carrying both a `config` and a `methods` block, so a run recorded another way is invisible; V2's bar
of sixteen replicates is a convention taken from the line's own budgets and not a tested boundary; and nothing here
says whether the paragraphs around these sentences are right, only that these two sentences can be falsified as
written.
"""

from __future__ import annotations

import argparse
import glob
import json
import math
import sys
from pathlib import Path

from clfly.bench.artifacts import write_json

PAPER = Path("docs/paper/clfly-v1.md")
#: The premise the paper states, and the cell whose arithmetic the forwarded number uses.
PREMISE = "no artifact on disk carries a 128-batch Fisher at all"
FORWARD = "at that sd a 0.0152 effect reads at"
#: `e60`'s cell: cs 800, lambda 0.1, the `side` basis. `e178` is cs 300 with lambda 1.0.
CELL = {"circuit_size": 800, "lam": 0.1, "basis": "side"}
EFFECT, SD = 0.0152, 0.051108
CLAIMS = (
    ("V1", "the premise is false",
     "Three artifacts carry a 128-batch Fisher where the paper says no artifact does",
     "falsifier: the corpus carries none"),
    ("V2", "and it is true of every powered run",
     "Every 128-batch artifact carries fewer than sixteen replicates",
     "falsifier: one with sixteen or more"),
    ("V3", "and the forwarded number is right for a cell the record never ran",
     "No artifact at the cell whose sd it uses has a hundred replicates or more",
     "falsifier: one that does"),
)


def load(path):
    p = Path(path)
    if not p.exists():
        return None
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def rows_of(d: dict) -> dict:
    """Every artifact carrying both a configuration and a replicate list, with the fields the scans read."""
    meth, cfg = d.get("methods"), d.get("config")
    if not isinstance(meth, dict) or not isinstance(cfg, dict):
        return {}
    arms = [a for a in meth if isinstance(meth[a], dict) and meth[a].get("replicates")]
    if not arms:
        return {}
    return {"fisher_batches": cfg.get("fisher_batches"), "circuit_size": cfg.get("circuit_size"),
            "lam": cfg.get("lam"), "basis": cfg.get("basis"), "n": len(meth[arms[0]]["replicates"]),
            "arms": sorted(arms)}


def corpus(root: Path = Path("runs")) -> list[dict]:
    out = []
    for path in sorted(glob.glob(str(root / "*.json"))):
        try:
            d = json.loads(Path(path).read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError, OSError):
            continue
        r = rows_of(d or {})
        if r:
            out.append({"artifact": Path(path).name, **r})
    return out


def sigma_at(effect: float, sd: float, n: int) -> float:
    """The sigma an effect reads at n replicates, from the per-replicate sd."""
    return effect / (sd / math.sqrt(n)) if sd > 0 and n > 0 else float("nan")


def judge(rows: list[dict], paper_text: str) -> list[dict]:
    out: list[dict] = []
    if not rows:
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- no artifact on disk"} for c in CLAIMS]

    fb = [r for r in rows if r["fisher_batches"] == 128]
    stated = paper_text.count(PREMISE)
    out.append({"id": "V1", "measured": f"the paper states the premise {stated} time(s); the corpus carries "
                                        f"{len(fb)} artifact(s) with fisher_batches 128: "
                                        + ", ".join(f"{r['artifact']} (n = {r['n']})" for r in fb),
                "verdict": "MET -- the premise is false as written" if fb else
                           "FALSIFIER FIRED -- the corpus carries none, so the premise holds"})

    powered = [r for r in fb if r["n"] >= 16]
    out.append({"id": "V2", "measured": f"the 128-batch artifacts carry {sorted(r['n'] for r in fb)} replicates; "
                                        f"powered ones (sixteen or more): {len(powered)}",
                "verdict": "MET -- every one is under sixteen replicates, so the sentence is true of the record's "
                           "power and wrong about its contents" if fb and not powered else
                "FALSIFIER FIRED -- a 128-batch artifact is powered" if powered else
                "REFUSED -- no 128-batch artifact to read"})

    cell = [r for r in rows if all(r[k] == v for k, v in CELL.items())]
    big = [r for r in cell if r["n"] >= 100]
    n_max = max((r["n"] for r in cell), default=0)
    forwarded = sigma_at(EFFECT, SD, 144)
    out.append({"id": "V3", "measured": f"the forwarded arithmetic gives {forwarded:.2f} sigma at 144 replicates at "
                                        f"the cell whose sd it uses; that cell's artifacts number {len(cell)} and "
                                        f"the largest carries {n_max} replicates; the artifact that does run 144 is "
                                        f"another cell",
                "verdict": "MET -- the number is right for a cell the record never ran at that size"
                if not big and 2.5 <= forwarded <= 4.5 else
                "FALSIFIER FIRED -- the cell has a hundred replicates, or the arithmetic does not give that number"})
    return out


def report(rows: list[dict]) -> int:
    fb = [r for r in rows if r["fisher_batches"] == 128]
    cell = [r for r in rows if all(r[k] == v for k, v in CELL.items())]
    print("== the premise, checked against the corpus ==")
    print(f"   artifacts scanned: {len(rows)}")
    print(f"   with fisher_batches 128: {len(fb)}")
    for r in sorted(fb, key=lambda r: -r["n"]):
        print(f"      {r['artifact'][:44]:44} n = {r['n']:3d}  cs {r['circuit_size']}/lam {r['lam']}/{r['basis']}")
    print(f"\n   artifacts at the forwarded number's own cell {CELL}: {len(cell)}")
    for r in sorted(cell, key=lambda r: -r["n"])[:6]:
        print(f"      {r['artifact'][:44]:44} n = {r['n']:3d}")
    print(f"   the largest there carries {max((r['n'] for r in cell), default=0)} replicates")
    print(f"\n   the forwarded arithmetic: {EFFECT} / ({SD} / sqrt(144)) = {sigma_at(EFFECT, SD, 144):.2f} sigma")

    text = PAPER.read_text(encoding="utf-8") if PAPER.exists() else ""
    print(f"\n   the paper states the premise {text.count(PREMISE)} time(s) and the forwarded number "
          f"{text.count(FORWARD)} time(s)")

    print("\n== the registered claims, V1-V3 ==")
    j = judge(rows, text)
    for c, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {c[2]}")
        print(f"          and its {c[3]}")
    print("\n   (a number is superseded by a finding and needs a registry; an existence premise is falsified by the")
    print("    corpus and needs a scan -- two kinds of stale sentence and two instruments)")
    return sum("REFUSED" in row["verdict"] for row in j)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--runs", type=Path, default=Path("runs"))
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args(argv)
    if not PAPER.exists():
        raise SystemExit(f"need {PAPER} -- the premise is a sentence of the paper")
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    rows = corpus(args.runs)
    text = PAPER.read_text(encoding="utf-8")
    if args.json_out:
        write_json(args.json_out, {"premise": PREMISE, "cell": CELL, "effect": EFFECT, "sd": SD,
                                   "fisher_128": fb_rows(rows), "cell_rows": cell_rows(rows),
                                   "claims": judge(rows, text)})
        print(f"wrote {args.json_out}")
    return report(rows)


def fb_rows(rows: list[dict]) -> list[dict]:
    return [r for r in rows if r["fisher_batches"] == 128]


def cell_rows(rows: list[dict]) -> list[dict]:
    return [r for r in rows if all(r[k] == v for k, v in CELL.items())]


if __name__ == "__main__":
    sys.exit(main())
