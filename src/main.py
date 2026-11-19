"""Точка входа приложения."""

import sys
from typing import List, Optional

from src.apt_repo import Record, RepoError, find_package, load_index
from src.config import Config, ConfigError, parse_args

EXIT_OK = 0
EXIT_ERROR = 2


def print_direct_dependencies(record: Record) -> None:
    """Вывести прямые зависимости пакета (альтернативы через « | »)."""
    print(f"Прямые зависимости {record.name} {record.version}:")
    if not record.depends:
        print("  (нет зависимостей)")
    for group in record.depends:
        print("  " + " | ".join(group))


def run(config: Config) -> None:
    """Выполнить сбор данных и вывести прямые зависимости."""
    if config.test_mode:
        raise RepoError("тестовый режим пока не поддерживается")
    index = load_index(config.repo)
    record = find_package(index, config.package, config.version)
    print_direct_dependencies(record)


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
