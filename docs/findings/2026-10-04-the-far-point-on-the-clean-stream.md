# The far point on the clean stream: the recovery is the world's and not the stream's, and the stream axis shrinks

*2026-10-04. `experiments/e403_the_far_point_on_the_clean_stream.py` puts the stream axis at the far point. `e394`
drew the card's world at three clean training streams -- `--seed0` with `--readout-seed 0 --loop-seed 0`, so the
read-out draw and the environment stay the card's -- and found the stream moves the body **0.0396** where `e393`'s
four engine redraws move it **0.0906**; both were at **twenty** updates. `e396` then found the world axis failing at
**five hundred** -- one of five worlds recovers and four end below an untrained body. This unit runs the same test
`e394` ran, at the budget where the world axis failed. Five claims, registered before any of the new runs' readings
was opened.*

## 1. Three streams at the far point

| stream | connectome's own reading | body after 500 updates | gain over the connectome | trained head |
|---|---|---|---|---|
| the card's | 0.6875 | **0.7729** | **+0.0854** | 0.7500 |
| **1** | 0.6875 | **0.7625** | **+0.0750** | 0.6875 |
| **2** | 0.6875 | **0.7406** | **+0.0531** | 0.5417 |

chance 0.2500. The read-out draw and all six environment fingerprints take **one** value across the three runs, so
only the training seeds move.

| claim | measured | verdict |
|---|---|---|
| AC1 one configuration except the stream | 30 pinned, 3 of the stream, **none** in neither list, **none** moved | **MET** |
| AC2 the draws are the card's | **1** value across the three | **MET** |
| AC3 the recovery replicates on every stream | **+0.0750** and **+0.0531** | **MET** |
| AC4 the initial reading does not move | **0.6875** three times, spread **0.0000** | **MET** |
| AC5 the stream axis is small at the far point too | **0.0323** against the worlds' **0.3344**, **0.097** of it | **MET** |

## 2. What the three streams say

**The far point's failure belongs to the world axis.** Four of five engine redraws end below an untrained body by
0.1479 to 0.2490; the card's world gains **+0.0854**, and with the read-out and the environment pinned and only the
training seeds moved it still gains **+0.0750** and **+0.0531** -- **every stream recovers**. So the one world that
keeps the cue is distinguished by **the world it is** and not by the seeds it was run with, and the failure of the
other four is a property of their draws rather than of the training.

**And the stream axis shrinks from the near point to the far one.** At twenty updates the three streams' bodies span
**0.0396** against the five worlds' **0.0906**, **0.437** of the world's spread. At five hundred the three streams
span **0.0323** against the worlds' **0.3344**, **0.097** of it -- the same axis, on the same worlds, worth a tenth
at the far point of what it was worth at the near one. So the two axes separate as the training runs: what the
weights end up computing is much more about which world the agent is in than about which seeds it was trained with.

**And the head separates the streams where the world does not.** The trained heads read 0.7500, 0.6875 and 0.5417 --
a spread of **0.2083**, six times the worlds' spread on the same three runs -- while the worlds' own readings span
0.0323. So on this axis the head is the variable part and the world the stable one, which is the mirror of the four
worlds that failed, where the heads read 0.75 to 0.83 and the worlds collapsed.

## 3. What it cannot settle, and what it registers

- **Two streams are two samples**, at one budget and one arm, and this is the card's world only: another world's
  streams are not drawn, so a stream that failed here would not have said whether another world's would too.
- **The control is seven identical fingerprints** and not a proof that no other draw followed `seed0`, since
  `--support-seed` and `--partition-seed` default to it.
- **And the head's spread is one replicate's reading each**, so the 0.2083 is a shape and not a mean difference.
- *And a probe is not a mechanism.*
