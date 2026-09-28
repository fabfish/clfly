# What the suite bought: nineteen of twenty sigmas rise, fourteen contrasts become eighteen, and one sign does not survive

*2026-09-29 02:05. Runs: **none new** — `experiments/e291_what_the_suite_bought.py` reads the configuration's two
suites, writing `runs/e291_what_the_suite_bought.json`. Seconds.*

## 1. The question nobody asked in the right currency

`e275` read what the larger suite did to each *arm's* spread, `e285` and `e286` read the same forty models at two
samples and found the spread falling, and `e289` read the paper's decomposition of it. None of them asked what the
suite did to the **contrasts** — the quantities the paper prints its claims as. The configuration is
`e140_r32_methods_frozenbias_40reps` (five arms, forty replicates) and its twin is
`e275_frozenbias_suite600_40reps`, trained from the same seeds, so every arm-versus-arm comparison is **paired over
the same forty replicates** at both suite sizes and the only thing that moved is the held-out sample. Twenty
contrasts: every pair of the five arms, on both metrics.

## 2. R1 MET — the suite sharpens them

**Nineteen of the twenty** contrasts have a larger sigma at the larger suite, with a **median ratio of 1.73**, and the
number resolved at two sigma goes from **14 of 20 to 18 of 20**. So the suite bought exactly what `e267` said it
would buy, in the currency the paper uses: four contrasts crossed the line, and the typical contrast is 73% sharper.

| contrast | metric | delta at 144 | sigma | delta at 600 | sigma |
|---|---|---|---|---|---|
| `ewc` − `replay` | final_accuracy | −0.03333 | **9.93** | −0.03062 | **15.22** |
| `ewc` − `ewc-block` | final_accuracy | −0.02431 | 6.61 | −0.02308 | 10.45 |
| `naive` − `replay` | final_accuracy | −0.01302 | 6.21 | −0.01446 | 11.39 |
| `ewc-block` − `naive` | final_accuracy | +0.00399 | 1.74 | +0.00692 | **4.47** |
| `ewc-block-rand` − `naive` | final_accuracy | +0.00382 | 1.32 | +0.00500 | **3.46** |
| `ewc` − `replay` | mean_forgetting | −0.00391 | 1.04 | **+0.00025** | 0.12 |

**R2 MET — and nothing that was resolved changed.** Of the fourteen contrasts resolved at two sigma at the first
suite, **none** lost its resolution and **none** changed direction. Every headline this configuration reports
survives the sample it is measured on.

## 3. R3 FIRED — and the exception is the contrast that was never resolved

**Nineteen of the twenty signs survive; one does not**: `ewc` − `replay` on `mean_forgetting` runs **−0.00391 at 1.04
sigma** at 144 items and **+0.00025 at 0.12 sigma** at 600. That is the corpus's own rule about unresolved contrasts
— a sigma below two is a direction nobody measured — applied to a **sample** instead of a seed: the one comparison
whose sign moved is the one whose sigma was smallest, and the movement is inside the noise of both readings. The
claim as registered was too strong, and what it fires on is the reason the corpus reports sigmas beside deltas.

## 4. What it cannot do

**One configuration**, chosen because `e267` gave it the largest requirement, so nothing here says the other two
behave the same way — though this is the only configuration in the corpus with a twin at a second suite size *and*
five arms. **Forty replicates** put about 11% on a contrast's sigma, so a contrast near two is one replicate away
from crossing, which is why R2 is stated over the ones already resolved. **The comparison is between two samples and
not between two suites held otherwise equal**: the second sample is a different draw of the same ratio, so the
movement includes the draw-to-draw component `e285` measured and nothing here separates a suite's effect from a
sample's. **A sigma is not a claim**: a contrast rising from 1.3 to 3.5 sigma has become resolvable, and a contrast
falling has not become false. **And only the 144- and 600-item suites are read** — the third sample of this
configuration is being trained, and the module discovers the suites rather than naming them, so the reading extends
itself when that artifact lands.
