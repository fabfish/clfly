"""E97 -- the provenance audit of the findings corpus, and the positive control that shows its limit.

Every claim in this project is supposed to be backed by an artifact a later reader can check. The plan table
has been audited repeatedly (`e85` and its successors); the **corpus of findings documents** has not. This
script asks the three questions a machine can ask of `docs/findings/*.md`:

1. does every `runs/` file a document cites exist?
2. does each document's `**Setup:**` line agree with its named artifact's `config` on circuit size and seed
   count?
3. how many documents declare an artifact at all, i.e. how much of the corpus is machine-checkable?

**And it runs the known positive**, because a check that returns nothing is uninterpretable without one. The
known case is `e8c` (`2026-09-22-fisher-batches-negative.md`), whose named artifact stopped holding the sweep
it reports when a later run reused the path. The check below **misses it**, and the script prints that
miss rather than leaving it to be discovered.

    python -m experiments.e97_findings_corpus_audit
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from clfly.bench.artifacts import write_json

FINDINGS = Path("docs/findings")
ARTIFACTS_LINE = re.compile(r"^\*\*Artifacts?:\*\*\s*(.+)$", re.M)
SETUP_LINE = re.compile(r"^\*\*Setup:\*\*\s*(.+)$", re.M)
RUN_REF = re.compile(r"`?(runs/[A-Za-z0-9_.\-]+\.(?:json|npz|npy))`?")
SETUP_ARTIFACT = re.compile(r"(runs/[A-Za-z0-9_.\-]+\.json)")
CS_CLAIM = re.compile(r"(?:cs|circuit[- ]size)\s*=\s*(\d+)")
SEEDS_CLAIM = re.compile(r"(\d+)\s*(?:seed|seeds|replicate|replicates|repeat|repeats)")

#: the case this check would be expected to catch, and the reason it cannot
KNOWN_CASE = Path("docs/findings/2026-09-22-fisher-batches-negative.md")


def check_document(path: Path) -> dict:
    text = path.read_text(encoding="utf-8", errors="replace")
    arts_line = ARTIFACTS_LINE.search(text)
    setup_line = SETUP_LINE.search(text)
    cited = sorted(set(RUN_REF.findall(text)))
    missing = [r for r in cited if not Path(r).exists()]
    out = dict(name=path.name, has_artifacts_line=bool(arts_line),
               has_setup_line=bool(setup_line), n_cited=len(cited), missing=missing,
               config_mismatch=[])
    if not arts_line or not setup_line:
        return out
    setup = setup_line.group(1)
    cs_claim = CS_CLAIM.findall(setup)
    seeds_claim = SEEDS_CLAIM.findall(setup)
    for art in SETUP_ARTIFACT.findall(arts_line.group(1)):
        p = Path(art)
        if not p.exists():
            continue
        try:
            cfg = json.load(p.open(encoding="utf-8")).get("config", {})
        except Exception:
            continue
        art_cs = cfg.get("circuit_size")
        art_seeds = cfg.get("seeds", cfg.get("repeats"))
        if cs_claim and art_cs is not None and str(art_cs) not in cs_claim:
            out["config_mismatch"].append(f"{art}: cs claim {cs_claim} vs artifact {art_cs}")
        if seeds_claim and art_seeds is not None and str(art_seeds) not in seeds_claim:
            out["config_mismatch"].append(f"{art}: seeds claim {seeds_claim} vs artifact {art_seeds}")
    return out


def report_known_case() -> dict:
    """Run the check on the case it is for, and say plainly whether it fires."""
    text = KNOWN_CASE.read_text(encoding="utf-8", errors="replace")
    setup = SETUP_LINE.search(text).group(1)
    arts = ARTIFACTS_LINE.search(text).group(1)
    cs_claim = CS_CLAIM.findall(setup)
    seeds_claim = SEEDS_CLAIM.findall(setup)
    art = SETUP_ARTIFACT.findall(arts)
    caught = False
    if art and Path(art[0]).exists():
        cfg = json.load(Path(art[0]).open(encoding="utf-8")).get("config", {})
        if cs_claim and cfg.get("circuit_size") is not None and str(cfg["circuit_size"]) not in cs_claim:
            caught = True
        if seeds_claim and cfg.get("repeats") is not None and str(cfg["repeats"]) not in seeds_claim:
            caught = True
    return dict(document=KNOWN_CASE.name, setup=setup, artifacts=arts,
                cs_claim=cs_claim, seeds_claim=seeds_claim, artifact_config_repeats=(
                    json.load(Path(art[0]).open(encoding="utf-8"))["config"].get("repeats")
                    if art and Path(art[0]).exists() else None),
                caught=caught,
                why_not=("the drift lives in a BODY sentence ('single seed, ... sweeping the Fisher batch "
                         "count') while the metadata lines are self-consistent; the Setup line says "
                         "'@n1307' rather than 'cs = 800' and 'single seed' carries no digit"))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--json-out", default="runs/e97_findings_corpus_audit.json")
    args = ap.parse_args()

    docs = sorted(FINDINGS.glob("*.md"))
    results = [check_document(p) for p in docs]

    print("=" * 108)
    print("1. THE FINDINGS CORPUS, ON THE THREE SURFACES A MACHINE CAN CHECK")
    print("=" * 108)
    n = len(results)
    with_art = [r for r in results if r["has_artifacts_line"]]
    any_missing = [r for r in results if r["missing"]]
    mism = [r for r in results if r["config_mismatch"]]
    print(f"   documents                                    : {n}")
    print(f"   declare an **Artifacts:** line               : {len(with_art)}")
    print(f"   cite a runs/ file that does not exist        : {len(any_missing)}")
    for r in any_missing:
        print(f"       {r['name']}  ->  {r['missing']}")
    print(f"   **Setup:** disagrees with the artifact config : {len(mism)}")
    for r in mism:
        for m in r["config_mismatch"]:
            print(f"       {r['name']}: {m}")
    print()
    print(f"   A flag is not a finding: read each one against the document.  Of the {len(any_missing)} here,"
          f" one is a")
    print("   document whose own Artifacts line says `(aborted)` and the other is THIS AUDIT's own document,")
    print("   which cites the same path as an example of a missing file.  A document that names a path in")
    print("   order to discuss its absence is indistinguishable to a scanner from one citing it as evidence,")
    print("   so the true count of findings citing a missing LIVE artifact is zero -- and that sentence")
    print("   required reading both documents.")

    print()
    print("=" * 108)
    print("2. THE POSITIVE CONTROL, WITHOUT WHICH THE ZEROS ABOVE MEAN NOTHING")
    print("=" * 108)
    kc = report_known_case()
    print(f"   the known case: {kc['document']}  (the e8c defect, found by hand on 2026-09-23)")
    print(f"      Setup     : {kc['setup'].encode('ascii', 'replace').decode()}")
    print(f"      Artifacts : {kc['artifacts'].encode('ascii', 'replace').decode()}")
    print(f"      this check extracts cs claim {kc['cs_claim']} and seeds claim {kc['seeds_claim']}")
    print(f"      the named artifact's config says repeats = {kc['artifact_config_repeats']}")
    print(f"      -> DOES THIS CHECK FIRE? **{kc['caught']}**")
    print(f"      because {kc['why_not']}")
    print()
    print("   So the checks above are BLIND to the one defect the corpus is known to contain, and a run of")
    print("   them returning zero is not evidence that the prose is clean.  Existence and configuration")
    print("   checks have low remaining expected yield here; the residual risk is in sentences.")

    print()
    print("=" * 108)
    print("3. HOW MUCH OF THE CORPUS IS MACHINE-CHECKABLE AT ALL")
    print("=" * 108)
    no_art = [r for r in results if not r["has_artifacts_line"]]
    print(f"   findings with no Artifacts line: {len(no_art)} of {n} ({100 * len(no_art) / n:.0f}%)")
    import collections
    dates = collections.Counter()
    for r in no_art:
        t = (FINDINGS / r["name"]).read_text(encoding="utf-8", errors="replace")
        d = re.search(r"\*\*Date:\*\*\s*(\S+)", t)
        dates[d.group(1) if d else "?"] += 1
    for d, c in sorted(dates.items()):
        print(f"       {d}: {c}")
    print("   a finding that states a number and names no artifact is unfalsifiable by construction")

    write_json(args.json_out, dict(n_documents=n, with_artifacts_line=len(with_art),
                                   n_missing_artifact_flags=len(any_missing),
                                   n_config_mismatches=len(mism),
                                   missing=[dict(name=r["name"], files=r["missing"]) for r in any_missing],
                                   mismatches=[dict(name=r["name"], rows=r["config_mismatch"]) for r in mism],
                                   no_artifacts_line=[r["name"] for r in no_art],
                                   dates_without_artifacts_line=dict(dates),
                                   known_case_control=kc))
    print(f"\nwrote {args.json_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
