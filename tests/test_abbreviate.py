import pytest
from parse.results import _abbreviate


def test_numbered_team():
    assert _abbreviate("ASHWELL 1") == "ASHW1"
    assert _abbreviate("HITCHIN 3") == "HITC3"


def test_numbered_team_st():
    assert _abbreviate("ST MARGS 1") == "ST M1"
    assert _abbreviate("ST MARGS 2") == "ST M2"


def test_no_number_team():
    assert _abbreviate("DATCHWORTH") == "DATCH"
    assert _abbreviate("GOSLING") == "GOSLG"
    assert _abbreviate("ST PAULS") == "ST PS"
    assert _abbreviate("WYMONDLEY") == "WYMOY"


def test_unknown_raises():
    with pytest.raises(KeyError):
        _abbreviate("UNKNOWN CLUB 1")
