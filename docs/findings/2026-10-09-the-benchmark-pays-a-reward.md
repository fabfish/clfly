# The benchmark pays a reward: its currency disagrees with the accuracy, and the arms' ordering is reversed

*2026-10-09. `experiments/e485_the_benchmark_pays_a_reward.py` reads the first runner artifact that carries a
**reward**: `--loop-reward` builds the loop's environment with the payout `e483` gave it, and `run_method` records a
**retention matrix in reward** beside the accuracy. **RA1 and RA4 MET** and **RA2 and RA3 both FIRED**.*

## 1. The two currencies

| the arm | the reward diagonal | the reward last row | the contrast | sigma | the accuracy diagonal | the accuracy last row |
|---|---|---|---|---|---|---|
| `naive` | -6.8857 | -6.5639 | **-0.3218** | **-4.91** | **0.7691** | 0.5191 |
| `ewc-block` | -6.8495 | -6.4992 | **-0.3503** | **-4.98** | 0.7073 | 0.4889 |
| `replay` | -6.8743 | -6.6866 | **-0.1877** | **-3.46** | 0.7389 | 0.6785 |

| claim | measured | verdict |
|---|---|---|
| RA1 the flag is the only field moved | **52** config fields, **0** differing past the inert rule, the flag `[None, True]`, and the environment's draw **22** fields with **0** differing, the payout's map being the one the flag adds | **MET** |
| RA2 the game's own currency keeps the diagonal | the diagonal is **below** the last row on every arm, at **-4.91**, **-4.98** and **-3.46** sigma | **FALSIFIER FIRED** |
| RA3 the two currencies order the arms the same way | the accuracy orders them `naive`, `replay`, `ewc-block` and the reward orders them **`ewc-block`, `replay`, `naive`** | **FALSIFIER FIRED** |
| RA4 the first task is one training in all three arms | the reward matrices' first rows are identical across the three arms, to six decimals | **MET** |

## 2. What the reward says

**The benchmark pays a reward now, and it is the opposite of what the benchmark measures.** On the accuracy the
sequence **forgets**: the diagonal is above the last row on every arm by **0.2500**, **0.2184** and **0.0604**. On the
reward it **gains**: the diagonal is **below** the last row on every arm, by **0.3218**, **0.3503** and **0.1877**, at
**-4.91**, **-4.98** and **-3.46** sigma. **So the sentence *the sequence forgets* is a sentence about the head and
not about the game**: what the world pays on a task the body is no longer training on goes **up** as the sequence
proceeds, on all three arms, and the accuracy the corpus counts goes down.

**And the arms' ordering is exactly reversed.** The accuracy diagonal ranks them `naive` (**0.7691**), `replay`
(**0.7389**), `ewc-block` (**0.7073**); the reward diagonal ranks them `ewc-block` (**-6.8495**), `replay`
(**-6.8743**), `naive` (**-6.8857**). **So the arm the benchmark calls best is the arm the world pays least**, and the
spread is the same order of magnitude in both currencies while the order is turned round. That is the same sentence
`e477` produced from the other side -- its QA4 was a **NULL** at **+0.0137** at **0.99** sigma when a policy was
trained toward a payout, so the game's objective neither bought nor cost the read-out -- and here it is at a
**reversal** rather than at a null.

**And the reward's own currency is a body's, which is what makes the disagreement readable.** The head reads and is
not paid, so a reward matrix moves only when the recurrent weights do, and the accuracy matrix moves when either
does. **So the two currencies disagree because one of them is the head's**: a task's accuracy can fall while the body
that carries it drives the world better, and the two are not two measurements of one thing.

**And the flag is the only field the reward moves.** **52** config fields with **none** differing past the inert rule,
and the environment's own draw -- **22** fields: the three populations, the cue templates, the drive's map, the read
map, the coupling, the world's dimensions and leak -- with none differing either, the payout's map being the one field
the flag adds. **And the three arms are one training on task 0**: their reward matrices' first rows are identical to
six decimals, which is what a claim needs when on that task there is neither a penalty nor a buffer.

## 3. What it cannot do

- **One configuration**: the card's neutral roll at one world, one budget and one seed stream.
- **And the payout is the cue's and not the label's**: the target is a linear read of the cue, so a reward on the
  label, on the action, or sparse in time is not in it.
- **And the reward is the noisiest currency the corpus has**: `e484` found the cue's share of the payout under the
  payout's own scatter at this cue noise, so the matrix is a coarse instrument and its **-3.46** to **-4.98** sigma
  are large numbers about small differences (**0.19** to **0.35** in a currency whose cells run about **-6.9**).
- **And the head is never paid**: what the reward says is a property of the world and the recurrent weights, and
  nothing here pays a decoder.
- **And twenty replicates are one body and one circuit**: every sigma is the paired one over the seeds the two runs
  share.
