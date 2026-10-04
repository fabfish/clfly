# Five candidates for the one: the weight of the cue's path into the action population is the only one that makes the card's world an extreme

*2026-10-04. `experiments/e400_five_candidates_for_the_one.py` puts five properties of the cue population against the
five worlds whose far-point readings exist, and **trains nothing**: every property is computed from the circuit's own
mask and the drawn populations, so the question costs five environment builds. Four of the five worlds are at the
same distance and one is not, so a property has to do more than the distance does -- it is asked to **order all
five** the way their readings order them. Five claims, registered before any property was computed.*

## 1. Five properties, five worlds

| world | cue seed | cue to action | gain | fan-out | two-hop frontier | action overlap | cue out-degree | path weight |
|---|---|---|---|---|---|---|---|---|
| **9** | 9 | 2 | **−0.2250** | 171 | 597 | 5 | 209 | **28.80** |
| **1** | 1 | 1 | **−0.1813** | 174 | 648 | 5 | 226 | **42.22** |
| **3** | 3 | 2 | **−0.1635** | 206 | 666 | 5 | 239 | **48.78** |
| **14** | 14 | 2 | **−0.1479** | 150 | 646 | 7 | 174 | **42.80** |
| **the card's** | -- | **2** | **+0.0854** | 184 | **675** | 7 | 199 | **77.34** |

The worlds are in the readings' order, worst first. **fan-out** is how many neurons the cue population reaches in one
hop; **two-hop frontier** how many it reaches in exactly two; **action overlap** how many of the action population it
reaches within two; **cue out-degree** how many outgoing edges its twelve neurons carry; **path weight** the total
absolute weight of the edges from its one-hop frontier into the action population.

| claim | measured | verdict |
|---|---|---|
| X1 the distance cannot order them | it takes **two** values, giving the card's world and the three failing two-hop draws the same one | **MET** |
| X2 no candidate orders them | the rank correlations are **0.2, 0.7, 1.0, −0.5, 0.9** and **none** is strictly monotone | **MET** |
| X3 the candidates are not all constant | **5 of 5** vary | **MET** |
| X4 the readings are the ones already published | **+0.0854** and four losses of 0.1479 to 0.2250 | **MET** |
| X5 no candidate makes the card's world an extreme | **two** properties put its value outside the losers' range | **FALSIFIER FIRED** |

## 2. What fired, and what it names

**The weight of the path, and not its length.** The card's cue population feeds the action population through edges
whose total absolute weight is **77.34**, against **28.80, 42.22, 42.80** and **48.78** on the four worlds that lose
the cue -- **1.6 times** the largest of them, and the only property whose value on the card's world is that far
outside the losers' range. Its rank correlation is **0.9**, the highest of the five: it is not monotone because
cue seed 3's path weight (48.78) is above cue seed 14's (42.80) while its reading is below. **The two-hop frontier**
is the other property outside the range, and by 1.4% -- 675 against a maximum of 666 -- where the path weight is out
by 59%. So the lead this unit produces is: the card's world is the one whose cue population is **loudest** into the
action population, and `e397`'s hop count and `e398`'s null were both about the path's *length*.

**And the rank correlation is not the test the claim asked for.** The claim's word is **monotone**, and the unit's
first version tested `|rho| == 1.0` on a float. **Action overlap** slipped through it for two reasons at once: it
takes only **two** values (5 for the three worst worlds and 7 for cue seed 14 and the card's), so a correlation with
ties is the tie-breaking's rather than the property's, and its computed `rho` is **0.9999999999999998**, so the
equality was false by float error and not by principle. A property that gives the card's world the same value as a
world that fails two rows away has not ordered anything. The test is now strict monotonicity, under which **none** of the five orders the
five, and the artifact carries both readings. That is the fourth reader defect this line has had to correct -- after
`e394`'s geometry check, `e395`'s missing `loop_cue_at` and `e399`'s guard -- and the first where the claim's own
word was the thing the code had stopped testing.

## 3. What it cannot settle, and what it registers

- **Five points with one positive.** A property that separates them can do so by chance, and the path weight's 1.6
  times is a **lead for a later unit** and not evidence: what would test it is a fresh cue draw whose path weight is
  high and whose reading is then measured, which this unit does not roll.
- **And the candidates are five of many.** The weighted spectrum of the cue's block, the overlap with the read-out
  draw, the distance from the cue to the *read-out* population and the depth of the action population's own tree are
  all unmeasured.
- **And these are near geometries.** None of the five sees the trained body, so a property that predicts the outcome
  is a correlate of the draw until a mechanism names it.
- *And a probe is not a mechanism.*
