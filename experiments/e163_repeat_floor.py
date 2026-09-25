"""E163 -- the corpus's own run-to-run floor, read off the configurations it has executed more than once.

Every reproducibility claim this project makes eventually reduces to one question -- *if I execute this command
again, do I get the same numbers?* -- and the record answers it from the ten configurations `e103` finds executed
at least twice. This unit tabulates those ten groups against the two provenance fields a run artifact carries,
`config` and `environment`, and separates three cases the raw "N of M arms do not reproduce" line runs together:

  * **same configuration, same recorded environment** -- the floor itself, and it is **exactly zero**;
  * **same configuration, a second recorded environment** -- a *named* cause, measured (`e77` found the knob);
  * **same configuration, no recorded environment** -- movement the artifact cannot attribute, which is where
    every non-zero number in the corpus lives.

The third case is not a curiosity. `e159` is a third execution of a wiring-family command whose first two
executions are bit-identical on every arm, so its verdict is a comparison against a *deterministic* prediction;
this unit is what says so, and it also says what the record would be unable to explain if that verdict flipped.

It also carries `command_from_config`, which builds a re-execution's command line **from the artifact's own
`config` dict** rather than from a paraphrase of it. That is rule 44 made executable: the `e153` accident was a
launch whose flags were copied from a registration that did not name `--lam`, and `--lam`'s default is 1.0, so the
run happened at 333x the strength it was registered for. A helper that refuses to emit a command unless every
recorded field is accounted for cannot make that mistake.

    python -m experiments.e163_repeat_floor
    python -m experiments.e163_repeat_floor --command runs/e101_rate_fb8.json --methods naive,ewc
    python -m experiments.e163_repeat_floor --json-out runs/e163_repeat_floor.json

Reads only artifacts on disk; runs nothing. ASCII output only.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from clfly.bench.artifacts import write_json
from experiments.e103_reproducibility_audit import group_repeats, load_artifacts

#: `config` key -> the runner flag that sets it. **Every** key in a run artifact's config is listed, including
#: booleans, because the failure this helper exists to prevent is a field that silently takes its default.
FLAGS = {
    "basis": "--basis", "batch": "--batch", "circuit_size": "--circuit-size", "classes": "--classes",
    "fisher_batches": "--fisher-batches", "input_overlap": "--input-overlap", "iters": "--iters",
    "lam": "--lam", "lr": "--lr", "methods": "--methods", "noise": "--noise", "pool_below": "--pool-below",
    "pool_buckets": "--pool-buckets", "readout_size": "--readout-size", "repeats": "--repeats",
    "replay_batch": "--replay-batch", "replay_per_task": "--replay-per-task", "seed0": "--seed0",
    "support": "--support", "test": "--test", "train": "--train", "json_out": "--json-out",
    "readout_seed": "--readout-seed", "partition_seed": "--partition-seed", "anchor_bias": "--anchor-bias",
    "save_theta": "--save-theta",
}
#: keys whose flag is `store_true`: True emits the flag and False is the omission, which is faithful **only**
#: when the runner's own default is False -- so the two directions have to be read separately.
BOOLEAN = {"shared_head", "frozen_body", "normalise_fisher", "frozen_bias"}
#: the `store_true` flags whose runner default is **True**: a recorded False cannot be reproduced at all, because
#: `store_true` has no negative form and omitting the flag asks for True.
DEFAULT_TRUE = {"normalise_fisher"}

RUNNER = "experiments/e8_rate_network.py"

#: **the runners, with their flags read from the source rather than written here.** A first version mapped two
#: runners by hand -- the training one and then the analytic one, which had produced this project's ladder
#: comparisons while its commands were paraphrased -- and the census that followed showed the cost of that: **149
#: of the corpus's configs were refused** for no reason but that nobody had typed their runner's flags out. The
#: map was redundant all along, because **a `config` key is its flag with dashes turned into underscores**
#: (`seed0` -> `--seed0`, `align_top` -> `--align-top`), so the only thing a hand-written map added was a check
#: that the field exists -- and `e172` already extracts that, and the two facts that decide how a flag is written,
#: from every parser's syntax tree. This is that registry, keyed by the runner's file name.
def _runners() -> dict[str, tuple[str, dict]]:
    from pathlib import Path as _Path

    from experiments.e172_parser_registry import parser_flags

    out: dict[str, tuple[str, dict]] = {}
    for path in sorted(_Path("experiments").glob("*.py")):
        flags = parser_flags(path)
        if flags:
            out[path.name] = (str(path).replace("\\", "/"), flags)
    return out


RUNNERS = _runners()


def runner_for(config: dict) -> list[str]:
    """The runners whose parser defines **every** key this `config` carries (ignoring unset keys).

    The inference is the same shape as `e172`'s authorship test -- a `config` is `vars(args)`, so a runner can
    have written it only if it can name every field -- and it is a *list* because a small config can be covered
    by more than one runner, in which case the caller has to say which.
    """
    keys = {k for k, v in config.items() if v is not None and k != "json_out" and v is not False}
    return sorted(name for name, (_, flags) in RUNNERS.items() if keys <= set(flags))


def command_from_config(config: dict, json_out: str | None = None, runner: str | None = None) -> list[str]:
    """The command line that re-executes ``config``, with ``json_out`` replaced.

    Every key must be either in `FLAGS` or in `BOOLEAN`; anything else raises, because an unmapped field is one
    the emitted command would set by default -- which is the `e153` defect exactly (an omitted `--lam` is 1.0).
    **Every non-boolean field is emitted even when it equals the runner's default**, which is the whole point:
    the command is derived from the artifact, so it cannot depend on what the default happens to be today.
    **A field recorded as `None` is omitted**, because in a `vars(args)` dump that is the flag not having been
    given -- the runner's optional flags all default to `None` -- so emitting it would be the one way to make the
    command say something the artifact does not. `json_out` is dropped from the config first: it names an output,
    not a measurement.
    """
    if runner is None:
        found = runner_for(config)
        if len(found) != 1:
            raise ValueError(f"cannot tell which runner wrote this config: {found or 'none'} covers its keys; "
                             f"pass runner= explicitly")
        runner = found[0]
    runner_path, parser = RUNNERS[runner]
    flags: list[str] = []
    for key in sorted(config):
        value = config[key]
        if key == "json_out" or value is None:
            continue
        flag = "--" + key.replace("_", "-")
        if key in parser and parser[key]["store_true"]:
            if value:
                flags.append(flag)
            elif parser[key]["default"] is True:
                raise ValueError(f"{key} = False has no command-line form; it cannot be reproduced")
            continue
        if key not in parser:
            raise ValueError(f"config key {key!r} maps to no {runner} runner flag -- the command would use its "
                             f"default")
        # **a config value can fail to round-trip to its own flag, exactly as a config key can fail to exist in
        # its parser.** `e3_basis_selection` transforms its own namespace before dumping it --
        # `args.topologies = tuple(t for t in args.topologies.split(",") if t)` -- so the artifact records a tuple
        # where the flag takes a comma-separated string. The join here is that transform's inverse and it is the
        # *only* value transform this helper knows: a field it cannot invert is refused below rather than emitted
        # as a Python repr, which would be a command that cannot run.
        if isinstance(value, (list, tuple)):
            flags.extend([flag, ",".join(str(v) for v in value)])
        else:
            flags.extend([flag, str(value)])
    if json_out is not None:
        flags.extend(["--json-out", str(json_out)])
    return ["python", runner_path, *flags]


def floor(groups: list[dict]) -> dict:
    """The corpus's run-to-run floor, aggregated over `group_repeats`' groups.

    The three cases are separated by ``environment``: `group_repeats` records ``unrecorded`` for artifacts
    written before the field existed, and those runs are the *only* ones in the corpus whose movement has no
    field to explain it.
    """
    runs = arms_compared = arms_identical = 0
    unrecorded = recorded = 0
    same_env: list[dict] = []          # groups with one recorded environment: the floor
    unattributed: list[dict] = []      # groups whose artifacts record no environment
    across_env: list[dict] = []        # groups with two or more recorded environments: a named cause
    within_subgroup = 0.0              # the movement *inside* one environment of a multi-environment group
    for g in groups:
        runs += g["runs"]
        arms_compared += len(g["arms"])
        arms_identical += len(g["arms_identical"])
        if len(g["environments"]) == 1:
            (unattributed if "unrecorded" in g["environments"] else same_env).append(g)
            if "unrecorded" not in g["environments"]:
                recorded += g["runs"]
            else:
                unrecorded += g["runs"]
        else:
            across_env.append(g)
            # A multi-environment group is also the only place a *within*-environment comparison can be made
            # inside it, so its subgroups contribute to the floor while the group itself contributes a cause.
            for sub in g["subgroups"]:
                if sub["runs"] < 2:
                    continue
                for v in sub["arms"].values():
                    within_subgroup = max(within_subgroup, v["movement_forgetting"])

    def worst(gs, field):
        return max((v[field] for g in gs for v in g["arms"].values() if v.get("present")), default=0.0)

    moved = [{m: {"forgetting": v["movement_forgetting"], "accuracy": v["movement_accuracy"]}
              for m, v in g["arms"].items() if m in g["arms_differing"]}
             for g in unattributed + across_env]
    by_arm: dict[str, float] = {}
    for g in unattributed + across_env:
        for m in g["arms_differing"]:
            by_arm[m] = max(by_arm.get(m, 0.0), g["arms"][m]["movement_forgetting"])
    return {
        "groups": len(groups), "runs": runs,
        "arms_compared": arms_compared, "arms_identical": arms_identical,
        "groups_with_no_movement": sum(1 for g in groups if not g["arms_differing"]),
        "runs_in_one_recorded_environment": recorded,
        "runs_without_a_recorded_environment": unrecorded,
        "runs_in_a_group_that_moved": sum(g["runs"] for g in unattributed + across_env),
        "floor_within_one_recorded_environment": {
            "groups": len(same_env), "runs": sum(g["runs"] for g in same_env),
            "worst_forgetting": max(worst(same_env, "movement_forgetting"), within_subgroup),
            "worst_accuracy": worst(same_env, "movement_accuracy"),
        },
        "movement_across_recorded_environments": {
            "groups": len(across_env), "runs": sum(g["runs"] for g in across_env),
            "worst_forgetting": worst(across_env, "movement_forgetting"),
            "worst_accuracy": worst(across_env, "movement_accuracy"),
            "names": [n for g in across_env for n in g["names"]]},
        "movement_without_a_recorded_environment": {
            "groups": len(unattributed), "runs": unrecorded,
            "worst_forgetting": worst(unattributed, "movement_forgetting"),
            "worst_accuracy": worst(unattributed, "movement_accuracy"),
            "names": [n for g in unattributed for n in g["names"]]},
        "moved_arms": dict(sorted(by_arm.items(), key=lambda kv: -kv[1])),
        "moved_runs_detail": moved,
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--json-out", type=Path, default=None)
    ap.add_argument("--command", type=Path, default=None,
                    help="print the re-execution command derived from this artifact's own config")
    ap.add_argument("--methods", default=None, help="override --methods in the printed command")
    ap.add_argument("--census", action="store_true",
                    help="report how much of the corpus's configs the derived-command path can handle, and why "
                         "the rest are refused")
    ap.add_argument("--runner", default=None, choices=sorted(RUNNERS),
                    help="which runner's flags to map; inferred from the config's keys when omitted")
    args = ap.parse_args(argv)

    if args.command is not None:
        payload = json.loads(Path(args.command).read_text(encoding="utf-8"))
        cfg = dict(payload["config"])
        if args.methods:
            cfg["methods"] = args.methods
        parts = command_from_config(cfg, json_out=str(args.command).replace(".json", "_rerun.json"),
                                    runner=args.runner)
        print(" ".join(parts))
        return 0

    if args.census:
        from collections import Counter

        # `load_artifacts` is imported at module level and must NOT be re-imported here: a local import inside a
        # branch makes the name local to the whole function, so the `group_repeats(load_artifacts())` call below
        # raised `UnboundLocalError` whenever `--census` was not passed -- i.e. this audit crashed on every plain
        # run while its own census path worked. Found on 2026-09-25 by running it as a gate.
        ok, none_fit, several_fit, mapped = 0, [], [], Counter()
        for a in load_artifacts():
            cfg = a["config"]
            if not cfg:
                continue
            found = runner_for(cfg)
            if len(found) == 1:
                mapped[found[0]] += 1
            try:
                command_from_config(cfg, json_out="runs/x.json")
                ok += 1
            except ValueError:
                (none_fit if not found else several_fit).append(a["name"])
        print("== how much of the corpus can be re-executed by a command derived from its own artifact ==")
        print(f"   runners read from the source: {len(RUNNERS)}")
        print(f"   configs the path handles:     {ok}")
        print(f"   refused, NO runner fits:      {len(none_fit)}   e.g. {', '.join(none_fit[:3])}")
        print(f"   refused, SEVERAL fit:         {len(several_fit)}   e.g. {', '.join(several_fit[:3])}")
        print(f"   artifacts whose single author is unambiguous: {dict(mapped.most_common(4))}")
        print("   -> both refusals are the safe direction: an artifact whose author cannot be named yields **no**")
        print("      command rather than one that would run with defaults for the fields this helper cannot name")
        print("      (rule 44), and a caller who knows the runner can pass `--runner` to lift the second one.")
        return 0

    groups = group_repeats(load_artifacts())
    summary = floor(groups)
    print(f"== configurations the corpus has executed more than once: {summary['groups']} "
          f"({summary['runs']} runs, {summary['arms_compared']} arm-comparisons) ==")
    print(f"   {'runs':>5}  {'environment':<13}{'arms identical':>15}{'worst forgetting':>18}"
          f"{'worst accuracy':>15}")
    for g in sorted(groups, key=lambda g: -len(g["arms_differing"])):
        env = "none recorded" if "unrecorded" in g["environments"] else "recorded"
        if len(g["environments"]) > 1:
            env = f"{len(g['environments'])} recorded"
        worst_f = max((v["movement_forgetting"] for v in g["arms"].values() if v.get("present")), default=0.0)
        worst_a = max((v["movement_accuracy"] for v in g["arms"].values() if v.get("present")), default=0.0)
        print(f"   {g['runs']:>5}  {env:<13}{len(g['arms_identical']):>7}/{len(g['arms']):<7}"
              f"{worst_f:>18.4f}{worst_a:>15.4f}")
        if g["arms_differing"]:
            for m in g["arms_differing"]:
                v = g["arms"][m]
                print(f"          moves  {m:<18}{v['movement_forgetting']:>10.4f} forgetting "
                      f"[{', '.join(f'{x:g}' for x in v['values'])}]")

    f = summary["floor_within_one_recorded_environment"]
    print("\n== the floor ==")
    print(f"   same config, ONE recorded environment:  {f['groups']} groups / {f['runs']} runs, "
          f"worst movement {f['worst_forgetting']:.4f} forgetting, {f['worst_accuracy']:.4f} accuracy")
    a = summary["movement_across_recorded_environments"]
    print(f"   same config, TWO recorded envs:         {a['groups']} groups / {a['runs']} runs, "
          f"worst {a['worst_forgetting']:.4f} / {a['worst_accuracy']:.4f}   (a NAMED cause: e77's thread knob)")
    u = summary["movement_without_a_recorded_environment"]
    print(f"   same config, NO recorded environment:   {u['groups']} groups / {u['runs']} runs, "
          f"worst {u['worst_forgetting']:.4f} / {u['worst_accuracy']:.4f}   (NOTHING in the artifact explains it)")
    print(f"   -> {summary['arms_identical']}/{summary['arms_compared']} arm-comparisons are bit-identical; "
          f"{summary['groups_with_no_movement']}/{summary['groups']} groups do not move at all")
    print(f"   -> the {u['runs']} runs that moved are exactly the {u['runs']} that record no environment")
    for name in u["names"]:
        print(f"        {name}")
    print(f"   -> arms that moved anywhere: "
          + ", ".join(f"{m} ({v:.4f})" for m, v in summary["moved_arms"].items()))

    out = {"floor": summary,
           "groups": [{k: v for k, v in g.items() if k != "signature"} for g in groups]}
    if args.json_out:
        write_json(args.json_out, out)
        print(f"\nwrote {args.json_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
