import csv
import textwrap
from parse.leagues import leagues


def _write(tmp_path, content):
    p = tmp_path / "combined.csv"
    p.write_text(textwrap.dedent(content))
    return p


def _read(path):
    return list(csv.DictReader(path.open()))


def test_totals(tmp_path):
    src = _write(tmp_path, """\
        fixture_date,division,home_team,away_team,home_sets,home_games,away_sets,away_games
        2025-05-01,1,TEAM A,TEAM B,2,26,1,13
        2025-05-08,1,TEAM B,TEAM A,1,13,2,26
    """)
    out = tmp_path / "leagues.csv"
    leagues(src, out_path=out)
    rows = {r["team"]: r for r in _read(out)}
    assert rows["TEAM A"]["sets_won"] == "4"
    assert rows["TEAM A"]["games_won"] == "52"
    assert rows["TEAM A"]["played"] == "2"
    assert rows["TEAM B"]["sets_won"] == "2"


def test_sorted_by_sets_descending(tmp_path):
    src = _write(tmp_path, """\
        fixture_date,division,home_team,away_team,home_sets,home_games,away_sets,away_games
        2025-05-01,1,TEAM A,TEAM B,1,13,2,26
    """)
    out = tmp_path / "leagues.csv"
    leagues(src, out_path=out)
    rows = _read(out)
    assert rows[0]["team"] == "TEAM B"
    assert rows[1]["team"] == "TEAM A"


def test_unplayed_teams_appear_with_zero_stats(tmp_path):
    src = _write(tmp_path, """\
        fixture_date,division,home_team,away_team,home_sets,home_games,away_sets,away_games
        2025-05-01,1,TEAM A,TEAM B,,,,
    """)
    out = tmp_path / "leagues.csv"
    leagues(src, out_path=out)
    rows = _read(out)
    teams = {r["team"] for r in rows}
    assert teams == {"TEAM A", "TEAM B"}
    assert all(r["played"] == "0" for r in rows)


def test_multiple_divisions_sorted(tmp_path):
    src = _write(tmp_path, """\
        fixture_date,division,home_team,away_team,home_sets,home_games,away_sets,away_games
        2025-05-01,2,DIV2 A,DIV2 B,2,26,1,13
        2025-05-01,1,DIV1 A,DIV1 B,2,26,1,13
    """)
    out = tmp_path / "leagues.csv"
    leagues(src, out_path=out)
    rows = _read(out)
    assert rows[0]["division"] == "1"
    assert rows[2]["division"] == "2"
