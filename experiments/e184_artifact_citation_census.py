"""E184 -- the other direction of the provenance audit: which artifacts can a later reader find BY NAME?

`e97` asks whether every artifact a **document** cites exists. `e105` asks whether a table's numbers are located by
the cells around them. `e127` asks whether a **row's** claim about the work matches the disk. None of them asks the
reverse of `e97`: is every file in `runs/` named by some document? The plan's own rule 8 is the reason it matters --
*"check that the artifact will contain the field the question needs"* -- and its complement is that a number whose
artifact cannot be found by name cannot be re-checked at all, which is the state `e97` calls *unfalsifiable by
construction*.

**A literal substring scan answers this question wrongly, and this script was written by measuring how wrongly.**
It reports **156** of the 376 files as never named. Two corrections, both of them measured classes rather than
taste, take that to **1**:

1. **Brace shorthand.** Findings cite `runs/e74_drawsd_min{8,16,128}.json` and
   `runs/e147_r32_frozenbias_ewc_lam3e-{3,4}.json`. A literal test for `e74_drawsd_min128.json` cannot see the
   shorthand that names it, and **34** of the corpus's files are cited *only* this way -- they are the class that
   makes the naive count wrong by 34 rows.
2. **The sibling test.** For the rest (`e104_frozen_r128_frozen.json`, say), no file name may appear while a
   *sibling* of the same experiment does, or the experiment's own report. That is a weaker statement -- the
   experiment was written up, this particular payload was not named -- and it is reported as its own class rather
   than folded into either extreme.

What is left after both is the number this audit exists to produce, and it is **printed with the two weaker classes
beside it**, because "1 file is un-named" and "every claim is traceable by name" are different statements.

    python -m experiments.e184_artifact_citation_census
    python -m experiments.e184_artifact_citation_census --list            # the un-named and sibling-only files
    python -m experiments.e184_artifact_citation_census --include-code    # let scripts' docstrings cite too
"""

from __future__ import annotations

import argparse
import collections
import glob
import json
import re
from pathlib import Path

RUNS = Path("runs")
DOC_GLOBS = ("docs/**/*.md", "README.md", "AGENTS.md")
#: a digit run in a name may be one member of a brace group in the citing text
DIGITS_RE = re.compile(r"[0-9]+")
#: a brace group whose members are all short: the table's own shorthands for a set of arms
BRACE_RE = re.compile(r"\{[^{}]*,[^{}]*\}")
PREFIX_RE = re.compile(r"(e[0-9]+)")


def corpus(docs_globs=DOC_GLOBS, include_code: bool = False) -> tuple[str, int]:
    """Every document's text, concatenated, and how many files went into it.

    Documents only by default: a later reader looks in the findings and the plan. `--include-code` adds `*.py`, and
    it is a *robustness* switch rather than the default, because a runner's docstring naming its own output is a
    weaker form of citation than a write-up -- and because the point of the audit is what a reader can find, not
    what the code remembers about itself.
    """
    paths = [Path(p) for g in docs_globs for p in glob.glob(g, recursive=True)]
    paths = [p for p in paths if p.is_file()]
    if include_code:
        paths += [p for p in Path("experiments").glob("*.py") if p.is_file()]
    return "\n".join(p.read_text(encoding="utf-8", errors="replace") for p in sorted(set(paths))), len(set(paths))


def shorthand_pattern(name: str) -> re.Pattern:
    """The name, with every digit run allowed to sit inside a brace group that lists it.

    `e74_drawsd_min128.json` becomes `e74_drawsd_min(?:\\{[\\d,\\s]*128[\\d,\\s]*\\}|128)\\.json`, so the text
    `e74_drawsd_min{8,16,128}.json` matches while `e74_drawsd_min{8,16}.json` does not. The member list is left
    loose on purpose: requiring the group's other members to be names in the corpus would make the citation
    checkable only after the citation convention is known, which is the thing being measured.
    """
    def repl(m: re.Match) -> str:
        d = m.group(0)
        return r"(?:\{[\d,\s]*" + d + r"[\d,\s]*\}|" + d + r")"
    return re.compile(DIGITS_RE.sub(repl, re.escape(name)))


