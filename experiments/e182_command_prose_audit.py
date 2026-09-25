"""E182 -- the flags the programme table's commands state, checked against the configs of the artifacts they name.

`e163` derives a command *from* a `config`, and `e172` decides which runner could have written one. This is the
opposite arrow: the plan states a command **in prose**, the artifact named beside it carries the `config` the run
actually ran with, and the two can disagree. Nothing in this project has ever compared them, and the failure it
would catch is the one this project is most exposed to -- a row whose command text was edited after the run, or
copied from a different row, while its numbers stayed.

**The first hand pass over this question produced 24 checks and 9 "mismatches", and every one of the nine was the
checker's error, not the table's.** The mechanism is worth stating because it is the whole design of this script:
the hand pass took the flags from a **whole row** and compared them with **every artifact the row mentions**, so a
row that cites four artifacts for four different purposes had each fragment of its command matched against the
wrong three. The three classes it produced:

- **A placeholder read as a value.** `` `e3 --control-draws K` `` -- `K` is a variable, and the hand pass compared
  the string `K` (or, worse, swallowed the following prose) against an artifact's `3`.
- **A bare `store_true` flag paired with the next flag.** `` `--extra-bases --seeds 18` `` has one value in it, and
  the hand pass read `--extra-bases` as true-valued and `--seeds` as its value.
- **A flag attributed to the wrong artifact in the same row.** Nine rows name several artifacts; the hand pass
  compared `--fisher-batches 32` (the command of `e133`) against `e116_*`'s config, which says 8 because it is a
  different experiment that the same row cites for a different reason.

So the checker is built around **attribution**, not around flag parsing, and it refuses to check anything it cannot
attribute:

- **checkable**: the row's first cell names **exactly one** artifact -- by file name, or by a single `eNNN` label
  that resolves to exactly one file under `runs/` -- and states at least one flag. Only these are compared.
- **ambiguous**: the first cell names more than one artifact. Not checked, counted.
- **unattributed**: the first cell states flags but names no artifact it can resolve (the ordinary case: the cell
  names its *runner*, e.g. `` `e8_rate_network.py --lam 0.1 --repeats 16` ``, and the artifact appears only in the
  status column). **Not checked, counted** -- attributing a prose flag to "the artifact the row also mentions" is
  precisely the error that produced all nine false positives.
- **no flags**: the row states no flags at all.

Within a checkable row: values are compared by **numeric equivalence** (`3e-3` equals `0.003`), placeholders are
skipped as non-literal (`K`, `{8,16,48}`, `<path>`, `0..5`, `N`), a `store_true` flag is required to have no value
(its `store_true`-ness read from `e172`'s registry, not guessed), and a flag no runner in the repository defines is
counted as unknown rather than compared.

``--readout-census`` answers the second question this audit raised, and closes it. An earlier suspicion was that
some runner **rewrites** a config value before writing it (the plan said "read-out 0" for an artifact whose config
says `readout_size: 1307`). It does not: the artifact's own `readout` block agrees with the run-time rule in **all
60** artifacts that carry a block to check, and `0`, `1307` and an absent field are **three spellings of the same
run** -- the whole state. The census prints that, and the one thing that *is* fragile: `1307` is the *achieved*
neuron count of `--circuit-size 800`, and `--circuit-size` is a **soft** budget (the extractor keeps every cell type
and lands above the target), so the same literal `--readout-size 1307` means "the whole state" at circuit 800 and "a
draw of 1307 neurons" at any circuit that achieves more than 1307 -- and the achieved count is recorded in the
`circuit` name and nowhere else, which 4 of the 144 artifacts do not have.

    python -m experiments.e182_command_prose_audit
    python -m experiments.e182_command_prose_audit --json-out runs/e182_prose_audit.json
    python -m experiments.e182_command_prose_audit --readout-census
"""

from __future__ import annotations

import argparse
import collections
import glob
import json
import re
from pathlib import Path

from experiments.e127_programme_table_audit import programme_rows
from experiments.e172_parser_registry import parser_flags, registry

PLAN = Path("docs/research_plan.md")
RUNS = Path("runs")

