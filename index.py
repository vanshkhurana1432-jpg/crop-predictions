from http.server import BaseHTTPRequestHandler
import json

# ── Dataset ──────────────────────────────────────────────────────────
DATA = [
    {"t": 20, "h": 60, "r": 80,  "c": "Poor"},
    {"t": 22, "h": 65, "r": 90,  "c": "Good"},
    {"t": 25, "h": 70, "r": 100, "c": "Good"},
    {"t": 28, "h": 75, "r": 120, "c": "Good"},
    {"t": 30, "h": 80, "r": 150, "c": "Good"},
    {"t": 32, "h": 85, "r": 160, "c": "Good"},
    {"t": 18, "h": 55, "r": 50,  "c": "Poor"},
    {"t": 24, "h": 68, "r": 95,  "c": "Good"},
    {"t": 27, "h": 72, "r": 110, "c": "Good"},
    {"t": 35, "h": 40, "r": 30,  "c": "Poor"},
    {"t": 21, "h": 62, "r": 85,  "c": "Good"},
    {"t": 26, "h": 74, "r": 105, "c": "Good"},
    {"t": 29, "h": 78, "r": 130, "c": "Good"},
    {"t": 31, "h": 45, "r": 40,  "c": "Poor"},
    {"t": 23, "h": 66, "r": 88,  "c": "Good"},
    {"t": 19, "h": 58, "r": 60,  "c": "Poor"},
    {"t": 33, "h": 42, "r": 35,  "c": "Poor"},
    {"t": 25, "h": 71, "r": 115, "c": "Good"},
    {"t": 28, "h": 76, "r": 125, "c": "Good"},
    {"t": 22, "h": 64, "r": 82,  "c": "Good"},
]


def predict(temp, hum, rain):
    """Decision rule: humidity >= 57.5 AND rainfall >= 75 -> Good, else Poor."""
    if hum >= 57.5 and rain >= 75:
        return "Good"
    return "Poor"


def render_rows():
    rows = ""
    for d in DATA:
        cls = d["c"].lower()
        rows += f"<tr><td>{d['t']}</td><td>{d['h']}</td><td>{d['r']}</td><td><span class='tag {cls}'>{d['c']}</span></td></tr>"
    return rows


PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Crop Condition Predictor</title>
<style>
  :root{{
    --soil:#3f3222; --soil-deep:#2a2118; --leaf:#4c6b3f; --leaf-dark:#3a5230;
    --cream:#f6f1e6; --paper:#fffdf8; --line:#e3d9c4; --poor:#b5563c;
  }}
  *{{box-sizing:border-box;}}
  body{{margin:0;background:var(--cream);color:var(--soil);font-family:sans-serif;line-height:1.5;}}
  .wrap{{max-width:720px;margin:0 auto;padding:48px 24px 80px;}}
  h1{{font-size:1.8rem;color:var(--soil-deep);}}
  p.sub{{color:#6b5d47;}}
  .card{{background:var(--paper);border:1px solid var(--line);border-radius:10px;padding:24px;margin-bottom:32px;}}
  table{{width:100%;border-collapse:collapse;font-size:0.9rem;}}
  th{{text-align:left;padding:10px;background:var(--soil-deep);color:var(--cream);}}
  td{{padding:8px 10px;border-top:1px solid var(--line);}}
  .tag{{padding:2px 10px;border-radius:100px;font-size:0.78rem;font-weight:500;}}
  .tag.good{{background:#e4ecdd;color:var(--leaf-dark);}}
  .tag.poor{{background:#f3e0d9;color:var(--poor);}}
  label{{display:block;font-size:0.85rem;margin-bottom:6px;color:#6b5d47;}}
  input{{width:100%;padding:10px;margin-bottom:16px;border:1px solid var(--line);border-radius:6px;font-size:1rem;}}
  button{{width:100%;padding:12px;background:var(--leaf);color:white;border:none;border-radius:6px;font-size:1rem;cursor:pointer;}}
  button:hover{{background:var(--leaf-dark);}}
  .result{{margin-top:16px;padding:14px;border-radius:8px;}}
  .result.good{{background:#e4ecdd;color:var(--leaf-dark);}}
  .result.poor{{background:#f3e0d9;color:var(--poor);}}
</style>
</head>
<body>
<div class="wrap">
  <h1>Crop Condition Predictor</h1>
  <p class="sub">Enter today's weather readings to predict Good or Poor crop condition.</p>

  <div class="card">
    <h2>Try a prediction</h2>
    <form method="POST" action="/">
      <label for="temp">Temperature (°C)</label>
      <input type="number" step="0.1" name="temp" id="temp" value="{temp}" required>
      <label for="hum">Humidity (%)</label>
      <input type="number" step="0.1" name="hum" id="hum" value="{hum}" required>
      <label for="rain">Rainfall (mm)</label>
      <input type="number" step="0.1" name="rain" id="rain" value="{rain}" required>
      <button type="submit">Predict Crop Condition</button>
    </form>
    {result_html}
  </div>

  <div class="card">
    <h2>Training dataset</h2>
    <table>
      <tr><th>Temp (°C)</th><th>Humidity (%)</th><th>Rainfall (mm)</th><th>Condition</th></tr>
      {rows}
    </table>
  </div>
</div>
</body>
</html>"""


def render_page(temp=25, hum=65, rain=100, result=None):
    result_html = ""
    if result:
        cls = "good" if result == "Good" else "poor"
        msg = "These conditions favor healthy crop growth." if result == "Good" else "These conditions are unfavorable for the crop."
        result_html = f"<div class='result {cls}'><strong>{result}</strong><br>{msg}</div>"
    return PAGE_TEMPLATE.format(temp=temp, hum=hum, rain=rain, result_html=result_html, rows=render_rows())


class handler(BaseHTTPRequestHandler):

    def _send_html(self, status, html):
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html.encode())

    def do_GET(self):
        self._send_html(200, render_page())

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode()
        # form-encoded: temp=25&hum=65&rain=100
        from urllib.parse import parse_qs
        fields = parse_qs(body)
        try:
            temp = float(fields["temp"][0])
            hum = float(fields["hum"][0])
            rain = float(fields["rain"][0])
        except (KeyError, ValueError, IndexError):
            self._send_html(400, render_page())
            return
        result = predict(temp, hum, rain)
        self._send_html(200, render_page(temp=temp, hum=hum, rain=rain, result=result))
