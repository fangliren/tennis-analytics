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
python parse/schedule.py
python parse/results.py
python parse/combine.py
```

## Test

```bash
pytest tests/
```
