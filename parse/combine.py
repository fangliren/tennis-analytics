
import csv
import pathlib
from config import PROJECT_ROOT



SCHEDULE_TABLES_DIR = PROJECT_ROOT / "tables" / "schedule"
RESULTS_TABLES_DIR  = PROJECT_ROOT / "tables" / "results"
COMBINED_TABLES_DIR = PROJECT_ROOT / "tables" / "combined"

RESULT_FIELDS = ["home_sets", "home_games", "away_sets", "away_games"]


def combine(schedule_csv: pathlib.Path, results_csv: pathlib.Path) -> None:

    with open(results_csv) as f:
        results_index = {
            (r["fixture_date"], r["division"], r["home_team"], r["away_team"]): r
            for r in csv.DictReader(f)
        }

    with open(schedule_csv) as f:
        schedule_rows = list(csv.DictReader(f))

    combined = []
    for row in schedule_rows:
        key = (row["fixture_date"], row["division"], row["home_team"], row["away_team"])
        result = results_index.get(key, {})
        combined.append({
            **row,
            **{field: result.get(field, "") for field in RESULT_FIELDS},
        })

    COMBINED_TABLES_DIR.mkdir(parents=True, exist_ok=True)
    out_path = COMBINED_TABLES_DIR / "combined.csv"

    fieldnames = list(schedule_rows[0].keys()) + RESULT_FIELDS
    with open(out_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(combined)

    matched = sum(1 for r in combined if r["home_sets"] != "")
    print(f"Combined written to {out_path} ({len(combined)} fixtures, {matched} with results)")


if __name__ == "__main__":
    schedule_csv = sorted(SCHEDULE_TABLES_DIR.glob("*.csv"))[-1]
    results_csv  = sorted(RESULTS_TABLES_DIR.glob("*.csv"))[-1]
    combine(schedule_csv, results_csv)
