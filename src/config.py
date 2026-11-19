"""Разбор и проверка параметров командной строки."""

import argparse
import os
import re
from dataclasses import dataclass
from typing import List, Optional

TEST_PACKAGE_PATTERN = re.compile(r"^[A-Z]+$")
APT_PACKAGE_PATTERN = re.compile(r"^[a-z0-9][a-z0-9+.\-]*$")
VERSION_PATTERN = re.compile(r"^[A-Za-z0-9.+~:\-]+$")
URL_SCHEMES = ("http://", "https://")
IMAGE_SUFFIX = ".png"


class ConfigError(Exception):
    """Ошибка в параметрах, заданных пользователем."""


@dataclass
class Config:
    """Параметры, настраиваемые пользователем."""

    package: str
    repo: str
    test_mode: bool
    version: Optional[str]
    output: str
    tree: bool


class _Parser(argparse.ArgumentParser):
    """Парсер, который сообщает об ошибках исключением."""

    def error(self, message):
        """Передать ошибку разбора аргументов как ConfigError."""
        raise ConfigError(message)


def build_parser() -> argparse.ArgumentParser:
    """Создать парсер опций командной строки."""
    parser = _Parser(
        prog="apt-deps-graph",
        description="Визуализация графа зависимостей пакетов apt.",
    )
    parser.add_argument("-p", "--package", required=True,
                        help="имя анализируемого пакета")
    parser.add_argument("-r", "--repo", required=True,
                        help="URL репозитория или путь к тестовому файлу")
    parser.add_argument("-t", "--test-mode", action="store_true",
                        help="режим работы с тестовым репозиторием")
    parser.add_argument("-v", "--version", default=None,
                        help="версия пакета")
    parser.add_argument("-o", "--output", default="graph.png",
                        help="имя файла с изображением графа")
    parser.add_argument("--tree", action="store_true",
                        help="вывести зависимости в виде ASCII-дерева")
    return parser


def validate_package(name: str, test_mode: bool) -> None:
    """Проверить имя пакета с учётом режима работы."""
    pattern = TEST_PACKAGE_PATTERN if test_mode else APT_PACKAGE_PATTERN
    if not pattern.match(name):
        kind = "большие латинские буквы" if test_mode else "формат apt"
        raise ConfigError(f"недопустимое имя пакета '{name}': ожидается "
                          f"{kind}")


def validate_repo(repo: str, test_mode: bool) -> None:
    """Проверить URL репозитория либо путь к тестовому файлу."""
    if test_mode:
        if not os.path.isfile(repo):
            raise ConfigError(f"файл тестового репозитория не найден: "
                              f"'{repo}'")
        return
    if not repo.startswith(URL_SCHEMES):
        raise ConfigError(f"URL репозитория должен начинаться с http:// "
                          f"или https://: '{repo}'")


def validate_version(version: Optional[str]) -> None:
    """Проверить формат версии пакета, если она задана."""
    if version is not None and not VERSION_PATTERN.match(version):
        raise ConfigError(f"недопустимая версия пакета: '{version}'")


def validate_output(output: str) -> None:
    """Проверить имя выходного файла с изображением."""
    if not output.lower().endswith(IMAGE_SUFFIX):
        raise ConfigError(f"файл изображения должен иметь расширение "
                          f"{IMAGE_SUFFIX}: '{output}'")
    directory = os.path.dirname(output) or os.curdir
    if not os.path.isdir(directory):
        raise ConfigError(f"каталог для изображения не существует: "
                          f"'{directory}'")


def parse_args(argv: Optional[List[str]] = None) -> Config:
    """Разобрать и проверить аргументы командной строки."""
    args = build_parser().parse_args(argv)
    validate_package(args.package, args.test_mode)
    validate_repo(args.repo, args.test_mode)
    validate_version(args.version)
    validate_output(args.output)
    return Config(
        package=args.package,
        repo=args.repo,
        test_mode=args.test_mode,
        version=args.version,
        output=args.output,
        tree=args.tree,
    )
