
import csv
import json
import pathlib
from collections import defaultdict
from datetime import date
from parse import PROJECT_ROOT


LEAGUES_CSV   = PROJECT_ROOT / "tables" / "leagues"  / "leagues.csv"
COMBINED_CSV  = PROJECT_ROOT / "tables" / "combined" / "combined.csv"
LEAGUES_HTML  = PROJECT_ROOT / "tables" / "leagues"  / "leagues.html"
HISTORIC_DIR  = PROJECT_ROOT / "tables" / "historic"

def _div_group(division: str) -> int:
    return int("".join(c for c in division if c.isdigit()))


def _hue(division: str, max_group: int) -> int:
    """Map a division's numeric group to a hue across 0°–280° (red → purple)."""
    return round((_div_group(division) - 1) / max(max_group - 1, 1) * 280)


def _header_color(division: str, max_group: int) -> str:
    return f"hsl({_hue(division, max_group)}, 60%, 26%)"

_PAGE_JS = """\
var _tip = document.createElement('div');
_tip.style.cssText = 'position:fixed;background:#0f172a;border:1px solid #334155;'
  + 'color:#cbd5e1;padding:6px 12px;border-radius:8px;font-size:.78rem;'
  + 'pointer-events:none;z-index:200;white-space:nowrap;display:none;'
  + 'box-shadow:0 4px 12px rgba(0,0,0,.5)';
document.body.appendChild(_tip);
function tipShow(el, e) {
  _tip.innerHTML = el.dataset.tip;
  _tip.style.display = 'block';
  tipMove(e);
  el._mm = function(ev) { tipMove(ev); };
  el.addEventListener('mousemove', el._mm);
}
function tipMove(e) {
  _tip.style.left = (e.clientX + 14) + 'px';
  _tip.style.top  = (e.clientY + 14) + 'px';
}
function tipHide(el) {
  _tip.style.display = 'none';
  if (el && el._mm) el.removeEventListener('mousemove', el._mm);
}

const FIXTURES     = __FIXTURES__;
const ALL_FIXTURES = __ALL_FIXTURES__;

var _prevState = null;

function _fixtureRow(f, showDiv, showYear, clickable) {
  var played = f.hs !== null;
  var score  = played
    ? f.hs + '–' + f.vs + '<br><small>' + f.hg + '–' + f.vg + ' games</small>'
    : '—';
  var dc = showDiv  ? '<td>' + f.v + '</td>' : '';
  var yc = showYear ? '<td class="yr">' + f.y + '</td>' : '';
  var cls = (played ? 'pl' : 'up') + (clickable ? ' h2h-link' : '');
  var oc  = clickable
    ? " onclick='showH2H(" + JSON.stringify(f.h) + "," + JSON.stringify(f.a) + ")'"
    : '';
  return '<tr class="' + cls + '"' + oc + '>'
    + '<td>' + f.d + '</td>' + dc + yc
    + '<td class="tm">' + f.h + '</td>'
    + '<td class="sc">' + score + '</td>'
    + '<td class="tm">' + f.a + '</td>'
    + '</tr>';
}

function showTeam(team) {
  _prevState = null;
  var rows = FIXTURES.filter(function(f) { return f.h === team || f.a === team; })
                     .sort(function(a,b) { return a.d < b.d ? -1 : 1; });
  _renderModal(team, rows, false, false, true);
}
function showDivision(div) {
  _prevState = null;
  var rows = FIXTURES.filter(function(f) { return f.v === div; })
                     .sort(function(a,b) { return a.d < b.d ? -1 : 1; });
  _renderModal('Division ' + div, rows, true, false, true);
}
function showH2H(home, away) {
  _prevState = {
    html:    document.getElementById('mo-rows').innerHTML,
    title:   document.getElementById('mo-title').textContent,
    showDiv: document.getElementById('th-div').style.display  !== 'none',
    showYr:  document.getElementById('th-yr').style.display   !== 'none',
    showBk:  document.getElementById('mo-back').style.display !== 'none',
  };
  var rows = ALL_FIXTURES.filter(function(f) {
    return (f.h === home && f.a === away) || (f.h === away && f.a === home);
  }).sort(function(a,b) { return a.d > b.d ? -1 : 1; });
  _renderModal(home + ' vs ' + away, rows, true, true, false);
  document.getElementById('mo-back').style.display = '';
}
function goBack() {
  if (!_prevState) return;
  document.getElementById('mo-title').textContent         = _prevState.title;
  document.getElementById('mo-rows').innerHTML            = _prevState.html;
  document.getElementById('th-div').style.display         = _prevState.showDiv ? '' : 'none';
  document.getElementById('th-yr').style.display          = _prevState.showYr  ? '' : 'none';
  document.getElementById('mo-back').style.display        = _prevState.showBk  ? '' : 'none';
  document.getElementById('mo-scroll').scrollTop = 0;
  _prevState = null;
}
function _renderModal(title, rows, showDiv, showYear, clickable) {
  document.getElementById('mo-title').textContent  = title;
  document.getElementById('th-div').style.display  = showDiv  ? '' : 'none';
  document.getElementById('th-yr').style.display   = showYear ? '' : 'none';
  document.getElementById('mo-back').style.display = 'none';
  document.getElementById('mo-rows').innerHTML =
    rows.map(function(f) { return _fixtureRow(f, showDiv, showYear, clickable); }).join('');
  document.getElementById('mo-scroll').scrollTop = 0;
  document.getElementById('modal').style.display = 'flex';
}
function closeModal() {
  document.getElementById('modal').style.display = 'none';
  _prevState = null;
}
document.addEventListener('keydown', function(e) { if (e.key === 'Escape') closeModal(); });
"""