def prefix(name: str) -> str:
    m = PREFIX_RE.match(name)
    return m.group(1) if m else "?"


def has_config(d: object) -> bool:
    """Whether a payload's `config` is `vars(args)` -- the shape `e163`, `e172` and `e182` read.

    The distinction is worth counting because those three audits are config-based, and the number of files they
    cannot see is the scope of every "all artifacts" claim any of them makes.
    """
    return isinstance(d, dict) and isinstance(d.get("config"), dict)


def config_signature(path: Path) -> str | None:
    """A payload's `config` minus `json_out` -- the identity of the RUN rather than of the file.

    Used for the one question the sibling test cannot answer: is an un-named payload a *duplicate* of a named one
    (the same configuration written twice, which a citation of either covers), or the only file that carries that
    configuration at all? Two of the 117 un-named runs have an identically configured named twin; 115 do not.
    """
    d = _load(path)
    if not has_config(d):
        return None
    c = dict(d["config"])
    c.pop("json_out", None)
    return json.dumps(c, sort_keys=True)


def audit(runs_dir: Path = RUNS, docs_globs=DOC_GLOBS, include_code: bool = False) -> dict:
    text, n_docs = corpus(docs_globs, include_code)
    names = sorted(Path(p).name for p in glob.glob(str(runs_dir / "*.json")))
    configs, reports = 0, 0
    for n in names:
        d = _load(runs_dir / n)
        configs += has_config(d)
        reports += not has_config(d)

    literal = [n for n in names if n in text]
    patterns = {n: shorthand_pattern(n) for n in names}
    shorthand_only = [n for n in names if n not in literal and patterns[n].search(text)]
    cited = set(literal) | set(shorthand_only)
    cited_prefixes = {prefix(n) for n in cited}
    sibling_only = [n for n in names if n not in cited and prefix(n) in cited_prefixes]
    unnamed = [n for n in names if n not in cited and prefix(n) not in cited_prefixes]
    naive_uncited = len(shorthand_only) + len(sibling_only) + len(unnamed)

    # the second-order question about the weakest class: a duplicate of a named run, or a distinct configuration?
    named_sigs = {config_signature(runs_dir / n) for n in literal
                  if config_signature(runs_dir / n) is not None}
    sib_runs = [n for n in sibling_only if config_signature(runs_dir / n) is not None]
    twins = [n for n in sib_runs if config_signature(runs_dir / n) in named_sigs]
    # and what IS cited for the experiments with the most un-named members: the citation's FORM, printed so a
    # reader can see that it is an aggregate report or a representative member of a sweep rather than nothing
    per_prefix: dict[str, dict] = {}
    for n in sibling_only:
        per_prefix.setdefault(prefix(n), {"sibling_only": 0, "cited": []})["sibling_only"] += 1
    for n in literal:
        if prefix(n) in per_prefix:
            per_prefix[prefix(n)]["cited"].append(n)
    top = dict(sorted(per_prefix.items(), key=lambda kv: -kv[1]["sibling_only"])[:6])
    return {"documents_scanned": n_docs, "corpus_chars": len(text),
            "artifacts": len(names), "runs_with_a_config": configs,
            "reports_without_a_config": reports,
            "cited_by_full_name": len(literal), "cited_only_by_a_shorthand": len(shorthand_only),
            "no_file_cited_but_a_sibling_is": len(sibling_only), "no_file_cited_at_all": len(unnamed),
            "uncited_before_expanding_shorthands": naive_uncited,
            "unnamed": unnamed, "unnamed_with_a_config": [n for n in unnamed if _config_ok(runs_dir / n)],
            "sibling_only": sibling_only, "shorthand_only": shorthand_only,
            "sibling_runs_with_a_named_identical_twin": twins,
            "sibling_runs_with_distinct_configurations": len(set(config_signature(runs_dir / n)
                                                                  for n in sib_runs if n not in twins)),
            "citation_form_of_the_experiments_with_most_un_named_members": top,
            "brace_groups_in_the_corpus": len(BRACE_RE.findall(text)),
            "unreadable": [n for n in names if _bad(runs_dir / n)]}


