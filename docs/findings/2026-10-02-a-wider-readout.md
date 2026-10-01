# A wider read-out: 512 of the draw's own neurons, and the decoder loses two decisions in 384

*2026-10-02. Nothing trains: `experiments/e345_a_wider_readout.py` builds one world, rolls the frozen connectome
network under both loops once, and fits four nested linear decoders on that one roll. Six seconds. Writes
`runs/e345_a_wider_readout.json`.*

## 1. The escape hatch `e343` named

`e343` fitted a linear decoder on the corpus's **32-neuron** read-out, read it through the other loop, and lost
**one decision in ninety-six** while the state moved by **117% of the peak**. Its own "what it cannot do" named
exactly what that leaves open:

> *One task, one read-out draw and one circuit: the read-out is the corpus's 32-neuron draw, and the question "would
> a wider or narrower read-out see it" is `e286`'s axis and not this unit's.*

`e286`, `e292` and the C2b status block all point at the read-out width as the variable that moves the corpus's own
numbers, so the escape is concrete: **the nil could be a property of a 32-dimensional decoder rather than of the
substrate.** This unit runs the same instrument along that axis.

## 2. One world, one roll, four decoders

The world is built **once**, with its widest draw excluded from the environment's populations, so all four rows see
the same cue templates, the same populations and the same world state. The decoder's input set is a **prefix** of
that one 512-neuron draw -- 8, then 32, then 128, then 512 -- so each row's inputs contain the last row's and the
only thing that changes is how many of the decoder's own neurons it gets. Because the roll does not depend on the
width, the closed and open trajectories are literally the same arrays at every row (**T1 MET**).

## 3. The answer

The task is four symbols (chance 0.25) on 768 train and 384 test examples; the whole last-step state diverges by
**26.15% of the peak**.

| width | divergence on the decoder's own neurons | its mean over them | within-loop closed / open | cross-loop closed / open | worst gap |
|---|---|---|---|---|---|
| 8 | 10.41% | 0.10% | 0.628 / 0.630 | 0.630 / 0.628 | **0.0026** |
| 32 | 10.41% | 0.07% | 0.820 / 0.820 | 0.820 / 0.820 | **0.0000** |
| 128 | 26.15% | 0.06% | 0.878 / 0.875 | 0.878 / 0.875 | **0.0000** |
| 512 | 26.15% | 0.06% | 0.826 / 0.828 | 0.831 / 0.826 | **0.0052** |

**T2 MET**: at the widest width the closed and open trajectories differ by **26.15% of the peak on the decoder's own
neurons** -- the channel is not being asked about a distance that never reached its inputs. **T3 MET**: the worst
cross-loop gap is **0.0052** -- **two held-out decisions in 384** -- against a falsifier at 0.10. **T4 MET**: the gap
goes from **0.0026** at 8 neurons to **0.0052** at 512, where the registration allowed a growth of 0.10.

**So the answer to `e343`'s open question is no: there is no read-out in this family that sees it.** A decoder with
sixteen times the inputs of the one `e343` used loses the same handful of decisions, and the gap does not grow with
the width. The escape hatch is closed, and the nil is the substrate's and not the decoder's width.

## 4. Why -- and it is visible in the same artifact

The divergence is a **maximum**, and this unit prints the mean beside it. At the widest width the maximum over the
decoder's own 512 neurons is **26.15% of the peak** and its **mean is 0.06%** -- a factor of four hundred. Counted
neuron by neuron, the channel moves **483 of the circuit's 952** neurons by at least 1% of the peak, **17** by at
least 10%, and **none** by 50%; on the draw's own 512: **267**, **8** and **none**.

**That is the mechanism behind the whole chain's dissociation, stated as numbers.** The channel is present on the
read-out, but on almost all of it by a thousandth of the state; `e342`'s "85%" and `e343`'s "117%" and "61% on the
decoder's own neurons" are maxima over a handful of neurons that no linear read-out has any reason to weight. The
labels are separable along directions made of thousands of neurons, and the channel moves eight of them.

## 5. What it cannot do, and where it points

*Width and capacity move together*: a 512-input, four-class probe has 2048 parameters against 768 training
examples, and its own-loop accuracy is **0.826** against 0.878 at 128 -- the widest row is not the best one, so part
of its 0.0052 can be capacity rather than the channel, which is why T3 and T4 are read against the within-loop
numbers and not against chance. *The probe is linear*, so this is the width of a linear read-out and not what a
non-linear decoder could see. *One task, one draw, one circuit, one strength*: four symbols, `scale = 1.0`,
`leak = 0.35`, and a single sample of the ladder the corpus has measured at 0, 32, 128, 300 and 700 through other
instruments. *A frozen body*: nothing trains here, so a trained decoder at 512 inputs is `e341`'s and `e344`'s
instrument and not this one's. *And the divergence is still a maximum over neurons and the last step*, which is not
a norm and not a projection.

**What is left is not a bigger read-out but a different object.** Three instruments now agree that the channel is
real in the state, invisible to every decoder that reads the state for a label, and concentrated on a few neurons:
`e342`'s frozen divergence, `e343`'s cross-loop decoder, and this unit's mean beside its maximum. If a benchmark
wants the loop to matter, the load has to come from somewhere a linear read-out of a fixed neuron set cannot
provide -- which is the same conclusion `e344` reached from the other end, that the answer does not move whether
memory is needed or not.
