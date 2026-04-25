
import csv
import json
import pathlib
from collections import defaultdict
from datetime import date
from parse import PROJECT_ROOT


LEAGUES_CSV  = PROJECT_ROOT / "tables" / "leagues"  / "leagues.csv"
COMBINED_CSV = PROJECT_ROOT / "tables" / "combined" / "combined.csv"
LEAGUES_HTML = PROJECT_ROOT / "tables" / "leagues"  / "leagues.html"

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

const FIXTURES = __FIXTURES__;

function showTeam(team) {
  openModal(team, FIXTURES.filter(f => f.h === team || f.a === team), false);
}
function showDivision(div) {
  openModal('Division ' + div, FIXTURES.filter(f => f.v === div), true);
}
function openModal(title, rows, showDiv) {
  rows = rows.slice().sort((a, b) => a.d < b.d ? -1 : 1);
  document.getElementById('mo-title').textContent = title;
  document.getElementById('th-div').style.display = showDiv ? '' : 'none';
  document.getElementById('mo-rows').innerHTML = rows.map(f => {
    const played = f.hs !== null;
    const score  = played
      ? f.hs + '–' + f.vs + '<br><small>' + f.hg + '–' + f.vg + ' games</small>'
      : '—';
    const dc = showDiv ? '<td>' + f.v + '</td>' : '';
    return '<tr class="' + (played ? 'pl' : 'up') + '">'
      + '<td>' + f.d + '</td>' + dc
      + '<td class="tm">' + f.h + '</td>'
      + '<td class="sc">' + score + '</td>'
      + '<td class="tm">' + f.a + '</td>'
      + '</tr>';
  }).join('');
  document.getElementById('modal').style.display = 'flex';
}
function closeModal() {
  document.getElementById('modal').style.display = 'none';
}
document.addEventListener('keydown', e => { if (e.key === 'Escape') closeModal(); });
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
         border-radius: 6px; }
.t-row:hover { background: rgba(255,255,255,0.03); }
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
</style>
</head>
<body>
<h1>🎾 Datchworth Tennis Leagues</h1>
<p class="subtitle">Updated __DATE__</p>
<div class="grid">
__CARDS__
</div>
<div id="modal" onclick="if(event.target===this)closeModal()">
  <div id="modal-panel">
    <div id="mo-hdr">
      <span id="mo-title"></span>
      <button id="mo-close" onclick="closeModal()">&#x2715;</button>
    </div>
    <div id="mo-scroll">
      <table id="mo-table">
        <thead><tr>
          <th>Date</th>
          <th id="th-div" style="display:none">Div</th>
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


def _medal(i: int) -> str:
    return ["🥇", "🥈", "🥉"][i] if i < 3 else f"{i + 1}."


def _make_card(division: str, rows: list[dict], max_group: int) -> str:
    sets_vals    = [int(r["sets_won"]) for r in rows]
    max_sets     = max(sets_vals) if any(s > 0 for s in sets_vals) else 1
    colors       = _bar_colors(len(rows), division, max_group)
    header_color = _header_color(division, max_group)

    rows_html = []
    for i, row in enumerate(rows):
        team   = row["team"]
        sets   = int(row["sets_won"])
        games  = int(row["games_won"])
        played = int(row["played"])
        pct    = round(sets / max_sets * 100)
        tip    = f"Played: {played} &middot; Sets: {sets} &middot; Games: {games}"
        stat   = f'{sets}<small>&middot;{games}g</small>' if played else '<span style="color:#334155">—</span>'

        rows_html.append(
            f'<div class="t-row" onmouseenter="tipShow(this,event)" onmouseleave="tipHide(this)"'
            f' data-tip="{tip}">'
            f'<span class="t-rank">{_medal(i)}</span>'
            f"<button class=\"t-btn\" onclick='showTeam({json.dumps(team)})'>{team}</button>"
            f'<div class="t-bar-outer"><div class="t-bar"'
            f' style="width:{pct}%;background:{colors[i]}"></div></div>'
            f'<span class="t-num">{stat}</span>'
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


def visualize(leagues_csv: pathlib.Path, combined_csv: pathlib.Path = COMBINED_CSV) -> None:
    divisions: dict[str, list[dict]] = defaultdict(list)
    with open(leagues_csv) as f:
        for row in csv.DictReader(f):
            divisions[row["division"]].append(row)

    fixtures = []
    with open(combined_csv) as f:
        for r in csv.DictReader(f):
            fixtures.append({
                "d":  r["fixture_date"],
                "v":  r["division"],
                "h":  r["home_team"],
                "a":  r["away_team"],
                "hs": int(r["home_sets"])  if r["home_sets"]  != "" else None,
                "hg": int(r["home_games"]) if r["home_games"] != "" else None,
                "vs": int(r["away_sets"])  if r["away_sets"]  != "" else None,
                "vg": int(r["away_games"]) if r["away_games"] != "" else None,
            })

    max_group = max(_div_group(d) for d in divisions)
    cards = [
        _make_card(div, divisions[div], max_group)
        for div in sorted(divisions)
    ]

    page_js = _PAGE_JS.replace("__FIXTURES__", json.dumps(fixtures))

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