def _load(p: Path):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def _bad(p: Path) -> bool:
    return _load(p) is None


def _config_ok(p: Path) -> bool:
    """Whether this un-named file is a RUN -- one of the payloads the audits call an artifact.

    The exit code asks about those and not about the audits' own report files: an un-named report is explainable by
    its plan row naming the *script*, while an un-named run with a config is a result nobody has written up. A count
    that mixed them would make this check fire on its own output.
    """
    return has_config(_load(p))


def report(res: dict, listing: bool = False) -> int:
    print(f"   documents scanned                    : {res['documents_scanned']}"
          f" ({res['corpus_chars']:,} chars, {res['brace_groups_in_the_corpus']} brace groups)")
    print(f"   artifacts in runs/                   : {res['artifacts']}")
    print(f"        carrying a `config` (= vars(args), what e163/e172/e182 read) : {res['runs_with_a_config']}")
    print(f"        audit reports with no config, i.e. invisible to those three : "
          f"{res['reports_without_a_config']}")
    print(f"   cited by full name                   : {res['cited_by_full_name']}")
    print(f"   cited ONLY through a brace shorthand : {res['cited_only_by_a_shorthand']}"
          f"   <- the naive scan calls all of these uncited")
    print(f"   in or out of docs?                   : the naive count is "
          f"{res['uncited_before_expanding_shorthands']} uncited, "
          f"and it is wrong by {res['cited_only_by_a_shorthand']}")
    print(f"   no file of the experiment cited, a sibling is : {res['no_file_cited_but_a_sibling_is']}")
    print(f"   NO file of the experiment cited anywhere      : {res['no_file_cited_at_all']}")
    for n in res["unnamed"]:
        print(f"        {n}")
    print(f"   of which RUNS (they carry a config), i.e. results nobody wrote up : "
          f"{len(res['unnamed_with_a_config'])}")
    for n in res["unnamed_with_a_config"]:
        print(f"        {n}")
    print(f"   the weakest class, sharpened: of the un-named RUNS, "
          f"{len(res['sibling_runs_with_a_named_identical_twin'])} are duplicates of a named run (the same config "
          f"written twice) and {res['sibling_runs_with_distinct_configurations']} carry a configuration that no "
          f"named file carries")
    print("   and what IS cited for the experiments with the most un-named members: the citation's FORM")
    for pref, d in res["citation_form_of_the_experiments_with_most_un_named_members"].items():
        print(f"        {pref}: {d['sibling_only']} un-named members, cited -> {', '.join(d['cited'][:3])}")
    if listing:
        print("   cited only by a shorthand:")
        for n in res["shorthand_only"]:
            print(f"        {n}")
        print("   no file cited, a sibling is (first 20):")
        for n in res["sibling_only"][:20]:
            print(f"        {n}")
    if res["unreadable"]:
        print(f"   unreadable as JSON: {res['unreadable']}")
    return len(res["unnamed_with_a_config"])


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--runs", type=Path, default=RUNS)
    p.add_argument("--include-code", action="store_true",
                   help="let `experiments/*.py` docstrings count as citations too (a robustness check)")
    p.add_argument("--list", action="store_true", help="print the shorthand-only and sibling-only files")
    p.add_argument("--json-out", type=Path, default=None)
    args = p.parse_args(argv)

    res = audit(args.runs, include_code=args.include_code)
    n = report(res, args.list)
    if args.json_out:
        from clfly.bench.artifacts import write_json
        write_json(args.json_out, res)
        print(f"wrote {args.json_out}")
    return 1 if n else 0


if __name__ == "__main__":
    raise SystemExit(main())
