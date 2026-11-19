"""Тесты визуализации графа."""

import pytest

from src.render import (RenderError, ascii_tree, d2_path_for, d2_quote,
                        render_image, to_d2, write_d2)


def test_d2_quote_escapes():
    assert d2_quote('a"b') == '"a\\"b"'
    assert d2_quote("g++") == '"g++"'


def test_to_d2_edges_and_isolated_nodes():
    text = to_d2({"A": ["B"], "B": []})
    assert '"A" -> "B"' in text
    assert text.splitlines()[-1] == '"B"'


def test_d2_path_for():
    assert d2_path_for("out/graph.png") == "out/graph.d2"


def test_write_d2(tmp_path):
    path = tmp_path / "g.d2"
    write_d2({"A": ["B"], "B": []}, str(path))
    assert '"A" -> "B"' in path.read_text(encoding="utf-8")


def test_write_d2_error(tmp_path):
    with pytest.raises(RenderError):
        write_d2({"A": []}, str(tmp_path / "missing" / "g.d2"))


def test_render_image_with_fake_tool(tmp_path, fake_d2):
    source = tmp_path / "g.d2"
    source.write_text("A -> B\n", encoding="utf-8")
    target = tmp_path / "g.png"
    render_image(str(source), str(target))
    assert target.exists()


def test_render_image_without_tool(tmp_path, no_d2):
    with pytest.raises(RenderError, match="не найдена"):
        render_image(str(tmp_path / "g.d2"), str(tmp_path / "g.png"))


def test_render_image_tool_failure(tmp_path, fake_d2):
    with pytest.raises(RenderError, match="ошибкой"):
        render_image(str(tmp_path / "missing.d2"), str(tmp_path / "g.png"))


def test_ascii_tree_chain():
    graph = {"A": ["B"], "B": ["C"], "C": []}
    assert ascii_tree(graph, "A") == "A\n└── B\n    └── C"


def test_ascii_tree_branches():
    graph = {"A": ["B", "C"], "B": ["D"], "C": [], "D": []}
    expected = "A\n├── B\n│   └── D\n└── C"
    assert ascii_tree(graph, "A") == expected


def test_ascii_tree_marks_repeats_and_cycles():
    graph = {"A": ["B", "C"], "B": ["C"], "C": ["A"]}
    lines = ascii_tree(graph, "A").splitlines()
    assert "├── B" in lines
    assert "│   └── C" in lines
    assert "│       └── A (цикл)" in lines
    assert "└── C (см. выше)" in lines


def test_ascii_tree_single_node():
    assert ascii_tree({"A": []}, "A") == "A"


def test_ascii_tree_deep_chain():
    depth = 3000
    graph = {str(i): [str(i + 1)] for i in range(depth)}
    graph[str(depth)] = []
    assert len(ascii_tree(graph, "0").splitlines()) == depth + 1
