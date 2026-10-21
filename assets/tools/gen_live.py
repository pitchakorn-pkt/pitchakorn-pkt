"""Nightly cards built from live GitHub data (run by .github/workflows/cards.yml).

    pip install fonttools pillow uharfbuzz
    GITHUB_TOKEN=... python3 assets/tools/gen_live.py

Writes assets/hours.svg (commits per hour of day, Asia/Bangkok) and assets/projects/<name>.svg.
"""
import datetime as dt, io, json, os, re, urllib.request
from pathlib import Path
import uharfbuzz as hb
from fontTools.ttLib import TTFont
from gen_assets import TOOLS, OUT, WHITE, MUTED, BLUE, DEEP, MOON, text_path

USER = "pitchakorn-pkt"
TZ = dt.timezone(dt.timedelta(hours=7))
SOFT = "#C8D0F0"
MALI = "https://github.com/google/fonts/raw/main/ofl/mali/Mali-Medium.ttf"

# area, repo, description (Thai; \u200b marks invisible line-break points), stack
PROJECTS = [
    ("AI", "pitchakorn-pkt/rod-mai-rod",
     "เว็บ\u200bวางแผน\u200bเดินทาง\u200bในไทย\u200bให้\u200bปลอดภัย เช็ก\u200bอากาศ ณ เวลา\u200bที่\u200bไปถึง\u200bแต่ละ\u200bจุด น้ำท่วม\u200bจาก\u200bดาวเทียม และ\u200bผู้ช่วย AI แก้\u200bทริป\u200bผ่าน\u200bแชท",
     ["FastAPI", "PostgreSQL", "Next.js", "LLM"]),
    ("AI", "pitchakorn-pkt/chuayduay",
     "ผู้ช่วย\u200bแก้\u200bปัญหา\u200bมือถือ\u200bและ\u200bคอม\u200bภาษาไทย agentic RAG 8 โมดูล ตอบ\u200bพร้อม\u200bแหล่ง\u200bอ้างอิง",
     ["FastAPI", "PostgreSQL", "RAG", "Docker"]),
    ("AI", "Mrbeer19/SENTINEL-AI",
     "security dashboard ที่\u200bให้ LLM ใน\u200bเครื่อง\u200bสืบ\u200bหลักฐาน แล้ว\u200bให้\u200bคน\u200bอนุมัติ\u200bการ block (กำลัง\u200bทำ)",
     ["Python", "Ollama", "React", "SQLite"]),
    ("VISION", "pitchakorn-pkt/led-colorwatch",
     "ตรวจ\u200bหา\u200bไฟ LED ที่\u200bสี\u200bเพี้ยน\u200bผ่าน\u200bกล้อง พร้อม\u200bหน้า\u200bเว็บ รัน\u200bได้\u200bทั้ง Windows macOS Linux",
     ["Python", "OpenCV"]),
    ("EMBEDDED", "pitchakorn-pkt/esp32c5-thread",
     "ESP32-C5 อ่าน\u200bค่า SHT40 ส่ง\u200bผ่าน Thread ขึ้น MQTT ทาง NAT64 พร้อม\u200bหน้า\u200bเว็บ\u200bตั้ง\u200bค่า\u200bเครือข่าย",
     ["ESP-IDF", "OpenThread", "MQTT"]),
]
LANG_COLOR = {"Python": "#FFD43B", "C": "#A8B9CC", "C++": "#5B9BE0", "TypeScript": "#5B9BE0", "JavaScript": "#F7DF1E"}


def gh(path):
    req = urllib.request.Request(f"https://api.github.com/{path}", headers={"Accept": "application/vnd.github+json"})
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def write(name, body):
    path = OUT / name; path.parent.mkdir(exist_ok=True)
    path.write_text(body)
    print(name, f"{len(body)/1024:.0f} KB")


