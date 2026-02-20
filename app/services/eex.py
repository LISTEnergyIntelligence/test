from typing import Any

import httpx
from fastapi import HTTPException

from app.config import settings
from app.services.base import DataProvider


class EexProvider(DataProvider):
    """EEX has multiple endpoints; this adapter keeps URL/query configurable per request."""

    default_endpoint = "https://webservice-eex.gvsi.com/query/json/getQuotes/settledate"

    async def fetch(self, dataset: str, **kwargs: Any) -> dict[str, Any]:
        if dataset not in {"day_ahead", "intraday", "mfrr"}:
            raise HTTPException(status_code=400, detail=f"Unsupported EEX dataset: {dataset}")

        params = {
            "priceSymbol": kwargs.get("price_symbol", "E.ATB_DA"),
            "chartstartdate": kwargs["start_date"].isoformat(),
            "chartstopdate": kwargs["end_date"].isoformat(),
        }

        async with httpx.AsyncClient(timeout=settings.request_timeout_seconds) as client:
            response = await client.get(self.default_endpoint, params=params)

        if response.status_code >= 400:
            raise HTTPException(
                status_code=response.status_code,
                detail={"message": "EEX request failed", "body": response.text[:1000]},
            )

        try:
            payload = response.json()
        except ValueError as exc:
            raise HTTPException(status_code=502, detail="EEX returned non-JSON response") from exc

        return {
            "source_url": str(response.request.url),
            "records": payload,
        }
