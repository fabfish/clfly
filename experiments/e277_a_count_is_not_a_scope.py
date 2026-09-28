"""E277 -- a count is not a scope: the paper's denominators have grown 2.4x and 6.4x since it wrote them.

`e270` checked one **existence premise** of the paper against the corpus and found it false. A **count** is the same
kind of claim one step down, and it fails in the same direction for the same reason: the corpus grows, so a number that
was the whole record becomes a share of it, and every **universal** quantified over that number silently narrows to the
share the number named.

    "every one of the 25 rate-network runs used 8 or 32"

is true of a quarter of the record now, and the number is the only thing in the sentence that says so. **A count is
not a scope.** The counts are extracted **by pattern** rather than by a hand-made registry -- unlike `e268`'s quoted
figures, a count about the corpus has a shape a regex can name -- so this audit is exhaustive over the forms it lists
and says which forms it did not look for.

Registered, all **confirmatory** and computed in the exploration that wrote the module:

- **W1 -- every count the paper states about the corpus is below today's corpus.** `216 artifacts` against **528** on
  disk, `25 rate-network runs` against **161** by the runner's configuration signature. The drift is one-sided:
  the record only grows. **Falsifier**: a stated count above the corpus's own.
- **W2 -- and at least one universal is quantified over such a count.** `every one of the 25 rate-network runs` names
  **25 of 161**, i.e. **16%** of what that noun now covers, so the sentence is about a minority of the record while
  reading as a statement about all of it. **Falsifier**: no universal over a count, or the share above a half.
- **W3 -- and that universal is false as written, independently of the count.** `8 or 32` is contradicted by **three**
  rate-network artifacts carrying `fisher_batches` 128 -- the same three `e270` found -- so the sentence is wrong twice
  over: about which runs it covers and about what those runs used. **Falsifier**: no rate-network artifact outside
  `8 or 32`.

**What it cannot do**: the patterns are the module's and a count written another way is invisible -- the module prints
how many counts it extracted and which noun forms it looked for; `rate-network` is defined by a configuration
signature (a `methods` list with `iters` and `circuit_size`), so an artifact of that line written without those keys
counts as something else; the corpus on disk is the whole input, so a count the paper states about the *findings*
corpus or the *plan* is checked only where the module names it; nothing here says a count was wrong when it was
written, only that it is not what it was; and the correction a reader needs is a scope (which runs, which corpus) and
not a bigger number.
"""

from __future__ import annotations

import argparse
import glob
import json
import re
import sys
from pathlib import Path

from clfly.bench.artifacts import write_json

PAPER = Path("docs/paper/clfly-v1.md")
FINDINGS = Path("docs/findings")
#: The forms this audit extracts, and the noun each one is checked against.
PATTERNS = (
    (re.compile(r"\b(\d+) of ([\d,]+) (artifacts|findings|drawings|families|matrices)\b"), "of"),
    (re.compile(r"\bthe (\d+) (rate-network runs|arms|rungs|figures|drawings|families)\b"), "the"),
    (re.compile(r"\bevery one of the (\d+)\b"), "every"),
)
#: The property the paper's rate-network universal states: every one used 8 or 32 Fisher batches.
EXPECTED_FISHER = (8, 32)
CLAIMS = (
    ("W1", "every count the paper states about the corpus is below today's corpus",
     "Each extracted count is smaller than what its noun covers on disk now",
     "falsifier: a stated count above the corpus's own"),
    ("W2", "and at least one universal is quantified over such a count",
     "A universal sentence of the paper names a count that is under half of what its noun now covers",
     "falsifier: no universal over a count, or the share above a half"),
    ("W3", "and that universal is false as written, independently of the count",
     "A rate-network artifact carries a Fisher batch count outside 8 and 32",
     "falsifier: none does"),
)


def load(path):
    p = Path(path)
    if not p.exists():
        return None
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def rate_network(root: Path = Path("runs")) -> list[dict]:
    """The line's artifacts, by its configuration signature, with the fields the universal is about."""
    out = []
    for path in sorted(glob.glob(str(root / "*.json"))):
        try:
            d = json.loads(Path(path).read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError, OSError):
            continue
        cfg = (d or {}).get("config") or {}
        if "methods" in cfg and "iters" in cfg and "circuit_size" in cfg:
            out.append({"artifact": Path(path).name, "fisher_batches": cfg.get("fisher_batches"),
                        "methods": cfg.get("methods")})
    return out


def counts(paper_text: str) -> list[dict]:
    """Every count the patterns find, with the sentence it sits in."""
    out = []
    for pattern, form in PATTERNS:
        for m in pattern.finditer(paper_text):
            start = paper_text.rfind(".", 0, m.start()) + 1
            end = paper_text.find(".", m.end())
            sentence = paper_text[start:end if end > 0 else len(paper_text)].strip()
            noun = m.group(3) if form == "of" else (m.group(2) if form == "the" else None)
            if noun is None:                     # `every one of the N` names its noun in the sentence
                noun = next((n for n in ("rate-network runs", "artifacts", "findings", "arms", "rungs")
                             if n in sentence), None)
            out.append({"form": form, "matched": m.group(0),
                        "numbers": [g for g in m.groups() if g and g.isdigit()],
                        "noun": noun, "sentence": sentence[:240]})
    return out


