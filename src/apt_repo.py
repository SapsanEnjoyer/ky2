"""Получение и разбор индекса пакетов Ubuntu (формат apt Packages)."""

import gzip
import lzma
import re
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Dict, Iterator, List, Optional

FIELD_NAMES = ("Package", "Version", "Depends", "Pre-Depends", "Provides")
INDEX_NAMES = ("Packages", "Packages.gz", "Packages.xz")
DEFAULT_INDEX = "Packages.gz"
FETCH_TIMEOUT = 60
USER_AGENT = "apt-deps-graph/1.0"
QUALIFIERS = re.compile(r"\(.*?\)|\[.*?\]|<.*?>")


class RepoError(Exception):
    """Ошибка получения или разбора данных репозитория."""


@dataclass
class Record:
    """Описание одной версии пакета из индекса."""

    name: str
    version: str
    depends: List[List[str]] = field(default_factory=list)
    provides: List[str] = field(default_factory=list)


def index_url(repo: str) -> str:
    """Получить URL файла Packages по адресу репозитория."""
    base = repo.rstrip("/")
    if base.rsplit("/", 1)[-1] in INDEX_NAMES:
        return base
    return f"{base}/{DEFAULT_INDEX}"


def decode_payload(url: str, payload: bytes) -> str:
    """Распаковать содержимое индекса в соответствии с его расширением."""
    if url.endswith(".gz"):
        payload = gzip.decompress(payload)
    elif url.endswith(".xz"):
        payload = lzma.decompress(payload)
    return payload.decode("utf-8", errors="replace")


def fetch_index(repo: str) -> str:
    """Скачать индекс пакетов репозитория и вернуть его текст."""
    url = index_url(repo)
    request = urllib.request.Request(
        url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=FETCH_TIMEOUT) as resp:
            payload = resp.read()
        return decode_payload(url, payload)
    except (urllib.error.URLError, OSError) as error:
        raise RepoError(f"не удалось скачать '{url}': {error}") from error
    except (EOFError, lzma.LZMAError) as error:
        raise RepoError(f"повреждённый индекс '{url}': {error}") from error


def _feed_line(line: str, current: Dict[str, str], last: List[str]) -> None:
    """Обработать одну строку стансы, обновив текущее описание."""
    if line[0] in " \t":
        if last[0] in current:
            current[last[0]] += " " + line.strip()
        return
    name, _, value = line.partition(":")
    last[0] = name
    if name in FIELD_NAMES:
        current[name] = value.strip()


def parse_stanzas(text: str) -> Iterator[Dict[str, str]]:
    """Разбить текст индекса на описания пакетов (нужные поля)."""
    current: Dict[str, str] = {}
    last = [""]
    for line in text.splitlines():
        if line.strip():
            _feed_line(line, current, last)
        elif current:
            yield current
            current, last[0] = {}, ""
    if current:
        yield current


def clean_name(item: str) -> str:
    """Убрать из имени зависимости версию, архитектуру и фильтры."""
    name = QUALIFIERS.sub("", item).strip()
    return name.split(":")[0]


def parse_depends(value: str) -> List[List[str]]:
    """Разобрать поле Depends в список групп альтернатив."""
    groups = []
    for part in value.split(","):
        names = [clean_name(item) for item in part.split("|")]
        names = [name for name in names if name]
        if names:
            groups.append(names)
    return groups


def parse_provides(value: str) -> List[str]:
    """Разобрать поле Provides в список имён виртуальных пакетов."""
    names = [clean_name(item) for item in value.split(",")]
    return [name for name in names if name]


def make_record(stanza: Dict[str, str]) -> Optional[Record]:
    """Построить Record из полей стансы; None, если нет имени."""
    name = stanza.get("Package")
    if not name:
        return None
    depends = parse_depends(stanza.get("Pre-Depends", ""))
    depends += parse_depends(stanza.get("Depends", ""))
    return Record(
        name=name,
        version=stanza.get("Version", ""),
        depends=depends,
        provides=parse_provides(stanza.get("Provides", "")),
    )


def parse_index(text: str) -> Dict[str, List[Record]]:
    """Построить словарь «имя пакета -> версии» из текста индекса."""
    index: Dict[str, List[Record]] = {}
    for stanza in parse_stanzas(text):
        record = make_record(stanza)
        if record:
            index.setdefault(record.name, []).append(record)
    return index


def load_index(repo: str) -> Dict[str, List[Record]]:
    """Скачать и разобрать индекс репозитория."""
    return parse_index(fetch_index(repo))


def find_package(index: Dict[str, List[Record]], name: str,
                 version: Optional[str]) -> Record:
    """Найти пакет заданной версии; без версии берётся первая запись."""
    records = index.get(name)
    if not records:
        raise RepoError(f"пакет '{name}' не найден в репозитории")
    if version is None:
        return records[0]
    for record in records:
        if record.version == version:
            return record
    available = ", ".join(record.version for record in records)
    raise RepoError(f"версия '{version}' пакета '{name}' не найдена; "
                    f"доступны: {available}")
