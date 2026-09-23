"""E103 -- which arms of a repeated configuration actually reproduce, and which artifacts predate the parser.

Two failures this project has now paid for twice, both detectable from the artifacts alone and neither
detected at the time:

1. **An arm that "cannot depend on the manipulated variable" was not reproducible anyway.** Two runs of one
   rate-network command, an hour apart, agreed on `naive` and `ewc` to the last digit and differed on
   `ewc-block`, `ewc-block-rand` and `replay` -- the three arms the comparison rested on
   (`docs/findings/2026-09-23-the-fisher-free-arm-was-not-fisher-free.md`).  Nothing in the repository said
   which arms reproduce, so the assumption went untested for four fires.

2. **An artifact's `config` keyset dates its code epoch, and its `mtime` does not.**  `e98`'s in-place
   normalisation rewrote seven rate-network artifacts and left them all with one timestamp; the epoch that
   survives is inside the payload, because a runner that dumps ``vars(args)`` cannot omit a flag its parser
   defines (`docs/research_plan.md`, rule 27).

Both checks are the same shape -- *compare an artifact against another artifact rather than against a memory of
the code* -- and both are one screenful of code, so they belong in a script that can be re-run rather than in a
paragraph that has to be re-read.

    python -m experiments.e103_reproducibility_audit
    python -m experiments.e103_reproducibility_audit --json-out runs/e103_reproducibility_audit.json

The exactness test is deliberate: ``replicates`` is compared as a **value**, not to four significant digits.
Rule 21 measured that the torch path is environment-shaped at about the fourth digit on the analytic line, so
an exact match is the strong statement and a near match is reported as movement rather than folded into it.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from clfly.bench.artifacts import write_json

RUNS = Path("runs")
#: the one key a config must differ in for two runs of the *same* command to coexist on disk
VOLATILE = ("json_out",)
#: replicate fields that define an arm, in the order they are reported. **Declared, not inferred**: comparing
#: the whole replicate dict makes the verdict a statement about the *schema*, and adding a field broke it --
#: `e107`, `e108` and `e109` put `theta_drift`, `interference` and `second_order` into the replicate records, and
#: the audit then reported "1 of 1 arms do not reproduce" for seven runs whose forgetting was identical to six
#: decimals. That is the same failure this module exists to catch, one level down: a verdict read off the wrong
#: object.
ARM_FIELDS = ("learned", "mean_forgetting", "retention", "final_accuracy",
              "forgetting_per_task", "final_per_task", "losses")
#: keys that describe rather than measure, so their presence or absence is not a difference in the arm
NON_ARM_KEYS = ("method", "replicates")


def load_artifacts(root: Path = RUNS, skip: tuple[str, ...] = ()) -> list[dict]:
    """Every parseable ``runs/*.json`` with a ``config`` dict, most recently modified last."""
    out = []
    for path in sorted(root.glob("*.json")):
        if path.name in skip:
            continue
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            continue
        if not isinstance(payload.get("config"), dict):
            continue
        cfg = payload["config"]
        out.append({"name": path.name, "config": cfg, "payload": payload,
                    "mtime": path.stat().st_mtime})
    out.sort(key=lambda a: a["mtime"])
    return out


def signature(config: dict) -> str:
    """A config's identity as a string, with the output path removed.

    Without dropping ``json_out`` no two runs of one command ever group -- the trap that would have made this
    script silently report zero repeated configurations rather than reporting an unreproducible arm.
    """
    trimmed = {k: v for k, v in config.items() if k not in VOLATILE}
    return json.dumps(trimmed, sort_keys=True, default=str)


def arm_matches(members: list[dict], method: str) -> dict:
    """Whether ``method``'s replicates are equal across ``members``, and by how much the means move.

    The comparison is over ``ARM_FIELDS``, **declared** rather than taken as the whole record: see the comment on
    that tuple. Any key a member carries beyond those is reported separately as instrumentation, so that a new
    measurement added to the runner shows up as a note rather than as an unreproducible arm.
    """
    reps, means, accs, extra = [], [], [], set()
    for m in members:
        entry = (m["payload"].get("methods") or {}).get(method)
        if not isinstance(entry, dict) or "replicates" not in entry:
            return {"present": False}
        reps.append(json.dumps([{k: r.get(k) for k in ARM_FIELDS} for r in entry["replicates"]],
                               sort_keys=True, default=str))
        extra |= {k for r in entry["replicates"] for k in r} - set(ARM_FIELDS) - set(NON_ARM_KEYS)
        means.append(float(entry.get("mean_forgetting", float("nan"))))
        accs.append(float(entry.get("final_accuracy", float("nan"))))
    spread = lambda xs: max(xs) - min(xs)                     # noqa: E731  (max-min over >=2 members)
    return {"present": True, "exact": len(set(reps)) == 1, "runs": len(reps),
            "movement_forgetting": spread(means), "movement_accuracy": spread(accs),
            "values": [round(x, 6) for x in means],
            "instrumentation_beyond_the_arm": sorted(extra)}


def group_repeats(artifacts: list[dict], min_runs: int = 2) -> list[dict]:
    """Group artifacts by config signature and report per-arm reproducibility for the groups of size >= min.

    When the members record **different environments**, the group is also split by environment and each
    subgroup is reported separately.  That split is the difference between "5 of 5 arms do not reproduce" and
    the answerable question -- "which arms fail to reproduce *in one environment*" -- and without it the audit
    reports a recorded cause as an unexplained one. Measured: the 8-batch group is five runs, of which two set
    `OMP_NUM_THREADS` explicitly; pooling them makes every arm look irreproducible, while within the three
    default-thread runs `naive` and `ewc` are bit-identical.
    """
    groups: dict[str, list[dict]] = {}
    for a in artifacts:
        if not isinstance(a["payload"].get("methods"), dict):
            continue                                          # analysis artifacts have no arms to compare
        groups.setdefault(signature(a["config"]), []).append(a)
    out = []
    for sig, members in groups.items():
        if len(members) < min_runs:
            continue
        methods = sorted(set().union(*[set(m["payload"]["methods"]) for m in members]))
        arms = {meth: arm_matches(members, meth) for meth in methods}
        arms = {k: v for k, v in arms.items() if v.get("present")}
        compared = [m for m, v in arms.items() if v["exact"]]
        record = {"signature": sig, "runs": len(members), "names": [m["name"] for m in members],
                  "arms": arms, "arms_compared": sorted(arms),
                  "arms_identical": compared,
                  "arms_differing": [m for m in arms if m not in compared],
                  "environments": {}, "subgroups": []}

        # 'environment' is absent from every artifact written before e102, so those runs are "unrecorded"
        # rather than grouped with each other by a shared empty dict.
        keyed: dict[str, list[dict]] = {}
        for m in members:
            env = m["payload"].get("environment")
            key = json.dumps(env, sort_keys=True, default=str) if isinstance(env, dict) else "unrecorded"
            keyed.setdefault(key, []).append(m)
        record["environments"] = {k: len(v) for k, v in keyed.items()}
        if len(keyed) > 1:
            for key, sub in sorted(keyed.items()):
                if len(sub) < 2:
                    record["subgroups"].append({"environment": key, "runs": 1,
                                                "names": [m["name"] for m in sub], "arms": {}})
                    continue
                sub_methods = sorted(set().union(*[set(m["payload"]["methods"]) for m in sub]))
                sub_arms = {meth: arm_matches(sub, meth) for meth in sub_methods}
                sub_arms = {k: v for k, v in sub_arms.items() if v.get("present")}
                record["subgroups"].append({
                    "environment": key, "runs": len(sub), "names": [m["name"] for m in sub],
                    "arms": sub_arms,
                    "arms_identical": sorted(k for k, v in sub_arms.items() if v["exact"]),
                    "arms_differing": sorted(k for k, v in sub_arms.items() if not v["exact"])})
        out.append(record)
    out.sort(key=lambda g: (-len(g["arms_differing"]), -g["runs"], g["names"][0]))
    return out


def maximal_keyset(configs: list[dict]) -> set[str]:
    """The key set that contains the most others -- the closest thing to "what the parser defines now".

    Candidates are ranked by how many other configs they are a superset of, ties broken by size and then by
    name order so the answer is deterministic.  A parser that only ever *adds* flags makes this the current
    parser's keyset; a script that reports a missing key is naming a flag its artifact predates.
    """
    sets = [set(c) for c in configs]
    if not sets:
        return set()
    def score(cand: set[str]) -> tuple[int, int, str]:
        cover = sum(1 for s in sets if cand >= s)
        return (-cover, -len(cand), "|".join(sorted(cand))[:200])
    return min(sets, key=score)


def family(name: str) -> str:
    """The runner an artifact belongs to, from its filename: ``e8_hardened_basis`` -> ``e8``.

    This project names artifacts ``e<N>_...``, and the number is the experiment, which is the runner.  A
    first version of this check used key overlap instead of the name and reported **50 artifacts** as
    predating a flag, nearly all of them from *other* runners whose configs simply carry different keys --
    which is the failure mode this module's own docstring warns about, committed in the first draft.
    """
    m = re.match(r"(e\d+)", name)
    return m.group(1) if m else name.split("_")[0]


def epoch_flags(artifacts: list[dict], min_family: int = 3) -> list[dict]:
    """Per artifact, which keys its own runner's newest artifact has and this one lacks (rule 27).

    **Scope, stated because the general form is not available.** The check applies to artifacts that carry
    per-arm results -- a benchmark run's ``config`` is ``vars(args)``, and only such a dump can be dated this
    way. An aggregate artifact's ``config`` is a hand-built summary (``e96_fisher_batch_sweep.json``'s has
    three keys), and asking it for ``replay_batch`` is asking the wrong object, so it is excluded rather than
    reported. The general check would take each runner's parser as the reference; that needs a registry this
    project does not have, and inventing one here would be a bigger change than the audit.

    The reference is the maximal keyset *within the artifact's family* (the leading ``e<N>`` of its filename),
    because a parser only ever gains flags. A first version used global key overlap and reported **50
    artifacts** as predating a flag, nearly all of them from other runners whose configs simply carry
    different keys.
    """
    by_family: dict[str, list[dict]] = {}
    for a in artifacts:
        if not isinstance(a["payload"].get("methods"), dict):
            continue
        by_family.setdefault(family(a["name"]), []).append(a)

    out = []
    for fam, members in sorted(by_family.items()):
        if len(members) < min_family:
            continue
        ref = maximal_keyset([m["config"] for m in members])
        for a in members:
            keys = set(a["config"])
            if keys > ref:
                continue                                      # this artifact IS a maximal keyset
            missing = sorted(ref - keys)
            if missing:
                out.append({"name": a["name"], "family": fam, "missing": missing,
                            "keys": len(keys), "reference": len(ref)})
    out.sort(key=lambda r: (r["family"], -len(r["missing"]), r["name"]))
    return out


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--runs", type=Path, default=RUNS)
    p.add_argument("--min-runs", type=int, default=2,
                   help="a configuration with fewer executions than this cannot be checked")
    p.add_argument("--skip", default="e103_reproducibility_audit.json",
                   help="comma-separated artifact names to leave out of the scan")
    p.add_argument("--json-out", type=Path, default=None)
    args = p.parse_args(argv)

    skip = tuple(s for s in args.skip.split(",") if s)
    artifacts = load_artifacts(args.runs, skip=skip)
    groups = group_repeats(artifacts, min_runs=args.min_runs)
    stale = epoch_flags(artifacts)

    print(f"artifacts with a config: {len(artifacts)}")
    print(f"repeated configurations (>= {args.min_runs} runs): {len(groups)}")
    for g in groups:
        print(f"\n  {g['runs']} runs: {', '.join(g['names'])}")
        for meth, v in sorted(g["arms"].items()):
            mark = "identical" if v["exact"] else "DIFFER   "
            print(f"    {meth:16} {mark} move {v['movement_forgetting']:.4f} forgetting, "
                  f"{v['movement_accuracy']:.4f} accuracy   {v['values']}")
            if v.get("instrumentation_beyond_the_arm"):
                print(f"    {'':16} (instrumentation recorded beyond the arm fields: "
                      f"{', '.join(v['instrumentation_beyond_the_arm'])})")
        if g["arms_differing"]:
            print(f"    -> {len(g['arms_differing'])} of {len(g['arms'])} arms do not reproduce: "
                  f"{', '.join(g['arms_differing'])}")
        if g["subgroups"]:
            print(f"    -> {len(g['environments'])} recorded environments: "
                  f"{ {k: v for k, v in sorted(g['environments'].items())} }")
            for sub in g["subgroups"]:
                if sub["runs"] < 2:
                    print(f"       {sub['runs']} run, not comparable: {', '.join(sub['names'])}")
                    continue
                print(f"       within one environment ({sub['runs']} runs: {', '.join(sub['names'])}): "
                      f"identical {sub['arms_identical'] or '[]'}, "
                      f"differing {sub['arms_differing'] or '[]'}")

    print(f"\nartifacts missing a key their own runner's newest artifact has: {len(stale)}")
    for r in stale:
        print(f"    {r['name']:44} [{r['family']}] lacks {', '.join(r['missing'])}")
    if not stale:
        print("    (none -- every artifact carries the keys its runner's newest artifact defines)")

    if args.json_out:
        write_json(args.json_out, {"n_artifacts": len(artifacts), "min_runs": args.min_runs,
                                   "repeated": groups, "missing_keys": stale})
        print(f"\nwrote {args.json_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
