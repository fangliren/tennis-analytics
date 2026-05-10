# tennis-analytics

Pulls and parses tennis league data from [datchworth.net](https://www.datchworth.net).

## What it does

Three scripts, run in order:

- **`parse/schedule.py`** — downloads the season fixture list (`Matrix.xlsx`) and parses it into a flat CSV of all fixtures (`tables/schedule/`)
- **`parse/results.py`** — downloads the results file (`Results.xls`) and parses played home fixtures into a CSV (`tables/results/`)
- **`parse/combine.py`** — joins the latest schedule and results CSVs into a single combined table (`tables/combined/`), with blank cells for fixtures not yet played

## Install

```bash
pip install -e ".[dev]"
```

## Run

```bash
python scripts/update.py
```

This downloads the latest results and regenerates the combined table. Pass `--refresh-schedule` to also re-download the fixture list (needed once per season). The repo also includes a GitHub Actions workflow (`.github/workflows/update.yml`) that runs this automatically every Tuesday at 02:00 UTC.

## Test

```bash
pytest tests/
```