def corpora(root: Path = Path("runs")) -> dict:
    rn = rate_network(root)
    return {"artifacts": len(glob.glob(str(root / "*.json"))), "rate-network runs": len(rn),
            "findings": len(glob.glob(str(FINDINGS / "*.md"))), "_rate_network": rn}


def judge(found: list[dict], have: dict) -> list[dict]:
    out: list[dict] = []
    mapped = [c for c in found if c["noun"] in have]
    if not mapped:
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- no count mapped to a corpus noun"} for c in CLAIMS]

    over = [(c["statement"], c["stated"], have[c["noun"]]) for c in mapped if c["stated"] > have[c["noun"]]]
    out.append({"id": "W1", "measured": "; ".join(f"{c['statement']}: the paper says {c['stated']}, the corpus has "
                                                  f"{have[c['noun']]} ({have[c['noun']] / c['stated']:.2f}x)"
                                                  for c in sorted(mapped, key=lambda c: -c["stated"])),
                "verdict": "MET -- every stated count is below today's corpus" if not over else
                           f"FALSIFIER FIRED -- stated above the corpus: {over}"})

    universals = [c for c in mapped if c["form"] == "every"]
    minority = [c for c in universals if c["stated"] < have[c["noun"]] / 2]
    out.append({"id": "W2", "measured": "; ".join(f"{c['statement']} names {c['stated']} of "
                                                  f"{have[c['noun']]} ({100 * c['stated'] / have[c['noun']]:.0f}%)"
                                                  for c in universals) or "no universal over a count",
                "verdict": "MET -- a universal of the paper names a minority of what its noun covers"
                if minority else "FALSIFIER FIRED -- no universal names a minority"})

    rn = have.get("_rate_network") or []
    odd = [r for r in rn if r["fisher_batches"] not in EXPECTED_FISHER]
    other = [r for r in odd if r["fisher_batches"] is not None]
    unrecorded = [r for r in odd if r["fisher_batches"] is None]
    out.append({"id": "W3", "measured": f"{len(rn)} rate-network artifacts; {len(other)} use a Fisher batch count "
                                        f"outside {EXPECTED_FISHER} and {len(unrecorded)} leave the field unrecorded"
                                        + (" -- " + ", ".join(f"{r['artifact']} ({r['fisher_batches']})" for r in odd)
                                           if odd else ""),
                "verdict": "MET -- the universal's clause is false as written" if odd else
                           "FALSIFIER FIRED -- every rate-network artifact uses 8 or 32"}),
    return out


def report(found: list[dict], have: dict) -> int:
    text = PAPER.read_text(encoding="utf-8") if PAPER.exists() else ""
    print("== the counts the paper states, against the corpus ==")
    print(f"   {'form':7} {'matched':44} {'noun':18} {'now':>6}")
    for c in found:
        now = have.get(c["noun"])
        print(f"   {c['form']:7} {c['matched'][:44]:44} {str(c['noun']):18} {str(now):>6}"
              + (f"   ({now / c['stated']:.2f}x)" if now and c["stated"] else ""))
    print(f"\n   counts extracted: {len(found)}; mapped to a corpus noun: "
          f"{sum(1 for c in found if c['noun'] in have)}")
    print(f"   the corpus: " + ", ".join(f"{k} {v}" for k, v in have.items() if not k.startswith("_")))

    m = judge(found, have)
    print("\n== the registered claims, W1-W3 ==")
    for c, row in zip(CLAIMS, m):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {c[2]}")
        print(f"          and its {c[3]}")
    print("\n   (a count is not a scope: the corpus grows, so a number that was the whole record becomes a share of")
    print("    it, and every universal quantified over that number narrows with it while the sentence still reads as a")
    print("    statement about all of it)")
    return sum("REFUSED" in row["verdict"] for row in m)


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
    text = PAPER.read_text(encoding="utf-8")
    have = corpora(args.runs)

    #: the count each count names is read from the sentence, so a sentence's numbers are what a reader would take
    counts_of = []
    for c in counts(text):
        nums = [int(n.replace(",", "")) for n in c["numbers"]]
        if not nums:
            continue
        c["stated"] = max(nums)
        c["statement"] = c["matched"]
        counts_of.append(c)
    if args.json_out:
        write_json(args.json_out, {"paper": str(PAPER), "patterns": [p.pattern for p, _ in PATTERNS],
                                   "counts": counts_of,
                                   "corpora": {k: v for k, v in have.items() if not k.startswith("_")},
                                   "claims": judge(counts_of, have)})
        print(f"wrote {args.json_out}")
    return report(counts_of, have)


if __name__ == "__main__":
    sys.exit(main())
