# Registered: the support share, and a correction to the mechanism candidate's direction

**Date:** 2026-09-26. **Registered before its runs.** Artifacts to be written:
`runs/e221_support{20,160}_rs{0,1}.json` (four runs, three cells each).

---

## 1. The correction this design starts from

The last two fires recorded a **candidate mechanism** for why the ladder's one-side level rises as the circuit
shrinks: *"at smaller circuits a task's support is a larger fraction of the neuron set, so one-sided damage goes
further"*. **That is backwards, and the numbers say so**: this line holds `--support` at 10% of the *circuit size*
while the circuit's neuron count is not proportional to it, so the support share of the neuron set is

| circuit size | `d` (neurons) | support | **support share** | one-side level |
|---|---|---|---|---|
| cs 300 | 952 | 30 | **3.2%** | 0.122–0.139 |
| cs 400 | 1 010 | 40 | **4.0%** | 0.125–0.139 |
| cs 800 | 1 307 | 80 | **6.1%** | 0.047–0.051 |

**The share is *smallest* where the one-side level is *highest*** — so if the share is the variable at all, its
direction is that a **smaller** share goes with a **higher** one-side level. That is testable at one circuit size by
varying the support, which no design in this record has done.

## 2. The design

Two supports at cs 800 — **20 (1.5% of the neurons)** and **160 (12.2%)**, against the convention's 80 — at two
drawings each, with the three levels the ratios need:

```
experiments/e2_topology_gap.py --circuit-size 800 --support {20,160} --seeds 3 --seed0 0 --q 0.02 \
  --topologies alloy1,inalloy1,erdos_renyi --rewire-seed {0,1} --no-realized \
  --json-out runs/e221_support{20,160}_rs{0,1}.json
```

**Cost (rule 49)**: at cs 800 this week's cells took **225–240 s** each, so four runs of three cells are
**45–50 min**, one command per drawing on an idle machine.

## 3. The claims

**U1 — the support share moves the one-side level, with the sign the correction implies.** The one-side level's mean
at **support 20** exceeds its mean at **support 160** by at least **1.3×** (the circuit-size comparison spans
2.6–2.9× between cs 800 and cs 300–400, so a support sweep at fixed size should show a fraction of that).
**Falsifier**: at or below **1.05×** — no difference, which would leave the circuit-size dependence of the one-side
level **without any tested explanation** and would make the size effect about something the support does not carry
(the neuron count itself, or the assembly geometry). **Null**: 1.05–1.3×, which would leave the effect real but
smaller than the size comparison and unresolved at two drawings per support.

**U2 — the top step follows the same variable.** At **support 20** the top step is **below 1.5×** and at
**support 160** it is **at or above 1.5×**, i.e. the ladder's shape at one circuit size tracks the support share the
way it tracks circuit size across sizes. **Falsifier**: the *reverse* ordering — support 20's top step at or above
support 160's — which would refute the share reading rather than merely fail to support it. **Null**: both below
1.5×, which leaves the shape unmoved at cs 800 whatever the support.

**Reported, not claimed**: every cell's level and top step, the support shares, and the drawing spread within each
support — since the one-side constructions' own spreads at cs 800 were **1.24×** (`inalloy`, three drawings) and
**3.34×** (`alloy`, five), which is what sets what two drawings per support can resolve.

## 4. What this cannot do

- **Separate the support count from the share** at one circuit size: at cs 800 the two move together, so a support
  effect is a share effect only by construction — the separation needs a second circuit size at the same share,
  which is a different design and is priced at another 45 min.
- **Resolve a 1.3× effect against a 3.34× drawing spread with two drawings per support**: the comparison is a mean
  of two against a mean of two, and this design's verdict is written to be refused rather than overread if the two
  drawings at a support disagree by more than the effect.
- **Say anything about the assembly geometry** (`TASK_ASSEMBLIES`, `rho`, the propagation depth), all of which are
  held at their defaults here.
- **Speak for the network substrate**, whose penalty is a different instrument entirely.
