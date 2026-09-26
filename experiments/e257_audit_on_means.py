"""E257 -- re-arming `e230`'s audit on its means, now that drawing the corpus has emptied its subject.

**`e230`'s own verdict moved to this column at 21:00**, so this module is now the *registration* of that change
and the report of what it found rather than the only place the means are judged; `e230` prints both columns and
declares on the means, and the two modules read the same 42 families.

`e230` asks whether a family's between-`rho` rank contrast is larger than its own drawing scatter, and it reads that
contrast from the **single-drawing** rho cells the record quotes. `e255` and `e256` then drew the whole `rho` grid at
both sizes, so no ladder family has a single-drawing rho group left: the audit's as-read column is undefined for them
and they **leave its scope** rather than being judged -- five of its forty-two families are still auditable, and its
declarations went from five to two in one session.

An instrument that loses its subject as the corpus improves needs re-arming, and `e230` already computes what is
needed: each rho group's **mean**, as its `between_mean` column, which it never judges on. This module reads every
family on that column:

    RESOLVABLE-BY-MEANS      the means contrast exceeds the family's own scatter at the reference rho
    NOT RESOLVABLE BY MEANS   it does not
    NO CONTRAST              the family has fewer than two rho groups, so neither reading is computable

    python -m experiments.e257_audit_on_means
    python -m experiments.e257_audit_on_means --json-out runs/e257_audit_on_means.json

Four registered claims, **all computed in the exploration that wrote this module** and disclosed as confirmatory: the
value here is that the instrument computes them, not that they are blind.

- **G1 -- the re-arming covers more families than the reading it replaces.** The means column yields a verdict for
  **more than five** families against the as-read column's five. **Falsifier**: five or fewer, which would make the
  re-arming pointless.
- **G2 -- and it answers the question for the families that left the scope.** At least one family is
  **RESOLVABLE-BY-MEANS** while its as-read column is undefined. **Falsifier**: none, i.e. every family that lost its
  as-read verdict is also unresolvable on the means.
- **G3 -- and it re-finds what leaving the scope had hidden.** The family **un-declared at 19:20 because it left the
  scope** -- cs 800 `alloy1` -- is **NOT RESOLVABLE** on the means (its means contrast is well inside its own
  scatter). **Falsifier**: it clears on the means, in which case the un-declaration was harmless as well as
  bookkeeping.
- **G4 -- the two surviving declarations survive the re-arming too.** Every family in `e230.DECLARED_UNRESOLVABLE` is
  also not resolvable on the means. **Falsifier**: a declared family that the means clear.

The exit code is the number of claims **REFUSED** because the corpus does not carry the field a claim needs.

**What it cannot do**: **31 of the 42 families have a single rho group**, so neither reading is computable for them at
all -- the means column widens the audit's scope from 5 to 11 families and not to 42, and the rest are un-auditable by
this design rather than resolvable; the means column compares a contrast built from **one mean per rho value** against
a scatter measured at `rho` 0.9 only, so a family whose scatter is larger elsewhere can still read resolvable; "means"
here means the mean of the drawings at each rho, so a family whose drawings straddle a code epoch inherits that (see
`e227`); and nothing here is a new measurement -- every number is `e230`'s own.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from clfly.bench.artifacts import write_json
from experiments import e230_rank_draw_census as e230

CLAIMS = (
    ("G1", "the re-arming covers more families than the reading it replaces",
     "The means column yields a verdict for more than five families, against the as-read column's five",
     "falsifier: five or fewer [confirmatory, computed in the exploration that wrote this module]"),
    ("G2", "and it answers the question for the families that left the scope",
     "At least one family is RESOLVABLE-BY-MEANS while its as-read column is undefined",
     "falsifier: none [confirmatory]"),
    ("G3", "and it re-finds what leaving the scope had hidden",
     "cs 800 alloy1, un-declared at 19:20 because it left the scope, is NOT RESOLVABLE on the means",
     "falsifier: it clears on the means [confirmatory]"),
    ("G4", "the two surviving declarations survive the re-arming too",
     "Every family in e230.DECLARED_UNRESOLVABLE is also not resolvable on the means",
     "falsifier: a declared family that the means clear [confirmatory]"),
)


def rows() -> list[dict]:
    """Every family of `e230`'s with both readings, its means verdict, and its as-read one."""
    out = []
    for f in e230.families(e230.rows_of()):
        within, means = f["within_at_ref"], f["between_mean"]
        single = f["between_single"]
        out.append({
            "circuit_size": f["circuit_size"], "topology": f["topology"],
            "drawings_at_ref": f["drawings_at_ref"], "within_at_ref": within,
            "between_mean": means, "between_single": single,
            "means_verdict": (None if means is None or within is None else means > within),
            "as_read_verdict": (None if single is None or within is None else single > within),
            "declared": (f["circuit_size"], f["topology"]) in e230.DECLARED_UNRESOLVABLE,
            "rho_groups": len(f["rho_groups"]),
        })
    return out


