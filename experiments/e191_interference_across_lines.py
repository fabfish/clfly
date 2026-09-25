"""E191 -- the cross-line overlap comparison on the quantity that SHARES A NAME, per pair.

`e189` compared the analytic line's `interference` with the network line's **accuracy drop**, and localised the
disagreement to the adjacent pairs. That was a proxy, and the corpus does not need one: `e8_rate_network.py`
records an **interference decomposition** for every pair a run makes available --
`methods.<m>.replicates[r].interference[j]["per_task"][k]` is the first-order damage to task `j` from the
displacement that training task `k` caused. So both lines can be split by task distance **on their own interference
terms**, which is what this reads.

    python -m experiments.e191_interference_across_lines

**Why it is not a repetition of `e189`.** The proxy's standard errors are large -- on the accuracy drop the network
line's FAR component clears 2σ in one comparison of nine -- and `e189` therefore retracted its own first claim that
the far component is shared between the lines. **On the interference account that retraction is wrong**: the far
component rises at 2.1–3.2σ in five of five admitted comparisons. So the finding is the composition `e189`'s first
version printed and its second version refused: **the lines disagree on the adjacent pairs and agree on the distant
ones** -- and the reason the second version could not see the far agreement is the proxy, not the data.

**And the dose read's admission rule is what caught a 333x penalty step dressed as an overlap effect**: the three
`e193` commands inherited the runner's default `--lam 1.0` while the family they are registered against runs
`--lam 3e-3`, and `lam` is inert for `naive` and is the penalty strength for the block arms. Each arm therefore takes
the first candidate baseline whose config diff is inert **for that arm** and that **carries that arm**, the row prints
the overlap pair it measures, and every choice is reversible by reading the row.

**One limit, found while writing this, and it bounds the split rather than the claim.** The artifact's
`interference[j]` carries `per_task[k]` as a dict per ordered pair (`first_order`, `cosine`, `grad_norm`,
`disp_norm`) but `second_order` as a **single** term per task `j`, taken against the *cumulative* displacement -- so
the second-order component **cannot** be split by task distance, and this audit reads the first-order one because
that is the only one the corpus records per pair.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from clfly.bench.artifacts import write_json
from experiments.e151_pertask_contrast_audit import paired
from experiments.e188_overlap_contrast import INERT_FOR, PAIRS, differing_fields, load

RUNS = Path("runs")
ANALYTIC = "e7_interference.json"

#: What a TARGET `--input-overlap` achieves as a Jaccard overlap, on `mb+cx+al@n1307` with three tasks of 80
#: neurons at seed 0 -- the circuit and construction every network run uses. Measured by
#: `overlap_controlled_supports` directly (and reproduced in the registration of the intermediate levels); `e7`'s
#: controlled sweep reports the same four decimals for the levels it shares, which is what makes the two lines'
#: x-axes commensurable. The table is a property of the circuit, the support and the seed and NOT of the annotation:
#: a reader re-running this on a different circuit must recompute it.
ACHIEVED_OVERLAP = {0.0: 0.0000, 0.25: 0.1429, 0.5: 0.3333, 0.75: 0.6000, 1.0: 1.0000}
#: The change from the disjoint arm that the registered P1 calls "more than half done", on `naive`: half of the
#: measured 0 -> 1 rise of +0.1234.
P1_HALF_DONE = 0.0617
#: P2's bar as registered: "the network's near rise should be >= 60% complete by achieved 0.3333", where "complete"
#: is of the NETWORK's OWN 0 -> 1 rise. Both texts carrying P2 -- the registration finding and the plan's cell --
#: state it that way, and neither says "60% of the analytic line", so the bar is absolute. The first version of this
#: read applied `prog >= 0.6 * analytic` instead, which at the midpoint is 45.9% against the registered 60% and so
#: would have decided the verdict on a bar the registration does not state.
P2_BAR = 0.60
#: What the registration QUOTES for the analytic line's own completion at the midpoint, and what the artifact
#: actually gives. The registered sentence says **80%**; the parenthetical it offers to support that number
#: (+0.0258 -> +0.0051 of a total fall to -0.0013) works out to **76%**, and `analytic_progress` computes **0.7645**
#: from `e7`'s six levels. So the sentence disagrees with its own arithmetic, and the read prints the artifact's
#: value beside the registration's rather than letting either stand unlabelled.
P2_REGISTERED_ANALYTIC_AT_MIDPOINT = 0.80

#: The directions each line states today, on the quantity this file reads. The network ones are tallies because
#: seven admitted comparisons will not be unanimous; the analytic ones are exact, being one artifact's six levels.
DECLARED = {("analytic", "near"): "falls", ("analytic", "far"): "rises"}
DECLARED_TALLY = {"near": {"rises": 8, "falls": 0, "unresolved": 1},      # the unresolved one is `replay`, 1.6s
                  "far": {"rises": 9, "falls": 0, "unresolved": 0}}       # 2.1 sigma to 7.4 sigma


def per_replicate_split(path: Path, method: str) -> dict | None:
    """Each replicate's mean interference over its adjacent pairs and over its distant ones.

    The split is by task distance inside one replicate, so the two components are paired observations of the same
    run rather than two pools -- and pairing across the overlap arms is then `e151.paired` on the per-replicate
    series.
    """
    if not Path(path).is_file():
        return None
    d = json.loads(Path(path).read_text(encoding="utf-8"))
    arm = (d.get("methods") or {}).get(method)
    if arm is None:
        return None
    near, far = [], []
    for rep in arm["replicates"]:
        n, f = [], []
        for j, rec in enumerate(rep.get("interference") or []):
            per_task = rec.get("per_task") or []
            for k in range(j + 1, len(per_task)):
                val = per_task[k]
                val = val.get("first_order", np.nan) if isinstance(val, dict) else val
                (n if k - j == 1 else f).append(val)
        near.append(float(np.mean(n)) if n else np.nan)
        far.append(float(np.mean(f)) if f else np.nan)
    return {"near": np.array(near), "far": np.array(far), "n_pairs_near": len(n), "n_pairs_far": len(f)}


def analytic_split(path: Path = RUNS / ANALYTIC) -> list[dict]:
    d = json.loads(path.read_text(encoding="utf-8"))
    return [{"level": r["level"], "near": r["mean_interference_near"], "far": r["mean_interference_far"]}
            for r in d["controlled"]]


def audit(runs_dir: Path = RUNS, pairs=PAIRS, declared=DECLARED) -> dict:
    levels = analytic_split(runs_dir / ANALYTIC)
    analytic = {c: ("rises" if levels[-1][c] > levels[0][c] else "falls" if levels[-1][c] < levels[0][c]
                    else "flat") for c in ("near", "far")}
    rows, refused = [], []
    tally = {c: {"rises": 0, "falls": 0, "unresolved": 0} for c in ("near", "far")}
    for label, method, lo, hi, expect in pairs:
        pa, pb = runs_dir / lo, runs_dir / hi
        if not pa.is_file() or not pb.is_file():
            refused.append({"label": label, "why": "artifact missing"})
            continue
        bad = {k: v for k, v in differing_fields(load(pa)["config"], load(pb)["config"]).items()
               if k not in INERT_FOR.get(method, set())}
        if bad or expect != "pair":
            refused.append({"label": label, "why": f"not a pair: {sorted(bad)}" if bad else "declared a refusal"})
            continue
        a, b = per_replicate_split(pa, method), per_replicate_split(pb, method)
        # BOTH arms have to carry the terms: checking only the first let a payload with no `interference` key
        # through as a row of NaNs, which is a number where a refusal belongs (the second version of `e188`'s
        # sibling audit made the same mistake with `retention`).
        if a is None or b is None or min(a["n_pairs_near"], b["n_pairs_near"], a["n_pairs_far"], b["n_pairs_far"]) == 0:
            refused.append({"label": label, "why": "no per-pair interference in one of the two payloads"})
            continue
        row = {"label": label, "method": method, "n": len(a["near"])}
        for c in ("near", "far"):
            p = paired(b[c], a[c])
            r = abs(p["change"]) / p["sem"] if p["sem"] else 0.0
            direction = "rises" if (r >= 2 and p["change"] > 0) else "falls" if (r >= 2 and p["change"] < 0) else "unresolved"
            tally[c][direction] += 1
            row[c] = {"change": p["change"], "sem": p["sem"], "sigma": r, "direction": direction,
                      "level0": float(np.nanmean(a[c])), "level1": float(np.nanmean(b[c]))}
        rows.append(row)
    mismatches = [{"what": f"analytic {c}", "declared": want, "got": analytic[c]}
                  for (line, c), want in declared.items() if line == "analytic" and analytic[c] != want]
    mismatches += [{"what": f"network {c} tally", "declared": want, "got": tally[c]}
                   for c, want in DECLARED_TALLY.items() if tally[c] != want]
    return {"analytic_levels": levels, "analytic_directions": analytic, "comparisons": rows,
            "network_tally": tally, "refused": refused, "mismatches": mismatches,
            "n_mismatches": len(mismatches)}


def report(res: dict) -> int:
    print("   == the analytic line, its own interference terms, six levels ==")
    print(f"   near: " + " -> ".join(f"{r['near']:+.4f}" for r in res["analytic_levels"]))
    print(f"   far : " + " -> ".join(f"{r['far']:+.4f}" for r in res["analytic_levels"]))
    print(f"        directions: near {res['analytic_directions']['near']}, far {res['analytic_directions']['far']}")
    print("   == the network line, its own interference terms, split by task distance ==")
    print(f"   {'comparison':48} {'near change':>22} {'far change':>22}")
    for r in res["comparisons"]:
        def fmt(c):
            return f"{r[c]['change']:+.5f}+/-{r[c]['sem']:.5f}({r[c]['sigma']:.1f}s)"
        print(f"   {r['label']:48} {fmt('near'):>22} {fmt('far'):>22}")
    for c in ("near", "far"):
        t = res["network_tally"][c]
        print(f"   {c:4}: {t['rises']} rise at 2 sigma, {t['falls']} fall, {t['unresolved']} unresolved")
    for r in res["refused"]:
        print(f"   refused -- {r['label']}: {r['why']}")
    print("   == the composition ==")
    print("        NEAR: analytic FALLS, network RISES -- the two lines are resolved and opposite (this is e189's")
    print("        localisation, now on the quantity that shares a name)")
    print("        FAR : both RISE, and the network's far component is resolved in NINE of nine comparisons")
    print("        (2.1 sigma to 7.4 sigma) on the account's own terms -- which is what e189's accuracy-drop proxy")
    print("        could not see, and the reason its second version retracted a claim its first version had right")
    print(f"   declarations the corpus contradicts: {res['n_mismatches']}")
    for m in res["mismatches"]:
        print(f"        {m['what']}: declared {m['declared']}, got {m['got']}")
    return res["n_mismatches"]


def analytic_progress(levels: list[float], path: Path = RUNS / ANALYTIC) -> dict:
    """How far the analytic near component has fallen, as a FRACTION of its own 0 -> 1 fall, per achieved overlap.

    P2 is a claim about the network's *shape* matching the analytic line's timing, and a shape claim needs both
    lines expressed the same way: the fraction of the total response completed at a given achieved overlap. The
    analytic fraction is fixed by `e7`'s six levels and is computed here from the artifact rather than quoted, so it
    cannot drift from the table it comes from.
    """
    block = analytic_split(path)
    total = block[0]["near"] - block[-1]["near"]
    if not total:
        return {}
    return {ach: (block[0]["near"] - next(b["near"] for b in block if abs(b["level"] - lv) < 1e-9)) / total
            for ach, lv in ((0.0526, 0.1), (0.1429, 0.25), (0.3333, 0.5), (0.6000, 0.75), (1.0, 1.0))
            if any(abs(b["level"] - lv) < 1e-9 for b in block)}


def admitting_baseline(level_config: dict, method: str, candidates: list[Path]) -> tuple[Path | None, list[str]]:
    """The first candidate baseline whose config diff from the level is INERT for this arm, and why others failed.

    This is the rule the two-point audit applies and the dose read was written without -- and it cost a real catch:
    the three launched level commands inherited the runner's default `--lam 1.0` while `e140`, the family's disjoint
    arm, runs `--lam 3e-3`. `lam` is inert for `naive` and is the penalty strength for the block arms, so the naive
    comparison is valid against `e140` and the block comparisons are not; they are valid against `e153`/`e159`, which
    are the lambda-1.0 family. A read that paired them all against `e140` would have reported a 333x penalty step as
    an overlap effect.
    """
    refusals = []
    for cand in candidates:
        if not Path(cand).is_file():
            refusals.append(f"{Path(cand).name}: absent")
            continue
        payload = load(cand)
        if method not in (payload.get("methods") or {}):
            refusals.append(f"{Path(cand).name}: does not carry the {method} arm")
            continue
        diff = sorted(differing_fields(payload["config"], level_config))
        bad = [k for k in diff if k not in INERT_FOR.get(method, set())]
        if bad:
            refusals.append(f"{Path(cand).name}: differs in {bad}, which {method} reads")
            continue
        return cand, refusals
    return None, refusals


def dose_read(levels: list[Path], baseline: Path = Path("runs/e140_r32_methods_plastic_40reps.json"),
              runs_dir: Path = RUNS, overlap1: Path = Path("runs/e144_r32_overlap1_methods_40reps.json"),
              candidates: list[Path] | None = None) -> dict:
    """Each intermediate level paired against the disjoint baseline, arm by arm, in the interference account.

    This is the read the registration of the intermediate levels asks for and it exists before the artifacts do, so
    that the level-by-level verdict is one command rather than a fresh argument -- which is what `e190` bought for
    `e178`. P1's bar is computed from the measured 0 -> 1 rise rather than restated: the registered sentence is that
    the value at achieved 0.3333 is *closer to the 1.0 end than to the 0.0 end*, i.e. more than half the 0 -> 1
    change.
    """
    base = load(baseline) if Path(baseline).is_file() else None
    rows = []
    for level in levels:
        if not Path(level).is_file():
            rows.append({"level": Path(level).name, "status": "not written yet"})
            continue
        d = load(level)
        target = (d.get("config") or {}).get("input_overlap")
        out = {"level": Path(level).name, "target_overlap": target,
               "achieved_overlap": ACHIEVED_OVERLAP.get(target), "arms": {}}
        if base is None:
            out["status"] = "baseline missing"
            rows.append(out)
            continue
        # the methods to try are the union of what the CANDIDATE baselines carry, intersected with the level's --
        # intersecting with the first baseline alone meant a level whose only arm is admitted by the second
        # baseline iterated over nothing and came out empty
        pool: set[str] = set()
        for cand in (candidates or [baseline]):
            if Path(cand).is_file():
                pool |= set((load(cand).get("methods") or {}))
        for method in sorted(pool & set(d.get("methods", {}))):
            use, refusals = admitting_baseline(d.get("config") or {}, method,
                                              candidates or [Path("runs/e116_r32_40reps.json"), baseline,
                                              Path("runs/e153_r32_overlap1_methods_40reps.json")])
            if use is None:
                out.setdefault("refused_arms", {})[method] = refusals
                continue
            a, b = per_replicate_split(use, method), per_replicate_split(level, method)
            if a is None or b is None or min(a["n_pairs_near"], b["n_pairs_near"], a["n_pairs_far"],
                                             b["n_pairs_far"]) == 0:
                continue
            base_overlap = (load(use)["config"] or {}).get("input_overlap")
            entry = {"n": len(a["near"]), "baseline": Path(use).name, "baseline_overlap": base_overlap,
                     "refusals": refusals}
            for comp in ("near", "far"):
                pn = paired(b[comp], a[comp])
                r = abs(pn["change"]) / pn["sem"] if pn["sem"] else 0.0
                entry[comp] = {"change": pn["change"], "sem": pn["sem"], "sigma": r,
                               "level0": float(np.nanmean(a[comp])), "level1": float(np.nanmean(b[comp]))}
            entry["P1_half_done"] = (entry.get("near", {}).get("change", 0.0) > P1_HALF_DONE
                                     if method == "naive" else None)
            # P2: the network's progress is its rise at this level over its OWN 0 -> 1 rise, and the bar is 60% of
            # it (see P2_BAR for why the sentence's "complete" is of the network's own rise).
            # The denominator is a 0 -> 1 rise ONLY when the arm's own admitted baseline sits at overlap 0.0. For
            # the block arms the admitted baseline is `e153`, which is ITSELF at overlap 1.0 (`e144` is the other
            # overlap-1 artifact the anchor names), so this pairing is a difference between two runs at the same
            # input overlap: it moves with `lam` and with `replay`, not with the x-axis. The first version printed
            # it as "N% of the line's own 0->1 rise" and gave the two block arms a P2 verdict off it (1% and 2%
            # against the analytic 40%), which is a statement about a quantity that was never measured. The
            # pairing is still recorded, under a name that says what it is, and no fraction is taken from it.
            # the replicate count has to agree before the pairing exists: without this a synthetic level paired
            # against the live overlap-1 artifact raised a broadcast error inside `paired` rather than being
            # refused, which is the same class of defect as an arm with the wrong count in `e188`'s audit
            full = per_replicate_split(overlap1, method) if Path(overlap1).is_file() else None
            if full is not None and len(full["near"]) != len(a["near"]):
                full = None
            if full is not None:
                pf = paired(full["near"], a["near"])
                anchor_overlap = (load(overlap1)["config"] or {}).get("input_overlap")
                if base_overlap == 0.0 and anchor_overlap == 1.0:
                    entry["full_rise"] = {"change": pf["change"], "sem": pf["sem"]}
                    if pf["change"]:
                        entry["progress_fraction"] = entry["near"]["change"] / pf["change"]
                else:
                    entry["anchor_minus_baseline"] = {
                        "change": pf["change"], "sem": pf["sem"], "baseline_overlap": base_overlap,
                        "anchor_overlap": anchor_overlap,
                        "why": "not a 0 -> 1 rise: this arm's own admitted baseline is not at overlap 0.0, so the "
                               "anchor pairing is a difference between two runs at the same input overlap"}
            out["arms"][method] = entry
        rows.append(out)
    return {"baseline": Path(baseline).name, "overlap1": Path(overlap1).name, "levels": rows,
            "analytic_progress": analytic_progress([0.0526, 0.1429, 0.3333, 0.6000, 1.0])}


def report_dose(res: dict) -> int:
    print(f"   == the dose-response: each level against the baseline each ARM admits (declared inert fields decide) ==")
    missing = 0
    analytic_mid = res["analytic_progress"].get(0.3333)
    for row in res["levels"]:
        if row.get("status"):
            print(f"        {row['level']}: {row['status']}")
            missing += 1
            continue
        print(f"        {row['level']}: target {row['target_overlap']} -> achieved Jaccard "
              f"{row['achieved_overlap']}")
        for method, e in row["arms"].items():
            near, far = e.get("near"), e.get("far")
            def fmt(c):
                return f"{c['change']:+.4f}+/-{c['sem']:.4f}({c['sigma']:.1f}s)" if c else "n/a"
            # The registered P1 bar is a statement about achieved 0.3333 -- the MIDPOINT -- and the first version
            # printed "NOT met" at every level, which is a claim the registration does not make (and fired at
            # achieved 0.1429, where P1 says nothing).
            at_midpoint = abs((row["achieved_overlap"] or 0) - 0.3333) < 1e-9
            tag = ""
            if method == "naive" and at_midpoint:
                tag = ("   P1's bar (> +0.0617, half the 0->1 rise) " +
                       ("MET" if near and near["change"] > P1_HALF_DONE else "NOT met"))
            elif method == "naive":
                tag = "   (P1's bar applies at achieved 0.3333, not here)"
            prog = e.get("progress_fraction")
            analytic = res["analytic_progress"].get(row["achieved_overlap"])
            ptxt = ""
            if prog is not None and analytic is not None:
                # The verdict uses the REGISTERED bar -- 60% of the network's own 0 -> 1 rise -- and the analytic
                # line's progress is printed as context, explicitly as the ratio it is rather than as a second
                # bar. The first version applied `prog >= 0.6 * analytic`, which is a 14-point looser threshold at
                # the midpoint and is nowhere in the registration. The verdict is withheld away from the midpoint,
                # for the reason P1's bar is: the sentence is written for achieved 0.3333.
                verdict = (" -- MET" if prog >= P2_BAR else " -- NOT met") if at_midpoint else \
                    "   (P2's bar is written for achieved 0.3333, not here)"
                ptxt = (f"   P2: {100 * prog:.0f}% of its own 0->1 rise (bar {100 * P2_BAR:.0f}%){verdict}"
                        f"   [the analytic line is {100 * analytic:.0f}% there, i.e. this line is at "
                        f"{100 * prog / analytic:.0f}% of the analytic's progress]")
            elif e.get("anchor_minus_baseline"):
                ptxt = ("   P2: withheld -- this arm's admitted baseline is itself at overlap "
                        f"{e['anchor_minus_baseline']['baseline_overlap']}, so the anchor pairing is not a 0->1 rise")
            pair = f"{e.get('baseline_overlap')} -> {row['target_overlap']}"
            print(f"             {method:16} {pair:14} vs {e.get('baseline', '?')[:24]:26} near {fmt(near):24} "
                  f"far {fmt(far):24} n {e['n']}{tag}{ptxt}")
    if analytic_mid is not None:
        print(f"        (P2's registration quotes the analytic line at "
              f"{100 * P2_REGISTERED_ANALYTIC_AT_MIDPOINT:.0f}% of its fall at achieved 0.3333, while `e7` gives "
              f"{100 * analytic_mid:.1f}% -- and the registration's own parenthetical arithmetic gives 76%. The bar "
              f"is on the NETWORK's own rise, so this discrepancy moves the context and not the bar.)")
    print("        (the achieved overlaps are a property of mb+cx+al@n1307, 3 tasks of 80, seed 0: recompute them "
          "for any other circuit.)")
    return missing


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--runs", type=Path, default=RUNS)
    p.add_argument("--dose", type=Path, action="append", default=None,
                   help="an artifact at an intermediate overlap level, paired against --baseline; repeatable")
    p.add_argument("--baseline", type=Path, action="append", default=None,
                   help="candidate disjoint baselines, tried in order and admitted per ARM (repeatable; default e140 then e153)")
    p.add_argument("--json-out", type=Path, default=None)
    args = p.parse_args(argv)

    if args.dose:
        cands = args.baseline or [Path("runs/e116_r32_40reps.json"),
                                  Path("runs/e140_r32_methods_plastic_40reps.json"),
                                  Path("runs/e153_r32_overlap1_methods_40reps.json")]
        dose = dose_read(args.dose, cands[0], args.runs, candidates=cands)
        n = report_dose(dose)
        if args.json_out:
            write_json(args.json_out, {"dose": dose})
            print(f"wrote {args.json_out}")
        return 0
    res = audit(args.runs)
    n = report(res)
    if args.json_out:
        write_json(args.json_out, res)
        print(f"wrote {args.json_out}")
    return 0 if n == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