_HTML = """\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Datchworth Tennis Leagues</title>
<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
       background: #0f172a; color: #e2e8f0; min-height: 100vh; padding: 44px 20px 60px; }
h1 { text-align: center; font-size: 2rem; color: #86efac;
     margin-bottom: 6px; letter-spacing: -0.5px; }
.subtitle { text-align: center; color: #475569; font-size: .82rem;
            margin-bottom: 44px; letter-spacing: .5px; text-transform: uppercase; }
.grid { display: grid; grid-template-columns: repeat(2, 1fr);
        gap: 22px; max-width: 1400px; margin: 0 auto; }
@media (max-width: 800px) { .grid { grid-template-columns: 1fr; } }
.card { background: #1e293b; border-radius: 14px; overflow: hidden;
        border: 1px solid #334155; box-shadow: 0 4px 24px rgba(0,0,0,.35); }
.card-header { padding: 11px 18px; font-weight: 700; font-size: .8rem;
               letter-spacing: 1.2px; text-transform: uppercase;
               color: rgba(255,255,255,.92); cursor: pointer;
               display: flex; justify-content: space-between; align-items: center; }
.card-header:hover { filter: brightness(1.15); }
.hdr-hint { font-size: .7rem; font-weight: 400; opacity: .6;
            letter-spacing: 0; text-transform: none; }
.team-list { padding: 6px 0 10px; }
.t-row { display: flex; align-items: center; gap: 8px; padding: 4px 14px;
         border-left: 3px solid transparent; }
.t-row:hover { background: rgba(255,255,255,0.03); }
.t-row.champion   { border-left-color:#fbbf24; background:rgba(251,191,36,.07); }
.t-row.promotion  { border-left-color:#60a5fa; background:rgba(96,165,250,.07); }

.t-row.relegation { border-left-color:#f87171; background:rgba(248,113,113,.07); }
.zone-break { border-top:1px dashed rgba(255,255,255,0.07); margin-top:2px; padding-top:5px; }
.ztag { font-size:.6rem; font-weight:700; padding:1px 6px; border-radius:10px;
        flex-shrink:0; white-space:nowrap; }
.ztag.champion   { background:rgba(251,191,36,.22); color:#fbbf24; }
.ztag.promotion  { background:rgba(96,165,250,.22);  color:#60a5fa; }

.ztag.relegation { background:rgba(248,113,113,.22);  color:#f87171; }
.legend { display:flex; justify-content:center; gap:18px; flex-wrap:wrap;
          margin-bottom:32px; font-size:.72rem; }
.l-item { display:flex; align-items:center; gap:5px; color:#64748b; }
.l-dot  { width:10px; height:10px; border-radius:50%; }
.l-dot.champion   { background:#fbbf24; }
.l-dot.promotion  { background:#60a5fa; }
.l-dot.relegation { background:#f87171; }
.t-rank { width: 26px; text-align: right; font-size: .78rem;
          flex-shrink: 0; color: #64748b; }
.t-btn { background: rgba(96,165,250,0.1); border: 1px solid rgba(96,165,250,0.22);
         color: #93c5fd; padding: 3px 10px; border-radius: 20px; cursor: pointer;
         font-size: .76rem; font-weight: 600; flex-shrink: 0; width: 118px;
         text-align: left; transition: background .15s, border-color .15s;
         white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
         font-family: inherit; letter-spacing: .2px; }
.t-btn:hover { background: rgba(96,165,250,0.28); border-color: rgba(96,165,250,0.55);
               color: #bfdbfe; }
.t-bar-outer { flex: 1; height: 8px; background: rgba(255,255,255,0.05);
               border-radius: 4px; overflow: hidden; min-width: 0; }
.t-bar { height: 100%; border-radius: 4px;
         transition: width .45s cubic-bezier(.4,0,.2,1); }
.t-num { font-size: .8rem; color: #94a3b8; flex-shrink: 0;
         min-width: 58px; text-align: right; }
.t-num small { color: #475569; font-size: .7rem; margin-left: 3px; }
#modal { display: none; position: fixed; inset: 0; background: rgba(0,0,0,.65);
         z-index: 100; align-items: center; justify-content: center; padding: 20px; }
#modal-panel { background: #1e293b; border-radius: 14px; border: 1px solid #334155;
               width: 100%; max-width: 820px; max-height: 85vh;
               display: flex; flex-direction: column; overflow: hidden; }
#mo-hdr { display: flex; align-items: center; justify-content: space-between;
          padding: 14px 20px; border-bottom: 1px solid #334155; flex-shrink: 0; }
#mo-title { font-weight: 700; font-size: 1rem; color: #86efac; }
#mo-close { background: none; border: none; color: #94a3b8; font-size: 1.2rem;
            cursor: pointer; padding: 4px 8px; border-radius: 6px; }
#mo-close:hover { background: #334155; color: #e2e8f0; }
#mo-scroll { overflow-y: auto; }
#mo-table { width: 100%; border-collapse: collapse; font-size: .88rem; }
#mo-table th { padding: 8px 14px; text-align: left; color: #64748b; font-weight: 600;
               font-size: .75rem; text-transform: uppercase; letter-spacing: .5px;
               border-bottom: 1px solid #334155;
               position: sticky; top: 0; background: #1e293b; }
#mo-table td { padding: 8px 14px; border-bottom: 1px solid #1a2742; }
#mo-table tr.pl td { color: #e2e8f0; }
#mo-table tr.up td { color: #64748b; font-style: italic; }
#mo-table td.tm { font-weight: 500; }
#mo-table td.sc { text-align: center; color: #86efac; font-weight: 600; white-space: nowrap; }
#mo-table tr.up td.sc { color: #334155; }
#mo-table small { color: #64748b; font-weight: 400; }
#mo-table td.yr { color: #475569; font-size: .78rem; }
#mo-table tr.h2h-link { cursor: pointer; }
#mo-table tr.h2h-link:hover td { background: rgba(96,165,250,0.06); }
#mo-back { background: none; border: 1px solid #334155; color: #94a3b8;
           font-size: .8rem; cursor: pointer; padding: 4px 10px;
           border-radius: 6px; margin-right: 8px; display: none; }
#mo-back:hover { background: #334155; color: #e2e8f0; }
</style>
</head>
<body>
<h1>🎾 Datchworth Tennis Leagues</h1>
<p class="subtitle">Updated __DATE__</p>
<div class="legend">
  <span class="l-item"><span class="l-dot champion"></span>Champion</span>
  <span class="l-item"><span class="l-dot promotion"></span>Promotion zone</span>
  <span class="l-item"><span class="l-dot relegation"></span>Relegation zone</span>
</div>
<div class="grid">
__CARDS__
</div>
<div id="modal" onclick="if(event.target===this)closeModal()">
  <div id="modal-panel">
    <div id="mo-hdr">
      <div style="display:flex;align-items:center;gap:4px">
        <button id="mo-back" onclick="goBack()">&#8592; Back</button>
        <span id="mo-title"></span>
      </div>
      <button id="mo-close" onclick="closeModal()">&#x2715;</button>
    </div>
    <div id="mo-scroll">
      <table id="mo-table">
        <thead><tr>
          <th>Date</th>
          <th id="th-div" style="display:none">Div</th>
          <th id="th-yr" style="display:none">Year</th>
          <th>Home</th>
          <th>Score</th>
          <th>Away</th>
        </tr></thead>
        <tbody id="mo-rows"></tbody>
      </table>
    </div>
  </div>
</div>
<script>
__JS__
</script>
</body>
</html>
"""


