"""Тесты разбора параметров командной строки."""

import pytest

from src.config import ConfigError, parse_args

APT_REPO = "http://archive.ubuntu.com/ubuntu/dists/noble/main/" \
           "binary-amd64/Packages.gz"


def test_parse_apt_mode():
    config = parse_args(["-p", "bash", "-r", APT_REPO, "-v", "5.2"])
    assert config.package == "bash"
    assert config.version == "5.2"
    assert config.test_mode is False
    assert config.output == "graph.png"


def test_parse_test_mode(tmp_path):
    repo = tmp_path / "repo.txt"
    repo.write_text("A: B\n")
    config = parse_args(["-p", "A", "-r", str(repo), "-t", "--tree"])
    assert config.test_mode is True
    assert config.tree is True
    assert config.order is False


def test_parse_order_flag():
    config = parse_args(["-p", "bash", "-r", APT_REPO, "--order"])
    assert config.order is True


def test_missing_package():
    with pytest.raises(ConfigError):
        parse_args(["-r", APT_REPO])


def test_bad_apt_package_name():
    with pytest.raises(ConfigError):
        parse_args(["-p", "Bad Name", "-r", APT_REPO])


def test_lowercase_name_in_test_mode(tmp_path):
    repo = tmp_path / "repo.txt"
    repo.write_text("A: B\n")
    with pytest.raises(ConfigError):
        parse_args(["-p", "a", "-r", str(repo), "-t"])


def test_bad_url():
    with pytest.raises(ConfigError):
        parse_args(["-p", "bash", "-r", "ftp://example.org/x"])


def test_missing_test_file(tmp_path):
    missing = str(tmp_path / "none.txt")
    with pytest.raises(ConfigError):
        parse_args(["-p", "A", "-r", missing, "-t"])


def test_bad_version():
    with pytest.raises(ConfigError):
        parse_args(["-p", "bash", "-r", APT_REPO, "-v", "1 2"])


def test_bad_output_suffix():
    with pytest.raises(ConfigError):
        parse_args(["-p", "bash", "-r", APT_REPO, "-o", "graph.jpg"])


def test_bad_output_directory(tmp_path):
    output = str(tmp_path / "missing" / "graph.png")
    with pytest.raises(ConfigError):
        parse_args(["-p", "bash", "-r", APT_REPO, "-o", output])
