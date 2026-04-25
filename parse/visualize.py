
import csv
import json
import pathlib
from collections import defaultdict
from datetime import date
from parse import PROJECT_ROOT


LEAGUES_CSV  = PROJECT_ROOT / "tables" / "leagues" / "leagues.csv"
LEAGUES_HTML = PROJECT_ROOT / "tables" / "leagues" / "leagues.html"

HEADER_COLORS = [
    "#0369a1", "#15803d", "#9333ea", "#b45309",
    "#be123c", "#0f766e", "#c2410c", "#4338ca",
    "#0e7490", "#65a30d", "#7c3aed", "#b91c1c",
    "#0d9488",
]


def _bar_colors(n: int) -> list[str]:
    result = []
    for i in range(n):
        t = i / max(n - 1, 1)
        r = int(74  + t * (22  - 74))
        g = int(222 + t * (101 - 222))
        b = int(128 + t * (52  - 128))
        alpha = round(0.92 - t * 0.42, 2)
        result.append(f"rgba({r},{g},{b},{alpha})")
    return result


def _medal(i: int) -> str:
    return ["🥇 ", "🥈 ", "🥉 "][i] if i < 3 else f"{i + 1}.  "


def _make_card(division: str, rows: list[dict], header_color: str, chart_id: str) -> tuple[str, str]:
    labels = [_medal(i) + r["team"] for i, r in enumerate(rows)]
    sets   = [int(r["sets_won"])  for r in rows]
    games  = [int(r["games_won"]) for r in rows]
    played = [int(r["played"])    for r in rows]
    colors = _bar_colors(len(rows))

    height = max(240, len(rows) * 36 + 60)

    card_html = (
        f'  <div class="card">\n'
        f'    <div class="card-header" style="background:{header_color}">Division {division}</div>\n'
        f'    <div class="chart-wrap" style="height:{height}px">'
        f'<canvas id="{chart_id}"></canvas></div>\n'
        f'  </div>'
    )

    chart_js = f"""
  new Chart(document.getElementById({json.dumps(chart_id)}), {{
    type: 'bar',
    data: {{
      labels: {json.dumps(labels)},
      datasets: [{{
        data: {json.dumps(sets)},
        backgroundColor: {json.dumps(colors)},
        borderRadius: 5,
        borderSkipped: false
      }}]
    }},
    options: {{
      indexAxis: 'y',
      plugins: {{
        legend: {{ display: false }},
        tooltip: {{
          callbacks: {{
            label: function(ctx) {{
              var i = ctx.dataIndex;
              return '  Sets: ' + ctx.raw + '   Games: ' + {json.dumps(games)}[i] + '   Played: ' + {json.dumps(played)}[i];
            }}
          }}
        }}
      }},
      scales: {{
        x: {{
          min: 0,
          grid: {{ color: 'rgba(255,255,255,0.06)' }},
          ticks: {{ color: '#64748b', stepSize: 1, precision: 0 }},
          title: {{ display: true, text: 'Sets Won', color: '#475569', font: {{ size: 11 }} }}
        }},
        y: {{
          grid: {{ display: false }},
          ticks: {{ color: '#cbd5e1', font: {{ size: 12 }} }}
        }}
      }},
      maintainAspectRatio: false,
      animation: {{ duration: 500 }}
    }}
  }});"""

    return card_html, chart_js


def visualize(leagues_csv: pathlib.Path) -> None:
    divisions: dict[str, list[dict]] = defaultdict(list)
    with open(leagues_csv) as f:
        for row in csv.DictReader(f):
            divisions[row["division"]].append(row)

    cards_html: list[str] = []
    scripts: list[str] = []
    for idx, division in enumerate(sorted(divisions)):
        color = HEADER_COLORS[idx % len(HEADER_COLORS)]
        card, script = _make_card(division, divisions[division], color, f"c{idx}")
        cards_html.append(card)
        scripts.append(script)

    today = date.today().isoformat()

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Datchworth Tennis Leagues</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  background: #0f172a;
  color: #e2e8f0;
  min-height: 100vh;
  padding: 44px 20px 60px;
}}
h1 {{
  text-align: center;
  font-size: 2rem;
  color: #86efac;
  margin-bottom: 6px;
  letter-spacing: -0.5px;
}}
.subtitle {{
  text-align: center;
  color: #475569;
  font-size: .82rem;
  margin-bottom: 44px;
  letter-spacing: 0.5px;
  text-transform: uppercase;
}}
.grid {{
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
  gap: 22px;
  max-width: 1440px;
  margin: 0 auto;
}}
.card {{
  background: #1e293b;
  border-radius: 14px;
  overflow: hidden;
  border: 1px solid #334155;
  box-shadow: 0 4px 24px rgba(0,0,0,.35);
  transition: box-shadow .2s;
}}
.card:hover {{ box-shadow: 0 8px 32px rgba(0,0,0,.5); }}
.card-header {{
  padding: 11px 18px;
  font-weight: 700;
  font-size: .8rem;
  letter-spacing: 1.2px;
  text-transform: uppercase;
  color: rgba(255,255,255,.92);
}}
.chart-wrap {{ padding: 12px 16px 16px; }}
</style>
</head>
<body>
<h1>🎾 Datchworth Tennis Leagues</h1>
<p class="subtitle">Updated {today}</p>
<div class="grid">
{chr(10).join(cards_html)}
</div>
<script>
{"".join(scripts)}
</script>
</body>
</html>"""

    LEAGUES_HTML.parent.mkdir(parents=True, exist_ok=True)
    LEAGUES_HTML.write_text(html, encoding="utf-8")
    print(f"Visualization written to {LEAGUES_HTML}")


if __name__ == "__main__":
    visualize(LEAGUES_CSV)
