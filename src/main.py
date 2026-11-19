"""Точка входа приложения."""

import sys
from typing import List, Optional

from src.apt_repo import RepoError, load_index
from src.config import Config, ConfigError, parse_args
from src.graph import Graph, build_graph, count_edges, find_cycles
from src.sources import make_apt_source, make_test_source

EXIT_OK = 0
EXIT_ERROR = 2


def print_graph(package: str, graph: Graph) -> None:
    """Вывести граф зависимостей в виде списков смежности."""
    print(f"Граф зависимостей {package} (BFS с рекурсией):")
    for name, deps in graph.items():
        print(f"  {name} -> {', '.join(deps) if deps else '-'}")
    print(f"Вершин: {len(graph)}, рёбер: {count_edges(graph)}")


def print_cycles(package: str, graph: Graph) -> None:
    """Сообщить о циклических зависимостях, если они есть."""
    cycles = find_cycles(graph, package)
    if not cycles:
        print("Циклических зависимостей нет")
        return
    print("Обнаружены циклические зависимости (замыкающие рёбра):")
    for source, target in cycles:
        print(f"  {source} -> {target}")


def make_source(config: Config):
    """Создать источник зависимостей для выбранного режима работы."""
    if config.test_mode:
        return make_test_source(config.repo, config.package, config.version)
    index = load_index(config.repo)
    return make_apt_source(index, config.package, config.version)


def run(config: Config) -> None:
    """Построить граф зависимостей и вывести его."""
    graph = build_graph(config.package, make_source(config))
    print_graph(config.package, graph)
    print_cycles(config.package, graph)


def main(argv: Optional[List[str]] = None) -> int:
    """Запустить приложение и вернуть код завершения."""
    try:
        run(parse_args(argv))
    except (ConfigError, RepoError) as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        return EXIT_ERROR
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
