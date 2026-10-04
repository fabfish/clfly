# The trained bodies: how far the training walked and which way do not separate the one world either

*2026-10-04. `experiments/e402_the_trained_bodies.py` measures what the trained body offers without rolling anything.
The six worlds whose five-hundred-update bodies are on disk have their weights saved, so the movement from the
connectome's own weights to the trained ones is a number, and how the six movements relate to each other is another.
Five claims, registered before any weight was loaded.*

## 1. Six bodies

| world | gain | mean relative movement | sem | mean cosine with the others | trained head |
|---|---|---|---|---|---|
| 9 | −0.2250 | 0.0771 | 0.00149 | +0.0403 | 0.8125 |
| 6 | −0.2083 | 0.0757 | 0.00117 | **+0.0414** | 0.5208 |
| 1 | −0.1813 | 0.0774 | 0.00111 | +0.0385 | 0.7500 |
| 3 | −0.1635 | 0.0776 | 0.00132 | **+0.0376** | 0.8333 |
| 14 | −0.1479 | **0.0730** | 0.00098 | **+0.0368** | 0.8333 |
| **the card's** | **+0.0854** | **0.0777** | 0.00151 | **+0.0389** | 0.7500 |

Twenty replicates each; the movement is `||theta_after - theta_initial|| / ||theta_initial||` and the cosine is
between this body's per-replicate movement and another world's *on the same replicate*.

| claim | measured | verdict |
|---|---|---|
| AB1 the six bodies start from one body | identical on **20 of 20** replicates | **MET** |
| AB2 how far the training walked does not separate the one | **0.0001** outside the failing range | **MET** |
| AB3 the movements are not one direction | largest mean cosine **+0.0414** | **MET** |
| AB4 the card's body is not an outlier | **+0.0389** inside 0.0368 to 0.0414 | **MET** |
| AB5 the head does not separate it either | **0.7500** inside 0.5208 to 0.8333 | **MET** |

## 2. What the five claims say together

**The training moves every world by the same distance.** The card's world's mean relative movement is **0.0777**
against 0.0730 to 0.0776 for the five that lose the cue -- **0.0001** outside their range, on standard errors of
0.0010 to 0.0015. Whatever the card's world does differently, it is not that its training walked further or less far.

**And the six updates are near-orthogonal.** Every world's mean cosine with the other five is between **0.0368** and
**0.0414**, so the updates do not share a direction the card's world could be the exception to: six worlds differing
in their whole environment draw move the weights along six nearly perpendicular directions, and the one that keeps
the cue is not distinguishable by how its direction relates to the others.

**And the card's body is not an outlier, and neither is its head.** Its mean cosine sits inside the failing five's
range, and its trained head reads **0.7500** inside the failing heads' 0.5208 to 0.8333 -- which matters because
`e379` and `e380` found the head and the world agree after training, so a head that separated the card's world would
have been a second reading of the same difference and not a second measurement of it.

**So the cheapest reading of "look at the trained body" is empty too.** `e397` to `e401` closed the draw's near
geometry -- the hop count, the five properties of `e400` and the weight's own test -- and this unit closes the two
numbers the saved weights offer. The card's world is now the only one of **ten** measured worlds that keeps the cue,
and it is not distinguished by where its cue population sits, how heavy its path is, how far its training moved, or
which way.

## 3. What it cannot settle, and what it registers

- **Two numbers are not a trajectory.** Relative movement and pairwise cosine say nothing about which *directions*
  in the weight space the updates took; a difference spread over a subspace orthogonal to the common direction would
  be invisible here, and the probe says the difference is real -- the card's world holds 0.0854 where the others lose
  0.1479 to 0.2490.
- **And the failing set is five of nine.** The four engine redraws and the four other cue populations that failed at
  the far point do not have both ends saved, so this compares the card's world with five and not with nine.
- **One budget and one arm**: the 500-update `naive` bodies only.
- *And a reading is not a mechanism*: what the bodies are measured on is how much of the label a linear fit recovers
  from the world's eight numbers.