# ---------- small text stays real <text> ----------
# Paths have no hinting, so 12-16 px text turns soft and jagged on 1x monitors.
# Real text uses the viewer's hinted system fonts (Thai falls back to Leelawadee UI / Thonburi).
SANS = "'Segoe UI','Leelawadee UI','Noto Sans Thai',-apple-system,BlinkMacSystemFont,'Helvetica Neue',Thonburi,sans-serif"
MONO = "'JetBrains Mono','Cascadia Mono',Consolas,'SF Mono',Menlo,monospace"
CARD = "#080F21"; EDGE = "#1A2547"; CHIP = "#0D1530"; CHIP_EDGE = "#22305A"

def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def txt(x, y, s, size, fill, family=MONO, weight=500, anchor="start", spacing=0):
    ls = f' letter-spacing="{spacing}"' if spacing else ""
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{family}" font-size="{size}" font-weight="{weight}" '
            f'fill="{fill}" text-anchor="{anchor}"{ls}>{s}</text>')

def mono_w(s, size, spacing=0):
    return len(s) * (size * 0.6 + spacing)  # every monospace face is ~0.6 em wide

# Mali is only used to measure Thai lines for wrapping; viewers' Thai fonts run a little wider.
_mali = {}
def mali():
    if not _mali:
        path = TOOLS / "fonts" / "Mali-Medium.ttf"
        if not path.exists():
            path.parent.mkdir(exist_ok=True)
            urllib.request.urlretrieve(MALI, path)
        data = path.read_bytes()
        _mali["hb"] = hb.Font(hb.Face(data))
        _mali["upm"] = TTFont(io.BytesIO(data))["head"].unitsPerEm
    return _mali["hb"], _mali["upm"]

def measure(s, size):
    hbf, upm = mali()
    buf = hb.Buffer(); buf.add_str(s); buf.guess_segment_properties()
    hb.shape(hbf, buf, {})
    return sum(p.x_advance for p in buf.glyph_positions) * size / upm

def wrap(s, size, width, max_lines):
    """Greedy wrap at spaces and zero-width spaces; the last line gets an ellipsis if text is left over."""
    tokens = re.split(r"(?<=[ \u200b])", s); lines = [""]
    for t in tokens:
        if measure((lines[-1] + t).strip(), size) <= width:
            lines[-1] += t
        elif len(lines) < max_lines:
            lines.append(t)
        else:
            while lines[-1] and measure(lines[-1].strip() + "…", size) > width:
                lines[-1] = lines[-1][:-1]
            lines[-1] = lines[-1].strip() + "…"; break
    return [l.replace("\u200b", "").strip() for l in lines]


# ---------- commits per hour ----------
def commit_hours():
    hours = [0] * 24; total = 0
    for page in range(1, 11):  # search API stops at 1000 results
        items = gh(f"search/commits?q=author:{USER}&sort=author-date&order=desc&per_page=100&page={page}")["items"]
        for it in items:
            t = dt.datetime.fromisoformat(it["commit"]["author"]["date"].replace("Z", "+00:00")).astimezone(TZ)
            hours[t.hour] += 1; total += 1
        if len(items) < 100:
            break
    return hours, total