#: an artifact's file name, with or without the `runs/` prefix the table writes when it is being registered
FILE_RE = re.compile(r"[A-Za-z0-9_./-]+\.json")
#: the programme's own label for a row's experiment; resolves to `runs/eNNN_*.json`
LABEL_RE = re.compile(r"(e[0-9]+)")
#: a long or short flag, as the commands in the table spell them
FLAG_RE = re.compile(r"--([a-z][a-z0-9-]*)")
#: a value that is a variable rather than a literal: `K`, `{8,16,48}`, `<path>`, `0..5`, `N`, `?`, `...`, `x`
PLACEHOLDER_RE = re.compile(r"^(?:[A-Z]$|\{.*\}|<.*>|.*\.\..*|\.\.\.|\?|x|\*)$")
#: a runner's file name, which must be removed before looking for `eNNN` labels: `e5_anisotropy_axis.py` starts
#: with `e5`, and the first version of this audit resolved it to the artifact `e5_anisotropy.json` and then
#: reported the row's `--seeds 12` as a mismatch against that artifact's `3`. A runner is not its experiment.
PY_RE = re.compile(r"[A-Za-z0-9_./-]+\.py")
#: a clause that names an artifact as a **referent** rather than as the row's own output -- L1097's `` `...`
#: against `e133`'s overlap-0.0 `naive` ``. The first version compared the command's `--input-overlap 1.0` with
#: `e133`'s `0.0` and called it a mismatch, which is the comparison the row is *making*, not an inconsistency.
COMPARISON_RE = re.compile(r"\b(?:against|vs\.?|versus|compared\s+(?:to|with))\b", re.IGNORECASE)
#: a flag, a braced or angled placeholder (kept whole so `{8,16,48}` is one token), or a run of non-space
TOKEN_RE = re.compile(r"--[a-z][a-z0-9-]*|\{[^}]*\}|<[^>]*>|\S+")


def artifact_names(runs_dir: Path = RUNS) -> dict:
    """Every artifact file name, and the index from an `eNNN` label to the files that carry it."""
    names = sorted(Path(p).name for p in glob.glob(str(runs_dir / "*.json")))
    by_label: dict[str, list[str]] = collections.defaultdict(list)
    for n in names:
        m = re.match(r"(e[0-9]+)", n)
        if m:
            by_label[m.group(1)].append(n)
    return {"names": set(names), "by_label": dict(by_label)}


def resolve(text: str, index: dict) -> tuple[list[str], int, int]:
    """The artifacts a piece of the table names, how many labels identify several files, and how many `.json`
    names the corpus does not have.

    Three ways the table names an artifact, and the second is the one that took three passes to see:

    - an explicit `*.json`, with or without the `runs/` prefix -- a row registering an artifact writes the bare
      name, "to be written as `e148_...json` under `runs/`";
    - a bare `eNNN` label, which identifies one file **only when exactly one file carries that prefix**;
    - and a runner's file name, which is **not** a reference to an artifact at all.

    A label that resolves to zero or to several files is *not* the same case, and the first version conflated them.
    The first failure of this audit was to count a zero-file label as unresolvable, which made the ordinary way a
    cell names its **runner** -- `e3` for `e3_basis_selection.py`, `e8` for `e8_rate_network.py` -- look like a
    reference that could not be resolved, and the row was skipped for a reason that was not true of it:

    - **zero files** -- the label names no artifact. Ignored here: a missing artifact is `e127`'s check A, which
      reads `runs/*.json` out of the row.
    - **several files** -- the label *is* an artifact reference and does not identify one. Returned as an
      *ambiguous label* rather than dropped, because dropping it is what made the hand pass read L1094 as a
      single-artifact row (it names `e140`, which is four files) and compare its five-method command with whichever
      file happened to survive.
    """
    scan = PY_RE.sub(" ", text)
    found: list[str] = []
    missing_files = 0
    for m in FILE_RE.finditer(scan):
        base = m.group(0).split("/")[-1]
        if base in index["names"]:
            if base not in found:
                found.append(base)
        else:
            missing_files += 1
    ambiguous = 0
    for label in sorted(set(LABEL_RE.findall(scan))):
        hits = index["by_label"].get(label, [])
        if len(hits) == 1 and hits[0] not in found:
            found.append(hits[0])
        elif len(hits) > 1:
            ambiguous += 1
    return found, ambiguous, missing_files


