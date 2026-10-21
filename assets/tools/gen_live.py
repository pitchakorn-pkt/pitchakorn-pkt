"""Nightly cards built from live GitHub data (run by .github/workflows/cards.yml).

    pip install fonttools pillow uharfbuzz
    GITHUB_TOKEN=... python3 assets/tools/gen_live.py

Writes assets/hours.svg (commits per hour of day, Asia/Bangkok) and assets/projects/<name>.svg.
"""
import datetime as dt, io, json, os, urllib.request
from pathlib import Path
import uharfbuzz as hb
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from gen_assets import (TOOLS, OUT, PANEL, LINE, WHITE, MUTED, BLUE, DEEP, MOON,
                        text_path)

USER = "pitchakorn-pkt"
TZ = dt.timezone(dt.timedelta(hours=7))
SOFT = "#C8D0F0"
MALI = "https://github.com/google/fonts/raw/main/ofl/mali/Mali-Medium.ttf"

# area, repo, description (Thai), stack
PROJECTS = [
    ("AI", "pitchakorn-pkt/rod-mai-rod",
     "เว็บวางแผนเดินทางในไทยให้ปลอดภัย เช็กอากาศ ณ เวลาที่ไปถึงแต่ละจุด น้ำท่วมจากดาวเทียม และผู้ช่วย AI แก้ทริปผ่านแชท",
     ["FastAPI", "PostgreSQL", "Next.js", "LLM"]),
    ("AI", "pitchakorn-pkt/chuayduay",
     "ผู้ช่วยแก้ปัญหามือถือและคอมภาษาไทย agentic RAG 8 โมดูล ตอบพร้อมแหล่งอ้างอิง",
     ["FastAPI", "PostgreSQL", "RAG", "Docker"]),
    ("AI", "Mrbeer19/SENTINEL-AI",
     "security dashboard ที่ให้ LLM ในเครื่องสืบหลักฐาน แล้วให้คนอนุมัติการ block (กำลังทำ)",
     ["Python", "Ollama", "React", "SQLite"]),
    ("VISION", "pitchakorn-pkt/led-colorwatch",
     "ตรวจหาไฟ LED ที่สีเพี้ยนผ่านกล้อง พร้อมหน้าเว็บ รันได้ทั้ง Windows macOS Linux",
     ["Python", "OpenCV"]),
    ("EMBEDDED", "pitchakorn-pkt/esp32c5-thread",
     "ESP32-C5 อ่านค่า SHT40 ส่งผ่าน Thread ขึ้น MQTT ทาง NAT64 พร้อมหน้าเว็บตั้งค่าเครือข่าย",
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


# ---------- Thai-capable text (shaped with harfbuzz so marks sit correctly) ----------
_mali = {}
def mali():
    if not _mali:
        path = TOOLS / "fonts" / "Mali-Medium.ttf"
        if not path.exists():
            path.parent.mkdir(exist_ok=True)
            urllib.request.urlretrieve(MALI, path)
        data = path.read_bytes()
        _mali["hb"] = hb.Font(hb.Face(data))
        _mali["tt"] = TTFont(io.BytesIO(data))
    return _mali["hb"], _mali["tt"]

def shape(s, size):
    """Return list of (glyph name, x, y) in px and total advance."""
    hbf, tt = mali(); k = size / tt["head"].unitsPerEm
    buf = hb.Buffer(); buf.add_str(s); buf.guess_segment_properties()
    hb.shape(hbf, buf, {})
    order = tt.getGlyphOrder(); out = []; x = 0
    for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
        out.append((order[info.codepoint], (x + pos.x_offset) * k, pos.y_offset * k))
        x += pos.x_advance
    return out, x * k

def thai_path(s, x, y, size):
    _, tt = mali(); gs = tt.getGlyphSet(); k = size / tt["head"].unitsPerEm
    pen = SVGPathPen(gs)
    glyphs, _ = shape(s, size)
    for name, gx, gy in glyphs:
        gs[name].draw(TransformPen(pen, (k, 0, 0, -k, x + gx, y - gy)))
    return pen.getCommands()

def wrap(s, size, width, max_lines):
    """Greedy wrap on spaces; the last line gets an ellipsis if text is left over."""
    words = s.split(" "); lines = [""]
    for w in words:
        trial = (lines[-1] + " " + w).strip()
        if shape(trial, size)[1] <= width:
            lines[-1] = trial
        elif len(lines) < max_lines:
            lines.append(w)
        else:
            while lines[-1] and shape(lines[-1] + "…", size)[1] > width:
                lines[-1] = lines[-1][:-1]
            lines[-1] += "…"; break
    return lines


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
    W, H = 840, 250; x0, x1, base, top = 40, 800, 200, 80
    bw = (x1 - x0) / 24; peak = max(hours) or 1
    night = sum(hours[h] for h in range(24) if h >= 21 or h < 5)
    busiest = max(range(24), key=lambda h: hours[h])
    cap, _ = text_path("WHEN I COMMIT", 40, 44, 12, name="JetBrainsMono", wght=600, spacing=2.4)
    info, iw = text_path(f"{total:,} commits  ·  busiest {busiest:02d}:00  ·  after 9 pm {round(100*night/max(total,1))}%",
                         0, 0, 12, name="JetBrainsMono", wght=500)
    info, _ = text_path(f"{total:,} commits  ·  busiest {busiest:02d}:00  ·  after 9 pm {round(100*night/max(total,1))}%",
                        x1 - iw, 44, 12, name="JetBrainsMono", wght=500)
    bars = []
    for h, n in enumerate(hours):
        bh = max(3, (base - top) * n / peak); x = x0 + h * bw + 4
        dark = h >= 19 or h < 6
        fill = WHITE if h == busiest else (BLUE if dark else "#5A6FC0")
        bars.append(f'<rect x="{x:.1f}" y="{base-bh:.1f}" width="{bw-8:.1f}" height="{bh:.1f}" rx="3" fill="{fill}"/>')
    ticks = "".join(
        f'<path d="{text_path(f"{h:02d}", x0 + h*bw + bw/2, base + 24, 12, name="JetBrainsMono", wght=500, anchor="middle")[0]}" fill="{MUTED}"/>'
        for h in (0, 6, 12, 18))
    # crescent over the late-night end, sun disc over noon
    mx = x0 + 22.5 * bw
    write("hours.svg", f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">
<style>.tw{{animation:tw 3s ease-in-out infinite}}@keyframes tw{{0%,100%{{opacity:.3}}50%{{opacity:1}}}}
@media (prefers-reduced-motion:reduce){{.tw{{animation:none}}}}</style>
<defs>
<linearGradient id="sky" x1="0" x2="1">
<stop offset="0" stop-color="#0A1129"/><stop offset=".25" stop-color="#16244D"/><stop offset=".5" stop-color="#22356B"/>
<stop offset=".75" stop-color="#16244D"/><stop offset="1" stop-color="#0A1129"/></linearGradient>
<mask id="cut"><rect width="{W}" height="{H}" fill="#fff"/><circle cx="{mx+6}" cy="{top-4}" r="9" fill="#000"/></mask>
</defs>
<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="22" fill="{PANEL}" stroke="{LINE}" stroke-width="2"/>
<rect x="{x0}" y="{top-20}" width="{x1-x0}" height="{base-top+20}" rx="10" fill="url(#sky)"/>
<circle cx="{mx}" cy="{top}" r="10" fill="{MOON}" mask="url(#cut)"/>
<circle class="tw" cx="{x0+1.5*bw}" cy="{top-2}" r="1.6" fill="{WHITE}"/>
<circle class="tw" cx="{x0+3.2*bw}" cy="{top+14}" r="1.2" fill="{WHITE}" style="animation-delay:-1s"/>
<circle class="tw" cx="{x0+20.5*bw}" cy="{top+6}" r="1.4" fill="{WHITE}" style="animation-delay:-2s"/>
{"".join(bars)}
<rect x="{x0}" y="{base}" width="{x1-x0}" height="1" fill="{LINE}"/>
{ticks}
<path d="{cap}" fill="{WHITE}"/>
<path d="{info}" fill="{MUTED}"/>
</svg>''')


# ---------- project cards ----------
def chip(x, y, label):
    p, w = text_path(label, 0, 0, 12, name="JetBrainsMono", wght=500)
    p, _ = text_path(label, x + 10, y + 16, 12, name="JetBrainsMono", wght=500)
    return f'<rect x="{x}" y="{y}" width="{w+20:.0f}" height="24" rx="12" fill="#131E3D" stroke="#26366A"/><path d="{p}" fill="{SOFT}"/>', w + 20

def project_card(area, repo, desc, stack, wide):
    meta = gh(f"repos/{repo}"); name = repo.split("/")[1]
    W = 840 if wide else 412; H = 196
    tag, tw = text_path(area, 0, 0, 11, name="JetBrainsMono", wght=600, spacing=2)
    tag, _ = text_path(area, 34, 41, 11, name="JetBrainsMono", wght=600, spacing=2)
    title, _ = text_path(name, 24, 82, 26, wght=600)
    lines = wrap(desc, 15, W - 48, 2)
    body = "".join(f'<path d="{thai_path(l, 24, 112 + i*24, 15)}" fill="{SOFT}"/>' for i, l in enumerate(lines))
    chips = []; cx = 24
    for s in stack:
        svg, w = chip(cx, 150, s); chips.append(svg); cx += w + 8
    lang = meta.get("language") or ""
    pushed = dt.datetime.fromisoformat(meta["pushed_at"].replace("Z", "+00:00")).astimezone(TZ)
    right = f"{lang}  ·  updated {pushed:%d %b %Y}" + (f"  ·  {meta['stargazers_count']} star" + "s" * (meta["stargazers_count"] > 1) if meta["stargazers_count"] else "")
    rp, rw = text_path(right, 0, 0, 12, name="JetBrainsMono", wght=500)
    rp, _ = text_path(right, W - 24 - rw, 41, 12, name="JetBrainsMono", wght=500)
    dot = f'<circle cx="{W-24-rw-12}" cy="37" r="5" fill="{LANG_COLOR.get(lang, MUTED)}"/>' if lang else ""
    write(f"projects/{name}.svg", f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">
<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="20" fill="{PANEL}" stroke="{LINE}" stroke-width="2"/>
<rect x="24" y="24" width="{tw+20:.0f}" height="24" rx="12" fill="{DEEP}" fill-opacity=".35"/>
<path d="{tag}" fill="{WHITE}"/>
{dot}<path d="{rp}" fill="{MUTED}"/>
<path d="{title}" fill="{WHITE}"/>
{body}
{"".join(chips)}
</svg>''')


if __name__ == "__main__":
    hours_card(*commit_hours())
    for i, p in enumerate(PROJECTS):
        project_card(*p, wide=(i == 0))
