from fastapi import FastAPI, HTTPException, Query

from app.models import DownloadFormat, DownloadResponse, FetchResponse, MarketQuery, Platform
from app.services.downloader import save_payload
from app.services.eex import EexProvider
from app.services.energy_charts import EnergyChartsProvider
from app.services.entsoe import EntsoeProvider

app = FastAPI(title="Electricity Market Data API", version="0.1.0")

providers = {
    Platform.entsoe: EntsoeProvider(),
    Platform.energy_charts: EnergyChartsProvider(),
    Platform.eex: EexProvider(),
}


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/fetch/{platform}/{dataset}", response_model=FetchResponse)
async def fetch_market_data(
    platform: Platform,
    dataset: str,
    bidding_zone: str = Query(default="DE_LU"),
    start_date: str = Query(..., description="YYYY-MM-DD"),
    end_date: str = Query(..., description="YYYY-MM-DD"),
    entsoe_token: str | None = Query(default=None, description="Optional ENTSO-E token override"),
):
    query = MarketQuery(bidding_zone=bidding_zone, start_date=start_date, end_date=end_date, entsoe_token=entsoe_token)
    provider = providers[platform]
    payload = await provider.fetch(dataset=dataset, **query.model_dump())

    return FetchResponse(platform=platform, dataset=dataset, **payload)


@app.post("/download/{platform}/{dataset}", response_model=DownloadResponse)
async def download_market_data(
    platform: Platform,
    dataset: str,
    file_format: DownloadFormat = Query(default=DownloadFormat.json),
    bidding_zone: str = Query(default="DE_LU"),
    start_date: str = Query(..., description="YYYY-MM-DD"),
    end_date: str = Query(..., description="YYYY-MM-DD"),
    entsoe_token: str | None = Query(default=None, description="Optional ENTSO-E token override"),
):
    query = MarketQuery(bidding_zone=bidding_zone, start_date=start_date, end_date=end_date, entsoe_token=entsoe_token)
    provider = providers.get(platform)
    if provider is None:
        raise HTTPException(status_code=404, detail=f"Provider not configured for {platform}")

    payload = await provider.fetch(dataset=dataset, **query.model_dump())
    filepath = save_payload(payload["records"], platform.value, dataset, file_format)

    return DownloadResponse(filename=filepath.name, format=file_format, path=str(filepath))