def hours_card(hours, total):
    W, H = 840, 256; x0, x1, base, top = 40, 800, 200, 82
    bw = (x1 - x0) / 24; peak = max(hours) or 1
    night = sum(hours[h] for h in range(24) if h >= 21 or h < 5)
    busiest = max(range(24), key=lambda h: hours[h])
    info = f"{total:,} commits  ·  busiest {busiest:02d}:00  ·  after 9 pm {round(100*night/max(total,1))}%"
    bars = []
    for h, n in enumerate(hours):
        bh = max(3, (base - top) * n / peak); x = x0 + h * bw + 4
        dark = h >= 19 or h < 6
        fill = WHITE if h == busiest else (BLUE if dark else "#4F62AE")
        bars.append(f'<rect x="{x:.1f}" y="{base-bh:.1f}" width="{bw-8:.1f}" height="{bh:.1f}" rx="3" fill="{fill}"/>')
    ticks = "".join(txt(x0 + h*bw + bw/2, base + 26, f"{h:02d}", 14, MUTED, anchor="middle") for h in (0, 6, 12, 18))
    mx = x0 + 22.5 * bw  # crescent over the late-night end
    write("hours.svg", f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">
<style>.tw{{animation:tw 3s ease-in-out infinite}}@keyframes tw{{0%,100%{{opacity:.3}}50%{{opacity:1}}}}
@media (prefers-reduced-motion:reduce){{.tw{{animation:none}}}}</style>
<defs>
<linearGradient id="sky" x1="0" x2="1">
<stop offset="0" stop-color="#050A18"/><stop offset=".25" stop-color="#0B1430"/><stop offset=".5" stop-color="#121D42"/>
<stop offset=".75" stop-color="#0B1430"/><stop offset="1" stop-color="#050A18"/></linearGradient>
<mask id="cut"><rect width="{W}" height="{H}" fill="#fff"/><circle cx="{mx+6}" cy="{top-4}" r="9" fill="#000"/></mask>
</defs>
<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="22" fill="{CARD}" stroke="{EDGE}" stroke-width="2"/>
<rect x="{x0}" y="{top-20}" width="{x1-x0}" height="{base-top+20}" rx="10" fill="url(#sky)"/>
<circle cx="{mx}" cy="{top}" r="10" fill="{MOON}" mask="url(#cut)"/>
<circle class="tw" cx="{x0+1.5*bw}" cy="{top-2}" r="1.6" fill="{WHITE}"/>
<circle class="tw" cx="{x0+3.2*bw}" cy="{top+14}" r="1.2" fill="{WHITE}" style="animation-delay:-1s"/>
<circle class="tw" cx="{x0+20.5*bw}" cy="{top+6}" r="1.4" fill="{WHITE}" style="animation-delay:-2s"/>
{"".join(bars)}
<rect x="{x0}" y="{base}" width="{x1-x0}" height="1" fill="{EDGE}"/>
{ticks}
{txt(40, 44, "WHEN I COMMIT", 14, WHITE, weight=700, spacing=2.4)}
{txt(x1, 44, info, 14, MUTED, anchor="end")}
</svg>''')


# ---------- project cards ----------
def chip(x, y, label):
    w = mono_w(label, 14) + 24
    return (f'<rect x="{x}" y="{y}" width="{w:.0f}" height="28" rx="14" fill="{CHIP}" stroke="{CHIP_EDGE}"/>'
            + txt(x + 12, y + 19, esc(label), 14, SOFT)), w

def project_card(area, repo, desc, stack, wide):
    meta = gh(f"repos/{repo}"); name = repo.split("/")[1]
    W = 840 if wide else 412; H = 208
    tw = mono_w(area, 13, 2)
    title, _ = text_path(name, 24, 86, 28, wght=600)
    lines = wrap(desc, 16, W - 48, 2)
    body = "".join(txt(24, 118 + i*25, esc(l), 16, SOFT, family=SANS, weight=400) for i, l in enumerate(lines))
    chips = []; cx = 24
    for s in stack:
        svg, w = chip(cx, 160, s); chips.append(svg); cx += w + 8
    lang = meta.get("language") or ""
    pushed = dt.datetime.fromisoformat(meta["pushed_at"].replace("Z", "+00:00")).astimezone(TZ)
    stars = meta["stargazers_count"]
    right = (f'<tspan fill="{LANG_COLOR.get(lang, MUTED)}">●</tspan> {esc(lang)}  ·  ' if lang else "") \
        + f"updated {pushed:%d %b %Y}" + (f"  ·  {stars} star" + "s" * (stars > 1) if stars else "")
    write(f"projects/{name}.svg", f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">
<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="20" fill="{CARD}" stroke="{EDGE}" stroke-width="2"/>
<rect x="24" y="22" width="{tw+22:.0f}" height="28" rx="14" fill="{DEEP}" fill-opacity=".3"/>
{txt(35, 41, area, 13, WHITE, weight=700, spacing=2)}
{txt(W-24, 41, right, 14, MUTED, anchor="end")}
<path d="{title}" fill="{WHITE}"/>
{body}
{"".join(chips)}
</svg>''')


if __name__ == "__main__":
    hours_card(*commit_hours())
    for i, p in enumerate(PROJECTS):
        project_card(*p, wide=(i == 0))