def bare(token: str) -> str:
    """A token with the table's punctuation removed, so `(e133)`, and `` `e133`, `` all read as `e133`."""
    return token.strip("`()[],;.")


def is_reference(token: str, index: dict) -> bool:
    """Whether this token names an artifact: a file the corpus has, or a label identifying exactly one file."""
    b = bare(token).split("/")[-1]
    if b in index["names"]:
        return True
    m = re.fullmatch(r"(e[0-9]+)", b)
    return bool(m and len(index["by_label"].get(m.group(1), [])) == 1)


def command_tokens(cell: str, index: dict) -> tuple[list[str], int, int]:
    """The tokens of the command the cell states, the tokens the cut discarded, and how many of those are flags.

    The command **ends where the cell first names an artifact**, unless that reference is itself a flag's value
    (`--json-out runs/x.json`). This is the table's own convention -- a row registering an artifact reads
    "..., its artifact to be written as `e148_....json` under `runs/`" -- and it is the third attribution rule this
    audit needed. Without it, L1046's cell is read as thirteen flags when it states nine and then *quotes* the
    three fields by which the derived command differs: the sentence "the derived command differs from the launched
    one in exactly three fields, `--circuit-size` (1500 -> 300), `--support` (150 -> 30) and `--json-out`" was
    parsed as a second command, and the audit reported the row's `--circuit-size` as both 300 and 1500.

    The count of **flags** in the discarded part is returned because the cut is a convention and not a guarantee: a
    cell that states its command after its artifact -- "`e9_ladder_d1874.json`, rerun as `--seeds 12`" -- has its
    flags silently unchecked, and a checker that does not say how often that happens is reporting its own scope as
    if it were the table's cleanliness.
    """
    toks = TOKEN_RE.findall(cell.replace("`", " "))
    cut = len(toks)
    for i, tok in enumerate(toks):
        if i and toks[i - 1].startswith("--"):
            continue                      # a flag's value, not the cell naming its own output
        if is_reference(tok, index):
            cut = i
            break
    lost = toks[cut:]
    return toks[:cut], len(lost), sum(1 for t in lost if t.startswith("--"))


def flag_pairs(tokens: list[str]) -> list[tuple[str, str | None]]:
    """Every flag in the tokens with the value they give it, `None` when they give none.

    A flag takes the next token as its value **only when that token is not itself a flag** -- the class-B error of
    the hand pass, which read `` `--extra-bases --seeds 18` `` as `--extra-bases` = `18`. Backticks are dropped
    before tokenising rather than matched as spans: the first version matched `` `[^`]+` `` as one token and so
    swallowed each command whole, finding **no flags at all in 136 of 138 rows** -- a checker reporting a clean
    table because it had stopped looking.
    """
    out: list[tuple[str, str | None]] = []
    for i, tok in enumerate(tokens):
        if not (tok.startswith("--") and len(tok) > 2):
            continue
        value = None
        if i + 1 < len(tokens) and not tokens[i + 1].startswith("--"):
            value = bare(tokens[i + 1])
        if value == "":
            value = None
        out.append((bare(tok)[2:], value))
    return out


def numerical(value) -> float | None:
    """A float for anything that reads as a number, `None` otherwise -- so `3e-3` equals `0.003`."""
    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    try:
        return float(str(value).strip().strip("`"))
    except ValueError:
        return None


def same(prose: str, config) -> bool:
    """Whether a value the table states is the value the artifact's config carries."""
    a, b = numerical(prose), numerical(config)
    if a is not None and b is not None:
        return a == b
    if a is not None or b is not None:
        return False
    return str(prose).strip() == str(config).strip()


