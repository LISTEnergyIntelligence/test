from datetime import date
from enum import Enum

from pydantic import BaseModel, Field, SecretStr


class Platform(str, Enum):
    entsoe = "entsoe"
    energy_charts = "energy_charts"
    eex = "eex"


class EntsoeDataset(str, Enum):
    day_ahead_prices = "day_ahead_prices"
    intraday_prices = "intraday_prices"
    mfrr_activated_energy = "mfrr_activated_energy"
    frequency_containment_reserves = "frequency_containment_reserves"


class DownloadFormat(str, Enum):
    json = "json"
    csv = "csv"


class MarketQuery(BaseModel):
    bidding_zone: str = Field(default="DE_LU", description="Bidding zone/domain code")
    start_date: date
    end_date: date
    entsoe_token: SecretStr | None = Field(default=None, description="Optional ENTSO-E token override")


class FetchResponse(BaseModel):
    platform: Platform
    dataset: str
    source_url: str
    records: list[dict] | list[str] | dict


class DownloadResponse(BaseModel):
    filename: str
    format: DownloadFormat
    path: str
