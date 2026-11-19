"""Построение графа зависимостей и операции над ним."""

from typing import Callable, Dict, Iterator, List, Tuple

Graph = Dict[str, List[str]]
Neighbours = Callable[[str], List[str]]
Edge = Tuple[str, str]

VISITING = "visiting"
DONE = "done"


def _bfs_level(level: List[str], neighbours: Neighbours,
               graph: Graph) -> None:
    """Обработать один уровень BFS и рекурсивно перейти к следующему."""
    next_level: List[str] = []
    for name in level:
        if name in graph:
            continue
        graph[name] = neighbours(name)
        next_level.extend(dep for dep in graph[name] if dep not in graph)
    if next_level:
        _bfs_level(next_level, neighbours, graph)


def build_graph(start: str, neighbours: Neighbours) -> Graph:
    """Построить граф достижимых от start зависимостей (BFS, рекурсия).

    Уже обработанные вершины повторно не раскрываются, поэтому
    циклические зависимости не приводят к бесконечному обходу.
    """
    graph: Graph = {}
    _bfs_level([start], neighbours, graph)
    return graph


def _children(graph: Graph, name: str) -> Iterator[str]:
    """Итератор по прямым зависимостям вершины."""
    return iter(graph.get(name, []))


def dfs_postorder(graph: Graph, start: str) -> Tuple[List[str], List[Edge]]:
    """Обойти граф в глубину без рекурсии.

    Возвращает порядок «зависимости раньше зависимых» и список рёбер,
    замыкающих циклы.
    """
    order: List[str] = []
    back_edges: List[Edge] = []
    state = {start: VISITING}
    stack = [(start, _children(graph, start))]
    while stack:
        node, children = stack[-1]
        child = next(children, None)
        if child is None:
            state[node] = DONE
            order.append(node)
            stack.pop()
        elif state.get(child) == VISITING:
            back_edges.append((node, child))
        elif child not in state:
            state[child] = VISITING
            stack.append((child, _children(graph, child)))
    return order, back_edges


def find_cycles(graph: Graph, start: str) -> List[Edge]:
    """Найти рёбра, замыкающие циклические зависимости."""
    return dfs_postorder(graph, start)[1]


def count_edges(graph: Graph) -> int:
    """Посчитать число рёбер графа."""
    return sum(len(deps) for deps in graph.values())
