# Electricity Market Data API (FastAPI)

FastAPI service to fetch and download electricity market datasets (day-ahead, intraday, mFRR/frequency related datasets) from multiple platforms:

- ENTSO-E Transparency Platform (token required)
- Energy Charts (public API)
- EEX Group market-data endpoint

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Add your ENTSO-E token in `.env` (or pass `entsoe_token` query parameter per request).

## Run

```bash
uvicorn app.main:app --reload
```

## Example requests

```bash
curl "http://127.0.0.1:8000/fetch/entsoe/day_ahead_prices?bidding_zone=10Y1001A1001A82H&start_date=2024-01-01&end_date=2024-01-02&entsoe_token=$ENTSOE_TOKEN"
curl "http://127.0.0.1:8000/fetch/energy_charts/day_ahead_prices?bidding_zone=DE_LU&start_date=2024-01-01&end_date=2024-01-05"
curl -X POST "http://127.0.0.1:8000/download/eex/day_ahead?file_format=csv&bidding_zone=DE_LU&start_date=2024-01-01&end_date=2024-01-31"
```

## Supported datasets

### ENTSO-E
- `day_ahead_prices`
- `intraday_prices`
- `mfrr_activated_energy`
- `frequency_containment_reserves`

### Energy Charts
- `day_ahead_prices`
- `intraday_prices`
- `frequency`

### EEX
- `day_ahead`
- `intraday`
- `mfrr`

## Notes

- ENTSO-E responses are currently returned as raw XML strings under `records.xml` for transparency.
- For EEX, symbols vary by product and market; default symbol is `E.ATB_DA` and can be extended in provider logic.
