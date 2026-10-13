"""Validation and ViennaRNA-adapter tests."""

import sys
from types import SimpleNamespace

import pytest

from rna_shape_predictor.folding import fold_rna, normalize_sequence, parse_dot_bracket


def test_fasta_and_transcription():
    assert normalize_sequence(">sample\nGGGTTT\nCCC") == "GGGUUUCCC"


@pytest.mark.parametrize("invalid", ["", "ACGN", "AU*GC", "A" * 501, ">one\nACGU\n>two\nACGU"])
def test_invalid_sequences_rejected(invalid):
    with pytest.raises(ValueError):
        normalize_sequence(invalid)


def test_dot_bracket_validation():
    assert parse_dot_bracket("(((...)))") == [[1, 9], [2, 8], [3, 7]]
    for malformed in ["((", ")(", "[[]]"]:
        with pytest.raises(ValueError):
            parse_dot_bracket(malformed)


def test_fold_uses_vienna_api(monkeypatch):
    monkeypatch.setitem(sys.modules, "RNA", SimpleNamespace(fold=lambda seq: ("(((...)))", -3.25)))
    result = fold_rna("GGGAAACCC")
    assert result["structure"] == "(((...)))"
    assert result["energy_kcal_mol"] == -3.25
    assert result["base_pairs"] == [[1, 9], [2, 8], [3, 7]]
    assert result["method"].startswith("ViennaRNA")


def test_fold_rejects_wrong_length(monkeypatch):
    monkeypatch.setitem(sys.modules, "RNA", SimpleNamespace(fold=lambda seq: ("...", -1.0)))
    with pytest.raises(RuntimeError):
        fold_rna("GGGAAACCC")


def test_live_viennarna_if_available():
    RNA = pytest.importorskip("RNA")
    result = fold_rna("GGGAAACCC")
    assert len(result["structure"]) == result["length"] == 9
    assert isinstance(result["energy_kcal_mol"], float)
    assert isinstance(result["base_pairs"], list)
