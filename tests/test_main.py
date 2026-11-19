"""Тесты точки входа приложения."""

import os

import pytest

from src.main import EXIT_ERROR, EXIT_OK, main

DATA = os.path.join(os.path.dirname(__file__), "data")
SINGLE = 1


def run_test_mode(name, package, capsys, output):
    """Запустить приложение на тестовом репозитории."""
    path = os.path.join(DATA, name)
    code = main(["-p", package, "-r", path, "-t", "-o", str(output)])
    return code, capsys.readouterr()


@pytest.fixture
def out_png(tmp_path):
    """Путь к выходному изображению во временном каталоге."""
    return tmp_path / "graph.png"


def test_apt_graph(mirror, capsys, fake_d2, out_png):
    code = main(["-p", "alpha", "-r", mirror, "-v", "1.0",
                 "-o", str(out_png)])
    out = capsys.readouterr().out
    assert code == EXIT_OK
    assert "Вершин: 4, рёбер: 5" in out
    assert "Циклических зависимостей нет" in out
    assert out_png.exists()


def test_chain_creates_image_and_d2(capsys, fake_d2, out_png):
    code, result = run_test_mode("chain.txt", "A", capsys, out_png)
    assert code == EXIT_OK
    assert "Вершин: 4, рёбер: 3" in result.out
    assert out_png.exists()
    assert out_png.with_suffix(".d2").exists()


def test_tree_option(capsys, fake_d2, out_png):
    path = os.path.join(DATA, "diamond.txt")
    main(["-p", "A", "-r", path, "-t", "--tree", "-o", str(out_png)])
    out = capsys.readouterr().out
    assert "├── B" in out
    assert "D (см. выше)" in out


def test_cycle(capsys, fake_d2, out_png):
    _, result = run_test_mode("cycle.txt", "A", capsys, out_png)
    assert "Обнаружены циклические" in result.out
    assert "  C -> A" in result.out


def test_inner_cycle_and_self_loop(capsys, fake_d2, out_png):
    _, result = run_test_mode("inner_cycle.txt", "A", capsys, out_png)
    assert "  D -> B" in result.out
    assert "  E -> E" in result.out


def test_large_graph(capsys, fake_d2, out_png):
    _, result = run_test_mode("large.txt", "A", capsys, out_png)
    assert "Вершин: 9" in result.out


def test_start_from_inner_package(capsys, fake_d2, out_png):
    _, result = run_test_mode("large.txt", "F", capsys, out_png)
    assert "Вершин: 3" in result.out


def test_isolated_package(capsys, fake_d2, out_png):
    _, result = run_test_mode("isolated.txt", "A", capsys, out_png)
    assert "Вершин: 1, рёбер: 0" in result.out


def test_missing_d2_reports_error(capsys, no_d2, out_png):
    code, result = run_test_mode("chain.txt", "A", capsys, out_png)
    assert code == EXIT_ERROR
    assert "d2 не найдена" in result.err


@pytest.mark.parametrize("name", ["broken_syntax.txt", "broken_name.txt",
                                  "duplicate.txt"])
def test_broken_test_repositories(name, capsys, out_png):
    code, result = run_test_mode(name, "A", capsys, out_png)
    assert code == EXIT_ERROR
    assert "Ошибка" in result.err


def test_unknown_package(capsys, out_png):
    code, _ = run_test_mode("chain.txt", "Z", capsys, out_png)
    assert code == EXIT_ERROR


def test_config_error(capsys):
    assert main(["-p", "BAD", "-r", "http://x"]) == EXIT_ERROR
    assert "Ошибка" in capsys.readouterr().err


def test_order_chain(capsys):
    path = os.path.join(DATA, "chain.txt")
    assert main(["-p", "A", "-r", path, "-t", "--order"]) == EXIT_OK
    lines = capsys.readouterr().out.splitlines()
    assert lines[1:] == ["  1. D", "  2. C", "  3. B", "  4. A"]


def test_order_diamond_shared_dependency_once(capsys):
    path = os.path.join(DATA, "diamond.txt")
    main(["-p", "A", "-r", path, "-t", "--order"])
    out = capsys.readouterr().out
    assert out.count(". D") == SINGLE
    assert out.index(". D") < out.index(". B") < out.index(". A")


def test_order_with_cycle_reports_broken_edge(capsys):
    path = os.path.join(DATA, "cycle.txt")
    main(["-p", "A", "-r", path, "-t", "--order"])
    out = capsys.readouterr().out
    assert "  1. C" in out
    assert "Циклы разорваны на рёбрах: C -> A" in out


def test_order_apt(mirror, capsys):
    main(["-p", "alpha", "-r", mirror, "--order"])
    out = capsys.readouterr().out
    assert out.splitlines()[-1] == "  4. alpha"
