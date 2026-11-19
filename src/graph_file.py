"""Тестовый репозиторий: файл с описанием графа зависимостей.

Формат: одна строка на пакет, ``A: B C`` — пакет A зависит от B и C.
Пустые строки и строки, начинающиеся с ``#``, игнорируются. Имена пакетов
состоят из больших латинских букв.
"""

import re
from typing import Dict, List

from src.apt_repo import RepoError

NAME_PATTERN = re.compile(r"^[A-Z]+$")
COMMENT_PREFIX = "#"


def _parse_line(number: int, line: str) -> List[str]:
    """Разобрать строку вида «A: B C» в список [A, B, C]."""
    head, separator, tail = line.partition(":")
    if not separator:
        raise RepoError(f"строка {number}: ожидается формат 'A: B C'")
    names = [head.strip()] + tail.split()
    for name in names:
        if not NAME_PATTERN.match(name):
            raise RepoError(f"строка {number}: недопустимое имя пакета "
                            f"'{name}' (нужны большие латинские буквы)")
    return names


def parse_graph_text(text: str) -> Dict[str, List[str]]:
    """Построить словарь «пакет -> зависимости» из текста файла."""
    graph: Dict[str, List[str]] = {}
    for number, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith(COMMENT_PREFIX):
            continue
        name, *deps = _parse_line(number, line)
        if name in graph:
            raise RepoError(f"строка {number}: пакет '{name}' описан "
                            f"повторно")
        graph[name] = list(dict.fromkeys(deps))
    return graph


def load_graph_file(path: str) -> Dict[str, List[str]]:
    """Прочитать тестовый репозиторий из файла."""
    try:
        with open(path, encoding="utf-8") as handle:
            return parse_graph_text(handle.read())
    except OSError as error:
        raise RepoError(f"не удалось прочитать '{path}': {error}") from error
    except UnicodeDecodeError as error:
        raise RepoError(f"файл '{path}' не в кодировке UTF-8") from error
