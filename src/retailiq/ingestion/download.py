"""Dataset acquisition utility for UCI Online Retail dataset."""

from __future__ import annotations

import io
import urllib.request
import zipfile
from pathlib import Path

from retailiq.config import settings


def download_dataset(
    target_path: Path | None = None,
    url: str | None = None,
    force: bool = False,
) -> Path:
    """Download the official UCI Online Retail dataset zip and extract Online Retail.xlsx."""
    dest = target_path or settings.dataset.raw_file_path
    download_url = url or settings.dataset.download_url

    if dest.exists() and not force:
        return dest

    dest.parent.mkdir(parents=True, exist_ok=True)

    print(f"[*] Downloading dataset archive from: {download_url}...")
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) RetailIQ/1.0"}
    req = urllib.request.Request(download_url, headers=headers)

    with urllib.request.urlopen(req) as response:
        content = response.read()

    print(f"[*] Download completed ({len(content):,} bytes). Extracting archive...")
    with zipfile.ZipFile(io.BytesIO(content)) as z:
        inner_file = settings.dataset.archive_inner_file
        if inner_file not in z.namelist():
            raise FileNotFoundError(
                f"Expected archive member '{inner_file}' not found. "
                f"Archive contents: {z.namelist()}"
            )

        with z.open(inner_file) as source, dest.open("wb") as target:
            target.write(source.read())

    print(f"[+] Successfully extracted dataset to: {dest} ({dest.stat().st_size:,} bytes)")
    return dest
