"""E64 -- the predictor's matched-pair record checked **per seed**, which was the last headline number without one.

The project's predictor is quoted as "**13 of 13** on every pair the excess metric can resolve, with the
sign record 24 of 25 overall".  Two earlier fires closed most of the rule-8 gaps -- `e47`/`e48` for the
C1 contrast, `e54` for the `naive` arm, `e57`+`e58` for the basis ladders -- and this one was the last:
`e6_predictor_6.json` stores only pooled means, so the 13 could not be re-analysed paired.

`e64` re-runs the same five conditions at the same six seeds with per-seed storage.  Every basis in a
condition sees the same task geometries **in the same order**, so a biological basis and its
size-matched control are matched observations and the contrast between them is a *paired* quantity.
This script asks the three questions the project asks of every contrast:

* are the per-seed signs unanimous, and in the direction the predictor called?
* does removing one seed change the pooled sign?
* which axis binds -- the task draw or the control draw?

    python -m experiments.e64_predictor_per_seed
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from scipy.stats import binomtest

ARTIFACT = "runs/e64_predictor_6_perseed.json"

RUNGS = ("side", "cell_class", "cell_type", "ito_lee_hemilineage", "supertype")

#: Measured control-draw sds at **cs = 800 / support 80** (d = 1307), most direct source first; the same
#: table `e66` uses, duplicated here for the reason `e12` gives -- so that editing one experiment cannot
#: silently change what another measured.
#:
#: **It is keyed by rung and this table's circuit is a property of it, not of the rung.** `e93` found that
#: four of `e6`'s five conditions run at **cs = 300** and were being handed these numbers, and `e94` then
#: measured all twenty of those pairs at their own configuration: **every ratio between the right value and
#: this one exceeds 1 (1.09 to 6.73, median 2.33)**, so the substitution was systematically optimistic rather
#: than merely noisy.  `draw_source` below is what a caller should use; this table is only the fallback for
#: conditions that share its circuit.
DRAW_SD_SOURCES = {
    "side": ("runs/e67_drawsd_side_min1.json", "e67, 8 draws"),
    "cell_class": ("runs/e17_cell_class_drawsd.json", "e17, 5 draws"),
    "ito_lee_hemilineage": ("runs/e17b_ito_lee_hemilineage_drawsd.json", "e17b, 5 draws"),
    "supertype": ("runs/e17b_supertype_drawsd.json", "e17b, 5 draws"),
    "cell_type": ("runs/e67_drawsd_cell_type_min1.json", "e67, 8 draws"),
}

#: which circuit size each of `e6`'s conditions ran at, so the fallback above can be *checked* against a
#: condition rather than assumed to suit it
CONDITION_CIRCUIT = {"baseline": 300, "wider-tasks": 300, "faster-drift": 300,
                     "rewired-swap2": 300, "larger-circuit": 800}
SHARED_TABLE_CIRCUIT = 800


def draw_source(label: str, rung: str):
    """``(path, description, circuit)`` for one condition's rung, preferring a same-configuration run.

    The order is: a cs = 300 measurement for that exact condition (`e86` did `baseline` and nothing else,
    `e94` the other three), then the shared table if — and only if — the condition shares the table's
    circuit.  Returns ``(None, None, None)`` when nothing applies, which is a *pending* denominator and not
    a substitute.

    **`e86`'s files are named for the rung alone and must not be reached by any condition but `baseline`.**
    The first version of this function looked for them by rung without checking the label, so
    `larger-circuit` — which ran at cs = 800 — picked up a cs = 300 measurement, i.e. it reproduced exactly
    the defect the function was written to remove.  The assertion at the call site caught it.
    """
    if label == "baseline":
        path = Path(f"runs/e86_drawsd_cs300_{rung}_min1.json")
        if path.exists():
            return path, "e86, cs = 300", 300
    path = Path(f"runs/e94_drawsd_{label}_{rung}_min1.json")
    if path.exists():
        return path, "e94, cs = 300", 300
    table = DRAW_SD_SOURCES.get(rung)
    if table is not None and CONDITION_CIRCUIT.get(label) == SHARED_TABLE_CIRCUIT:
        return Path(table[0]), table[1], SHARED_TABLE_CIRCUIT
    return None, None, None


#: What `e6_predictor_6` reports, so the reproduction is checked rather than assumed.
PUBLISHED = dict(sign_agree=24, n_pairs=25, sign_agree_resolvable=13, n_resolvable=13)


def load(path: str):
    p = Path(path)
    if not p.exists():
        return None
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def sign_test(dl: np.ndarray) -> tuple[int, int, int, float]:
    pos = int((dl > 0).sum())
    neg = int((dl < 0).sum())
    tied = int((dl == 0).sum())
    n = pos + neg
    return pos, neg, tied, (float(binomtest(pos, n).pvalue) if n else float("nan"))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--artifact", default=ARTIFACT)
    ap.add_argument("--json-out", default="runs/e64_predictor_per_seed_analysis.json")
    args = ap.parse_args()

    art = load(args.artifact)
    if art is None:
        raise SystemExit(f"artifact absent: {args.artifact}")

    #: The guard that matters: the first launch of `e64` produced an artifact that looked complete and
    #: could not answer the question, because `e6`'s row builder did not carry this field through.
    if not any(r.get("excess_per_seed") for c in art["conditions"] for r in c["rows"]):
        raise SystemExit(
            "no `excess_per_seed` in the rows -- this artifact reproduces the pooled numbers and "
            "proves nothing per seed. e6_predictor.run_condition must copy the field into its rows."
        )

    n_seeds = art["conditions"][0]["n_seeds"]
    out: dict = {"artifact": args.artifact, "n_seeds": n_seeds, "published": PUBLISHED,
                 "conditions": {}}

    print("=" * 112)
    print(f"1. EVERY MATCHED PAIR, PER SEED ({n_seeds} seeds per condition)")
    print("=" * 112)
    print("   delta = excess(bio) - excess(control) at the SAME task seed, so it is paired.  negative")
    print("   delta = the biological basis is closer to the oracle, which is the predictor's claim.")
    print("   `call` is what the predictor said; `pooled` is whether it was right on the means.\n")

    all_pairs = []
    for cond in art["conditions"]:
        label = cond["condition"]["label"]
        rows = {r["basis"]: r for r in cond["rows"]}
        print(f"   --- {label} ({cond['condition']['topology']}, d = {cond['d']}) ---")
        print(f"   {'rung':<22}{'delta':>10}{'seed sem':>10}{'sigma':>8}{'signs':>10}"
              f"{'p':>8}{'LOO min':>9}{'flip':>6}{'call':>6}{'ok':>5}")
        for rung in RUNGS:
            b, r = rows.get(f"bio:{rung}"), rows.get(f"rand:{rung}")
            if b is None or r is None or not b.get("excess_per_seed") or not r.get("excess_per_seed"):
                print(f"   {rung:<22} not checkable per seed")
                continue
            bv = np.asarray(b["excess_per_seed"], float)
            rv = np.asarray(r["excess_per_seed"], float)
            n = min(bv.size, rv.size)
            dl = bv[:n] - rv[:n]
            sem = float(dl.std(ddof=1) / np.sqrt(n)) if n > 1 else float("nan")
            sigma = abs(float(dl.mean())) / sem if sem else float("inf")
            pos, neg, tied, p = sign_test(dl)
            loo, flip = [], False
            for i in range(n):
                keep = np.delete(dl, i)
                s = float(keep.std(ddof=1) / np.sqrt(keep.size))
                loo.append(abs(float(keep.mean() / s)) if s else float("inf"))
                if np.sign(keep.mean()) != np.sign(dl.mean()):
                    flip = True
            #: what the predictor said: it calls the arm with the lower pressure better, so the
            #: predicted sign of the excess delta is the sign of the pressure delta.
            call = -1 if b["pressure"] < r["pressure"] else +1
            ok = [] if tied == n else (np.sign(dl.mean()) == call)
            draw_path, draw_label, draw_circuit = draw_source(label, rung)
            sd = None
            if draw_path is not None:
                a = load(draw_path)
                sd = float(a["control_sd_across_draws"]) if a else None
            #: a denominator from the wrong circuit is worse than none: it is a number where the honest
            #: answer is "not measured", and `e94` measured it to be optimistic by a median of 2.33x
            assert sd is None or draw_circuit == CONDITION_CIRCUIT.get(label), (
                f"{label}/{rung}: draw sd from circuit {draw_circuit} but the condition ran at "
                f"{CONDITION_CIRCUIT.get(label)}")
            sigma_rule = abs(float(dl.mean())) / float(np.hypot(sem, sd)) if sd else None
            rec = dict(condition=label, topology=cond["condition"]["topology"], rung=rung,
                       n=int(n), delta=float(dl.mean()), seed_sem=sem, sigma_task=sigma,
                       signs="".join("+" if v > 0 else ("0" if v == 0 else "-") for v in dl),
                       n_pos=pos, n_neg=neg, n_tied=tied, sign_p=p,
                       loo_min=float(min(loo)), loo_flips=bool(flip), call=int(call),
                       pooled_ok=bool(ok), unanimity=int(len(set(np.sign(dl[(dl != 0)]))) == 1),
                       draw_sd=sd, sigma_rule=sigma_rule,
                       draw_source=draw_label, draw_circuit=draw_circuit)
            all_pairs.append(rec)
            print(f"   {rung:<22}{dl.mean():>+10.5f}{sem:>10.5f}{sigma:>8.1f}"
                  f"{rec['signs']:>10}{p:>8.4f}{min(loo):>9.1f}{str(flip):>6}"
                  f"{'bio' if call < 0 else 'rand':>6}{str(ok):>5}")
        print()
    out["pairs"] = all_pairs

    print("=" * 112)
    print("2. THE HEADLINE, PER SEED")
    print("=" * 112)
    resolvable = [p for p in all_pairs if p["sigma_task"] > 2.0]
    agr = sum(p["pooled_ok"] for p in all_pairs)
    agr_res = sum(p["pooled_ok"] for p in resolvable)
    print(f"   pooled sign record           {agr}/{len(all_pairs)}      "
          f"(published {PUBLISHED['sign_agree']}/{PUBLISHED['n_pairs']})")
    print(f"   on pairs above 2 sigma       {agr_res}/{len(resolvable)}      "
          f"(published {PUBLISHED['sign_agree_resolvable']}/{PUBLISHED['n_resolvable']})")
    if seg := [p for p in resolvable if p["delta"] != 0]:
        unan = sum(p["unanimity"] for p in seg)
        flips = [p for p in seg if p["loo_flips"]]
        print(f"\n   of the {len(resolvable)} resolvable pairs, "
              f"{unan} have completely unanimous per-seed signs")
        print(f"   and {len(flips)} of them change their pooled sign if one seed is removed")
        print(f"   smallest leave-one-out sigma among them: "
              f"{min(p['loo_min'] for p in seg):.2f}")
        for p in seg:
            if not p["unanimity"] or p["loo_flips"]:
                print(f"     -> {p['condition']}/{p['rung']}: signs {p['signs']}, "
                      f"LOO min {p['loo_min']:.2f}, flips {p['loo_flips']}")
    out["headline"] = dict(sign_agree=agr, n_pairs=len(all_pairs),
                           sign_agree_resolvable=agr_res, n_resolvable=len(resolvable),
                           unanimous=sum(p["unanimity"] for p in resolvable),
                           loo_flips=sum(p["loo_flips"] for p in resolvable))

    print()
    print("=" * 112)
    print("3. AND WITH THE CONTROL-DRAW COMPONENT, WHICH IS THE SECOND AXIS")
    print("=" * 112)
    print(f"   {'condition / rung':<40}{'sigma(task)':>12}{'draw sd':>10}{'source':>22}"
          f"{'sigma(rule)':>13}")
    for p in all_pairs:
        if p["draw_sd"] is None:
            continue
        print(f"   {p['condition'] + ' / ' + p['rung']:<40}{p['sigma_task']:>12.2f}"
              f"{p['draw_sd']:>10.5f}{str(p['draw_source']):>22}{p['sigma_rule']:>13.2f}")
    under = [p for p in all_pairs if p["sigma_rule"] is not None and p["sigma_rule"] < 2.0]
    print(f"\n   pairs that fall below 2 sigma once the draw sd is folded in: "
          f"{len(under)} of {sum(1 for p in all_pairs if p['sigma_rule'] is not None)}")
    for p in under:
        print(f"     -> {p['condition']}/{p['rung']}: {p['sigma_task']:.2f} -> "
              f"{p['sigma_rule']:.2f}")
    out["under_2_with_draw"] = [dict(condition=p["condition"], rung=p["rung"],
                                     sigma_task=p["sigma_task"], sigma_rule=p["sigma_rule"])
                                for p in under]

    #: The most conservative denominator the project can quote: pair resolvable only if it clears 2
    #: sigma with the *measured* control-draw component folded in.  A predictor should be scored on
    #: what is measurable, and this is the smallest set of measurable pairs.
    rule_ok = [p for p in all_pairs if p["sigma_rule"] is not None and p["sigma_rule"] > 2.0]
    mis = [p for p in rule_ok if not p["pooled_ok"]]
    print()
    print("=" * 112)
    print("4. THE MOST CONSERVATIVE HEADLINE: PAIRS THAT CLEAR 2 SIGMA WITH THE DRAW COMPONENT IN")
    print("=" * 112)
    print(f"   pairs clearing 2 sigma on the task axis alone:        {sum(1 for p in all_pairs if p['sigma_task'] > 2.0)}"
          f" of {len(all_pairs)}")
    print(f"   pairs clearing 2 sigma with the measured draw sd too: {len(rule_ok)} of {len(all_pairs)}")
    print(f"   of those, called correctly:                           "
          f"{sum(p['pooled_ok'] for p in rule_ok)} of {len(rule_ok)}")
    for p in mis:
        print(f"     -> the miss: {p['condition']}/{p['rung']}, sigma(task) {p['sigma_task']:.2f}, "
              f"sigma(rule) {p['sigma_rule']:.2f}, signs {p['signs']}, "
              f"predicted {'bio' if p['call'] < 0 else 'rand'}")
    out["conservative"] = dict(n_task_2sigma=sum(1 for p in all_pairs if p["sigma_task"] > 2.0),
                               n_rule_2sigma=len(rule_ok),
                               correct_rule_2sigma=sum(p["pooled_ok"] for p in rule_ok),
                               misses=[dict(condition=p["condition"], rung=p["rung"],
                                            sigma_task=p["sigma_task"], sigma_rule=p["sigma_rule"],
                                            signs=p["signs"], delta=p["delta"]) for p in mis])

    Path(args.json_out).parent.mkdir(parents=True, exist_ok=True)
    with open(args.json_out, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1, default=str)
    print(f"\nwrote {args.json_out}")


if __name__ == "__main__":
    main()
