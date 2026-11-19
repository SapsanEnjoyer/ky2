"""Тесты получения и разбора индекса apt."""

import pytest

from src.apt_repo import (RepoError, clean_name, fetch_index, find_package,
                          index_url, parse_depends, parse_index,
                          parse_provides)


def test_index_url_variants():
    base = "http://host/ubuntu/dists/noble/main/binary-amd64"
    assert index_url(base) == base + "/Packages.gz"
    assert index_url(base + "/") == base + "/Packages.gz"
    assert index_url(base + "/Packages.xz") == base + "/Packages.xz"


def test_clean_name_removes_qualifiers():
    assert clean_name("libfoo:any (>= 1.2)") == "libfoo"
    assert clean_name("pkg [amd64] <!nocheck>") == "pkg"


def test_parse_depends_alternatives():
    groups = parse_depends("a (>= 1), b | c:any, , d")
    assert groups == [["a"], ["b", "c"], ["d"]]


def test_parse_provides():
    assert parse_provides("x (= 1), y") == ["x", "y"]


def test_parse_index(sample_index):
    index = parse_index(sample_index)
    assert set(index) == {"alpha", "beta", "gamma", "delta", "libc6"}
    alpha = index["alpha"][0]
    assert alpha.depends == [["beta"], ["gamma", "delta"], ["libc6"]]
    assert alpha.provides == ["virt-alpha"]
    assert index["beta"][0].depends == [["libc6"], ["gamma"]]


def test_find_package_with_version(sample_index):
    index = parse_index(sample_index)
    assert find_package(index, "beta", "2.0").version == "2.0"
    assert find_package(index, "beta", None).name == "beta"


def test_find_package_errors(sample_index):
    index = parse_index(sample_index)
    with pytest.raises(RepoError, match="не найден"):
        find_package(index, "missing", None)
    with pytest.raises(RepoError, match="доступны"):
        find_package(index, "beta", "9.9")


def test_fetch_plain_and_gzip(mirror):
    plain = fetch_index(mirror + "/Packages")
    packed = fetch_index(mirror)
    assert plain == packed
    assert "Package: alpha" in plain


def test_fetch_missing_file(mirror):
    with pytest.raises(RepoError, match="не удалось скачать"):
        fetch_index(mirror + "/missing/Packages.gz")
