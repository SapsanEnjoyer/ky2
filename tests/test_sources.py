"""Тесты источников зависимостей."""

import os

import pytest

from src.apt_repo import RepoError, parse_index
from src.sources import (build_provides, make_apt_source, make_test_source,
                         resolve_group)

DATA = os.path.join(os.path.dirname(__file__), "data")


def test_provides_map(sample_index):
    index = parse_index(sample_index)
    assert build_provides(index) == {"virt-alpha": "alpha"}


def test_resolve_prefers_known_alternative(sample_index):
    index = parse_index(sample_index)
    assert resolve_group(["unknown", "delta"], index, {}) == "delta"


def test_resolve_uses_provider(sample_index):
    index = parse_index(sample_index)
    provides = build_provides(index)
    assert resolve_group(["virt-alpha"], index, provides) == "alpha"


def test_resolve_unknown_keeps_first(sample_index):
    index = parse_index(sample_index)
    assert resolve_group(["x", "y"], index, {}) == "x"


def test_apt_source_neighbours(sample_index):
    index = parse_index(sample_index)
    neighbours = make_apt_source(index, "alpha", "1.0")
    assert neighbours("alpha") == ["beta", "gamma", "libc6"]
    assert neighbours("beta") == ["libc6", "gamma"]
    assert neighbours("missing") == []


def test_test_source_requires_known_package():
    path = os.path.join(DATA, "chain.txt")
    with pytest.raises(RepoError, match="не описан"):
        make_test_source(path, "Z", None)


def test_test_source_rejects_version():
    path = os.path.join(DATA, "chain.txt")
    with pytest.raises(RepoError, match="версия"):
        make_test_source(path, "A", "1")
