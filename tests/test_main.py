"""Тесты точки входа приложения."""

from src.main import EXIT_ERROR, EXIT_OK, main


def test_main_prints_direct_dependencies(mirror, capsys):
    code = main(["-p", "alpha", "-r", mirror, "-v", "1.0"])
    out = capsys.readouterr().out
    assert code == EXIT_OK
    assert "Прямые зависимости alpha 1.0" in out
    assert "gamma | delta" in out


def test_main_package_without_dependencies(mirror, capsys):
    assert main(["-p", "delta", "-r", mirror]) == EXIT_OK
    assert "нет зависимостей" in capsys.readouterr().out


def test_main_unknown_package(mirror, capsys):
    assert main(["-p", "nothing", "-r", mirror]) == EXIT_ERROR
    assert "Ошибка" in capsys.readouterr().err


def test_main_config_error(capsys):
    assert main(["-p", "BAD", "-r", "http://x"]) == EXIT_ERROR
    assert "Ошибка" in capsys.readouterr().err


def test_main_test_mode_not_supported_yet(tmp_path, capsys):
    repo = tmp_path / "repo.txt"
    repo.write_text("A: B\n")
    assert main(["-p", "A", "-r", str(repo), "-t"]) == EXIT_ERROR
