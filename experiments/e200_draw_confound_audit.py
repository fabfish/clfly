"""E200 -- are the corpus's own comparisons measured on the SAME draws, or on two different ones?

Today's work established three things this audit depends on: the substrate makes at least two RNG draws per run (the
overlap suite's **supports** and the **read-out subset**); two support draws move the learning quantities by 3.3-6.6σ
on identical configurations and identical seeds; and `e198 --reconstruct` can now identify the draw of **264 of the
299** live (artifact, draw) pairs in the corpus, at zero cost. **So the question this asks is answerable for the
corpus as it stands:**

    for every comparison the corpus declares, do both sides draw the same supports and the same read-out subset?

A comparison whose two sides differ in a draw is measuring the draw as well as the manipulation -- which is exactly
what the axis replication was built to detect, one family at a time, and which nothing has ever checked corpus-wide.
**This is analysis only**: it reads artifact metadata, reconstructs draws with `e198`'s validated functions, and never
re-measures anything.

    python -m experiments.e200_draw_confound_audit
    python -m experiments.e200_draw_confound_audit --json-out runs/e200_draw_confound_audit.json

## What a verdict means, and what it does not

`SAME` means both sides' identified draws agree, so the contrast is attributable to the manipulation. `CONFOUNDED`
means a draw differs and the contrast inherits it -- **not** that the contrast is wrong, since a draw difference may
be small (the read-out draw is unresolved on everything it has been tried on) or may be the point (the replication's
families are *designed* to differ in a draw, one level at a time). `UNIDENTIFIED` means at least one side's draw
cannot be established, which after `e198 --reconstruct` is 35 of the 299 live pairs.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from experiments.e188_overlap_contrast import PAIRS as DECLARED_PAIRS, admitting_baseline, load
from experiments.e198_artifact_draw_census import (_circuit_neurons as reconstruct_neurons,
                                                    reconstruct_readout, reconstruct_supports)

RUNS = Path("runs")

#: The dose families, each read level-by-level against the baseline each arm admits. `same_draw_expected` marks the
#: families that are DESIGNED to hold one draw fixed: `e193`'s levels were run at support draw 0 and read-out 0 like
#: their baselines, while `e195`/`e197`/`e199` vary one draw on purpose and are read within themselves.
DOSE_FAMILIES = (
    ("e193 levels (support 0, read-out 0)", "e193_r32_overlap{n:03d}_methods_40reps.json", (25, 50, 75), True),
    ("e195 levels (support 1)", "e195_r32_ovl{n}_ss1_naive_40reps.json", ("00", "05", "10"), True),
    ("e197 levels (support 2)", "e197_r32_ovl{n}_ss2_naive_40reps.json", ("00", "05", "10"), True),
    ("e199 levels (read-out 1)", "e199_r32_ovl{n}_rs1_naive_40reps.json", ("00", "10"), True),
)


def draws_of(d: dict) -> dict:
    """Each draw's KEY -- what decides whether two artifacts drew the same thing -- and its fingerprint.

    **The key and not the fingerprint is what decides a confound**, because a fingerprint bundles the draw with the
    manipulation: two artifacts at different target overlaps necessarily have different support fingerprints (the
    overlap IS the support construction) while using the SAME support draw. Comparing fingerprints flagged 19 of 19
    pairs on the first run of this audit, including every level-against-its-baseline comparison whose whole point is
    that the overlaps differ -- which is the false-alarm class `e126`'s preamble is about.

    A key is `None` when the draw is not live on that artifact.
    """
    c = d.get("config") or {}
    n = reconstruct_neurons(d)
    out = {}
    size = c.get("readout_size")
    if size and n and 0 < size < n:
        seed = c.get("readout_seed")
        out["readout"] = {"key": (seed if seed is not None else c.get("seed0", 0), n, size),
                          "fingerprint": reconstruct_readout(d)}
    if c.get("input_overlap") is not None and n:
        seed = c.get("support_seed")
        out["support_draw"] = {"key": (seed if seed is not None else c.get("seed0", 0), n, c.get("support")),
                               "fingerprint": reconstruct_supports(d)}
    return out


def compare(a: Path, b: Path) -> dict:
    """One pair's draw agreement, per draw, judged on the KEY and reported with both fingerprints.

    `same draw` means both sides used the same (seed, neuron count, size) -- so the supports may still *differ*
    because the manipulation says they must, which is why the fingerprints are printed beside the verdict rather
    than used as it.
    """
    da, db = load(a), load(b)
    fa, fb = draws_of(da), draws_of(db)
    out = {"a": Path(a).name, "b": Path(b).name, "per_draw": {}}
    for key in ("readout", "support_draw"):
        ka, kb = (fa.get(key) or {}).get("key"), (fb.get(key) or {}).get("key")
        if ka is None and kb is None:
            out["per_draw"][key] = "not live"
        elif ka is None or kb is None:
            out["per_draw"][key] = "live on one side only"
        elif ka == kb:
            out["per_draw"][key] = "same draw"
        else:
            out["per_draw"][key] = "DIFFERENT DRAW"
    verdicts = set(out["per_draw"].values())
    out["verdict"] = ("CONFOUNDED" if "DIFFERENT DRAW" in verdicts else
                      "partly unidentified" if verdicts & {"live on one side only"} else
                      "not live" if verdicts == {"not live"} else "SAME DRAW")
    return out


def audit(runs_dir: Path = RUNS) -> dict:
    rows = []
    for label, method, lo, hi, expect in DECLARED_PAIRS:
        a, b = runs_dir / lo, runs_dir / hi
        if not a.is_file() or not b.is_file():
            rows.append({"what": label, "family": "e188/e191 declared pairs", "status": "artifact missing"})
            continue
        rows.append({"what": label, "family": "e188/e191 declared pairs", **compare(a, b)})
    for fam, pattern, levels, _same in DOSE_FAMILIES:
        # A family's OWN endpoints come first: the draw-varying families (e195/e197/e199) are correctly REFUSED
        # against draw 0's baselines, since `support_seed` is not an inert field, so without their own endpoints their
        # pairs would silently be absent from this audit -- and an absent pair reads like a clean one.
        own = [runs_dir / pattern.format(n=n) for n in levels]
        own = [f for f in own if f.is_file()]
        for n in levels:
            level = runs_dir / pattern.format(n=n)
            if not level.is_file():
                continue
            d = load(level)
            for method in sorted(d.get("methods") or {}):
                use, _ = admitting_baseline(d.get("config") or {}, method,
                                            own + [runs_dir / "e116_r32_40reps.json",
                                                   runs_dir / "e140_r32_methods_plastic_40reps.json",
                                                   runs_dir / "e153_r32_overlap1_methods_40reps.json"])
                if use is None:
                    continue
                rows.append({"what": f"{method} at each level", "family": fam, "level": level.name,
                             **compare(Path(use), level)})
    return {"pairs": rows}


def report(res: dict) -> int:
    rows = res["pairs"]
    print(f"   == are the corpus's comparisons measured on the same draws: {len(rows)} pairs ==")
    tally = {}
    for r in rows:
        tally[r.get("verdict", r.get("status"))] = tally.get(r.get("verdict", r.get("status")), 0) + 1
    for k, v in sorted(tally.items(), key=lambda kv: -kv[1]):
        print(f"   {k:14} {v:4}")
    for key in ("readout", "support_draw"):
        conf = [r for r in rows if r.get("per_draw", {}).get(key) == "DIFFERENT DRAW"]
        un = [r for r in rows if r.get("per_draw", {}).get(key) == "live on one side only"]
        print(f"   {key:14} confounded in {len(conf)}, unidentified in {len(un)}")
    print()
    print("   the CONFOUNDED pairs, named:")
    for r in rows:
        if r.get("verdict") == "CONFOUNDED":
            which = [k for k, v in r["per_draw"].items() if v == "DIFFERENT DRAW"]
            print(f"     [{r.get('family', '?')[:34]}] {r['a']} vs {r['b']}  differs in {', '.join(which)}")
    return 0


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--runs", type=Path, default=RUNS)
    p.add_argument("--json-out", type=Path, default=None)
    a = p.parse_args(argv)
    res = audit(a.runs)
    if a.json_out:
        from clfly.bench.artifacts import write_json
        write_json(a.json_out, res)
        print(f"wrote {a.json_out}")
    return report(res)


if __name__ == "__main__":
    sys.exit(main())
