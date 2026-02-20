from datetime import date
from typing import Any

import httpx
from fastapi import HTTPException

from app.config import settings
from app.services.base import DataProvider


class EnergyChartsProvider(DataProvider):
    """Public API docs: https://api.energy-charts.info/"""

    base_url = "https://api.energy-charts.info"

    async def fetch(self, dataset: str, **kwargs: Any) -> dict[str, Any]:
        bidding_zone: str = kwargs["bidding_zone"].replace("_", "-")
        start_date: date = kwargs["start_date"]
        end_date: date = kwargs["end_date"]

        endpoint = {
            "day_ahead_prices": "/price",
            "intraday_prices": "/price",
            "frequency": "/frequency",
        }.get(dataset)

        if endpoint is None:
            raise HTTPException(status_code=400, detail=f"Unsupported Energy Charts dataset: {dataset}")

        params = {
            "bzn": bidding_zone,
            "start": start_date.isoformat(),
            "end": end_date.isoformat(),
        }

        async with httpx.AsyncClient(timeout=settings.request_timeout_seconds) as client:
            response = await client.get(f"{self.base_url}{endpoint}", params=params)

        if response.status_code >= 400:
            raise HTTPException(
                status_code=response.status_code,
                detail={"message": "Energy Charts request failed", "body": response.text[:1000]},
            )

        try:
            payload = response.json()
        except ValueError as exc:
            raise HTTPException(status_code=502, detail="Energy Charts returned non-JSON response") from exc

        return {
            "source_url": str(response.request.url),
            "records": payload,
        }