def known_flags() -> dict[str, dict]:
    """The flags any runner in this repository defines, keyed by config key, from `e172`'s registry.

    Keyed by config key because a `config` is `vars(args)`: `--readout-size` is stored as `readout_size`, and the
    table writes the flag while the artifact stores the key, so the two are reconciled here rather than guessed
    per call site. A flag no runner defines is not compared -- it is counted, because an unknown flag is as likely
    to be this audit's parsing error as the table's.
    """
    merged: dict[str, dict] = {}
    for path in sorted(Path("experiments").glob("*.py")):
        for flag, meta in parser_flags(path).items():
            merged.setdefault(flag, meta)
    return merged


def audit(plan: Path = PLAN, runs_dir: Path = RUNS) -> dict:
    rows, unparseable = programme_rows(plan)
    index = artifact_names(runs_dir)
    flags = known_flags()
    # `e172.registry` is what the *runners* define; a flag in the table spelling a key no runner carries is counted
    runners = len(registry(Path("experiments")))

    checks: list[dict] = []
    # Two ledgers, and they must not be added together: `skips` counts ROWS that could not be attributed or read,
    # `flag_skips` counts FLAGS inside a row that was attributed. The first version kept one counter for both, so
    # its denominator was a sum of rows and flags -- a number that looks like a scope and is not one.
    skips: collections.Counter = collections.Counter()
    flag_skips: collections.Counter = collections.Counter()
    discarded_total = 0
    dropped_flags_total = 0
    for r in rows:
        # The command's own artifact is the one named *before* any comparison clause; a reference introduced by
        # "against" / "vs" is the row's baseline, and comparing the command's flags with it is comparing the two
        # sides of a contrast the row exists to make.
        marker = COMPARISON_RE.search(r["what"])
        home = r["what"][:marker.start()] if marker else r["what"]
        tokens, discarded, dropped_flags = command_tokens(home, index)
        discarded_total += discarded
        dropped_flags_total += dropped_flags
        pairs = flag_pairs(tokens)
        if not pairs:
            skips["row states no flag"] += 1
            continue
        named, ambiguous, missing_files = resolve(home, index)
        if not named:
            whole, _, _ = resolve(r["what"], index)
            skips["first cell names an artifact only as a comparison partner" if whole
                   else "first cell names no artifact it can resolve"] += 1
            continue
        if len(named) > 1:
            skips["first cell names more than one artifact"] += 1
            continue
        if ambiguous:
            skips["first cell names a label that identifies several files"] += 1
            continue
        if missing_files:
            skips["first cell names a `.json` the corpus does not have"] += 1
            continue
        artifact = named[0]
        path = runs_dir / artifact
        if not path.is_file():
            # a row registering an artifact the run has not written yet: there is no config to be right or wrong
            skips["named artifact not yet written (a registration)"] += 1
            continue
        try:
            config = (json.loads(path.read_text(encoding="utf-8")) or {}).get("config") or {}
        except (json.JSONDecodeError, OSError):
            skips["artifact unreadable"] += 1
            continue
        if not config:
            skips["artifact carries no config"] += 1
            continue
        for flag, value in pairs:
            key = flag.replace("-", "_")
            if key not in flags:
                flag_skips["flag no runner in this repository defines"] += 1
                continue
            if flags[key]["store_true"]:
                if value is not None and not PLACEHOLDER_RE.match(value):
                    checks.append({"line": r["line"], "artifact": artifact, "flag": flag,
                                   "prose": value, "config": None, "key": key,
                                   "verdict": "mismatch: store_true flag given a value"})
                else:
                    flag_skips["store_true flag, no value to compare"] += 1
                continue
            if value is None:
                flag_skips["flag stated with no value"] += 1
                continue
            if PLACEHOLDER_RE.match(value):
                flag_skips["value is a placeholder rather than a literal"] += 1
                continue
            if key not in config:
                checks.append({"line": r["line"], "artifact": artifact, "flag": flag, "prose": value,
                               "config": None, "key": key,
                               "verdict": "mismatch: the artifact's config does not carry this key"})
                continue
            # A config value can be a list (`e3 --topologies real` runs `["real"]`), so the cell's value agreeing
            # with one member is agreement -- said out loud in the verdict, because a silent pass here would hide
            # a cell that states one member of a family the run actually swept.
            in_list = isinstance(config[key], list) and any(same(value, v) for v in config[key])
            ok = in_list or same(value, config[key])
            checks.append({"line": r["line"], "artifact": artifact, "flag": flag, "prose": value,
                           "config": config[key], "key": key,
                           "verdict": "match (a member of the config's list)" if in_list else
                                      ("match" if ok else "MISMATCH")})
    mismatches = [c for c in checks if not c["verdict"].startswith("match")]
    attributed = {c["line"] for c in checks}
    return {"path": str(plan), "rows": len(rows), "unparseable": len(unparseable),
            "runners_in_registry": runners, "checks": checks, "n_checks": len(checks),
            "checked_rows": len(attributed), "mismatches": mismatches, "n_mismatches": len(mismatches),
            "skips": dict(skips), "n_skips": sum(skips.values()),
            "flag_skips": dict(flag_skips),
            "rows_accounted_for": len(attributed) + sum(skips.values()),
            "tokens_discarded_after_the_cell_named_its_artifact": discarded_total,
            "flags_in_the_discarded_part_never_checked": dropped_flags_total}


