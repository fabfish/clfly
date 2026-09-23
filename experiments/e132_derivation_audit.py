"""E132 -- rule 34 as a *check* rather than a habit: recompute the stated prediction from the stated input.

Rule 34 was written from `e128`, where §4.2 said *"85% predicted a 2.6× fall"* and **2.6× never followed from
85%** — it needed 94.7%, the accuracy `variance_fraction` of an artifact at a different read-out. One fire later
the same discipline found a second instance: `e120`'s registration derived **ρ ≈ 0.14** from two sd's through a
formula it named in the same paragraph, and the formula gives **0.246** on its own rounded input and **0.364** on
the artifacts' values. **Two defects in three checks is a high enough yield that the check should be code**,
which is the line rule 22 already drew for the programme table: *"the check is one line and needs no artifacts"*
— and it was performed by hand for two days until it was made mechanical.

    python -m experiments.e132_derivation_audit                      # every document under docs/
    python -m experiments.e132_derivation_audit --show-unchecked     # plus the lines it cannot evaluate

**Two formula families are checked by arithmetic**, because they are the ones this corpus actually uses:

1. **A removable share implies an sd fall.** `<f>% predicted a <Y>× fall` must satisfy
   `Y = 1/sqrt(0.1·f + 1 − f)`: a tenfold test set divides the removable variance by ten and leaves the rest.
   This is the family `e128`'s `2.6×` belongs to.
2. **A σ reduction at a stated sem implies a draw sd.** `<A>σ -> <B>σ at a seed sem of <s> implies an assumed
   draw sd of <d>` must satisfy `d = s·sqrt((A/B)² − 1)`, because a single-draw contrast's uncertainty is
   `sqrt(sem² + draw²)`. This family's one instance is **correct** (`e129`'s check: 1.031e-3 against a stated
   1.028e-3), which is the useful half of a checker's record.

**Everything else is enumerated rather than checked**, and the counts are printed, because a checker that
silently covers part of its subject looks like coverage: the script lists the paragraphs containing `implies a`,
`Solving for`, `predicts a` and `would give a` beside two or more numbers, so the next pass knows where to look.
**It cannot check a derivation whose formula the sentence does not name** — `e128`'s `2.6×` was one, and it was
caught by recomputing by hand from the *clause before it*.

## Three ways this checker was wrong before it was right, and each is a way prose defeats a checker

- **It read lines, not sentences.** The derivation it exists to check wraps across two lines
  (`... implies an assumed draw sd of` / `**1.028e-3**, ...`), so the first version **found nothing to check
  while the corpus held a derivation it could evaluate**. It now joins each paragraph.
- **It reported three already-corrected quotations as defects.** This project's convention is to leave a wrong
  sentence standing and correct it after — often in a `>` blockquote below — so a same-line test is not enough.
  It now looks five paragraphs ahead. **That lookahead is also an evasion route**: a document could hide a live
  defect by writing a correction marker near it, and that hole is closed by reading rather than by this script.
  The skipped count is printed so the exclusion is visible rather than silent.
- **Its own report was unreadable** until the failures were printed with their inputs, the formula's answer and
  the claimed value on adjacent lines, which is the form that makes a flag actionable rather than a diagnosis.
"""

from __future__ import annotations

import argparse
import math
import re
from pathlib import Path

# 1. "85% predicted a 2.6x fall" -- f% of the variance removable, a tenfold test set
SHARE_RE = re.compile(r"(\d+(?:\.\d+)?)\s*%\s*predicted\s+an?\s*\*{0,2}(\d+(?:\.\d+)?)\s*[×x]")
# 2. "15.53 sigma -> 4.47 sigma at a seed sem of 0.00031 implies an assumed draw sd of 1.028e-3"
DRAW_RE = re.compile(r"(\d+(?:\.\d+)?)\s*σ\s*(?:→|->)\s*(\d+(?:\.\d+)?)\s*σ\s*at a\s*(?:seed\s+)?sem of\s*"
                     r"([\d.]+(?:e-?\d+)?)\s*implies an assumed draw sd of\s*\*{0,2}([\d.]+(?:e-?\d+)?)")
# candidates that carry a derivation the script cannot evaluate
UNCHECKED = ("implies a", "implies an", "Solving for", "solving for", "predicts a", "would give a",
             "Solving the", "solving the")
# markers of the quote-then-correct convention
# The exclusion set is EMPIRICAL and grew with the corpus: a fourth class appeared the moment this fire
# summarised its own findings in a table that quotes a claim beside the verdict "wrong", with no dated marker
# anywhere. Each addition is also a wider evasion route, which is why the skip count is printed.
CORRECTION_MARKERS = ("repaired", "wrong", "corrected", "Corrected", "should be", "not what",
                      "amended", "Amended", "qualifies", "superseded", "never followed",
                      "does not follow", "doesn't follow", "out by", "unreproducible",
                      "not reproducible", "inconsistent")
LOOKAHEAD = 5


def paragraphs(lines: list[str]) -> list[tuple[int, str, bool]]:
    """``(first_line_number, joined_text, is_blockquote)`` per paragraph, so a WRAPPED sentence is one string.

    The blockquote flag is what makes the correction exclusion precise: this project's convention is to leave a
    wrong sentence standing and put a dated correction **immediately after it as a `>` blockquote**, so that is
    what a marker should be looked for in. A lookahead over ordinary paragraphs reached a correction five
    paragraphs away about a *different* figure and silently skipped a correct derivation -- the false-negative
    side of the same exclusion, and it cost the checker its only real subject.
    """
    out: list[tuple[int, str, bool]] = []
    start, buf, quote = 1, [], False
    for n, line in enumerate(lines, 1):
        if line.strip():
            if not buf:
                start, quote = n, line.lstrip().startswith(">")
            buf.append(line.lstrip().lstrip(">").strip())
        elif buf:
            out.append((start, " ".join(buf), quote))
            buf = []
    if buf:
        out.append((start, " ".join(buf), quote))
    return out