def _bar_colors(n: int, division: str, max_group: int) -> list[str]:
    hue = _hue(division, max_group)
    result = []
    for i in range(n):
        t = i / max(n - 1, 1)
        lightness = round(62 - t * 26)   # bright for rank 1, dim for last
        alpha     = round(0.90 - t * 0.32, 2)
        result.append(f"hsla({hue}, 72%, {lightness}%, {alpha})")
    return result


_ZONE_TAG = {
    "champion":   ("", "champion"),
    "promotion":  ("", "promotion"),
    "chasing":    ("", "safe"),
    "relegation": ("", "relegation"),
    "safe":       ("", "safe"),
}


def _position_zones(division: str, n: int, max_group: int) -> list[str]:
    """Return a zone label for each position 0..n-1."""
    zones = ["safe"] * n
    group = _div_group(division)

    if division == "1":
        if n > 0: zones[0] = "champion"
        for i in range(max(1, n - 2), n): zones[i] = "relegation"
    elif division == "2":
        for i in range(min(2, n)): zones[i] = "promotion"
        for i in range(max(2, n - 3), n): zones[i] = "relegation"
    elif division in ("3A", "3B"):
        if n > 0: zones[0] = "promotion"
        if n > 1: zones[1] = "chasing"  # overridden dynamically in visualize()
        for i in range(max(2, n - 2), n): zones[i] = "relegation"
    elif group == max_group:
        for i in range(min(2, n)): zones[i] = "promotion"  # no relegation
    else:
        for i in range(min(2, n)): zones[i] = "promotion"
        for i in range(max(2, n - 2), n): zones[i] = "relegation"

    return zones


