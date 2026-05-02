"""Upstream source version fetcher for mmrrc-ingest.

MMRRC catalog has no in-band versioning; use HTTP Last-Modified.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from kozahub_metadata_schema import (
    now_iso,
    urls_from_download_yaml,
    version_from_http_last_modified,
)


INGEST_DIR = Path(__file__).resolve().parents[1]
DOWNLOAD_YAML = INGEST_DIR / "download.yaml"


def get_source_versions() -> list[dict[str, Any]]:
    urls = urls_from_download_yaml(DOWNLOAD_YAML)
    ver, method = version_from_http_last_modified(urls[0]) if urls else ("unknown", "unavailable")
    return [
        {
            "id": "infores:mmrrc",
            "name": "Mutant Mouse Resource & Research Centers (MMRRC)",
            "urls": urls,
            "version": ver,
            "version_method": method,
            "retrieved_at": now_iso(),
        }
    ]