def judge(rs: list[dict]) -> list[dict]:
    covered = [r for r in rs if r["means_verdict"] is not None]
    as_read = [r for r in rs if r["as_read_verdict"] is not None]
    no_contrast = [r for r in rs if r["means_verdict"] is None]
    out: list[dict] = []

    out.append({"id": "G1", "measured": f"the means column covers {len(covered)} families against the as-read column's "
                                        f"{len(as_read)}, with {len(no_contrast)} having no contrast at all",
                "verdict": "MET -- more than five" if len(covered) > len(as_read) else
                           "FALSIFIER FIRED -- no more coverage than the reading it replaces"})

    gained = [r for r in covered if r["as_read_verdict"] is None and r["means_verdict"]]
    out.append({"id": "G2", "measured": "; ".join(f"cs {r['circuit_size']} {r['topology']} "
                                                  f"means {r['between_mean']:.2f} against within {r['within_at_ref']:.2f}"
                                                  for r in sorted(gained, key=lambda r: -(r["between_mean"] /
                                                                                          r["within_at_ref"]))[:6])
                            or "no family gained a verdict",
                "verdict": "MET -- the re-arming answers for families the as-read column cannot see" if gained else
                           "FALSIFIER FIRED -- every family that lost its as-read verdict is unresolvable on means"})

    cs800 = [r for r in rs if r["circuit_size"] == 800 and r["topology"] == "alloy1"]
    if not cs800 or cs800[0]["means_verdict"] is None:
        out.append({"id": "G3", "verdict": "REFUSED -- cs 800 alloy1 carries no means contrast"})
    else:
        r = cs800[0]
        out.append({"id": "G3", "measured": f"cs 800 alloy1: means {r['between_mean']:.2f} against its own scatter "
                                            f"{r['within_at_ref']:.2f} (a ratio of "
                                            f"{r['between_mean'] / r['within_at_ref']:.2f})",
                    "verdict": "MET -- it is not resolvable on the means either" if not r["means_verdict"] else
                               "FALSIFIER FIRED -- it clears on the means"})

    declared = [r for r in rs if r["declared"]]
    cleared = [r for r in declared if r["means_verdict"]]
    out.append({"id": "G4", "measured": "; ".join(f"cs {r['circuit_size']} {r['topology']} means "
                                                  f"{r['between_mean']:.2f} against {r['within_at_ref']:.2f}"
                                                  for r in declared) or "nothing is declared",
                "verdict": "MET -- every declared family is also unresolvable on the means" if not cleared else
                           f"FALSIFIER FIRED -- {[r['topology'] for r in cleared]} clears on the means"})
    return out


def report(rs: list[dict]) -> int:
    covered = [r for r in rs if r["means_verdict"] is not None]
    no_contrast = [r for r in rs if r["means_verdict"] is None]
    print("== e230's families on the means column: the audit re-armed for a drawn corpus ==")
    print(f"   {len(rs)} families: {len(covered)} carry a means contrast, {len(no_contrast)} have a single rho group "
          f"and no contrast at all")
    print(f"   {'cell':>9} {'family':14} {'draw':>5} {'within':>7} {'means':>7} {'means verdict':>14} "
          f"{'as read':>8} {'as-read verdict':>16}")
    for r in sorted(covered, key=lambda r: (r["circuit_size"], r["topology"])):
        single = f"{r['between_single']:.2f}" if r["between_single"] is not None else "-"
        as_read = (("RESOLVABLE" if r["as_read_verdict"] else "NOT RESOLVABLE")
                   if r["as_read_verdict"] is not None else "OUT OF SCOPE")
        means_v = "RESOLVABLE" if r["means_verdict"] else "NOT RESOLVABLE"
        print(f"   cs {r['circuit_size']:>3}     {r['topology']:14} {r['drawings_at_ref']:>5} "
              f"{r['within_at_ref']:>7.2f} {r['between_mean']:>7.2f} {means_v:>14} {single:>8} {as_read:>16}"
              + ("  [DECLARED]" if r["declared"] else ""))

    gained = [r for r in covered if r["as_read_verdict"] is None]
    print(f"\n   {len(gained)} of the {len(covered)} are families the as-read column cannot see at all:")
    for r in sorted(gained, key=lambda r: -(r["between_mean"] / r["within_at_ref"])):
        print(f"      cs {r['circuit_size']} {r['topology']:14} means {r['between_mean']:>6.2f} against within "
              f"{r['within_at_ref']:>5.2f}  ->  {'RESOLVABLE' if r['means_verdict'] else 'NOT RESOLVABLE'}")

    print(f"\n   and {len(no_contrast)} families carry a single rho group, so neither reading applies to them:")
    print("      " + ", ".join(f"cs {r['circuit_size']}/{r['topology']}" for r in no_contrast[:12])
          + (" ..." if len(no_contrast) > 12 else ""))

    print("\n== the registered claims, G1-G4 ==")
    j = judge(rs)
    for c, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row.get('measured', '')}  -> {row['verdict']}")
        print(f"          the claim was: {c[2]}")
        print(f"          and its {c[3]}")
    print("\n   (the means column compares a contrast built from one mean per rho value against a scatter measured at")
    print("    rho 0.9 only, and 31 of the 42 families have a single rho group and are un-auditable by this design)")
    return sum("REFUSED" in r["verdict"] for r in j)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args(argv)
    rs = rows()
    if args.json_out:
        write_json(args.json_out, {"families": rs, "claims": judge(rs)})
        print(f"wrote {args.json_out}")
    return report(rs)


if __name__ == "__main__":
    sys.exit(main())
