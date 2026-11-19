"""Точка входа приложения."""

import sys
from typing import List, Optional

from src.config import Config, ConfigError, parse_args

EXIT_OK = 0
EXIT_ERROR = 2


def print_config(config: Config) -> None:
    """Вывести параметры пользователя в формате ключ-значение."""
    version = config.version if config.version else "не задана"
    print(f"package: {config.package}")
    print(f"repo: {config.repo}")
    print(f"test_mode: {config.test_mode}")
    print(f"version: {version}")
    print(f"output: {config.output}")
    print(f"tree: {config.tree}")


def main(argv: Optional[List[str]] = None) -> int:
    """Запустить приложение и вернуть код завершения."""
    try:
        config = parse_args(argv)
    except ConfigError as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        return EXIT_ERROR
    print_config(config)
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
