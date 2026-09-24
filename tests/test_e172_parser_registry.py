"""`e172` turns a stated premise into a checked one, and the check's own limit into a measured fact.

Two things are pinned: the registry reads parsers **statically** (so it cannot be fooled by a parser built at
import time), and the corpus's four artifacts that no parser claims are explained rather than left as defects --
their `config` carries a key the runner **assigns at runtime** rather than any flag, which is the one way a
`config` can carry something a parser does not define.
"""

from __future__ import annotations

from pathlib import Path

from experiments import e172_parser_registry as e172


def test_the_registry_reads_flags_from_syntax_not_from_running_the_module(tmp_path):
    src = tmp_path / "runner.py"
    src.write_text(
        "import argparse\n"
        "p = argparse.ArgumentParser()\n"
        "p.add_argument('--foo-bar', type=int)\n"
        "p.add_argument('--flag', action='store_true')\n"
        "name = '--not-a-flag'\n"
        "p.add_argument(name)\n"
        "class Exploding:\n"
        "    def __init__(self): raise RuntimeError('must not run')\n",
        encoding="utf-8")
    assert e172.parser_keys(src) == {"foo_bar", "flag"}
    # a file that does not parse contributes nothing rather than raising
    bad = tmp_path / "bad.py"
    bad.write_text("def (:\n", encoding="utf-8")
    assert e172.parser_keys(bad) == set()


def test_a_config_is_claimed_by_the_parsers_that_define_every_key_it_carries(tmp_path):
    parsers = {"a.py": {"x", "y", "z"}, "b.py": {"x"}, "c.py": {"y", "z"}}
    assert e172.candidates({"x": 1}, parsers) == ["a.py", "b.py"]
    assert e172.candidates({"x": 1, "z": 2}, parsers) == ["a.py"]
    assert e172.candidates({"w": 1}, parsers) == []


def test_the_registry_dates_forty_times_the_artifacts_e103_can_and_the_four_it_cannot_are_explained():
    from experiments.e103_reproducibility_audit import load_artifacts

    parsers = e172.registry()
    assert len(parsers) >= 70
    assert len(parsers["e8_rate_network.py"]) == 30
    res = e172.classify(load_artifacts(), parsers)
    assert len(res["unique"]) >= 280 and len(res["unclaimed"]) == 4
    # the four are unclaimed for one reason: each carries `save_theta`, which its own runner does NOT define
    configs = {a["name"]: set(a["config"]) for a in load_artifacts()}
    unclaimed = {r["name"] for r in res["unclaimed"]}
    assert unclaimed and all("save_theta" in configs[n] for n in unclaimed)
    # and `save_theta` is not unknown to the tree: it is a FLAG in one runner and a runtime-written synonym in the
    # two runners whose artifacts carry it -- the same key name meaning two different things
    assert [n for n, keys in parsers.items() if "save_theta" in keys] == ["e8_rate_network.py"]
    for name in ("e122_path_geometry.py", "e124_barrier_distribution.py"):
        assert "save_theta" not in parsers[name]
        assert "args.save_theta = args.theta_dir" in (e172.EXPERIMENTS / name).read_text(encoding="utf-8")
    # the registry's coverage against e103's relative rule
    from experiments.e103_reproducibility_audit import epoch_flags

    dated = len(res["unique"]) + len(res["ambiguous"])
    assert dated == 304 and len(epoch_flags(load_artifacts())) == 7
