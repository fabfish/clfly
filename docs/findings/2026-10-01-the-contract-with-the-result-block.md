# The contract with the result block: the three fields the decomposition turned out to be, and the share that did not move

*2026-10-01 10:52. Runs: **none new** — `experiments/e314_the_contract_with_the_result_block.py` reads the corpus
against the **eleven** fields `clfly/bench/conformance.py` now declares, writing
`runs/e314_the_contract_with_the_result_block.json`. Seconds.*

## 1. Why the list grew

`e309` declared eight fields a result must carry for a third party to recompute the benchmark's numbers, and found
**76 of 547** artifacts carrying all eight. `e313` then showed that **the decomposition the block prescribes is
already written down per task** under `learned`, `final_per_task` and `forgetting_per_task`, and that the retention
matrix is the *redundancy* over them. A contract that asked for the matrix and not the fields was asking a reader to
re-derive three stored numbers.

Those three join the list, and the matrix stays: it is what an independent implementation is checked against.

## 2. All four claims, over eleven fields

| | |
|---|---|
| artifacts read (on `e301`'s collapse) | **552** |
| carrying **all eleven** | **76 (14%)** |
| the **scarcest** field | **a read-out draw, 76 (14%)** |

- **K1 MET**: a field the benchmark needs is carried by a seventh of the corpus.
- **K2 MET**: the three added fields are carried by **147** artifacts each — **more than a quarter**, unlike the
  read-out draw's 76 — so the fields a reader can actually use are not the scarce ones, and `e103`'s fingerprint
  remains the rarest thing a result must carry.
- **K3 MET**: **76 of 552 (14%)** carry all eleven.
- **K4 MET, and sharper than `e309` could say it**: the counts run **0, 1, 8, 9, 10, 11** and **nothing between two
  and seven**. So the record is one of **three** things — nothing (163), a seed and nothing else (242), or the result
  block and however much of the rest (147) — and never a partial result.

## 3. What did not move, and that is the point

**The numbers K1, K2 and K3 turn on are the same as `e309`'s**: the same 76 artifacts, the same scarcest field, the
same share. Adding three required fields *could only have shrunk* the conformant set, and it did not, **because the
three fields ride with the matrix they are the cells of**. That is the corpus telling us its runners are consistent —
and it is also the sharpest version of `e309`'s point: a contract's cost is paid by the runners that record least,
and this corpus's least-recording runners are not the ones that made the results.

## 4. What it cannot do

**The eleven are still this unit's selection from a reader's task**, so a benchmark that also wanted the per-task
observability spectrum or the pairwise principal angles would add a twelfth and move nothing here except the
denominators. **Adding fields can only shrink the conformant set**, and the fact that it did not here is a fact about
this corpus and not a guarantee: a corpus whose runners recorded the matrix alone would show the drop. **A predicate
reads one spelling**, unchanged from `e309`. **And conformance is still not quality**: an artifact can carry all
eleven and be wrong, which is every other unit's business.

**RE-READ 2026-10-03: K1 HAS FIRED, as it has for `e309`.** The scarcest of the eleven fields is carried by
**exactly a quarter** of the corpus -- 0.25 on 688 artifacts -- where the claim asked for under a quarter and set
its falsifier at a quarter or more. The window's closed-loop runs (`e374` to `e379`) are what carried the rate to
the boundary, each of them an artifact that must carry the per-task fields and need not carry the read-out draw.
The live test reads K1's verdict off the artifact and pins its measured percentage, and K2, K3 and K4 stay MET: the
read-out draw is still the scarcest of the eleven, the three added fields are still carried well above a quarter,
and the hole in the record's levels is still two to seven.

## RE-READ 2026-10-03, second: K3 reaches its bar too

The previous RE-READ read K1's verdict off the artifact when the scarcest field reached exactly a quarter. `e388` to
`e390` added twenty-one closed-loop runs which all carry the full field set, and the same thing has now happened to
K3: the conformant share is **187 of 740, 0.253**, over the quarter its bar asks for, so **K3 reads FALSIFIER FIRED
at 25%** and its verdict is read off the artifact with its percentage pinned, as K1's is. K1 still fires at 29%, and
K2 and K4 stay MET: the fields a reader can use are still not the scarce ones, and the record is still nothing, a
seed, or the result block and more.

### And the artifact face was still carrying it

As in `e309`, the `< 0.25` survived in the artifact face of the test, and the gate's re-run of this unit wrote the
stored reader with the larger corpus: **187 of 740, 0.253**. That face now asserts a **minority** and reads K3's
verdict off the artifact with its percentage pinned, exactly as the live face does. **K3 reads FALSIFIER FIRED at
25%** on both.
