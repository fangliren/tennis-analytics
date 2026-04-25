

import csv
import pathlib
import requests
import openpyxl
from datetime import datetime
from parse import PROJECT_ROOT, expand



SCHEDULE_ONLINE = "https://www.datchworth.net/Images/Matrix.xlsx"
SCHEDULE_LOCAL_DIR = PROJECT_ROOT / "downloads" / "schedule"
TABLES_DIR = PROJECT_ROOT / "tables" / "schedule"


def download_schedule() -> None:

    SCHEDULE_LOCAL_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    local_path = SCHEDULE_LOCAL_DIR / f"schedule_{timestamp}.xlsx"

    response = requests.get(SCHEDULE_ONLINE)
    response.raise_for_status()

    with open(local_path, "wb") as f:
        f.write(response.content)

    print(f"Schedule downloaded to {local_path}")


def parse_schedule(xlsx_path: pathlib.Path) -> None:

    wb = openpyxl.load_workbook(xlsx_path)
    ws = wb.active
    assert ws is not None, "Workbook has no active sheet"
    rows = list(ws.iter_rows(values_only=True))

    # Row 2 (index 1): division names sit at odd column indices 1, 3, 5, ...
    divisions = []
    for col_idx in range(1, len(rows[1]), 2):
        div_name = rows[1][col_idx]
        if div_name is not None:
            divisions.append((str(div_name), col_idx))

    # Data starts at row 4 (skip first 3 header rows), grouped in chunks of 4
    data_rows = rows[3:]

    fixtures = []
    for group_start in range(0, len(data_rows), 4):
        group = data_rows[group_start:group_start + 4]
        fixture_date = group[0][0]
        if fixture_date is None:
            continue
        if isinstance(fixture_date, datetime):
            fixture_date = fixture_date.date()

        for div_name, col_idx in divisions:
            for row in group:
                home = row[col_idx]     if col_idx     < len(row) else None
                away = row[col_idx + 1] if col_idx + 1 < len(row) else None
                if home is not None and away is not None:
                    fixtures.append({
                        "fixture_date": fixture_date,
                        "division": div_name,
                        "home_team": expand(str(home)),
                        "away_team": expand(str(away)),
                    })

    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    out_path = TABLES_DIR / "schedule.csv"

    with open(out_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["fixture_date", "division", "home_team", "away_team"])
        writer.writeheader()
        writer.writerows(fixtures)

    print(f"Schedule parsed to {out_path} ({len(fixtures)} fixtures)")


if __name__ == "__main__":
    download_schedule()
    latest = sorted(SCHEDULE_LOCAL_DIR.glob("*.xlsx"))[-1]
    parse_schedule(latest)
