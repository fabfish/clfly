# Where the climb starts: the bottom is flat from fourteen to thirty, and the recovery begins after it

*2026-10-03. `experiments/e390_where_the_climb_starts.py` samples the wide step's first task at five budgets between
`e389`'s twenty updates and `e380`'s five hundred -- **30**, **45**, **65**, **85**, **100** -- the same cell and
rate at the corpus's twenty replicates, with the twenty point read from `e389`'s artifact and the five-hundred point
rolled from `e380`'s saved bodies. The reader is `runs/e390_where_the_climb_starts.json`. Five claims, registered
before any of the new runs' readings was opened.*

## 1. The whole trajectory, one update to five hundred

| iterations | probe on task 0's examples | sem | trained head, task 0 |
|---|---|---|---|
| 1 | 0.6792 | 0.0087 | 0.0833 |
| 5 | 0.5979 | 0.0224 | 0.2083 |
| 14 | **0.5479** | 0.0228 | 0.2083 |
| 20 | 0.5740 | 0.0243 | -- |
| **30** | **0.5677** | **0.0221** | **0.2708** |
| **45** | **0.5844** | **0.0182** | **0.2708** |
| **65** | **0.6146** | **0.0149** | **0.3542** |
| **85** | **0.6167** | **0.0209** | **0.3542** |
| **100** | **0.6385** | **0.0188** | **0.3333** |
| 500 | **0.7729** | 0.0153 | 0.7500 |

chance 0.2500; the connectome's own weights read **0.6875** on these examples. The rows before 20 are `e389`'s, at
the same twenty replicates; 20 comes from that artifact and 500 from `e380`'s run, rolled here at the same count.

| claim | measured | verdict |
|---|---|---|
| K1 one configuration except the budget | `iters` and `repeats` alone differing, on all six runs | **MET** |
| K2 the far end is above the near end | **+0.1990** | **MET** |
| K3 the climb is under way by a hundred | **+0.0906** above the floor | **MET** |
| K4 it rises at every sample on the way | the budget of **20** is not above **30** | **FALSIFIER FIRED** |
| K5 the climb is above the instrument | **2.92** times the widest error | **NULL** |

## 2. What fired, and what it answers

**The bottom is flat from the floor to thirty, and the recovery starts after it.** The readings over the interval
are 0.5740, **0.5677**, 0.5844, 0.6146, 0.6167, 0.6385. The step from 20 to 30 goes the wrong way by **0.0063**,
which is a quarter of the standard errors at those budgets (0.0243 and 0.0221), so K4's strict-rise falsifier fired
on a move that is not a drop: what the series shows is a **plateau** running from the floor at 14 (0.5479) through
20 and 30, and a climb starting between **30** and **45**. Of the four steps after that, 45 to 65 is the first
clearly above its noise, **+0.0302** against 0.0182 and 0.0149.

**And the climb to a hundred is a shallower thing than the gap to five hundred.** K5 returned **NULL** at **2.92**
times the widest error: the span from the lowest sampled reading to the highest is 0.0708, against a widest error of
0.0243. So the recovery from the floor to a hundred is about three standard errors of movement, where the whole
distance to five hundred is **0.1990** -- most of the recovery happens after a hundred updates.

**And the head starts steering where the world starts climbing.** Every reading at or below the floor has the
trained head at 0.2083, below chance; at 30 it is **0.2708**, at 65 and 85 **0.3542**, and at 100 **0.3333**. The
head walks up with the body rather than after it, which is the same coupling `e379` and `e380` found at the two ends
of the window.

**Reported and not claimed**: the five-hundred point reads **0.7729** here where `e384`'s series recorded **0.7792**
from the same run, so that series' far end was the same artifact read at five replicates for the probe. The
difference is 0.0063, inside the error.

## 3. What the trajectory now is

One update leaves 0.6792; five leave 0.5979; the floor is **0.5479** at fourteen; the bottom is flat to **30**;
the climb is **0.6385** at a hundred; five hundred is **0.7729**. The wide step's first task is now a measured
trajectory at one replicate count from one update to five hundred, with the descent, the floor, the flat bottom and
the climb each sampled.

## 4. What it cannot settle, and what it registers

- **The climb's start is bounded between 30 and 45.** Five samples put the last flat budget and the first rising one
  two samples apart; a start inside one of those gaps is invisible.
- **Between a hundred and five hundred there is nothing.** The largest single unmeasured stretch in the trajectory
  is four hundred updates wide, and it holds most of the recovery; sampling it is what this leaves open.
- *One cell and one draw*: the action source at `cue@0`, so the cue source and the tight end are not resolved this
  way. *And a probe is not a mechanism*: a reading says how much of the label a linear fit recovers from the world's
  eight numbers, so the climb is a shape in what is recoverable and not a named process.
