"""E506 -- the window or the position: whether what the pass needs is the label's window in drive steps or its place
in the pass.

`e505` moved the label's cue across a three-trial pass -- trial **0**, **1** and **2**, so **11**, **7** and **3**
drive steps to the read -- and the pass read **0.8538**, **0.8392** and **0.8580** with the label first and fell to
**0.3257**, **0.3069**, **0.3274** at trial **1** and **0.2566**, **0.2576** and **0.2542** at trial **2**. Its own
*cannot do* closed on *three placements is not a curve's shape* and *the window and the placement are still one axis
here, three trials being one pass length*: at three trials the label at trial **1** has a window of **7** and at trial
**2** a window of **3**, and no other pass in the corpus carries either window, so the placement's step and the
window's fall are the same movement. **This unit adds the four-trial pass** -- trials of three steps -- so the label at
trial **0**, **1** and **2** has windows **11**, **8** and **5**, and the window becomes a variable with more than one
pass length behind it: window **11** is carried by three pass lengths (two, three and four trials) and window **5** by
two (two and four trials). The question is whether what the pass needs is the **window** or the **position**.

Three runs and one instrument:

  * `e506 ... label_at0` -- `e497`'s own command with `--loop-episode 4` and `--loop-label-at 0`, the label at the
    pass's first trial, eleven drive steps (new);
  * `e506 ... label_at1` -- the same command with `--loop-label-at 1`, the label at the second trial, eight drive
    steps (new);
  * `e506 ... label_at2` -- the same command with `--loop-label-at 2`, the label at the third trial, five drive steps
    (new);

beside every placement run the corpus already holds: `e495`'s two-trial label-first (window **11**), `e497`'s
three-trial label-first (window **11**), `e505`'s label-at-1 and label-at-2 (windows **7** and **3**) and `e493`'s
two-trial label-last (window **5**).

Three claims, registered before any new run's reading was opened.

- **WA1 -- the three runs are one flag apart.** Each pair of the three four-trial runs agrees on every recorded
  `config` field except the placement (the output path and the saved weights being bookkeeping), and the draw differs
  in the placement field only; each run carries **twenty** replicates. **Falsifier**: any other config field
  differing, a draw field added or missing beyond the placement, or a replicate count other than twenty.
- **WA2 -- the read is a function of the window and not of the position.** Across every placement the corpus and these
  runs hold, placements carrying the **same window** at **different pass lengths** read alike -- their accuracy
  diagonals differ by less than the registered bound, which is **the window-eleven family's own spread across its
  three pass lengths**, derived from the runs at read time and not from the head -- while placements at different
  windows differ as the window falls, and the move from the largest window to the smallest, this unit's four-trial
  label-first against the three-trial label-at-2, is positive and resolved at **two** sigma on at least two arms.
  **Falsifier**: two placements at the same window differing by more than the registered bound, or the end-to-end move
  not resolving. *It can fire: the two-trial window-5 placement is near chance (`e493`'s label-last at **0.3104**,
  **0.2944** and **0.3031**), so a four-trial label-at-2 that reads above it by more than the window-eleven spread
  would say the window is not the whole of it.*
- **WA3 -- the label's share follows the window.** Measured at the card's body with deterministic cues and the
  episode's other symbols held fixed, the label's own part of the read at the last step is ordered by the **window**
  across pass lengths -- placements at the same window carry shares within the registered factor of **2** of each
  other, and the share falls as the window falls. **Falsifier**: two same-window shares outside the factor, or a share
  that does not fall.

**What it can do beyond that.** It separates the two readings `e505` could not: if the four-trial window-5 placement
reads where the two-trial window-5 placement reads, the placement's step is a window and the position is a name for
it; if it reads elsewhere, what orders the pass is where the label sits in the trial order and the window is a
coincidence of the pass's own split. Either way the read, the world, the boundary channel and the placement flag are
held fixed and only the pass's length and the placement move.

**What it cannot do.** *Four pass lengths at most, three of them sharing one window*: two, three and four trials, with
window **11** carried by three of them and window **5** by two, so the six-trial split and the placements beyond each
pass's own trials are not in it, and a window carried by a single pass length (**8**, **7** and **3**) is a placement
and not a test. *And the pass's length and the trial's length move together*: the pass is twelve steps, so a pass of
`N` trials has trials of `12/N` steps and the label at trial `i` leaves `11 - i * 12/N` drive steps -- what would
separate a step's worth of window from a trial's is a twelve-step pass with a fixed trial length, and that is not
measured here. *And the payout is not on these runs*: the three commands carry no `--loop-reward`, so nothing here is
read against the world's currency. *And one read and one body*: the model's own thirty-two columns, which `e493`
showed is the better of the corpus's two, at a body that has never been trained, so a share is where that body puts
the label and the trained arms are the measurement. *And one world, budget and seed stream*: the card's own setting
with `--seed0 0`, so a second world and a second stream are not in it.
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
from pathlib import Path

import numpy as np

from clfly.bench.artifacts import write_json
from experiments import e489_the_benchmark_has_an_episode as e489

ARMS = e489.ARMS
#: every placement the corpus and these runs hold: the key, the pass's length in trials, the 0-based trial index of
#: the cue the label names, and the run on disk it is read from
PLACEMENTS = (
    ("two_at0", 2, 0, Path("runs/e495_earned_label_episode2_labelfirst_20reps.json")),
    ("two_at1", 2, 1, Path("runs/e493_earned_label_episode2_modelread_20reps.json")),
    ("three_at0", 3, 0, Path("runs/e497_earned_label_episode3_labelfirst_20reps.json")),
    ("three_at1", 3, 1, Path("runs/e505_label_at1_episode3_20reps.json")),
    ("three_at2", 3, 2, Path("runs/e505_label_at2_episode3_20reps.json")),
    ("four_at0", 4, 0, Path("runs/e506_label_at0_episode4_20reps.json")),
    ("four_at1", 4, 1, Path("runs/e506_label_at1_episode4_20reps.json")),
    ("four_at2", 4, 2, Path("runs/e506_label_at2_episode4_20reps.json")),
)
#: the three runs this unit adds, the four-trial pass at trial 0, 1 and 2
NEW = ("four_at0", "four_at1", "four_at2")
#: the placement pair, as fields in the config and in the environment's draw
MOVED = ("loop_label_first", "loop_label_at")
DRAW_MOVED = ("label_first", "label_at")
BOOKKEEPING = ("json_out", "save_theta")
EPISODE = e489.EPISODE
TAU = e489.TAU
SIZE = e489.SIZE
READOUT_SIZE = e489.READOUT_SIZE
N_SYMBOLS = e489.N_SYMBOLS
SYMBOLS = 4
CHANCE = e489.CHANCE
MIN_REPS = 20
SIGMA = 2.0
ARMS_NEEDED = 2
PLACES = 4
#: how far the label's share may move between two placements at the same window and still be "the same window"
FACTOR = 2.0
#: the largest window, whose family is the bound's own yardstick, and the smallest the corpus holds
BIG_WINDOW = (TAU - 1) - 0 * (TAU // 2)
SMALL_WINDOW = (TAU - 1) - 2 * (TAU // 3)
#: the end-to-end move, the largest window to the smallest: this unit's four-trial label-first against the
#: three-trial label-at-2, and the same-pass move beside it as an extra reading
END_FROM, END_TO = "four_at0", "three_at2"
ALT_FROM, ALT_TO = "three_at0", "three_at2"


def window(trials: int, at: int) -> int:
    """The drive steps between the label's cue and the read at the pass's last step.

    The pass is twelve steps and trial ``at`` of a pass of ``trials`` trials opens at step ``at * (tau // trials)``,
    so its window is ``tau - 1 - at * (tau // trials)`` -- **the pass's length and the trial's length move together
    here**, and a trial's worth of window is not separated from a step's.
    """
    return (TAU - 1) - at * (TAU // trials)


#: each placement's window in drive steps
WINDOW = {key: window(trials, at) for key, trials, at, _ in PLACEMENTS}
#: the placements grouped by their window, so the windows carried by more than one pass length are the tests
GROUPS = {w: sorted(k for k in WINDOW if WINDOW[k] == w) for w in sorted(set(WINDOW.values()), reverse=True)}
CLAIMS = (
    ("WA1", "the three runs are one flag apart",
     "Each pair of the three four-trial runs agrees on every recorded config field except the placement, the output "
     "path and the saved weights; the draw differs in the placement field only; and each run carries twenty replicates",
     "falsifier: any other config field differing, a draw field added or missing beyond the placement, or a replicate "
     "count other than twenty"),
    ("WA2", f"the read is a function of the window and not of the position, at {SIGMA:.0f} sigma on {ARMS_NEEDED} arms",
     "Across every placement the corpus and these runs hold, placements carrying the same window at different pass "
     "lengths read alike -- their accuracy diagonals differ by less than the window-eleven family's own spread across "
     "its three pass lengths -- while placements at different windows differ as the window falls, and the move from the "
     "largest window to the smallest is positive and resolved at two sigma on at least two arms",
     "falsifier: two placements at the same window differing by more than the registered bound, or the end-to-end move "
     "not resolving"),
    ("WA3", f"the label's share follows the window, within the factor {FACTOR:.0f}",
     "Measured at the card's body with deterministic cues and the episode's other symbols held fixed, the label's own "
     "part of the read at the last step is ordered by the window across pass lengths, with placements at the same "
     "window carrying shares within the registered factor of each other and the share falling as the window falls",
     "falsifier: two same-window shares outside the factor, or a share that does not fall"),
)


def _inert(key: str, old, new) -> bool:
    if key in MOVED or key in BOOKKEEPING:
        return True
    if {old, new} == {None, False}:
        return True
    return False


def _paired(a: list, b: list) -> dict:
    d = [x - y for x, y in zip(a, b)]
    n = len(d)
    mean = statistics.fmean(d) if n else 0.0
    sd = statistics.stdev(d) if n > 1 else 0.0
    se = sd / math.sqrt(n) if n else 0.0
    return {"n": n, "mean": mean, "sd": sd, "se": se, "sigma": (mean / se) if se > 0 else 0.0}


def load(path) -> dict | None:
    p = Path(path)
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _roll(path: Path) -> dict | None:
    """One run's per-arm reading, with its config and draw kept whole for the placement's own comparison."""
    doc = load(path)
    if not doc:
        return None
    methods = doc.get("methods") or {}
    got = {}
    for arm in ARMS:
        reps = (methods.get(arm) or {}).get("replicates") or []
        if not reps:
            return None
        got[arm] = {"replicates": len(reps),
                    "accuracy_diagonal": [statistics.fmean(r["learned"]) for r in reps],
                    "accuracy_last": [statistics.fmean(r["final_per_task"]) for r in reps]}
    return {"artifact": path.name, "arms": got, "config": doc.get("config") or {},
            "env_draw": doc.get("env_draw") or {}}


def _compare(mine: dict, other: dict) -> dict:
    """One run's config and draw against another's, the inert rule applied to the config.

    Both runs are the four-trial pass, so the placement is a pair of fields and the comparison is asked whether every
    field **outside** that pair agrees and whether the draw moved the placement and nothing else.
    """
    cfg, their_cfg = mine["config"], other["config"]
    same, inert, differ = {}, {}, {}
    for k in sorted(set(cfg) | set(their_cfg)):
        old, new = their_cfg.get(k), cfg.get(k)
        if old == new:
            same[k] = new
        elif _inert(k, old, new):
            inert[k] = [old, new]
        else:
            differ[k] = [old, new]
    mine_draw, their_draw = mine["env_draw"], other["env_draw"]
    moved = sorted(set(mine_draw) | set(their_draw))
    draw_differ = sorted(k for k in moved if mine_draw.get(k) != their_draw.get(k))
    return {"same": len(same), "inert": sorted(inert), "differ": differ,
            "moved": {k: cfg.get(k) for k in MOVED},
            "draw": {"added": sorted(set(mine_draw) - set(their_draw)),
                     "missing": sorted(set(their_draw) - set(mine_draw)),
                     "differ": draw_differ,
                     "differ_outside": [k for k in draw_differ if k not in DRAW_MOVED]}}


def share_of_placements() -> dict:
    """The label's own part of the read at the last step, at each placement the window table holds.

    The cues are deterministic and the episode's other symbols are held fixed across the examples, so one symbol is
    one trajectory and what varies from one symbol to the next is the label. What is reported for each placement is
    the across-symbol spread as a share of that read's own scale, **one width, one read, one world**, beside the
    window in drive steps the placement leaves between the label's cue and the read.
    """
    import torch

    from clfly.connectome import annotate, circuits, graph
    from clfly.network import env as fly_env
    from clfly.network.model import RateConfig, build_net

    torch.manual_seed(0)
    conn, ann = graph.build(), annotate.load_annotations()
    circ = circuits.extract(conn, ann, hops=0, max_neurons=SIZE)
    net = build_net(circ, RateConfig(tau=TAU)).torch_model()
    rs = np.sort(np.random.default_rng(0).choice(circ.n_neurons, size=READOUT_SIZE, replace=False))
    n = SYMBOLS * 12
    y = np.arange(n) % SYMBOLS
    got = {}
    for key, trials, at, _ in PLACEMENTS:
        other = np.tile(np.arange(1, trials, dtype=np.int64), (n, 1)) % SYMBOLS
        env = fly_env.build(circ, readout_subset=rs, seed=0, n_symbols=N_SYMBOLS, tau=TAU, scale=1.0, gain=1.0,
                            noise=0.0, world_modes=0, world_leak=0.35, world_dims=8, world_coupled=True, cue_at=0,
                            boundary=True, episode=trials, label_at=at)
        u = torch.from_numpy(np.asarray(env.cue_input(y, episode_symbols=other), dtype=np.float32))
        fn = env.feedback()
        with torch.no_grad():
            traj = net(u, feedback=fn)
        w = traj[:, -1, :][:, rs].detach()
        means = [w[y == s].mean(dim=0) for s in range(SYMBOLS)]
        across = max(float((means[i] - means[j]).norm()) for i in range(SYMBOLS) for j in range(i + 1, SYMBOLS))
        within = statistics.fmean([float((w[y == s] - means[s]).norm(dim=1).mean()) for s in range(SYMBOLS)])
        scale = float(w.norm(dim=1).mean())
        got[key] = {"trials": trials, "at": at, "window": WINDOW[key], "across": across, "within": within,
                    "scale": scale, "share": (across / scale) if scale else 0.0, "width": int(w.shape[1])}
    return got


def reading(paths: dict | None = None) -> dict:
    """Every placement's roll, the window table, the pairs the three new runs make and the share instrument.

    A run that is absent is recorded as absent rather than refused here, so each claim refuses on its own input: the
    three new runs are the four-trial ones' claim, the whole window table is the window's, and the share instrument is
    the share's.
    """
    out = {"ok": True, "reason": None, "placements": {}, "share": {}, "recovery": {}, "spans": {}}
    chosen = dict(paths or {key: path for key, _, _, path in PLACEMENTS})
    rolls = {key: _roll(chosen[key]) for key, _, _, _ in PLACEMENTS}
    out["placements"] = {k: v for k, v in rolls.items() if v is not None}
    absent = [k for k, v in rolls.items() if v is None]
    #: the three new runs compared pairwise, which is WA1's own input
    pairs = (("four_at0", "four_at1"), ("four_at1", "four_at2"), ("four_at0", "four_at2"))
    out["recovery"]["pairs"] = {f"{a}|{b}": (_compare(rolls[a], rolls[b])
                                             if rolls[a] is not None and rolls[b] is not None else None)
                                for a, b in pairs}
    #: each four-trial run's own contrasts over the replicate seeds, and their last rows
    def _diag(key, arm):
        return rolls[key]["arms"][arm]["accuracy_diagonal"] if rolls[key] is not None else None

    def _last(key, arm):
        return rolls[key]["arms"][arm]["accuracy_last"] if rolls[key] is not None else None

    out["recovery"]["four_pairs"] = {
        f"{a}|{b}": ({arm: _paired(_diag(a, arm), _diag(b, arm)) for arm in ARMS}
                     if rolls[a] is not None and rolls[b] is not None else None) for a, b in pairs}
    out["recovery"]["end_to_end"] = ({arm: _paired(_diag(END_FROM, arm), _diag(END_TO, arm)) for arm in ARMS}
                                     if rolls[END_FROM] is not None and rolls[END_TO] is not None else None)
    out["recovery"]["alt_end_to_end"] = ({arm: _paired(_diag(ALT_FROM, arm), _diag(ALT_TO, arm)) for arm in ARMS}
                                         if rolls[ALT_FROM] is not None and rolls[ALT_TO] is not None else None)
    try:
        out["share"] = share_of_placements()
    except (ImportError, OSError, ValueError) as exc:
        return {**out, "ok": False, "reason": f"the connectome could not be built: {exc}"}
    #: the window table: one row per placement, and the spread across the placements at each shared window
    spread = {}
    for w, keys in GROUPS.items():
        here = [k for k in keys if rolls[k] is not None]
        if len(here) < 2:
            continue
        spread[w] = {arm: max(_diag_means(rolls, k, arm) for k in here)
                     - min(_diag_means(rolls, k, arm) for k in here) for arm in ARMS}
    out["spans"] = {
        "arms": list(ARMS), "chance": CHANCE, "sigma": SIGMA, "arms_needed": ARMS_NEEDED, "factor": FACTOR,
        "big_window": BIG_WINDOW, "small_window": SMALL_WINDOW, "episode": EPISODE, "tau": TAU,
        "replicates": sorted({v["replicates"] for roll in out["placements"].values()
                              for v in roll["arms"].values()}),
        "absent": absent, "windows": dict(WINDOW), "groups": {w: list(k) for w, k in GROUPS.items()},
        #: the config and the draw are carried **inside the spans**, as every unit's reading is: a top-level
        #: `config` would be counted as a run's own configuration by the corpus's own census
        "accuracy_diagonal": {k: ({arm: round(_diag_means(rolls, k, arm), PLACES) for arm in ARMS}
                                  if rolls[k] is not None else None) for k, _, _, _ in PLACEMENTS},
        "accuracy_last": {k: ({arm: round(_last_means(rolls, k, arm), PLACES) for arm in ARMS}
                              if rolls[k] is not None else None) for k, _, _, _ in PLACEMENTS},
        "spread": spread,
        "bound": (max(spread.get(BIG_WINDOW, {}).values()) if spread.get(BIG_WINDOW) else None),
        "share": {k: round(v["share"], PLACES) for k, v in out["share"].items()},
        "share_window": {k: v["window"] for k, v in out["share"].items()},
    }
    return out


def _diag_means(rolls: dict, key: str, arm: str) -> float:
    return statistics.fmean(rolls[key]["arms"][arm]["accuracy_diagonal"])


def _last_means(rolls: dict, key: str, arm: str) -> float:
    return statistics.fmean(rolls[key]["arms"][arm]["accuracy_last"])


def judge(r: dict) -> list[dict]:
    if not r.get("ok"):
        return [{"id": c[0], "measured": "", "verdict": f"REFUSED -- {r.get('reason', 'an input is absent')}"}
                for c in CLAIMS]
    rolls = r["placements"]
    s = r["spans"]
    #: WA1 -- the three runs are one flag apart
    if any(k not in rolls for k in NEW):
        j1 = {"id": "WA1", "measured": "a four-trial run is absent",
              "verdict": "REFUSED -- one of the three four-trial runs is not on disk, so the flag's own config and "
                         "draw are not compared"}
    else:
        rows, bad = {}, []
        for pair, cmp in r["recovery"]["pairs"].items():
            extra = [k for k in cmp["differ"] if k not in MOVED]
            draw_extra = cmp["draw"]["differ_outside"]
            reps = sorted({v["replicates"] for v in rolls[pair.split("|")[0]]["arms"].values()})
            rows[pair] = {"differ": sorted(cmp["differ"]), "extra": extra, "moved": cmp["moved"],
                          "added": cmp["draw"]["added"], "missing": cmp["draw"]["missing"],
                          "draw_extra": draw_extra, "replicates": reps}
            if extra or draw_extra or cmp["draw"]["added"] or cmp["draw"]["missing"] or reps != [MIN_REPS]:
                bad.append(pair)
        j1 = {"id": "WA1",
              "measured": "; ".join(
                  f"the pair {pair}: **{len(rows[pair]['differ'])}** config fields differing past the inert rule "
                  f"({rows[pair]['differ']}, the placement pair moved {rows[pair]['moved']}), the draw differing in "
                  f"{rows[pair]['draw_extra']} outside the placement with added {rows[pair]['added']} and missing "
                  f"{rows[pair]['missing']}, replicates {rows[pair]['replicates']}" for pair in rows),
              "verdict": "MET -- the three runs are one flag apart: the placement pair is the only field past the "
                         "inert rule and the draw moves the placement and nothing else" if not bad else
                         f"FALSIFIER FIRED -- {bad} over { {pair: rows[pair] for pair in bad} }"}
    #: WA2 -- the read is a function of the window and not of the position
    if r["spans"]["absent"]:
        j2 = {"id": "WA2", "measured": f"the window table is missing {r['spans']['absent']}",
              "verdict": "REFUSED -- a placement run is not on disk, so the same-window placements are not compared"}
    else:
        bound = s["bound"]
        over = [(w, a, round(s["spread"][w][a], PLACES)) for w in s["spread"] for a in ARMS
                if bound is not None and s["spread"][w][a] > bound + 1e-9]
        rec = r["recovery"]["end_to_end"]
        resolved = [a for a in ARMS if rec[a]["mean"] > 0.0 and rec[a]["sigma"] >= SIGMA]
        j2 = {"id": "WA2",
              "measured": f"the same-window spreads are "
                          f"{ {w: {a: round(s['spread'][w][a], PLACES) for a in ARMS} for w in s['spread']} } against "
                          f"the window-eleven bound of **{bound if bound is None else round(bound, PLACES)}**, with "
                          f"**{len(over)}** arm-windows over it ({over}); the end-to-end move, "
                          f"{END_FROM} (window {WINDOW[END_FROM]}) less {END_TO} (window {WINDOW[END_TO]}), is "
                          f"{ {a: round(rec[a]['mean'], PLACES) for a in ARMS} } at "
                          f"{ {a: round(rec[a]['sigma'], 2) for a in ARMS} } sigma, resolving on "
                          f"**{len(resolved)}** of three arms ({resolved}); the groups are "
                          f"{s['groups']}",
              "verdict": f"MET -- the read is a function of the window: **{len(over)}** arm-windows over the "
                         f"same-window bound of {bound if bound is None else round(bound, PLACES)} and the "
                         f"end-to-end move resolving on **{len(resolved)}** of three arms, at the bar of "
                         f"{ARMS_NEEDED}" if (not over and len(resolved) >= ARMS_NEEDED) else
                         f"FALSIFIER FIRED -- {len(over)} arm-windows over the same-window bound ({over}) and "
                         f"{len(resolved)} of three arms resolving ({resolved})"}
    #: WA3 -- the label's share follows the window
    if not r["share"]:
        j3 = {"id": "WA3", "measured": "the share instrument is absent",
              "verdict": "REFUSED -- the share of the read is not measured, so the label's own part is not ordered"}
    else:
        sh = r["share"]
        out_of = []
        for w, keys in s["groups"].items():
            here = [k for k in keys if k in sh]
            if len(here) < 2:
                continue
            vals = [sh[k]["share"] for k in here]
            lo = min(vals)
            if lo <= 0.0 or max(vals) > lo * FACTOR:
                out_of.append((w, {k: round(sh[k]["share"], PLACES) for k in here}))
        windows = sorted({sh[k]["window"] for k in sh}, reverse=True)
        means = {w: statistics.fmean([sh[k]["share"] for k in sh if sh[k]["window"] == w]) for w in windows}
        ladder = [means[w] for w in windows]
        falls = all(ladder[i] >= ladder[i + 1] for i in range(len(ladder) - 1)) and ladder[0] > ladder[-1]
        j3 = {"id": "WA3",
              "measured": f"the label's own part of the read at the last step as a share of its scale, by window: "
                          + ", ".join(f"window {w} **{means[w]:.4f}** ({[k for k in sh if sh[k]['window'] == w]})"
                                      for w in windows)
                          + f", with **{len(out_of)}** same-window families outside the factor of {FACTOR:.0f} "
                            f"({out_of})",
              "verdict": f"MET -- the share follows the window: every same-window family within the factor of "
                         f"{FACTOR:.0f} and the shares falling {ladder[0]:.4f} to {ladder[-1]:.4f}" if
                         (not out_of and falls) else
                         f"FALSIFIER FIRED -- same-window families outside the factor {out_of}, ladder "
                         f"{[round(x, PLACES) for x in ladder]}"}
    return [j1, j2, j3]


def report(r: dict) -> int:
    print("== the window or the position ==")
    if not r.get("ok"):
        print(f"   REFUSED -- {r.get('reason', 'an input is absent')}")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)
    print("   `e505` moved the label across a three-trial pass and left the window and the position one axis; this")
    print("   adds the four-trial pass, so window 11 is carried by three pass lengths and window 5 by two")
    s = r["spans"]
    print(f"\n   {'placement':<11} {'pass':>4} {'trial':>5} {'window':>6} {'share':>8}  "
          + "  ".join(f"{a:>9}" for a in ARMS) + f"  {'last mean':>9}")
    for key, trials, at, _ in PLACEMENTS:
        diag = s["accuracy_diagonal"][key]
        if diag is None:
            print(f"   {key:<11} {trials:>4} {at:>5} {WINDOW[key]:>6} {'-':>8}  " + "  ".join(f"{'-':>9}" for _ in ARMS))
            continue
        share = s["share"].get(key)
        print(f"   {key:<11} {trials:>4} {at:>5} {WINDOW[key]:>6} "
              f"{(f'{share:.4f}' if share is not None else '-'):>8}  "
              + "  ".join(f"{diag[a]:>9.4f}" for a in ARMS) + "  "
              + f"{statistics.fmean(s['accuracy_last'][key][a] for a in ARMS):>9.4f}")
    print(f"\n   the same-window spreads against the window-eleven bound of "
          f"{s['bound'] if s['bound'] is None else round(s['bound'], PLACES)}: "
          f"{ {w: {a: round(s['spread'][w][a], PLACES) for a in ARMS} for w in s['spread']} }")
    rec = r["recovery"]["end_to_end"]
    if rec:
        print(f"   the end-to-end move, {END_FROM} less {END_TO}: "
              + ", ".join(f"{a} {rec[a]['mean']:+.4f} at {rec[a]['sigma']:+.2f} sigma" for a in ARMS))
    alt = r["recovery"]["alt_end_to_end"]
    if alt:
        print(f"   the same-pass move, {ALT_FROM} less {ALT_TO}: "
              + ", ".join(f"{a} {alt[a]['mean']:+.4f} at {alt[a]['sigma']:+.2f} sigma" for a in ARMS))
    print("\n== the registered claims, WA1-WA3 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e505` showed the placement is an axis; this asks whether the axis is the window or the position)")
    return sum("REFUSED" in row["verdict"] for row in j)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args(argv)
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")

    r = reading()
    r["claims"] = judge(r)
    if args.json_out:
        write_json(args.json_out, r)
        print(f"wrote {args.json_out}")
    return report(r)


if __name__ == "__main__":
    sys.exit(main())
