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


def _parse_schedule_rows(xlsx_path: pathlib.Path, expand_fn=expand) -> list:
    """Parse a schedule XLSX file and return a list of fixture dicts.

    expand_fn(code) converts an abbreviation to a full team name.  Defaults to
    the current-season expand(); historic callers pass their own variant.
    """
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
    fixtures = []
    for group_start in range(0, len(rows[3:]), 4):
        group = rows[3:][group_start:group_start + 4]
        fixture_date = group[0][0]
        if fixture_date is None:
            continue
        if isinstance(fixture_date, datetime):
            fixture_date = fixture_date.date()

        for div_name, col_idx in divisions:
            for row in group:
                home_raw = row[col_idx] if col_idx < len(row) else None
                away_raw = row[col_idx + 1] if col_idx + 1 < len(row) else None
                if home_raw is not None and away_raw is not None:
                    home = expand_fn(str(home_raw))
                    away = expand_fn(str(away_raw))
                    if home is None or away is None:
                        continue
                    fixtures.append({
                        "fixture_date": fixture_date,
                        "division": div_name,
                        "home_team": home,
                        "away_team": away,
                    })
    return fixtures


def parse_schedule(xlsx_path: pathlib.Path) -> None:
    fixtures = _parse_schedule_rows(xlsx_path)

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