def _rank(i: int) -> str:
    return f"{i + 1}."


def _make_card(division: str, rows: list[dict], max_group: int,
               zone_overrides=None) -> str:
    sets_vals    = [int(r["sets_won"]) for r in rows]
    max_sets     = max(sets_vals) if any(s > 0 for s in sets_vals) else 1
    colors       = _bar_colors(len(rows), division, max_group)
    header_color = _header_color(division, max_group)
    zones        = _position_zones(division, len(rows), max_group)
    if zone_overrides:
        for pos, z in zone_overrides.items():
            if pos < len(zones):
                zones[pos] = z

    rows_html = []
    for i, row in enumerate(rows):
        team   = row["team"]
        sets   = int(row["sets_won"])
        games  = int(row["games_won"])
        played = int(row["played"])
        pct    = round(sets / max_sets * 100)
        tip    = f"Played: {played} &middot; Sets: {sets} &middot; Games: {games}"
        stat   = f'{sets}<small>&middot;{games}g</small>' if played else '<span style="color:#334155">—</span>'
        tag_html, zone_cls = _ZONE_TAG[zones[i]]
        separator = " zone-break" if i > 0 and zones[i] != zones[i - 1] else ""

        rows_html.append(
            f'<div class="t-row {zone_cls}{separator}"'
            f' onmouseenter="tipShow(this,event)" onmouseleave="tipHide(this)"'
            f' data-tip="{tip}">'
            f'<span class="t-rank">{_rank(i)}</span>'
            f"<button class=\"t-btn\" onclick='showTeam({json.dumps(team)})'>{team}</button>"
            f'<div class="t-bar-outer"><div class="t-bar"'
            f' style="width:{pct}%;background:{colors[i]}"></div></div>'
            f'<span class="t-num">{stat}</span>'
            f'{tag_html}'
            f'</div>'
        )

    return (
        '<div class="card">'
        f'<div class="card-header" style="background:{header_color}"'
        f" onclick='showDivision({json.dumps(division)})'>"
        f'Division {division}'
        '<span class="hdr-hint">&#9655; fixtures</span></div>'
        '<div class="team-list">'
        + "".join(rows_html)
        + "</div></div>"
    )


