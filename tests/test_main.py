"""Тесты точки входа приложения."""

import os

import pytest

from src.main import EXIT_ERROR, EXIT_OK, main

DATA = os.path.join(os.path.dirname(__file__), "data")


def run_test_mode(name, package, capsys):
    """Запустить приложение на тестовом репозитории."""
    path = os.path.join(DATA, name)
    code = main(["-p", package, "-r", path, "-t"])
    return code, capsys.readouterr()


def test_apt_graph(mirror, capsys):
    code = main(["-p", "alpha", "-r", mirror, "-v", "1.0"])
    out = capsys.readouterr().out
    assert code == EXIT_OK
    assert "alpha -> beta, gamma, libc6" in out
    assert "Циклических зависимостей нет" in out


def test_chain(capsys):
    code, result = run_test_mode("chain.txt", "A", capsys)
    assert code == EXIT_OK
    assert "Вершин: 4, рёбер: 3" in result.out


def test_diamond(capsys):
    _, result = run_test_mode("diamond.txt", "A", capsys)
    assert "Вершин: 4, рёбер: 4" in result.out
    assert "Циклических зависимостей нет" in result.out


def test_cycle(capsys):
    _, result = run_test_mode("cycle.txt", "A", capsys)
    assert "Обнаружены циклические" in result.out
    assert "  C -> A" in result.out


def test_inner_cycle_and_self_loop(capsys):
    _, result = run_test_mode("inner_cycle.txt", "A", capsys)
    assert "  D -> B" in result.out
    assert "  E -> E" in result.out


def test_large_graph(capsys):
    _, result = run_test_mode("large.txt", "A", capsys)
    assert "Вершин: 9" in result.out


def test_start_from_inner_package(capsys):
    _, result = run_test_mode("large.txt", "F", capsys)
    assert "Вершин: 3" in result.out


def test_isolated_package(capsys):
    _, result = run_test_mode("isolated.txt", "A", capsys)
    assert "Вершин: 1, рёбер: 0" in result.out


@pytest.mark.parametrize("name", ["broken_syntax.txt", "broken_name.txt",
                                  "duplicate.txt"])
def test_broken_test_repositories(name, capsys):
    code, result = run_test_mode(name, "A", capsys)
    assert code == EXIT_ERROR
    assert "Ошибка" in result.err


def test_unknown_package(capsys):
    code, result = run_test_mode("chain.txt", "Z", capsys)
    assert code == EXIT_ERROR


def test_config_error(capsys):
    assert main(["-p", "BAD", "-r", "http://x"]) == EXIT_ERROR
    assert "Ошибка" in capsys.readouterr().err
