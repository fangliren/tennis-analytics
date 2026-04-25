
import csv
import pathlib
import requests
import xlrd
from datetime import datetime
from typing import Any
from config import PROJECT_ROOT
from parse import TEAM_ABBREVIATIONS



RESULTS_ONLINE = "https://www.datchworth.net/images/Results.xls"
RESULTS_LOCAL_DIR = PROJECT_ROOT / "downloads" / "results"
TABLES_DIR = PROJECT_ROOT / "tables" / "results"

COLUMNS_NEEDED = ["MyTeam", "DIV", "FixDate", "HomeAway", "Oppo", "SetsWon", "GamesWon", "SetsLost", "GamesLost"]

RENAME = {
    "MyTeam":    "home_team",
    "DIV":       "division",
    "FixDate":   "fixture_date",
    "Oppo":      "away_team",
    "SetsWon":   "home_sets",
    "GamesWon":  "home_games",
    "SetsLost":  "away_sets",
    "GamesLost": "away_games",
}


def _abbreviate(full_name: str) -> str:
    parts = full_name.rsplit(" ", 1)
    if len(parts) == 2 and parts[1].isdigit():
        return TEAM_ABBREVIATIONS[parts[0]] + parts[1]
    return TEAM_ABBREVIATIONS[full_name]


def download_results() -> None:

    RESULTS_LOCAL_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    local_path = RESULTS_LOCAL_DIR / f"results_{timestamp}.xls"

    response = requests.get(RESULTS_ONLINE)
    response.raise_for_status()

    with open(local_path, "wb") as f:
        f.write(response.content)

    print(f"Results downloaded to {local_path}")


def parse_results(xls_path: pathlib.Path) -> None:

    wb = xlrd.open_workbook(str(xls_path))
    ws = wb.sheet_by_index(0)

    headers = ws.row_values(0)
    col_index = {name: headers.index(name) for name in COLUMNS_NEEDED}

    rows = []
    for row_idx in range(1, ws.nrows):
        raw = ws.row_values(row_idx)

        if raw[col_index["HomeAway"]] != "Home":
            continue

        record: dict[str, Any] = {RENAME.get(col, col): raw[col_index[col]] for col in COLUMNS_NEEDED if col != "HomeAway"}

        record["home_team"]    = _abbreviate(record["home_team"])
        record["away_team"]    = _abbreviate(record["away_team"])
        record["fixture_date"] = xlrd.xldate_as_datetime(record["fixture_date"], wb.datemode).date()
        record["division"]     = record["division"].lstrip("0") or "0"

        home_sets  = int(record["home_sets"])
        away_sets  = int(record["away_sets"])
        home_games = int(record["home_games"])
        away_games = int(record["away_games"])

        record["home_sets"]  = home_sets
        record["away_sets"]  = away_sets
        record["home_games"] = home_games
        record["away_games"] = away_games

        if home_sets + away_sets != 3:
            print(f"WARNING row {row_idx + 1}: home_sets ({home_sets}) + away_sets ({away_sets}) != 3")
        if home_games + away_games != 39:
            print(f"WARNING row {row_idx + 1}: home_games ({home_games}) + away_games ({away_games}) != 39")

        rows.append(record)

    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = TABLES_DIR / f"results_{timestamp}.csv"

    fieldnames = ["fixture_date", "division", "home_team", "away_team", "home_sets", "home_games", "away_sets", "away_games"]
    with open(out_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Results parsed to {out_path} ({len(rows)} rows)")


if __name__ == "__main__":
    download_results()
    latest = sorted(RESULTS_LOCAL_DIR.glob("*.xls"))[-1]
    parse_results(latest)
