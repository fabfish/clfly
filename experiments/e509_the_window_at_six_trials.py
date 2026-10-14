"""E509 -- the window at six trials: whether the drive steps between the label's cue and the read order a pass whose
trials are two steps long.

`e506` separated the label's **window** in drive steps from its **position** in the pass by adding the four-trial
pass: window **11** is carried by two, three and four trials and window **5** by two and four, and the placements at
a shared window read alike (**0.3104**, **0.2944** and **0.3031** against **0.3031**, **0.2986** and **0.2903**,
differing by at most **0.0128** where the window-eleven family's own spread is **0.0312**) while a same-position pair
does not. Its own *cannot do* closed on *four pass lengths at most, three of them sharing one window*, with windows
**8**, **7** and **3** each a single pass length and the six-trial split not in it. **This unit adds the six-trial
pass** -- trials of **two** steps, because the pass is twelve steps and six divides it -- so the label at trial **1**,
**2** and **3** has windows **9**, **7** and **5**, and the six-trial placements **overlap three windows the corpus
already carries**: window **7** on the three-trial pass (the label at trial **1**) and window **5** on the two- and
four-trial passes. If the window is the variable, the six-trial placements at windows **7** and **5** read what their
windows predict; if the position or the number of cues after the label is what matters, they will not.

Three runs and one instrument:

  * `e509 ... label_at1` -- `e506`'s own command with `--loop-episode 6` and `--loop-label-at 1`, the label at the
    pass's second trial, nine drive steps (new);
  * `e509 ... label_at2` -- the same command with `--loop-label-at 2`, the label at the third trial, seven drive steps
    (new);
  * `e509 ... label_at3` -- the same command with `--loop-label-at 3`, the label at the fourth trial, five drive steps
    (new);

beside every placement run the corpus already holds: `e495`'s two-trial runs (windows **11** and **5**), `e497`'s
three-trial label-first (window **11**), `e505`'s label-at-1 and label-at-2 (windows **7** and **3**) and `e506`'s
four-trial label-first, label-at-1 and label-at-2 (windows **11**, **8** and **5**). Eleven placements, the six-trial
three among them.

Four claims, registered before any new run's reading was opened.

- **YA1 -- the three runs are one flag apart.** Each pair of the three six-trial runs agrees on every recorded
  `config` field except the placement, the output path and the saved weights; the draw differs in the placement field
  only; and each run carries **twenty** replicates. **Falsifier**: any other config field differing, a draw field
  added or missing beyond the placement, or a replicate count other than twenty.
- **YA2 -- the six-trial pass reads what its windows predict.** The six-trial placement at window **7** reads within
  the registered same-window spread of the three-trial window-**7** placement, and the six-trial placement at window
  **5** reads within it of the two- and four-trial window-**5** placements -- with the spread registered from the
  placements already on disk rather than from the head, being the largest spread any same-window family those runs
  carry shows at read time (the window-eleven family's own, **0.0312** as `e506` measured it). **Falsifier**: either
  six-trial placement outside the registered spread from its window's family. *It can fire: the three-trial window-7
  placement reads **0.3257**, **0.3069** and **0.3274** and the four-trial window-5 placement **0.3031**, **0.2986**
  and **0.2903**, so a six-trial placement at either window reading above the four-trial window-8 point's **0.3667**
  or below the three-trial window-3 point's **0.2566** would say the window is not the whole of it.*
- **YA3 -- the label's share follows the same window.** Measured at the card's body with deterministic cues and the
  episode's other symbols held fixed, the six-trial placements' shares of the read are ordered by the window -- the
  window-**9** share above the window-**7** share above the window-**5** share -- and each falls within the registered
  factor of **2** of the placements at the same window in the other pass lengths (window **7** against the three-trial
  placement's **0.0489**, window **5** against the two-trial placement's **0.0386** and the four-trial one's
  **0.0362**). **Falsifier**: a share that does not fall, or one outside the factor.
- **YA4 -- the window is not the position.** The six-trial placement at trial **2** (window **7**) reads nearer the
  three-trial placement at trial **1** (window **7**, a different position and a different number of cues after the
  label) than to any placement at the same **position** in another pass length -- the three-trial and four-trial
  placements at trial **2**, windows **3** and **5** -- and the six-trial window-**9** point's per-arm accuracy mean
  sits inside the band its neighbouring measured windows span, the window-**8** placement and the window-**11**
  family. **Falsifier**: the window-7 pair further apart than a same-position pair, or the window-9 point outside the
  band the neighbouring windows bound. *It can fire: the six-trial label-at-2 leaves **three** cues after it where the
  three-trial label-at-1 leaves **one**, so a pass ordered by the cues after the label rather than by the steps would
  put it with the trial-2 placements and not with the window-7 one.*

**What it can do beyond that.** It is the fourth pass length in the corpus and the first whose trials are shorter than
three steps, so it tests the window where the number of cues after the label is not what the other pass lengths make
it: at six trials the label's trial index is one third of the window's fall, so the six-trial placements at windows
**7** and **5** are read beside the placements their windows already carry at pass lengths whose trial is four and
three steps long. Either the window predicts them or the conclusion `e506` wrote is a coincidence of the three pass
lengths it had.

**What it cannot do.** *Four pass lengths, still not a step of window separated from a trial*: the window is
`11 - i * 12/N`, so a six-trial step of two also changes how many cues follow the label -- the six-trial label-at-2
leaves three cues after it where the three-trial label-at-1 leaves one -- and what would separate a step's worth of
window from a trial's is a twelve-step pass with a fixed trial length, and that is not measured here. *And windows
**1** and **3** on the six-trial pass are not run*: the label at trial **4** and trial **5** would leave windows **3**
and **1**, and window **1** is carried by nothing in the corpus, so the six-trial end of the ladder stops at window
**5** as the measured one and window **9** is the only new window. *And the payout is not on these runs*: the three
commands carry no `--loop-reward`, so nothing here is read against the world's currency. *And one read and one body*:
the model's own thirty-two columns, which `e493` showed is the better of the corpus's two, at a body that has never
been trained, so a share is where that body puts the label and the trained arms are the measurement. *And one world,
budget and seed stream, and three arms*: the card's own setting with `--seed0 0`, so a second world and a second
stream are not in it, and a claim over three arms is not a claim about the world.
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
    ("six_at1", 6, 1, Path("runs/e509_label_at1_episode6_20reps.json")),
    ("six_at2", 6, 2, Path("runs/e509_label_at2_episode6_20reps.json")),
    ("six_at3", 6, 3, Path("runs/e509_label_at3_episode6_20reps.json")),
)
#: the three runs this unit adds, the six-trial pass at trial 1, 2 and 3
NEW = ("six_at1", "six_at2", "six_at3")
#: every placement whose run predates this unit: the spread YA2 reads its families inside is derived from **these**
DISK = tuple(key for key, _, _, _ in PLACEMENTS if key not in NEW)
#: the placement, as fields in the config and in the environment's draw
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
PLACES = 4
#: how far the label's share may move between two placements at the same window and still be "the same window"
FACTOR = 2.0
#: the two six-trial placements YA2 tests, the window each is read at, and the on-disk family it is read against
TESTS = (("six_at2", 7), ("six_at3", 5))
#: YA4's three placements at the same position as the six-trial trial-2 placement, and the pairs beside them
SIX = "six_at2"
WINDOW_PAIR = "three_at1"
SAME_POSITION = ("three_at2", "four_at2")
#: YA4's window-9 point and the two neighbouring windows that bound it
NINE = "six_at1"
LOWER_WINDOW, UPPER_WINDOW = "four_at1", "four_at0"
WINDOW_11 = ("two_at0", "three_at0", "four_at0")


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
    ("YA1", "the three runs are one flag apart",
     "Each pair of the three six-trial runs agrees on every recorded config field except the placement, the output "
     "path and the saved weights; the draw differs in the placement field only; and each run carries twenty "
     "replicates",
     "falsifier: any other config field differing, a draw field added or missing beyond the placement, or a "
     "replicate count other than twenty"),
    ("YA2", "the six-trial pass reads what its windows predict, inside the registered spread",
     "The six-trial placement at window 7 reads within the registered same-window spread of the three-trial window-7 "
     "placement, and the six-trial placement at window 5 reads within it of the two- and four-trial window-5 "
     "placements, the spread being the largest any same-window family the on-disk runs carry shows at read time",
     "falsifier: either six-trial placement outside the registered spread from its window's family"),
    ("YA3", f"the label's share follows the same window, within the factor {FACTOR:.0f}",
     "Measured at the card's body with deterministic cues and the episode's other symbols held fixed, the six-trial "
     "placements' shares of the read are ordered by the window and fall within the registered factor of the "
     "placements at the same window in the other pass lengths",
     "falsifier: a share that does not fall, or one outside the factor"),
    ("YA4", "the window is not the position",
     "The six-trial placement at trial 2 (window 7) reads nearer the three-trial placement at trial 1 (window 7, a "
     "different position and a different number of cues after the label) than to any placement at the same position "
     "in another pass length, and the six-trial window-9 point sits inside the band the measured windows 8 and 11 "
     "bound",
     "falsifier: the window-7 pair further apart than a same-position pair, or the window-9 point outside the band "
     "the neighbouring windows bound"),
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


def _roll(path) -> dict | None:
    """One run's per-arm reading, with its config and draw kept whole for the placement's own comparison."""
    if path is None:
        return None
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

    Both runs are the six-trial pass, so the placement is a pair of fields and the comparison is asked whether every
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
    window in drive steps the placement leaves between the label's cue and the read -- the instrument `e506` built,
    over every placement the corpus now holds.
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


def _diag(rolls: dict, key: str, arm: str) -> float:
    return statistics.fmean(rolls[key]["arms"][arm]["accuracy_diagonal"])


def _last(rolls: dict, key: str, arm: str) -> float:
    return statistics.fmean(rolls[key]["arms"][arm]["accuracy_last"])


def disk_spreads(rolls: dict) -> dict:
    """The spread each same-window family the on-disk runs carry shows, at read time.

    Only the placements whose runs predate this unit are read here, so the registered bound is the corpus's own and
    not something this unit's three runs could move. A family carried by one pass length has no spread and is not in
    it: the window-eleven family, carried by two, three and four trials, and the window-five family, by two and four.
    """
    out = {}
    for w, keys in GROUPS.items():
        here = [k for k in keys if k in DISK and rolls.get(k)]
        if len(here) < 2:
            continue
        out[w] = {arm: max(_diag(rolls, k, arm) for k in here) - min(_diag(rolls, k, arm) for k in here)
                  for arm in ARMS}
    return out


def _distance(rolls: dict, a: str, b: str) -> float:
    """How far apart two placements read: the largest per-arm gap between their accuracy diagonals."""
    return max(abs(_diag(rolls, a, arm) - _diag(rolls, b, arm)) for arm in ARMS)


def _assemble(rolls: dict, shares: dict) -> dict:
    """The reading from the rolls and the shares: the window table, the pairs, the bound and the instrument.

    A run that is absent is recorded as absent rather than refused here, so each claim refuses on its own input: the
    three new runs are YA1's, the six-trial placements beside their window families are YA2's, the shares are YA3's
    and the same-position pair and the window-9 band are YA4's.
    """
    out = {"ok": True, "reason": None, "placements": {}, "share": shares or {}, "recovery": {}, "spans": {}}
    out["placements"] = {k: v for k, v in rolls.items() if v is not None}
    absent = [k for k, v in rolls.items() if v is None]
    #: the three new runs compared pairwise, which is YA1's own input
    pairs = (("six_at1", "six_at2"), ("six_at2", "six_at3"), ("six_at1", "six_at3"))
    out["recovery"]["pairs"] = {f"{a}|{b}": (_compare(rolls[a], rolls[b])
                                            if rolls.get(a) is not None and rolls.get(b) is not None else None)
                                for a, b in pairs}
    #: each six-trial run's own contrasts over the replicate seeds, and their last rows
    out["recovery"]["six_pairs"] = {
        f"{a}|{b}": ({arm: _paired(rolls[a]["arms"][arm]["accuracy_diagonal"],
                                   rolls[b]["arms"][arm]["accuracy_diagonal"]) for arm in ARMS}
                     if rolls.get(a) is not None and rolls.get(b) is not None else None) for a, b in pairs}
    out["recovery"]["end_to_end"] = ({arm: _paired(rolls["six_at1"]["arms"][arm]["accuracy_diagonal"],
                                                   rolls["six_at3"]["arms"][arm]["accuracy_diagonal"])
                                      for arm in ARMS}
                                     if rolls.get("six_at1") is not None and rolls.get("six_at3") is not None
                                     else None)
    #: the window table: one row per placement, the on-disk families' spreads, and the registered bound
    spread = disk_spreads(rolls)
    bound = max((v for s in spread.values() for v in s.values()), default=None)
    out["spans"] = {
        "arms": list(ARMS), "chance": CHANCE, "factor": FACTOR, "episode": EPISODE, "tau": TAU,
        "replicates": sorted({v["replicates"] for roll in out["placements"].values()
                              for v in roll["arms"].values()}),
        "absent": absent, "new": list(NEW), "disk": list(DISK), "windows": dict(WINDOW),
        "groups": {str(w): list(k) for w, k in GROUPS.items()},
        "tests": {key: w for key, w in TESTS},
        #: the config and the draw are carried **inside the spans**, as every unit's reading is: a top-level
        #: `config` would be counted as a run's own configuration by the corpus's own census
        "accuracy_diagonal": {k: ({arm: round(_diag(rolls, k, arm), PLACES) for arm in ARMS}
                                  if rolls.get(k) is not None else None) for k, _, _, _ in PLACEMENTS},
        "accuracy_last": {k: ({arm: round(_last(rolls, k, arm), PLACES) for arm in ARMS}
                              if rolls.get(k) is not None else None) for k, _, _, _ in PLACEMENTS},
        "share": {k: round(v["share"], PLACES) for k, v in (shares or {}).items()},
        "share_window": {k: v["window"] for k, v in (shares or {}).items()},
        "spread": spread,
        "bound": bound,
    }
    return out


def reading(paths: dict | None = None, shares_fn=None) -> dict:
    """Every placement's roll, the window table, the three new runs' pairs and the share instrument.

    ``paths`` overrides the run each placement is read from and ``shares_fn`` the instrument, so a caller can drive
    the reading on synthetic rolls without the connectome; both default to the runs and the instrument registered
    above.
    """
    chosen = {key: path for key, _, _, path in PLACEMENTS} if paths is None else dict(paths)
    rolls = {key: _roll(chosen.get(key)) for key, _, _, _ in PLACEMENTS}
    try:
        shares = share_of_placements() if shares_fn is None else shares_fn()
    except (ImportError, OSError, ValueError) as exc:
        out = _assemble(rolls, {})
        return {**out, "ok": False, "reason": f"the connectome could not be built: {exc}"}
    return _assemble(rolls, shares)


def judge(r: dict) -> list[dict]:
    if not r.get("ok"):
        return [{"id": c[0], "measured": "", "verdict": f"REFUSED -- {r.get('reason', 'an input is absent')}"}
                for c in CLAIMS]
    rolls = r["placements"]
    s = r["spans"]
    #: YA1 -- the three runs are one flag apart
    if any(k not in rolls for k in NEW):
        j1 = {"id": "YA1", "measured": "a six-trial run is absent",
              "verdict": "REFUSED -- one of the three six-trial runs is not on disk, so the flag's own config and "
                         "draw are not compared"}
    else:
        #: every six-trial run's own replicate count, so a run that is the first member of no pair is still checked
        reps_by_run = {k: sorted({v["replicates"] for v in rolls[k]["arms"].values()}) for k in NEW}
        rows, bad = {}, []
        for pair, cmp in r["recovery"]["pairs"].items():
            extra = [k for k in cmp["differ"] if k not in MOVED]
            draw_extra = cmp["draw"]["differ_outside"]
            a, b = pair.split("|")
            reps = {k: reps_by_run[k] for k in (a, b)}
            rows[pair] = {"differ": sorted(cmp["differ"]), "extra": extra, "moved": cmp["moved"],
                          "added": cmp["draw"]["added"], "missing": cmp["draw"]["missing"],
                          "draw_extra": draw_extra, "replicates": reps}
            if extra or draw_extra or cmp["draw"]["added"] or cmp["draw"]["missing"] or any(
                    reps[k] != [MIN_REPS] for k in reps):
                bad.append(pair)
        if any(reps_by_run[k] != [MIN_REPS] for k in NEW):
            mentioned = {x for pair in bad for x in pair.split("|")}
            bad += [k for k in NEW if reps_by_run[k] != [MIN_REPS] and k not in mentioned]
        j1 = {"id": "YA1",
              "measured": "; ".join(
                  f"the pair {pair}: **{len(rows[pair]['differ'])}** config fields differing past the inert rule "
                  f"({rows[pair]['differ']}, the placement pair moved {rows[pair]['moved']}), the draw differing in "
                  f"{rows[pair]['draw_extra']} outside the placement with added {rows[pair]['added']} and missing "
                  f"{rows[pair]['missing']}, replicates {rows[pair]['replicates']}" for pair in rows)
                  + f"; and each six-trial run's own replicates {reps_by_run}",
              "verdict": "MET -- the three runs are one flag apart: the placement pair is the only field past the "
                         "inert rule, the draw moves the placement and nothing else, and each run carries twenty "
                         "replicates" if not bad else
                         f"FALSIFIER FIRED -- {bad} over { {pair: rows.get(pair, reps_by_run.get(pair)) for pair in bad} }"}
    #: YA2 -- the six-trial pass reads what its windows predict
    need = [key for key, _ in TESTS]
    refs_missing = []
    for key, w in TESTS:
        for ref in [k for k in GROUPS[w] if k in DISK]:
            if ref not in rolls:
                refs_missing.append(ref)
    if any(k not in rolls for k in need) or refs_missing or s["bound"] is None:
        j2 = {"id": "YA2", "measured": f"a six-trial placement or its window family is absent ({refs_missing})",
              "verdict": "REFUSED -- a six-trial placement or the on-disk family at its window is not on disk, so "
                         "the registered spread's own test is not made"}
    else:
        bound = s["bound"]
        rows, over = {}, []
        for key, w in TESTS:
            here = [k for k in GROUPS[w] if k in DISK and k in rolls]
            gaps = {arm: max(abs(_diag(rolls, key, arm) - _diag(rolls, ref, arm)) for ref in here) for arm in ARMS}
            widest = max(gaps.values())
            rows[key] = {"window": w, "family": here, "gaps": {a: round(gaps[a], PLACES) for a in ARMS},
                         "widest": round(widest, PLACES),
                         "read": {a: round(_diag(rolls, key, a), PLACES) for a in ARMS},
                         "family_read": {k: {a: round(_diag(rolls, k, a), PLACES) for a in ARMS} for k in here}}
            if widest > bound + 1e-9:
                over.append(key)
        families = {str(w): {a: round(v, PLACES) for a, v in s['spread'][w].items()} for w in s['spread']}
        j2 = {"id": "YA2",
              "measured": "; ".join(
                  f"the six-trial window-{rows[key]['window']} placement reads "
                  f"{rows[key]['read']} against its family {rows[key]['family_read']}, the largest per-arm gap "
                  f"**{rows[key]['widest']}** ({rows[key]['gaps']})" for key, _ in TESTS)
                  + f", against the registered bound of **{round(bound, PLACES)}** "
                    f"(the on-disk same-window families' spreads: {families})",
              "verdict": f"MET -- the six-trial pass reads what its windows predict: both placements inside the "
                         f"registered bound of {round(bound, PLACES)} from their windows' families" if not over else
                         f"FALSIFIER FIRED -- {over} outside the registered bound of {round(bound, PLACES)} over "
                         f"{ {k: rows[k] for k in over} }"}
    #: YA3 -- the label's share follows the same window
    sh = r["share"]
    if any(k not in sh for k in NEW):
        j3 = {"id": "YA3", "measured": "the share instrument is absent at a six-trial placement",
              "verdict": "REFUSED -- the share of the read is not measured at a six-trial placement, so the label's "
                         "own part is not ordered"}
    else:
        ladder = [sh["six_at1"]["share"], sh["six_at2"]["share"], sh["six_at3"]["share"]]
        falls = ladder[0] > ladder[1] > ladder[2]
        out_of = []
        for key, w in TESTS:
            here = [k for k in GROUPS[w] if k in DISK and k in sh]
            if not here:
                continue
            vals = [sh[key]["share"]] + [sh[k]["share"] for k in here]
            lo = min(vals)
            if lo <= 0.0 or max(vals) > lo * FACTOR:
                out_of.append((w, {k: round(sh[k]["share"], PLACES) for k in [key] + here}))
        j3 = {"id": "YA3",
              "measured": f"the label's own part of the read at the last step as a share of its scale, at the three "
                          f"six-trial placements: window 9 **{ladder[0]:.4f}**, window 7 **{ladder[1]:.4f}** and "
                          f"window 5 **{ladder[2]:.4f}**, against the same-window families "
                          f"{ {str(w): {k: round(sh[k]['share'], PLACES) for k in GROUPS[w] if k in sh} for w in [t[1] for t in TESTS]} }, "
                          f"with **{len(out_of)}** six-trial families outside the factor of {FACTOR:.0f} ({out_of})",
              "verdict": f"MET -- the label's share follows the window: the six-trial ladder falls {ladder[0]:.4f} "
                         f"to {ladder[1]:.4f} to {ladder[2]:.4f} and every same-window family is within the factor of "
                         f"{FACTOR:.0f}" if (falls and not out_of) else
                         f"FALSIFIER FIRED -- the ladder is {[round(x, PLACES) for x in ladder]} (falls {falls}) and "
                         f"**{len(out_of)}** families outside the factor of {FACTOR:.0f} ({out_of})"}
    #: YA4 -- the window is not the position
    need4 = (SIX, WINDOW_PAIR, *SAME_POSITION, NINE)
    if any(k not in rolls for k in need4) or any(k not in rolls for k in WINDOW_11):
        j4 = {"id": "YA4", "measured": "a placement YA4 reads is absent",
              "verdict": "REFUSED -- the window-7 pair, a same-position placement or the window-9 band's ends are "
                         "not on disk, so the two read differently"}
    else:
        d_window = _distance(rolls, SIX, WINDOW_PAIR)
        gaps = {k: _distance(rolls, SIX, k) for k in SAME_POSITION}
        nearer = d_window < min(gaps.values())
        band, outside = {}, []
        for arm in ARMS:
            lo = min([_diag(rolls, LOWER_WINDOW, arm)] + [_diag(rolls, k, arm) for k in WINDOW_11])
            hi = max([_diag(rolls, LOWER_WINDOW, arm)] + [_diag(rolls, k, arm) for k in WINDOW_11])
            value = _diag(rolls, NINE, arm)
            band[arm] = {"value": round(value, PLACES), "lo": round(lo, PLACES), "hi": round(hi, PLACES),
                         "inside": (lo - 1e-9) <= value <= (hi + 1e-9)}
            if not band[arm]["inside"]:
                outside.append(arm)
        j4 = {"id": "YA4",
              "measured": f"the six-trial trial-2 placement (window 7) reads **{round(d_window, PLACES)}** from the "
                          f"three-trial trial-1 placement (window 7) and {gaps} from the trial-2 placements "
                          f"{list(SAME_POSITION)} (windows {[WINDOW[k] for k in SAME_POSITION]}), the distance being "
                          f"the largest per-arm gap; the window-9 point's band per arm {band} with "
                          f"**{len(outside)}** arms outside it ({outside})",
              "verdict": f"MET -- the window is not the position: the window-7 pair reads {round(d_window, PLACES)} "
                         f"apart, nearer than every same-position pair, and the window-9 point sits inside the band "
                         f"the window-8 and window-11 placements bound" if (nearer and not outside) else
                         f"FALSIFIER FIRED -- nearer {nearer} (window-7 pair {round(d_window, PLACES)} against "
                         f"{gaps}) and **{len(outside)}** arms outside the window-9 band ({outside})"}
    return [j1, j2, j3, j4]


def report(r: dict) -> int:
    print("== the window at six trials ==")
    if not r.get("ok"):
        print(f"   REFUSED -- {r.get('reason', 'an input is absent')}")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)
    print("   `e506` separated the window from the position over two, three and four trials; this adds the six-trial")
    print("   pass, trials of two steps, so the label at trial 1, 2 and 3 has windows 9, 7 and 5 -- three of them")
    print("   windows the corpus already carries")
    s = r["spans"]
    print(f"\n   {'placement':<11} {'pass':>4} {'trial':>5} {'window':>6} {'share':>8}  "
          + "  ".join(f"{a:>9}" for a in ARMS) + f"  {'last mean':>9}")
    for key, trials, at, _ in PLACEMENTS:
        diag = s["accuracy_diagonal"][key]
        if diag is None:
            print(f"   {key:<11} {trials:>4} {at:>5} {WINDOW[key]:>6} {'-':>8}  "
                  + "  ".join(f"{'-':>9}" for _ in ARMS))
            continue
        share = s["share"].get(key)
        print(f"   {key:<11} {trials:>4} {at:>5} {WINDOW[key]:>6} "
              f"{(f'{share:.4f}' if share is not None else '-'):>8}  "
              + "  ".join(f"{diag[a]:>9.4f}" for a in ARMS) + "  "
              + f"{statistics.fmean(s['accuracy_last'][key][a] for a in ARMS):>9.4f}")
    print(f"\n   the on-disk families' spreads against the registered bound of "
          f"{s['bound'] if s['bound'] is None else round(s['bound'], PLACES)}: "
          f"{ {w: {a: round(s['spread'][w][a], PLACES) for a in ARMS} for w in s['spread']} }")
    rec = r["recovery"]["end_to_end"]
    if rec:
        print("   the six-trial end-to-end move, trial 1 less trial 3: "
              + ", ".join(f"{a} {rec[a]['mean']:+.4f} at {rec[a]['sigma']:+.2f} sigma" for a in ARMS))
    print("\n== the registered claims, YA1-YA4 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e506` read the window over three pass lengths; this asks whether a fourth, six trials long, reads")
    print("    what its windows predict)")
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
