"""Точка входа приложения."""

import sys
from typing import List, Optional

from src.apt_repo import RepoError, load_index
from src.config import Config, ConfigError, parse_args
from src.graph import (Graph, build_graph, count_edges, dfs_postorder,
                       find_cycles)
from src.render import (RenderError, ascii_tree, d2_path_for, render_image,
                        write_d2)
from src.sources import make_apt_source, make_test_source

EXIT_OK = 0
EXIT_ERROR = 2


def print_summary(graph: Graph) -> None:
    """Вывести число вершин и рёбер построенного графа."""
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


def print_load_order(package: str, graph: Graph) -> None:
    """Вывести порядок загрузки: зависимости раньше зависимых пакетов."""
    order, cycles = dfs_postorder(graph, package)
    print(f"Порядок загрузки зависимостей {package}:")
    for number, name in enumerate(order, start=1):
        print(f"  {number}. {name}")
    if cycles:
        print("Циклы разорваны на рёбрах: " + ", ".join(
            f"{source} -> {target}" for source, target in cycles))


def make_source(config: Config):
    """Создать источник зависимостей для выбранного режима работы."""
    if config.test_mode:
        return make_test_source(config.repo, config.package, config.version)
    index = load_index(config.repo)
    return make_apt_source(index, config.package, config.version)


def save_image(config: Config, graph: Graph) -> None:
    """Сохранить описание D2 и построить изображение графа."""
    d2_path = d2_path_for(config.output)
    write_d2(graph, d2_path)
    render_image(d2_path, config.output)
    print(f"Описание графа D2: {d2_path}")
    print(f"Изображение графа: {config.output}")


def run(config: Config) -> None:
    """Построить граф и вывести порядок загрузки либо дерево и картинку."""
    graph = build_graph(config.package, make_source(config))
    if config.order:
        print_load_order(config.package, graph)
        return
    print_summary(graph)
    print_cycles(config.package, graph)
    if config.tree:
        print(ascii_tree(graph, config.package))
    save_image(config, graph)


def main(argv: Optional[List[str]] = None) -> int:
    """Запустить приложение и вернуть код завершения."""
    try:
        run(parse_args(argv))
    except (ConfigError, RepoError, RenderError) as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        return EXIT_ERROR
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
