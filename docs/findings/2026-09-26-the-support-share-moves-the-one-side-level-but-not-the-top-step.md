# The support share moves the one-side level (1.42×) and does not organize the top step

*2026-09-26 05:43, `runs/e221_support{20,160}_rs{0,1}.json` — four drawings, twelve cells, ~35 min. Read by
`e222_support_read.py`, exit 0. The registration is
`docs/findings/2026-09-26-registered-the-support-share-and-a-correction-to-the-mechanism-direction.md`.*

## 1. The verdicts

| | claim | verdict |
|---|---|---|
| **U1** | the one-side level's mean at support 20 exceeds its mean at support 160 by ≥1.3× | **MET** — **1.42×** (0.07642 against 0.05374) |
| **U2** | the top step below 1.5× at support 20 and at or above 1.5× at support 160 | **outside all three registered outcomes** — 1.96× and 2.10× |

## 2. The sweep

| support (share of 1307 neurons) | drawing | `alloy1` | `inalloy1` | `erdos_renyi` | one-side mean | top step |
|---|---|---|---|---|---|---|
| **20** (1.53%) | rs0 | 0.09440 | 0.07805 | 0.16335 | 0.08623 | 1.73× |
| **20** | rs1 | 0.06072 | 0.07249 | 0.15903 | 0.06660 | 2.19× |
| 80 (6.12%, `e213`/`e216`) | five + three | 0.05136 | 0.04668 | 0.14187 | 0.04902 | 2.76× |
| **160** (12.24%) | rs0 | 0.09911 | 0.03541 | 0.12165 | 0.06726 | 1.23× |
| **160** | rs1 | 0.03836 | 0.04207 | 0.12492 | 0.04022 | 2.97× |

**U1's MET is the support the corrected candidate needed**: within one circuit size, a **smaller** share of the
neurons engaged goes with a **higher** one-side level — 0.07642 at 1.53% against 0.05374 at 12.24% — which is the
direction the arithmetic implied when the candidate was corrected (the share is *smallest* where the one-side level
is *highest*, across circuit sizes). So the share is a variable the one-side level responds to.

## 3. But U2 landed outside its own registration, and that is worth stating plainly

U2's three registered outcomes were **MET** (below 1.5× at support 20, at or above 1.5× at support 160), its
**falsifier** (the reverse ordering), and its **null** (*"both below 1.5×, which leaves the shape unmoved at cs 800
whatever the support"*). What the data give is **neither**: both top steps are **at or above 1.5×** (1.96× and
2.10×), the ordering is in the *predicted* direction, and the two are **1.07× apart** — inside the 1.2× margin the
reader declares for calling an ordering real. So the registration's null band was written too narrow and the
outcome is an *unregistered shape*, which the reader's declared margin classified rather than the registration.

**And the shape is non-monotone in support**: the top step is 2.76× at the convention's 80, **1.96× at 20** and
**2.10× at 160** — both a smaller *and* a larger share lower it relative to the convention. So the share does not
organize the top step the way it organizes the one-side level.

## 4. What this does to the mechanism candidate

- **Supported**: the one-side level responds to the share of the circuit engaged (1.42×), in the direction the
  correction implies.
- **Not supported**: the top step. The cs-800 top step (2.76×) is not reproduced by either a smaller or a larger
  support, and the support relation is not monotone, so the circuit-size dependence of the ladder's top step (1.18×
  at cs 300, 1.11× at cs 400) still has **no tested explanation**.
- **And the effect is at the scale of the noise**: at support 20 the two drawings' one-side means span 1.29× and at
  support 160 they span **1.67×**, against the 1.42× mean effect — so a design that quoted one drawing per support
  could have reported any of 1.0×, 1.9× or 2.1× for the same comparison. The registered falsifier (≤1.05×) is
  excluded and the MET stands, but only because two drawings per support were measured rather than one.

## 5. What this cannot do

Four drawings in total, so every number here is a mean of two; the support count and the share move together at one
circuit size, so "share" is a share only by construction (separating them needs a second circuit size at the same
share); the assembly geometry (`TASK_ASSEMBLIES`, `rho`, the propagation depth) is held at its defaults throughout;
and nothing here speaks for the network substrate. The honest one-line state: **the share is a real variable for the
one-side level and not for the ladder's shape.**
