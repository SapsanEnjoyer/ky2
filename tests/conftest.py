"""Общие фикстуры тестов."""

import functools
import gzip
import http.server
import threading

import pytest

SAMPLE_INDEX = """Package: alpha
Version: 1.0
Depends: beta (>= 1.0), gamma | delta:any,
 libc6 [amd64]
Provides: virt-alpha (= 1.0)

Package: beta
Version: 2.0
Pre-Depends: libc6
Depends: gamma

Package: gamma
Version: 3.1
Description: no dependencies
 multi-line text

Package: delta
Version: 0.1

Package: libc6
Version: 2.39
"""


@pytest.fixture
def sample_index():
    """Текст небольшого индекса пакетов."""
    return SAMPLE_INDEX


@pytest.fixture
def mirror(tmp_path):
    """Локальный HTTP-сервер с файлами Packages и Packages.gz."""
    (tmp_path / "Packages").write_text(SAMPLE_INDEX, encoding="utf-8")
    with gzip.open(tmp_path / "Packages.gz", "wt", encoding="utf-8") as f:
        f.write(SAMPLE_INDEX)
    handler = functools.partial(
        http.server.SimpleHTTPRequestHandler, directory=str(tmp_path))
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{server.server_address[1]}"
    server.shutdown()
    server.server_close()
