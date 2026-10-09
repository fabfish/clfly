# The method ordering on another substrate: replay leads the penalty by more on the assembly suite

*2026-10-09. `experiments/e476_the_ordering_on_another_substrate.py` makes the run `e276` named as the one measurement
it could not take: the `r32` line's own command with the **assembly suite** in place of the overlap builder, at the
same circuit, head, budget, strength and seed, forty replicates, `naive`, `ewc-block` and `replay`. Four claims, all
four **MET**.*

## 1. The two substrates

| the suite | the baseline's diagonal | the penalty's | the buffer's | the baseline's forgetting | the penalty's | the buffer's |
|---|---|---|---|---|---|---|
| **overlap 0.0** (`e140`) | 0.9125 | 0.9168 | **0.9609** | +0.0750 | +0.0573 | **-0.0034** |
| **assembly** (`e476`) | 0.8455 | 0.8326 | **0.9540** | +0.1622 | +0.1799 | **-0.0057** |

| the contrast | overlap 0.0 | sigma | assembly | sigma |
|---|---|---|---|---|
| `replay` minus `ewc-block`, diagonal | +0.0441 | +9.09 | **+0.1214** | **+13.41** |
| `replay` minus `ewc-block`, forgetting | -0.0607 | -8.42 | **-0.1857** | **-14.06** |
| `ewc-block` minus `naive`, diagonal | +0.0043 | +0.80 | -0.0128 | -1.33 |
| `ewc-block` minus `naive`, forgetting | -0.0177 | -2.09 | +0.0177 | +1.22 |
| `replay` minus `naive`, diagonal | +0.0484 | +9.83 | **+0.1085** | **+13.96** |

| claim | measured | verdict |
|---|---|---|
| RA1 the assembly run is one configuration with the register's own except the suite | **53** keys compared, **0** differing past the inert rule and **20** admitted by it, `input_overlap` **0.0** against **null**, circuit and read-out draw equal, **40** replicates on each arm | **MET** |
| RA2 and replay beats the penalty on another substrate | **+0.1214** at **+13.41** sigma, against the register's **+0.0441** at **+9.09** | **MET** |
| RA3 and it does not pay for it in forgetting | **-0.1857** at **-14.06** sigma, against the register's **-0.0607** at **-8.42** | **MET** |
| RA4 and the penalty's own gain over the baseline is still a null | **-0.0128** at **-1.33** sigma, against the register's **+0.0043** at **+0.80** | **MET** |

## 2. What the second substrate says

**The ordering travels, and it widens.** `e276` read the corpus's largest method contrast off the overlap line and
wrote that whether it survives *"a different substrate -- which is a run, not a re-reading"* was the one thing it could
not do. On the circuit's own three tasks -- olfactory identity, heading, olfactory input, with disjoint supports
instead of an exact overlap -- `replay` leads `ewc-block` by **+0.1214** at **13.41** sigma, against **+0.0441** at
**9.09** on the register's overlap-0.0 run, and by **-0.1857** at **-14.06** sigma on forgetting against **-0.0607** at
**-8.42**. **So the sentence `e276` published is not one line's**: the buffer's advantage is larger on the second
substrate than on any of the three configurations it read, and it is larger in both currencies at once.

**And the widening is the baseline's, not the buffer's.** The buffer lands at **0.9609** and **0.9540** on the two
substrates -- **0.0069** apart -- while the arms that store nothing fall much further: `naive` from **0.9125** to
**0.8455**, `ewc-block` from **0.9168** to **0.8326**. On forgetting the same three move **-0.0034** to **-0.0057**,
**+0.0750** to **+0.1622** and **+0.0573** to **+0.1799**. **So what the assembly suite costs is the two arms without
the buffer**, and the buffer's own level is nearly substrate-invariant: the ordering's growth is the widening gap
between a method that keeps its examples and two that do not, on a suite that punishes not keeping them more.

**And the penalty's own gain over the baseline is a null on both, and on the second it is if anything negative.**
`ewc-block` minus `naive` is **+0.0043** at **0.80** sigma on the register's run and **-0.0128** at **-1.33** sigma on
the assembly suite, and on forgetting **-0.0177** at **-2.09** against **+0.0177** at **+1.22**. **So the two halves of
`e276`'s reading reproduce together**: what carries the interface's signature -- the biological basis's anchoring --
buys nothing over the baseline on either substrate, while the textbook method that has no connectome in it carries the
whole contrast.

**And the two artifacts' `config`s are a generation apart, and that is checked rather than waived.** `e140` predates
the closed-loop block, the sequence builder and `--task-order`, so it records neither those keys nor their defaults.
The comparison uses the project's own rule for that case, read from the registry `e172` builds off the runner's syntax
tree: a key the older artifact **lacks**, whose value in the newer one equals that flag's **default**, is inert --
both runs took the flag's default path and the older one did not write it down. **20** keys are admitted that way and
**no** key both artifacts record disagrees, and `methods` is in that set on the strength of `e102`/`e104`'s C0 check
that each arm trains independently from the same initial body and the same task draws.

## 3. What it cannot do

- **One substrate and one setting**: `lam = 3e-3` on a plastic body at five hundred updates, so `e140`'s frozen-bias
  configuration and `e153`'s `lam = 1.0` overlap-1.0 one are not run, and the two arms `ewc` and `ewc-block-rand` are
  absent, so the **basis** contrast is not in it.
- **And the suite and the arm list move together**: the assembly suite carries no overlap knob, so the difference from
  `e140` is the builder and not a dose, and nothing here says what an intermediate support overlap would cost.
- **And the inert rule is a rule and not a measurement**: it reads the runner's syntax tree, not the code path `e140`
  ran, so a flag whose default changed since that run would be admitted wrongly -- which is why the admitted keys are
  printed.
- **And forty replicates are not the population**: every sigma here is the paired one over the seeds the two runs
  share, and the two runs are one draw of the circuit, the head and the supports each.
- **And a diagonal is not a mechanism**: what each arm buys and what it spends is `e423`'s reading on the card's world,
  and the widening above is an accounting of levels and not a decomposition.

## RE-READ 2026-10-09: the owed run is made, and the ordering is larger on the second substrate

`e276`'s fourth bullet says *"no run is made: this is a read of runs the register already has, and the missing
measurement is the one that would say whether the ordering survives a different substrate -- which is a run, not a
re-reading."* The run is made, on the assembly suite at `e140`'s own settings: `replay` minus `ewc-block` is
**+0.1214** at **13.41** sigma on the diagonal and **-0.1857** at **-14.06** on forgetting, against **+0.0441** at
**9.09** and **-0.0607** at **-8.42** on the register's overlap-0.0 run, and `ewc-block` minus `naive` is a null on
both (**0.80** and **-1.33** sigma). **So the ordering travels and widens, and the widening belongs to the baseline**:
the buffer lands **0.0069** apart on the two substrates while the arms without it fall by **0.067** and **0.084**. What
this finding's own numbers said stands; what changes is that its scope is no longer one line's
(`docs/findings/2026-10-09-the-ordering-on-another-substrate.md`).
