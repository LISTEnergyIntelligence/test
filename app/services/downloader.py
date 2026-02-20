from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

from app.config import settings
from app.models import DownloadFormat


def save_payload(payload: Any, platform: str, dataset: str, file_format: DownloadFormat) -> Path:
    filename = f"{platform}_{dataset}.{file_format.value}"
    path = settings.download_dir / filename

    if file_format == DownloadFormat.json:
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        return path

    if isinstance(payload, dict):
        payload = [payload]

    dataframe = pd.DataFrame(payload)
    dataframe.to_csv(path, index=False)
    return path
