
import csv
import pathlib
from collections import defaultdict
from parse import PROJECT_ROOT


COMBINED_CSV      = PROJECT_ROOT / "tables" / "combined" / "combined.csv"
LEAGUES_TABLES_DIR = PROJECT_ROOT / "tables" / "leagues"


def leagues(combined_csv: pathlib.Path) -> None:
    totals: dict[tuple[str, str], dict[str, int]] = defaultdict(
        lambda: {"played": 0, "sets_won": 0, "games_won": 0}
    )

    with open(combined_csv) as f:
        for row in csv.DictReader(f):
            home_key = (row["division"], row["home_team"])
            away_key = (row["division"], row["away_team"])

            # ensure every team appears even if they haven't played yet
            totals[home_key]
            totals[away_key]

            if row["home_sets"] == "":
                continue

            totals[home_key]["played"]    += 1
            totals[home_key]["sets_won"]  += int(row["home_sets"])
            totals[home_key]["games_won"] += int(row["home_games"])

            totals[away_key]["played"]    += 1
            totals[away_key]["sets_won"]  += int(row["away_sets"])
            totals[away_key]["games_won"] += int(row["away_games"])

    rows = [
        {"division": div, "team": team, **stats}
        for (div, team), stats in totals.items()
    ]
    rows.sort(key=lambda r: (r["division"], -r["sets_won"], -r["games_won"]))

    LEAGUES_TABLES_DIR.mkdir(parents=True, exist_ok=True)
    out_path = LEAGUES_TABLES_DIR / "leagues.csv"

    with open(out_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["division", "team", "played", "sets_won", "games_won"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"Leagues written to {out_path} ({len(rows)} teams)")


if __name__ == "__main__":
    leagues(COMBINED_CSV)
