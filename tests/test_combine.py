import csv
import textwrap
import parse.combine as combine_module
from parse.combine import combine


def _csv(tmp_path, name, content):
    p = tmp_path / name
    p.write_text(textwrap.dedent(content))
    return p


def test_matched_fixture(tmp_path, monkeypatch):
    monkeypatch.setattr(combine_module, "COMBINED_TABLES_DIR", tmp_path)
    schedule = _csv(tmp_path, "schedule.csv", """\
        fixture_date,division,home_team,away_team
        2025-05-01,1,TEAM A,TEAM B
    """)
    results = _csv(tmp_path, "results.csv", """\
        fixture_date,division,home_team,away_team,home_sets,home_games,away_sets,away_games
        2025-05-01,1,TEAM A,TEAM B,2,26,1,13
    """)
    combine(schedule, results)
    rows = list(csv.DictReader((tmp_path / "combined.csv").open()))
    assert rows[0]["home_sets"] == "2"
    assert rows[0]["away_sets"] == "1"
    assert rows[0]["home_games"] == "26"


def test_unplayed_fixture_gets_empty_fields(tmp_path, monkeypatch):
    monkeypatch.setattr(combine_module, "COMBINED_TABLES_DIR", tmp_path)
    schedule = _csv(tmp_path, "schedule.csv", """\
        fixture_date,division,home_team,away_team
        2025-05-01,1,TEAM A,TEAM B
    """)
    results = _csv(tmp_path, "results.csv", """\
        fixture_date,division,home_team,away_team,home_sets,home_games,away_sets,away_games
    """)
    combine(schedule, results)
    rows = list(csv.DictReader((tmp_path / "combined.csv").open()))
    assert rows[0]["home_sets"] == ""
    assert rows[0]["away_sets"] == ""


def test_partial_results(tmp_path, monkeypatch):
    monkeypatch.setattr(combine_module, "COMBINED_TABLES_DIR", tmp_path)
    schedule = _csv(tmp_path, "schedule.csv", """\
        fixture_date,division,home_team,away_team
        2025-05-01,1,TEAM A,TEAM B
        2025-05-08,1,TEAM B,TEAM A
    """)
    results = _csv(tmp_path, "results.csv", """\
        fixture_date,division,home_team,away_team,home_sets,home_games,away_sets,away_games
        2025-05-01,1,TEAM A,TEAM B,2,26,1,13
    """)
    combine(schedule, results)
    rows = list(csv.DictReader((tmp_path / "combined.csv").open()))
    assert rows[0]["home_sets"] == "2"
    assert rows[1]["home_sets"] == ""