def spelling(row: dict) -> str:
    """How an artifact writes its read-out: the three equivalent forms, and the case whose meaning is lost.

    The label for an artifact with no achieved count says so rather than guessing a direction -- the first version
    classified it as "a literal below the achieved count", which is a statement about a quantity the artifact does
    not carry, and the test caught it.
    """
    if row["readout_size"] is None:
        return "absent"
    if not row["readout_size"]:
        return "0"
    if row["achieved_n"] is None:
        return "a literal, with no achieved count to compare it to"
    if row["readout_size"] == row["achieved_n"]:
        return "the achieved count itself"
    return ("a literal above the achieved count" if row["readout_size"] > row["achieved_n"]
            else "a literal below the achieved count")


def readout_census(runs_dir: Path = RUNS) -> dict:
    """What `--readout-size` means across the corpus: which values are the whole state, and whose meaning is lost.

    Three facts, and the third is the fragile one: `circuit_size` is a **soft** budget, so the achieved neuron
    count is the circuit's `@nNNNN` name and not the config; `--readout-size` at or above the achieved count is
    the whole state (and so is a literal `0`, and so is the flag's absence); and an artifact without a `circuit`
    name does not record the achieved count, so for those the meaning of the value cannot be recovered at all.
    """
    rows: list[dict] = []
    for p in sorted(glob.glob(str(runs_dir / "*.json"))):
        try:
            d = json.loads(Path(p).read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        if not isinstance(d, dict) or not isinstance(d.get("config"), dict):
            continue
        c = d["config"]
        if "readout_size" not in c:
            continue
        named = re.search(r"@n([0-9]+)", d.get("circuit") or "")
        n = int(named.group(1)) if named else None
        size = c["readout_size"]
        if n is None:
            klass = "achieved count not recorded"
        elif not size or size >= n:
            klass = "the whole state"
        else:
            klass = "a draw of this size"
        rows.append({"artifact": Path(p).name, "readout_size": size, "achieved_n": n, "class": klass,
                     "readout_block_size": (d.get("readout") or {}).get("size"),
                     "readout_seed": c.get("readout_seed")})
    by_class = collections.Counter(r["class"] for r in rows)
    # the run-time rule the runner applies, checked against the artifact's own `readout` block where it has one.
    # The denominator matters and is not `len(rows)`: the block was added to the runner late, so only 60 of the 144
    # artifacts carry it, and a claim of "0 disagreements" over 144 would be a claim about 84 artifacts that cannot
    # disagree because they say nothing.
    checkable = [r for r in rows if r["achieved_n"] is not None and r["readout_block_size"] is not None]
    contradicting = [r for r in checkable
                     if r["readout_block_size"] != (r["achieved_n"]
                                                    if (not r["readout_size"]
                                                        or r["readout_size"] >= r["achieved_n"])
                                                    else r["readout_size"])]
    spellings = collections.Counter(spelling(r) for r in rows)
    whole = [r for r in rows if r["class"] == "the whole state"]
    return {"artifacts_with_a_readout_size": len(rows), "classes": dict(by_class), "spellings": dict(spellings),
            "whole_state_by_achieved_count": collections.Counter(
                "n=%d" % r["achieved_n"] for r in whole if r["achieved_n"] is not None),
            "readout_block_contradicts_the_rule": contradicting,
            "n_artifacts_with_a_readout_block_to_check": len(checkable),
            "n_artifacts_recording_no_achieved_count": by_class["achieved count not recorded"],
            "rows": rows}


def report(res: dict, census: dict | None = None) -> int:
    print(f"== {res['path']} ==")
    print(f"   table rows parsed                                   : {res['rows']}"
          f" ({res['unparseable']} unparseable)")
    print(f"   runners contributing a flag table (e172 registry)    : {res['runners_in_registry']}")
    print(f"   attributed rows / flag checks performed              : {res['checked_rows']} rows / "
          f"{res['n_checks']} flags")
    print(f"   MISMATCHES                                          : {res['n_mismatches']}")
    for c in res["mismatches"]:
        print(f"        line {c['line']:5} {c['artifact']}  --{c['flag']} states {c['prose']!r}, "
              f"config has {c['config']!r}  [{c['verdict']}]")
    print("   attributed rows and flags that matched:")
    matched = collections.Counter((c["line"], c["artifact"]) for c in res["checks"]
                                  if c["verdict"].startswith("match"))
    for (line, artifact), n in sorted(matched.items()):
        print(f"        line {line:5} {artifact:42} {n} flag(s) agree")
    print(f"   rows the checker could not attribute, by reason (they sum with the rows above):")
    for reason, n in sorted(res["skips"].items(), key=lambda x: -x[1]):
        print(f"        {n:4}  {reason}")
    print(f"   of the attributed rows: {res['rows_accounted_for']} of {res['rows']} rows accounted for")
    print(f"   flags inside an attributed row that were not compared, by reason:")
    for reason, n in sorted(res["flag_skips"].items(), key=lambda x: -x[1]):
        print(f"        {n:4}  {reason}")
    print(f"   prose the checker never read (tokens after the cell named its artifact): "
          f"{res['tokens_discarded_after_the_cell_named_its_artifact']}")
    print(f"   flags in that discarded part, therefore never checked                    : "
          f"{res['flags_in_the_discarded_part_never_checked']}")
    if census:
        print("== --readout-census ==")
        print(f"   artifacts carrying a `readout_size`                  : "
              f"{census['artifacts_with_a_readout_size']}")
        for k, v in sorted(census["classes"].items(), key=lambda x: -x[1]):
            print(f"        {v:4}  means {k}")
        for k, v in sorted(census["spellings"].items(), key=lambda x: -x[1]):
            print(f"        {v:4}  spelled as {k}")
        print(f"   whole-state runs, by the circuit's achieved count     : "
              f"{dict(census['whole_state_by_achieved_count'])}")
        print(f"   artifacts whose own `readout` block contradicts the rule: "
              f"{len(census['readout_block_contradicts_the_rule'])} of "
              f"{census['n_artifacts_with_a_readout_block_to_check']} that carry a block to check")
        print(f"   artifacts that record no achieved count (no `circuit` name): "
              f"{census['n_artifacts_recording_no_achieved_count']}")
    return res["n_mismatches"]


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--path", type=Path, default=PLAN)
    p.add_argument("--runs", type=Path, default=RUNS)
    p.add_argument("--readout-census", action="store_true",
                   help="also print what `--readout-size` means across the corpus, and where the meaning is lost")
    p.add_argument("--json-out", type=Path, default=None)
    args = p.parse_args(argv)

    res = audit(args.path, args.runs)
    census = readout_census(args.runs) if args.readout_census else None
    n = report(res, census)
    if args.json_out:
        from clfly.bench.artifacts import write_json
        write_json(args.json_out, {**res, "readout_census": census})
        print(f"wrote {args.json_out}")
    return 1 if n else 0


if __name__ == "__main__":
    raise SystemExit(main())
