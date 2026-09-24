"""E172 -- the runner-to-parser registry `e103` asked for, built from the AST, and the first test of its premise.

`e103`'s epoch check dates an artifact by asking what the **newest artifact of its own filename family** has that
it lacks. Its docstring names the general form it could not reach: *"the general check would take each runner's
parser as the reference; that needs a registry this project does not have"*. This builds it, statically:

  * for every `experiments/*.py`, the `--flags` its argparse defines, read from the **AST** rather than by running
    it (so the registry cannot be fooled by a parser that is only constructed under `__main__`, and cannot execute
    a module to find out);
  * for every artifact carrying a `config`, **which parsers could have produced it** -- a `config` is `vars(args)`,
    so a runner is a candidate exactly when its parser defines every key the artifact carries;
  * and the **missing keys against today's parser**, which is `e103`'s question asked absolutely instead of
    relatively.

**And it is the first test of the premise both `e103` and rule 47 rest on.** "A parser only ever gains flags" has
been stated and never checked; a `config` key that **no** current parser defines refutes it for that runner (or
means the artifact came from a runner no longer in the tree), and a removed flag is exactly why rule 47's
start-time correction cannot date an artifact by its keyset alone.

    python -m experiments.e172_parser_registry
    python -m experiments.e172_parser_registry --json-out runs/e172_parser_registry.json

Reads source and artifacts on disk; runs nothing. ASCII output only.
"""

from __future__ import annotations

import argparse
import ast
from pathlib import Path

from clfly.bench.artifacts import write_json
from experiments.e103_reproducibility_audit import epoch_flags, family, load_artifacts

#: where the runners live, and which files can define a parser at all
EXPERIMENTS = Path("experiments")
#: a `config` key is a flag name with dashes turned into underscores, so the registry's keys are too
FLAG_PREFIX = "--"


def parser_keys(path: Path) -> set[str]:
    """Every `config` key this file's argparse defines, read from its syntax tree.

    Walks for ``add_argument("--flag", ...)`` calls rather than importing the module: a registry that ran code to
    fill itself would be a registry of whatever the code does at import time, and the point of the check is to be
    independent of the runner it describes. A file that does not parse contributes nothing.
    """
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except (SyntaxError, UnicodeDecodeError):
        return set()
    keys: set[str] = set()
    for node in ast.walk(tree):
        if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                and node.func.attr == "add_argument"):
            continue
        for arg in node.args:
            if isinstance(arg, ast.Constant) and isinstance(arg.value, str) and arg.value.startswith(FLAG_PREFIX):
                keys.add(arg.value[len(FLAG_PREFIX):].replace("-", "_"))
    return keys


def registry(directory: Path = EXPERIMENTS) -> dict[str, set[str]]:
    """Every experiment file that defines at least one flag, by name."""
    return {p.name: keys for p in sorted(directory.glob("*.py"))
            if (keys := parser_keys(p))}


def candidates(config: dict, parsers: dict[str, set[str]]) -> list[str]:
    """The runners whose parser defines every key this `config` carries -- its possible authors.

    A `config` is `vars(args)`, so this is containment and not equality: an artifact from an older epoch of a
    runner carries a **subset** of that runner's current flags.
    """
    return sorted(name for name, keys in parsers.items() if set(config) <= keys)


def classify(artifacts: list[dict], parsers: dict[str, set[str]]) -> dict:
    """Per artifact: who could have written it, and what today's parser has that it lacks."""
    out: dict = {"unclaimed": [], "ambiguous": [], "unique": [], "no_config": 0}
    for a in artifacts:
        config = a["config"]
        if not config:
            out["no_config"] += 1
            continue
        found = candidates(config, parsers)
        record = {"name": a["name"], "keys": len(config), "candidates": found}
        if not found:
            out["unclaimed"].append(record)
        elif len(found) == 1:
            record["missing_vs_today"] = sorted(parsers[found[0]] - set(config))
            out["unique"].append(record)
        else:
            best = max(found, key=lambda n: (len(parsers[n] & set(config)), len(parsers[n]), n))
            record["maximal"] = best
            record["missing_vs_today"] = sorted(parsers[best] - set(config))
            out["ambiguous"].append(record)
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args(argv)

    parsers = registry()
    artifacts = load_artifacts()
    res = classify(artifacts, parsers)
    out: dict = {"parsers": len(parsers), "artifacts": len(artifacts),
                 "unclaimed": res["unclaimed"], "ambiguous": res["ambiguous"],
                 "unique": res["unique"], "no_config": res["no_config"]}

    print("== the registry ==")
    print(f"   experiment files defining at least one flag: {len(parsers)}")
    print(f"   artifacts carrying a config: {len(artifacts)} (of which {res['no_config']} carry an empty one)")
    print(f"   {'':<28}{'artifacts':>10}")
    print(f"   unambiguous author           {len(res['unique']):>10}")
    print(f"   more than one possible author{len(res['ambiguous']):>10}")
    print(f"   NO possible author           {len(res['unclaimed']):>10}")

    print("\n== the premise behind both `e103` and rule 47: does any parser only gain flags? ==")
    if res["unclaimed"]:
        print(f"   {len(res['unclaimed'])} artifact(s) carry a key no current parser defines:")
        for r in res["unclaimed"][:8]:
            print(f"      {r['name'][:44]:<46}{r['keys']} keys: no parser defines them all")
        print("   -> a `config` is `vars(args)`, so each of these either came from a runner no longer in the tree")
        print("      or from a flag that was **removed** -- which is the case rule 47's keyset dating cannot see")
        print("      and its start-time check exists to survive.")
    else:
        print("   every artifact's config is contained in some current parser: no flag has been removed, so")
        print("   'a parser only gains flags' holds over this corpus and the keyset dating is sound.")

    dated = [r for r in res["unique"] + res["ambiguous"]]
    oldest = sorted(dated, key=lambda r: -len(r["missing_vs_today"]))[:4]
    print("\n== what the registry adds to `e103`'s dating ==")
    print(f"   artifacts the registry can date against a parser: {len(dated)} of {len(artifacts)}")
    print(f"   (e103 can date only those whose own filename family has three or more members, and it dates them")
    print(f"    against the newest sibling on disk rather than against the runner)")
    print(f"   {'artifact':<46}{'keys':>6}{'missing vs today':>18}")
    for r in oldest:
        print(f"   {r['name'][:44]:<46}{r['keys']:>6}{len(r['missing_vs_today']):>18}")
    relative = epoch_flags(artifacts)
    out["dated_vs_e103"] = {"registry": len(dated), "e103_relative": len(relative)}
    print(f"\n   named by `e103`'s relative rule: {len(relative)} artifact(s); by the registry: {len(dated)}")

    if args.json_out:
        write_json(args.json_out, out)
        print(f"\nwrote {args.json_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
