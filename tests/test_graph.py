"""Тесты построения графа и обхода."""

from src.graph import build_graph, count_edges, dfs_postorder, find_cycles

DIAMOND_EDGES = 4


def source_from(mapping):
    """Создать функцию зависимостей по словарю."""
    return lambda name: mapping.get(name, [])


def test_chain():
    graph = build_graph("A", source_from({"A": ["B"], "B": ["C"]}))
    assert graph == {"A": ["B"], "B": ["C"], "C": []}


def test_bfs_levels_order():
    mapping = {"A": ["B", "C"], "B": ["D"], "C": ["E"]}
    graph = build_graph("A", source_from(mapping))
    assert list(graph) == ["A", "B", "C", "D", "E"]


def test_diamond_visits_shared_node_once():
    mapping = {"A": ["B", "C"], "B": ["D"], "C": ["D"]}
    graph = build_graph("A", source_from(mapping))
    assert list(graph) == ["A", "B", "C", "D"]
    assert count_edges(graph) == DIAMOND_EDGES


def test_cycle_terminates():
    mapping = {"A": ["B"], "B": ["C"], "C": ["A"]}
    graph = build_graph("A", source_from(mapping))
    assert set(graph) == {"A", "B", "C"}
    assert find_cycles(graph, "A") == [("C", "A")]


def test_self_dependency():
    graph = build_graph("A", source_from({"A": ["A", "B"]}))
    assert find_cycles(graph, "A") == [("A", "A")]


def test_no_cycles_in_dag():
    mapping = {"A": ["B", "C"], "B": ["C"]}
    graph = build_graph("A", source_from(mapping))
    assert find_cycles(graph, "A") == []


def test_postorder_dependencies_first():
    mapping = {"A": ["B", "C"], "B": ["C"]}
    graph = build_graph("A", source_from(mapping))
    order, _ = dfs_postorder(graph, "A")
    assert order == ["C", "B", "A"]


def test_deep_chain_does_not_overflow_dfs():
    depth = 5000
    mapping = {str(i): [str(i + 1)] for i in range(depth)}
    graph = {name: deps for name, deps in mapping.items()}
    graph[str(depth)] = []
    order, cycles = dfs_postorder(graph, "0")
    assert len(order) == depth + 1
    assert cycles == []