def _read_fixtures(combined_csv: pathlib.Path, include_unplayed: bool = True) -> list[dict]:
    rows = []
    with open(combined_csv) as f:
        for r in csv.DictReader(f):
            played = r["home_sets"] != ""
            if not played and not include_unplayed:
                continue
            rows.append({
                "y":  r["fixture_date"][:4],
                "d":  r["fixture_date"],
                "v":  r["division"],
                "h":  r["home_team"],
                "a":  r["away_team"],
                "hs": int(r["home_sets"])  if played else None,
                "hg": int(r["home_games"]) if played else None,
                "vs": int(r["away_sets"])  if played else None,
                "vg": int(r["away_games"]) if played else None,
            })
    return rows


def visualize(leagues_csv: pathlib.Path, combined_csv: pathlib.Path = COMBINED_CSV,
              historic_dir: pathlib.Path = HISTORIC_DIR) -> None:
    divisions: dict[str, list[dict]] = defaultdict(list)
    with open(leagues_csv) as f:
        for row in csv.DictReader(f):
            divisions[row["division"]].append(row)

    # Current-season fixtures (including unplayed) — used for team/division modals.
    fixtures = _read_fixtures(combined_csv, include_unplayed=True)

    # All fixtures across seasons — used for H2H lookup.
    all_fixtures = list(fixtures)
    if historic_dir.exists():
        for year_dir in sorted(historic_dir.iterdir()):
            hist_csv = year_dir / "combined.csv"
            if hist_csv.exists():
                all_fixtures.extend(_read_fixtures(hist_csv, include_unplayed=False))

    max_group = max(_div_group(d) for d in divisions)

    # Determine which 3A/3B second-place team is currently leading the promotion race.
    zone_overrides: dict[str, dict[int, str]] = {}
    rows3a = divisions.get("3A", [])
    rows3b = divisions.get("3B", [])
    if len(rows3a) > 1 and len(rows3b) > 1:
        key3a = (int(rows3a[1]["sets_won"]), int(rows3a[1]["games_won"]))
        key3b = (int(rows3b[1]["sets_won"]), int(rows3b[1]["games_won"]))
        if key3a == key3b:
            zone_overrides["3A"] = {1: "promotion"}
            zone_overrides["3B"] = {1: "promotion"}
        elif key3a > key3b:
            zone_overrides["3A"] = {1: "promotion"}
            zone_overrides["3B"] = {1: "chasing"}
        else:
            zone_overrides["3A"] = {1: "chasing"}
            zone_overrides["3B"] = {1: "promotion"}

    cards = [
        _make_card(div, divisions[div], max_group, zone_overrides.get(div))
        for div in sorted(divisions)
    ]

    page_js = (_PAGE_JS
               .replace("__FIXTURES__",     json.dumps(fixtures))
               .replace("__ALL_FIXTURES__", json.dumps(all_fixtures)))

    html = (
        _HTML
        .replace("__DATE__",  date.today().isoformat())
        .replace("__CARDS__", "\n".join(cards))
        .replace("__JS__",    page_js)
    )

    LEAGUES_HTML.parent.mkdir(parents=True, exist_ok=True)
    LEAGUES_HTML.write_text(html, encoding="utf-8")
    print(f"Visualization written to {LEAGUES_HTML}")


if __name__ == "__main__":
    visualize(LEAGUES_CSV)
