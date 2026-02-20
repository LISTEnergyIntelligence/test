from datetime import date
from typing import Any

import httpx
from fastapi import HTTPException

from app.config import settings
from app.models import EntsoeDataset
from app.services.base import DataProvider


DATASET_PARAMS = {
    EntsoeDataset.day_ahead_prices: {"documentType": "A44", "processType": "A01"},
    EntsoeDataset.intraday_prices: {"documentType": "A44", "processType": "A14"},
    EntsoeDataset.mfrr_activated_energy: {"documentType": "A83", "businessType": "A96"},
    EntsoeDataset.frequency_containment_reserves: {"documentType": "A81", "type_MarketAgreement.type": "A01"},
}


class EntsoeProvider(DataProvider):
    base_url = "https://web-api.tp.entsoe.eu/api"

    @staticmethod
    def _date_to_entsoe(value: date) -> str:
        return value.strftime("%Y%m%d0000")

    async def fetch(self, dataset: str, **kwargs: Any) -> dict[str, Any]:
        token_override = kwargs.get("entsoe_token")
        token = token_override.get_secret_value() if token_override else settings.entsoe_token
        if not token:
            raise HTTPException(status_code=400, detail="ENTSOE token is missing. Set ENTSOE_TOKEN.")

        try:
            ds = EntsoeDataset(dataset)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=f"Unsupported ENTSOE dataset: {dataset}") from exc

        start_date: date = kwargs["start_date"]
        end_date: date = kwargs["end_date"]
        bidding_zone: str = kwargs["bidding_zone"]

        params = {
            "securityToken": token,
            "in_Domain": bidding_zone,
            "out_Domain": bidding_zone,
            "periodStart": self._date_to_entsoe(start_date),
            "periodEnd": self._date_to_entsoe(end_date),
            **DATASET_PARAMS[ds],
        }

        async with httpx.AsyncClient(timeout=settings.request_timeout_seconds) as client:
            response = await client.get(self.base_url, params=params)

        if response.status_code >= 400:
            raise HTTPException(
                status_code=response.status_code,
                detail={"message": "ENTSO-E request failed", "body": response.text[:2000]},
            )

        return {
            "source_url": str(response.request.url),
            "records": {"xml": response.text},
        }
