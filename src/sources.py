"""Источники зависимостей: реальный индекс apt и тестовый файл."""

from typing import Dict, List, Optional

from src.apt_repo import Record, RepoError, find_package
from src.graph import Neighbours
from src.graph_file import load_graph_file


def build_provides(index: Dict[str, List[Record]]) -> Dict[str, str]:
    """Сопоставить виртуальным пакетам первый реальный пакет-поставщик."""
    provides: Dict[str, str] = {}
    for name, records in index.items():
        for virtual in records[0].provides:
            provides.setdefault(virtual, name)
    return provides


def resolve_group(group: List[str], index: Dict[str, List[Record]],
                  provides: Dict[str, str]) -> str:
    """Выбрать из группы альтернатив пакет, известный индексу."""
    for name in group:
        if name in index:
            return name
    for name in group:
        if name in provides:
            return provides[name]
    return group[0]


def apt_neighbours(index: Dict[str, List[Record]], root: Record) -> Neighbours:
    """Создать функцию получения зависимостей по индексу apt."""
    provides = build_provides(index)

    def neighbours(name: str) -> List[str]:
        """Вернуть список зависимостей пакета без повторов."""
        record = root if name == root.name else index.get(name, [None])[0]
        if record is None:
            return []
        names = [resolve_group(group, index, provides)
                 for group in record.depends]
        return list(dict.fromkeys(names))

    return neighbours


def make_apt_source(index: Dict[str, List[Record]], package: str,
                    version: Optional[str]) -> Neighbours:
    """Подготовить источник зависимостей для реального репозитория."""
    root = find_package(index, package, version)
    return apt_neighbours(index, root)


def make_test_source(path: str, package: str,
                     version: Optional[str]) -> Neighbours:
    """Подготовить источник зависимостей для тестового репозитория."""
    if version is not None:
        raise RepoError("в тестовом режиме версия пакета не используется")
    graph = load_graph_file(path)
    if package not in graph:
        raise RepoError(f"пакет '{package}' не описан в файле '{path}'")
    return lambda name: graph.get(name, [])