def carries_correction(paras: list[tuple[int, str, bool]], i: int) -> bool:
    """Is paragraph ``i`` part of a quote-then-correct pair?

    A marker in the paragraph itself, or in the **next blockquote** -- which is the convention's form. The
    lookahead is bounded to one paragraph and restricted to blockquotes, because widening it skipped a correct
    derivation whose section happened to contain the word "corrected" further down.
    """
    if any(m in paras[i][1] for m in CORRECTION_MARKERS):
        return True
    if i + 1 < len(paras) and paras[i + 1][2]:
        return any(m in paras[i + 1][1] for m in CORRECTION_MARKERS)
    return False


def share_sd_fall(fraction: float) -> float:
    """The sd fall a tenfold test set gives when `fraction` of the variance is removable."""
    return 1.0 / math.sqrt(0.1 * fraction + (1.0 - fraction))


def implied_draw_sd(sigma_single: float, sigma_corrected: float, seed_sem: float) -> float:
    """The draw sd that would inflate a seed-only sem into the published σ."""
    ratio = sigma_single / sigma_corrected
    return seed_sem * math.sqrt(max(ratio * ratio - 1.0, 0.0))


def audit(path: Path) -> dict:
    lines = path.read_text(encoding="utf-8").splitlines()
    paras = paragraphs(lines)
    checks, unchecked, skipped = [], [], []
    for i, (start, text, _q) in enumerate(paras):
        if carries_correction(paras, i):
            if SHARE_RE.search(text) or DRAW_RE.search(text):
                skipped.append({"line": start, "text": text[:110].encode("ascii", "replace").decode()})
            continue
        for m in SHARE_RE.finditer(text):
            f, claimed = float(m.group(1)) / 100.0, float(m.group(2))
            expected = share_sd_fall(f)
            checks.append({"line": start, "family": "share -> sd fall", "inputs": {"share": f},
                           "claimed": claimed, "expected": expected,
                           "agrees": abs(claimed - expected) <= 0.01 * max(expected, 1.0),
                           "text": text[:110].encode("ascii", "replace").decode()})
        for m in DRAW_RE.finditer(text):
            a, b = float(m.group(1)), float(m.group(2))
            sem, claimed = float(m.group(3)), float(m.group(4))
            expected = implied_draw_sd(a, b, sem)
            checks.append({"line": start, "family": "sigma reduction -> draw sd",
                           "inputs": {"sigma_single": a, "sigma_corrected": b, "seed_sem": sem},
                           "claimed": claimed, "expected": expected,
                           "agrees": abs(claimed - expected) <= 0.01 * max(expected, 1e-9),
                           "text": text[:110].encode("ascii", "replace").decode()})
        low = text.lower()
        if any(u.lower() in low for u in UNCHECKED) and len(re.findall(r"\d", text)) >= 2:
            unchecked.append({"line": start, "text": text[:110].encode("ascii", "replace").decode()})
    return {"path": str(path), "checks": checks, "unchecked": unchecked, "skipped_as_corrected": skipped}


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--paths", type=Path, nargs="*", default=None)
    p.add_argument("--show-unchecked", action="store_true",
                   help="list the derivation-bearing paragraphs whose formula the script cannot evaluate")
    p.add_argument("--json-out", type=Path, default=None)
    args = p.parse_args(argv)

    paths = args.paths or ([Path("docs/paper/clfly-v1.md"), Path("docs/research_plan.md")]
                           + sorted(Path("docs/findings").glob("*.md")))
    n_checked = n_agree = n_unchecked = n_skipped = 0
    rows, failures = [], []
    for path in paths:
        if not path.is_file():
            continue
        res = audit(path)
        rows.append(res)
        n_unchecked += len(res["unchecked"])
        n_skipped += len(res["skipped_as_corrected"])
        for c in res["checks"]:
            n_checked += 1
            if c["agrees"]:
                n_agree += 1
            else:
                failures.append((path, c))
    for path, c in failures:
        print(f"== {path} ==")
        print(f"   line {c['line']:5} [{c['family']}] inputs {c['inputs']}")
        print(f"         claimed {c['claimed']:.4g}   the formula gives {c['expected']:.4g}")
        print(f"         {c['text']}")
    if args.show_unchecked:
        print("\n-- enumerated but NOT checked (the formula is not named in the sentence) --")
        for res in rows:
            for u in res["unchecked"]:
                print(f"   {Path(res['path']).name:52} line {u['line']:5}  {u['text']}")
    print(f"\ndocuments                            : {len(rows)}")
    print(f"derivations checked by arithmetic    : {n_checked}")
    print(f"  ... that agree                     : {n_agree}")
    print(f"  ... that do NOT                    : {n_checked - n_agree}")
    print(f"derivation-bearing paragraphs NOT checked : {n_unchecked}")
    print(f"candidate paragraphs skipped as already-corrected : {n_skipped}")
    print("NOTE: the skip is the quote-then-correct convention AND a way to hide a live defect by writing a"
          "\n      correction marker near it; the count is printed so the exclusion is visible, not silent.")
    if args.json_out:
        from clfly.bench.artifacts import write_json
        write_json(args.json_out, {"checked": n_checked, "agree": n_agree, "unchecked": n_unchecked,
                                   "skipped": n_skipped,
                                   "failures": [{"path": str(p), **c} for p, c in failures], "rows": rows})
        print(f"wrote {args.json_out}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
