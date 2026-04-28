import pytest
from parse import expand
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


def test_expand_direct():
    assert expand("DATCH") == "DATCHWORTH"
    assert expand("ST PS") == "ST PAULS"


def test_expand_numbered():
    assert expand("ELLI1") == "ELLISWICK 1"
    assert expand("HITC3") == "HITCHIN 3"


def test_expand_st_numbered():
    assert expand("ST M1") == "ST MARG 1"
    assert expand("ST M2") == "ST MARG 2"


def test_expand_unknown_raises():
    with pytest.raises(KeyError):
        expand("ZZZ1")
