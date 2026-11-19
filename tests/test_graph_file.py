"""Тесты тестового репозитория (файл с графом)."""

import os

import pytest

from src.apt_repo import RepoError
from src.graph_file import load_graph_file, parse_graph_text

DATA = os.path.join(os.path.dirname(__file__), "data")


def data_path(name):
    """Путь к файлу тестового репозитория."""
    return os.path.join(DATA, name)


def test_parse_ignores_comments_and_blank_lines():
    text = "# c\n\nA: B C\nB:\n"
    assert parse_graph_text(text) == {"A": ["B", "C"], "B": []}


def test_parse_removes_duplicate_dependencies():
    assert parse_graph_text("A: B B C\n") == {"A": ["B", "C"]}


def test_load_diamond():
    graph = load_graph_file(data_path("diamond.txt"))
    assert graph["A"] == ["B", "C"]


def test_syntax_error_reports_line():
    with pytest.raises(RepoError, match="строка 2"):
        load_graph_file(data_path("broken_syntax.txt"))


def test_invalid_name():
    with pytest.raises(RepoError, match="недопустимое имя"):
        load_graph_file(data_path("broken_name.txt"))


def test_duplicate_package():
    with pytest.raises(RepoError, match="повторно"):
        load_graph_file(data_path("duplicate.txt"))


def test_missing_file():
    with pytest.raises(RepoError, match="не удалось прочитать"):
        load_graph_file(data_path("nothing.txt"))
