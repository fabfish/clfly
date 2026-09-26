# The floor's task-draw band: the level claim survives, and the long-queued run was not needed

*2026-09-26 21:40. Runs: **none new** — `experiments/e258_floor_task_draw_band.py` reads every `real` draw the corpus
already carries at `rho` 0.9 (`runs/e258_floor_task_draw_band.json`). JSON-only, seconds.*

## 1. The queued item, resolved

This line has carried one open item for many fires: *"the cs-300 task drift's remaining candidate is the support draw —
a run recording the support fingerprint at cs 300/support 30/seeds 3, against `e217`'s absence of one."* Read against
the corpus it resolves in two parts, and the second turns out to be the better question:

**The run is not needed.** The `support_draw.fingerprint_sha1` convention belongs to the runners that take
`--support-seed` — the overlap suite, where `e198`'s census finds **137 artifacts with a live support draw and 8
identifying it (5.8%)**. **The ladder runner has no such flag**: its supports are drawn from the connectome **from the
task seeds**, so `(seeds, seed0, q)` *is* the draw's identity — and the artifacts that vary it are already on disk.

**And what they show is worth having.** At the reference `rho` 0.9 the two cells carry:

    cs 800/support 80   8 draws   0.01739, 0.01749, 0.01749, 0.01762, 0.01762, 0.01830, 0.01830, 0.01902   span 1.094x
    cs 300/support 30   6 draws   0.02516, 0.02577, 0.02645, 0.02723, 0.02745, 0.02978                     span 1.184x

## 2. Verdicts

**W1 MET — the floor is a draw at both cells**: 1.094× at cs 800 and **1.184×** at cs 300.

**W2 MET — and the size effect is bigger than the draw.** The rise from cs 800's floor to cs 300's runs **1.323× to
1.713×** over draw pairs, against the largest task-draw span of 1.184×. So **"the floor rises as the circuit shrinks"
survives being re-drawn** — the first claim in this session's audit line to do so.

**W3 MET — but the quoted pair is at the top of its band.** `e217`'s cs-300 floor is **0.02978, rank 6 of 6** among
that cell's draws and 1.184× over the smallest, so the record's quoted comparison (0.02978 against a cs-800 draw,
**1.627×**) sits at the **top** of the band rather than in it. The honest form of the number is a band:

    the floor's size effect        1.32x (smallest cs-300 draw over the largest cs-800)
                              to   1.71x (largest cs-300 draw over the smallest cs-800)
    the record's quoted pair       1.63x  -- the top of it

## 3. What that does to the ledger, and why it matters here

This session's audits have moved three quoted figures (**the cs-300 rank contrasts**, **`alloy1`'s 3.34× spread**, **the
late advantage**) and found three that held (the top step 2.76×/3.02×, the (1,0) margin, the low-`rho` rank curve on
the rewire draw). **The floor's level adds a fourth that holds**, and it is the first one checked against the **task**
draw rather than the **rewire** draw — so the two kinds of lottery this record has measured (which construction is
drawn, and which task is built inside it) both turn out to leave this claim standing, while each of them is large
enough at other cells to have taken other claims apart.

The one thing that does not stand is the *quoted number* being read as central: **0.02978 is the largest of six draws
of its own cell**, which is the same shape as `e242`'s finding about the register's 2.76× and `e253`'s about the top
step. Quoting the band is the fix, and the band's direction is not in doubt.

## 4. What it cannot do

The draws are the corpus's own and unevenly distributed — **six at cs 300, eight at cs 800, and one at cs 400/support
40** — so the two bands are estimated from different numbers of draws, and **the ladder's middle rung gets no band at
all**. The draws vary `seeds` and `seed0` **together**, so "task draw" here mixes the seed count with the seed offset;
`e181`/`e202`/`e204`/`e206` vary only `seed0` (at `seeds` 12) and span 1.09× among themselves, so the wider 1.184× span
comes from comparing those with the two `seeds` 3 artifacts. The `rho`-sweep artifacts at both cells are excluded
because a different `rho` is a different task geometry and not another draw of the same one. And the excesses are
`e2_topology_gap`'s own, so a code epoch between them is invisible here (`e227`).
