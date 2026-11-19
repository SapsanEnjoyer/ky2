"""Визуализация графа: текст D2, изображение PNG и ASCII-дерево."""

import os
import shutil
import subprocess
from typing import List, Set, Tuple

from src.graph import Graph

D2_BINARY = "d2"
D2_SUFFIX = ".d2"
RENDER_TIMEOUT = 300
BRANCH = "├── "
LAST_BRANCH = "└── "
PIPE = "│   "
BLANK = "    "
SEEN_MARK = " (см. выше)"
CYCLE_MARK = " (цикл)"


class RenderError(Exception):
    """Ошибка построения изображения графа."""


def d2_quote(name: str) -> str:
    """Заключить имя вершины в кавычки по правилам D2."""
    escaped = name.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def to_d2(graph: Graph) -> str:
    """Построить описание графа на языке D2."""
    lines = ["direction: right"]
    for name, deps in graph.items():
        if not deps:
            lines.append(d2_quote(name))
        lines.extend(f"{d2_quote(name)} -> {d2_quote(dep)}" for dep in deps)
    return "\n".join(lines) + "\n"


def d2_path_for(image_path: str) -> str:
    """Получить путь к файлу D2 рядом с изображением."""
    return os.path.splitext(image_path)[0] + D2_SUFFIX


def write_d2(graph: Graph, path: str) -> None:
    """Сохранить описание графа D2 в файл."""
    try:
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(to_d2(graph))
    except OSError as error:
        raise RenderError(f"не удалось записать '{path}': {error}") from error


def render_image(d2_path: str, image_path: str) -> None:
    """Построить изображение из файла D2 утилитой d2."""
    binary = shutil.which(D2_BINARY)
    if binary is None:
        raise RenderError("утилита d2 не найдена в PATH "
                          "(установка: https://d2lang.com)")
    try:
        result = subprocess.run(
            [binary, d2_path, image_path], capture_output=True,
            text=True, timeout=RENDER_TIMEOUT, check=False)
    except (OSError, subprocess.TimeoutExpired) as error:
        raise RenderError(f"не удалось запустить d2: {error}") from error
    if result.returncode:
        raise RenderError(f"d2 завершилась с ошибкой: "
                          f"{result.stderr.strip()}")


def _tree_children(graph: Graph, name: str, prefix: str) -> List[Tuple]:
    """Подготовить записи стека для потомков вершины (в обратном порядке)."""
    deps = graph.get(name, [])
    items = []
    for position, dep in enumerate(deps):
        last = position == len(deps) - 1
        items.append(("node", dep, prefix, last))
    return items[::-1]


def ascii_tree(graph: Graph, root: str) -> str:
    """Построить ASCII-дерево зависимостей без рекурсии.

    Повторно встреченные вершины не раскрываются и помечаются.
    """
    lines = [root]
    expanded: Set[str] = {root}
    on_path: Set[str] = {root}
    stack = [("exit", root)] + _tree_children(graph, root, "")
    while stack:
        item = stack.pop()
        if item[0] == "exit":
            on_path.discard(item[1])
            continue
        _, name, prefix, last = item
        mark = ""
        if name in on_path:
            mark = CYCLE_MARK
        elif name in expanded:
            mark = SEEN_MARK
        lines.append(prefix + (LAST_BRANCH if last else BRANCH) + name + mark)
        if mark:
            continue
        expanded.add(name)
        on_path.add(name)
        stack.append(("exit", name))
        child_prefix = prefix + (BLANK if last else PIPE)
        stack.extend(_tree_children(graph, name, child_prefix))
    return "\n".join(lines)
