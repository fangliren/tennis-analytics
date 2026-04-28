from parse.visualize import _position_zones


def test_division_1():
    # champion at top, relegation at bottom two, safe in middle
    assert _position_zones("1", 6, 3) == ["champion", "safe", "safe", "safe", "relegation", "relegation"]


def test_division_1_small():
    # with only 3 teams both non-champion spots are relegation
    assert _position_zones("1", 3, 3) == ["champion", "relegation", "relegation"]


def test_division_2():
    assert _position_zones("2", 6, 3) == ["promotion", "promotion", "safe", "relegation", "relegation", "relegation"]


def test_division_3a():
    assert _position_zones("3A", 6, 3) == ["promotion", "chasing", "safe", "safe", "relegation", "relegation"]


def test_division_3b():
    assert _position_zones("3B", 6, 3) == ["promotion", "chasing", "safe", "safe", "relegation", "relegation"]


def test_division_3a_small():
    # no relegation slots when n=2
    assert _position_zones("3A", 2, 3) == ["promotion", "chasing"]


def test_bottom_division_no_relegation():
    # last group: promotion only, no relegation
    assert _position_zones("4A", 5, 4) == ["promotion", "promotion", "safe", "safe", "safe"]


def test_middle_division():
    # a plain numbered division that isn't 1, 2, 3A/3B, or the last group
    assert _position_zones("3", 5, 4) == ["promotion", "promotion", "safe", "relegation", "relegation"]
