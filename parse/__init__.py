import pathlib

PROJECT_ROOT = pathlib.Path(__file__).resolve().parent.parent

TEAM_ABBREVIATIONS = {
    "ASHWELL": "ASHW",
    "ASTON": "ASTO",
    "CODICOTE": "CODI",
    "DATCHWORTH": "DATCH",
    "DELLCOTT": "DELL",
    "DIGSWELL": "DIGS",
    "ELLISWICK": "ELLI",
    "GOSLING": "GOSLG",
    "HITCHIN": "HITC",
    "HODDESDON": "HODD",
    "KIMPTON": "KIMP",
    "KNEBWORTH": "KNEB",
    "LEGENDS": "LEGE",
    "LETCHWORTH": "LETC",
    "LISTER": "LIST",
    "ODYSSEY": "ODYS",
    "ORCHARD": "ORCH",
    "PIRTON": "PIRT",
    "ST MARGS": "ST M",    # alias used in results data — comes first
    "ST PAULS": "ST PS",
    "TEWIN": "TEWI",
    "WATTON": "WATT",
    "WELWYN": "WELW",
    "WESTON": "WEST",
    "WHEATHAM": "WHEA",         # alias used in results data — comes first
    "WHEATHAMPSTEAD": "WHEA",   # canonical — comes last, wins reverse dict
    "WYMONDLEY": "WYMOY",
    "ST MARG": "ST M",          # canonical — comes last, wins reverse dict
}

# Reverse mapping: abbreviation prefix → canonical full club name.
# Aliases above are listed before their canonical counterpart so the
# canonical name wins when the dict is inverted (last write wins).
ABBREVIATION_TO_TEAM = {abbrev: name for name, abbrev in TEAM_ABBREVIATIONS.items()}


def expand(code: str) -> str:
    """Convert an abbreviated team code to its full club name.

    "ELLI1" → "ELLISWICK 1",  "ST M1" → "ST MARG 1",  "ST PS" → "ST PAULS"
    """
    if code in ABBREVIATION_TO_TEAM:
        return ABBREVIATION_TO_TEAM[code]
    i = len(code)
    while i > 0 and code[i - 1].isdigit():
        i -= 1
    prefix = code[:i].rstrip()
    number = code[i:]
    return ABBREVIATION_TO_TEAM[prefix] + " " + number
