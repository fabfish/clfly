"""E76 -- the C2b rung question at sixteen replicates on BOTH rungs, which e46 left half-done.

`e46` is the project's best-powered C2b measurement: `cell_class` at lambda = 0.1 with **sixteen**
replicates, where the published three-replicate figure had been -0.0648 (2.65 sigma) and is
**+0.0039 +- 0.0161 (0.24 sigma)** instead. It closed with what remained:

    the paired `side - cell_class` contrast at 2.13 sigma loses its main term; `side` needs its own
    16-replicate run before the contrast can be restated.

`e60` is that run -- `--basis side`, the same lambda / Fisher batches / iters / repeats -- and this
script restates the contrast.

Two checks come first, because comparing two runs is where this project has been wrong before: the two
configurations are diffed **field by field**, and the `naive` arms are required to agree bit for bit.
The naive arm carries no penalty and no basis, so it is the one arm the two runs must share exactly if
the seeds are aligned -- and if they are not aligned, every paired figure below is meaningless.

    python -m experiments.e76_c2b_cross_rung_powered
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from scipy.stats import binomtest

SIDE = "runs/e60_side_lam0.1_16reps.json"
CELL_CLASS = "runs/e46_c2b_powered.json"

#: What the three-replicate run published, for the comparison.
PUBLISHED_3REP = {"side": (0.0069, 0.48), "cell_class": (-0.0648, 2.65),
                  "side - cell_class": (0.0718, 2.13)}

METRICS = ("final_accuracy", "mean_forgetting")


def load(path: str):
    p = Path(path)
    if not p.exists():
        return None
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def per_replicate(blk: dict, metric: str) -> np.ndarray:
    return np.asarray([r[metric] for r in blk["replicates"]], dtype=float)


def paired_stats(dl: np.ndarray) -> dict:
    n = dl.size
    mean = float(dl.mean())
    sem = float(dl.std(ddof=1) / np.sqrt(n)) if n > 1 else float("nan")
    loo, flip, lev = [], False, 0.0
    for i in range(n):
        keep = np.delete(dl, i)
        s = float(keep.std(ddof=1) / np.sqrt(keep.size))
        loo.append(abs(float(keep.mean() / s)) if s else float("inf"))
        if sem:
            lev = max(lev, abs(float(keep.mean()) - mean) / sem)
        if np.sign(keep.mean()) != np.sign(mean):
            flip = True
    pos = int((dl > 0).sum())
    neg = int((dl < 0).sum())
    tied = int((dl == 0).sum())
    p = float(binomtest(pos, pos + neg).pvalue) if (pos + neg) else float("nan")
    return dict(n=n, delta=mean, sem=sem, sigma=(abs(mean) / sem if sem else float("inf")),
                signs="".join("+" if v > 0 else ("0" if v == 0 else "-") for v in dl),
                n_pos=pos, n_neg=neg, n_tied=tied, sign_p=p,
                loo_min=float(min(loo)), loo_flips=bool(flip), leverage=float(lev))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json-out", default="runs/e76_c2b_cross_rung_powered.json")
    args = ap.parse_args()

    a, b = load(SIDE), load(CELL_CLASS)
    if a is None or b is None:
        raise SystemExit(f"need both artifacts ({SIDE}, {CELL_CLASS})")

    print("=" * 108)
    print("1. THE TWO RUNS, DIFFED FIELD BY FIELD BEFORE ANYTHING IS COMPARED")
    print("=" * 108)
    keys = sorted(set(a["config"]) | set(b["config"]))
    #: `basis` is the variable under study, so it is *expected* to differ and is the only field that
    #: may.  Everything else -- lambda, Fisher batches, iters, repeats, seeds, circuit, head, read-out,
    #: noise -- has to match or the two runs are not the same computation.
    EXPECTED = {"json_out", "basis"}
    differ = [(k, a["config"].get(k), b["config"].get(k)) for k in keys if k not in EXPECTED
              and a["config"].get(k) != b["config"].get(k)]
    basis_a, basis_b = a["config"].get("basis"), b["config"].get("basis")
    print(f"   fields compared (excluding `json_out` and `basis`): {len(keys) - 2};"
          f"   fields that differ: {len(differ)}")
    for k, va, vb in differ:
        print(f"     {k}: side = {va!r}   cell_class = {vb!r}")
    print(f"   `basis` differs by design: {basis_a!r} against {basis_b!r} -- it is the variable")
    if differ:
        print("\n   an unexpected difference means the two runs are not the same computation, and the")
        print("   paired figures below would be comparing different things")
    else:
        print("   -> identical apart from the basis under study, at the same sixteen replicate seeds")

    na, nb = a["methods"]["naive"], b["methods"]["naive"]
    same = all(x["final_accuracy"] == y["final_accuracy"] and x["mean_forgetting"] == y["mean_forgetting"]
               for x, y in zip(na["replicates"], nb["replicates"]))
    print(f"\n   naive arms bit-identical across the {len(na['replicates'])} replicates: {same}")
    if not same:
        raise SystemExit("naive arms disagree -- the replicate seeds are not aligned, stop")
    out = {"configs_identical": not differ, "differing_fields": differ, "naive_aligned": same}

    print()
    print("=" * 108)
    print("2. EACH RUNG'S OWN BIOLOGICAL-MINUS-CONTROL DELTA, PAIRED OVER 16 REPLICATES")
    print("=" * 108)
    rows = {}
    for metric in METRICS:
        print(f"   {metric}")
        print(f"   {'rung':<16}{'delta':>11}{'sem':>10}{'sigma':>8}{'signs':>19}{'p':>9}"
              f"{'LOO min':>9}{'flip':>6}{'lev':>6}   published (3 reps)")
        for name, art in (("side", a), ("cell_class", b)):
            st = paired_stats(per_replicate(art["methods"]["ewc-block"], metric) -
                              per_replicate(art["methods"]["ewc-block-rand"], metric))
            pub, psig = PUBLISHED_3REP[name]
            print(f"   {name:<16}{st['delta']:>+11.5f}{st['sem']:>10.5f}{st['sigma']:>8.2f}"
                  f"{st['signs']:>19}{st['sign_p']:>9.4f}{st['loo_min']:>9.2f}"
                  f"{str(st['loo_flips']):>6}{st['leverage']:>6.2f}   {pub:+.4f} / {psig:.2f}σ")
            rows[f"{name}/{metric}"] = st
        print()
    out["rungs"] = rows

    print("=" * 108)
    print("3. THE CONTRAST e46 ASKED FOR -- `side` MINUS `cell_class`, PAIRED OVER THE SAME 16 SEEDS")
    print("=" * 108)
    print("   this is the one figure the three-replicate run published as its cross-rung result,")
    print("   and the only one that was never restated at power\n")
    print(f"   {'metric':<18}{'delta':>11}{'sem':>10}{'sigma':>8}{'signs':>19}{'p':>9}{'LOO min':>9}{'flip':>6}")
    cross = {}
    for metric in METRICS:
        ds = per_replicate(a["methods"]["ewc-block"], metric) - per_replicate(a["methods"]["ewc-block-rand"], metric)
        dc = per_replicate(b["methods"]["ewc-block"], metric) - per_replicate(b["methods"]["ewc-block-rand"], metric)
        st = paired_stats(ds - dc)
        print(f"   {metric:<18}{st['delta']:>+11.5f}{st['sem']:>10.5f}{st['sigma']:>8.2f}"
              f"{st['signs']:>19}{st['sign_p']:>9.4f}{st['loo_min']:>9.2f}{str(st['loo_flips']):>6}")
        cross[metric] = st
    out["cross_rung"] = cross
    pub, psig = PUBLISHED_3REP["side - cell_class"]
    print(f"\n   published at 3 replicates: {pub:+.4f} at {psig:.2f} sigma")

    print()
    print("=" * 108)
    print("4. AND WHAT THE RUN CAN SEE AT ALL")
    print("=" * 108)
    floors = {}
    for name, st in (("side", rows["side/final_accuracy"]),
                     ("cell_class", rows["cell_class/final_accuracy"])):
        floor = 2.0 * st["sem"]
        floors[name] = floor
        claimed = abs(PUBLISHED_3REP[name][0])
        print(f"   {name:<12} detection floor at 16 replicates (2 sems) = {floor:.4f};  "
              f"the three-replicate claim was {claimed:.4f}, i.e. {claimed/floor:.2f}x the floor")
    cross_floor = 2.0 * cross["final_accuracy"]["sem"]
    cross_claimed = abs(PUBLISHED_3REP["side - cell_class"][0])
    print(f"   {'cross-rung':<12} detection floor = {cross_floor:.4f};  "
          f"the three-replicate claim was {cross_claimed:.4f}, i.e. "
          f"{cross_claimed/cross_floor:.2f}x the floor")
    print(f"\n   so the three-replicate `cell_class` figure was {abs(PUBLISHED_3REP['cell_class'][0])/floors['cell_class']:.1f}x")
    print(f"   the powered run's own detection floor and is not there, and the cross-rung figure was")
    print(f"   {cross_claimed/cross_floor:.1f}x its floor and is not there either.")
    out["detection_floors"] = dict(floors, **{"side - cell_class": cross_floor})

    Path(args.json_out).parent.mkdir(parents=True, exist_ok=True)
    with open(args.json_out, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1, default=str)
    print(f"\nwrote {args.json_out}")


if __name__ == "__main__":
    main()
