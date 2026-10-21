"""Build the profile SVGs from room.jpg + logos/.

    pip install fonttools pillow
    python3 assets/tools/gen_assets.py

Writes into assets/: banner.svg, music.svg, stack.svg, title-*.svg.
Text is converted to paths, so every viewer sees the same font.
"""
import base64, io, random, re, urllib.request
from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from PIL import Image

TOOLS = Path(__file__).parent
OUT = TOOLS.parent
FONTS = {  # downloaded on first run, not committed
    "Fredoka": "https://github.com/google/fonts/raw/main/ofl/fredoka/Fredoka%5Bwdth,wght%5D.ttf",
    "JetBrainsMono": "https://github.com/google/fonts/raw/main/ofl/jetbrainsmono/JetBrainsMono%5Bwght%5D.ttf",
}
SONG = ("golden hour", "JVKE")

# sampled from room.jpg
BG = "#080F21"; PANEL = "#0E1730"; LINE = "#22305A"; WHITE = "#EEF0FF"; MUTED = "#8E9BC8"
BLUE = "#7E95FF"; DEEP = "#4A63D8"; MOON = "#F6D9BF"; BLUSH = "#F1A9B8"; WARM = "#FFD9A0"

_fonts = {}
def font(name, wght):
    key = (name, wght)
    if key not in _fonts:
        path = TOOLS / "fonts" / f"{name}.ttf"
        if not path.exists():
            path.parent.mkdir(exist_ok=True)
            urllib.request.urlretrieve(FONTS[name], path)
        f = TTFont(path)
        axes = {"wght": wght}
        if "wdth" in [a.axisTag for a in f["fvar"].axes]:
            axes["wdth"] = 100
        _fonts[key] = instantiateVariableFont(f, axes)
    return _fonts[key]

def text_path(s, x, y, size, name="Fredoka", wght=600, spacing=0.0, anchor="start"):
    """Return (svg path d, advance width) for s with baseline at y."""
    f = font(name, wght); gs = f.getGlyphSet(); cmap = f.getBestCmap()
    k = size / f["head"].unitsPerEm
    width = sum(f["hmtx"][cmap[ord(c)]][0] * k + spacing for c in s) - spacing
    if anchor == "middle": x -= width / 2
    pen = SVGPathPen(gs); cx = x
    for c in s:
        g = cmap[ord(c)]
        gs[g].draw(TransformPen(pen, (k, 0, 0, -k, cx, y)))
        cx += f["hmtx"][g][0] * k + spacing
    return pen.getCommands(), width

def write(name, body):
    (OUT / name).write_text(body)
    print(name, f"{len(body)/1024:.0f} KB")

def glow(id_, color):
    return (f'<radialGradient id="{id_}"><stop offset="0" stop-color="{color}" stop-opacity=".55"/>'
            f'<stop offset=".45" stop-color="{color}" stop-opacity=".18"/><stop offset="1" stop-color="{color}" stop-opacity="0"/></radialGradient>')

# ---------- banner ----------
def banner():
    im = Image.open(TOOLS / "room.jpg").convert("RGB")
    buf = io.BytesIO(); im.save(buf, "JPEG", quality=86, optimize=True, progressive=True)
    img = base64.b64encode(buf.getvalue()).decode()
    W, H = im.size
    rnd = random.Random(20261021)

    def drops(n, x0, x1, y0, y1, op):
        out = []
        for _ in range(n):
            x = rnd.uniform(x0, x1); y = rnd.uniform(y0, y1); L = rnd.uniform(20, 42)
            out.append(f'<line x1="{x:.0f}" y1="{y:.0f}" x2="{x-L*.16:.1f}" y2="{y+L:.0f}" stroke-opacity="{rnd.uniform(op*.45, op):.2f}" '
                       f'style="animation-duration:{rnd.uniform(.55,.9):.2f}s;animation-delay:{-rnd.uniform(0,1):.2f}s"/>')
        return "".join(out)

    def sparkles(pts):
        out = []
        for x, y, r in pts:
            out.append(f'<path class="tw" d="M{x} {y-r} Q{x} {y} {x+r} {y} Q{x} {y} {x} {y+r} Q{x} {y} {x-r} {y} Q{x} {y} {x} {y-r}Z" '
                       f'fill="{WHITE}" style="animation-delay:{-rnd.uniform(0,3):.2f}s"/>')
        return "".join(out)

    # window glass in room.jpg coordinates (measured on a grid overlay)
    pane_l = "990,40 1128,40 1128,330 1035,330 1035,250 990,250"
    pane_r = "1168,40 1430,40 1430,180 1380,190 1360,250 1300,280 1270,330 1168,330"

    name, _ = text_path("Pitchakorn", 96, 318, 124, wght=600)
    sub, _ = text_path("COMPUTER ENGINEERING @ RMUTT", 100, 404, 27, name="JetBrainsMono", wght=500, spacing=5.2)
    z = "".join(
        f'<path class="z" d="{text_path("z", 1395, 190, s, wght=700)[0]}" fill="{WHITE}" style="animation-delay:{d}s"/>'
        for s, d in ((26, 0), (34, -1.3), (42, -2.6)))
    drops_left = drops(110, 0, 900, -60, H, .28)
    drops_glass = drops(70, 985, 1435, -60, 330, .5)
    rain_layer = (f'<g class="rain" clip-path="url(#left)">{drops_left}</g>'
                  f'<g class="rain" clip-path="url(#glass)">{drops_glass}</g>')
    write("banner.svg", f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">
<style>
.rain line{{stroke:#C7D3FF;stroke-width:1.6;stroke-linecap:round;animation:fall .7s linear infinite}}
@keyframes fall{{from{{transform:translate(22px,-140px)}}to{{transform:translate(-22px,140px)}}}}
.pulse{{animation:pulse 4s ease-in-out infinite}}
.screen{{animation:pulse 2.6s ease-in-out infinite}}
.lamp{{animation:flick 6s steps(1) infinite}}
@keyframes pulse{{0%,100%{{opacity:.55}}50%{{opacity:1}}}}
@keyframes flick{{0%,100%{{opacity:.9}}47%{{opacity:.6}}49%{{opacity:.95}}51%{{opacity:.7}}53%{{opacity:.9}}}}
.tw{{transform-box:fill-box;transform-origin:center;animation:tw 3s ease-in-out infinite}}
@keyframes tw{{0%,100%{{opacity:.25;transform:scale(.6)}}50%{{opacity:1;transform:scale(1)}}}}
.z{{opacity:.85;animation:zz 3.9s ease-out infinite}}
@keyframes zz{{0%{{transform:translate(0,0);opacity:0}}20%{{opacity:.85}}100%{{transform:translate(-40px,-120px);opacity:0}}}}
@media (prefers-reduced-motion:reduce){{.rain line,.pulse,.screen,.lamp,.tw,.z{{animation:none}}}}
</style>
<defs>
{glow("gMoon", MOON)}{glow("gScreen", BLUE)}{glow("gNight", WARM)}{glow("gLamp", WARM)}
<linearGradient id="bar" x1="0" x2="1"><stop offset="0" stop-color="{BLUE}"/><stop offset="1" stop-color="{BLUE}" stop-opacity="0"/></linearGradient>
<clipPath id="glass"><polygon points="{pane_l}"/><polygon points="{pane_r}"/></clipPath>
<clipPath id="left"><rect width="920" height="{H}"/></clipPath>
</defs>
<rect width="{W}" height="{H}" fill="{BG}"/>
<image href="data:image/jpeg;base64,{img}" width="{W}" height="{H}"/>
{rain_layer}
<g style="mix-blend-mode:screen">
<circle class="pulse" cx="1236" cy="108" r="110" fill="url(#gMoon)"/>
<ellipse class="screen" cx="1500" cy="470" rx="300" ry="150" fill="url(#gScreen)"/>
<circle class="pulse" cx="1060" cy="308" r="70" fill="url(#gNight)" style="animation-delay:-1.5s"/>
<circle class="lamp" cx="1935" cy="305" r="90" fill="url(#gLamp)"/>
</g>
<g clip-path="url(#glass)">{sparkles([(1030, 75, 6), (1090, 160, 4), (1320, 70, 5), (1395, 120, 4), (1190, 210, 3.5)])}</g>
{sparkles([(140, 120, 5), (560, 90, 4), (760, 190, 3.5), (420, 560, 4), (820, 600, 3)])}
{z}
<path d="{name}" fill="{WHITE}"/>
<rect x="100" y="352" width="120" height="5" rx="2.5" fill="url(#bar)"/>
<path d="{sub}" fill="{MUTED}"/>
</svg>''')

# ---------- music card ----------
def music(title, artist):
    W, H = 620, 160; cx, cy, R = 92, 80, 56
    grooves = "".join(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{LINE}" stroke-width="1"/>' for r in range(26, R, 5))
    t, _ = text_path(title, 182, 82, 26, wght=600)
    a, _ = text_path(artist, 182, 108, 16, wght=400)
    lab, _ = text_path("NOW PLAYING", 182, 46, 11, name="JetBrainsMono", wght=600, spacing=2)
    rnd = random.Random(7); bars = []
    for i in range(18):
        bars.append(f'<rect x="{420 + i*10}" y="56" width="6" height="48" rx="3" fill="url(#eq)" '
                    f'style="animation-duration:{rnd.uniform(.6,1.1):.2f}s;animation-delay:{-rnd.uniform(0,1):.2f}s"/>')
    write("music.svg", f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">
<style>
.disc{{transform-origin:{cx}px {cy}px;animation:spin 5s linear infinite}}
.bars rect{{transform-box:fill-box;transform-origin:50% 100%;animation:eq 1s ease-in-out infinite alternate}}
@keyframes spin{{to{{transform:rotate(360deg)}}}}
@keyframes eq{{from{{transform:scaleY(.18)}}to{{transform:scaleY(1)}}}}
.prog{{transform-box:fill-box;transform-origin:0 50%;animation:prog 30s linear infinite}}
@keyframes prog{{from{{transform:scaleX(.1)}}to{{transform:scaleX(1)}}}}
@media (prefers-reduced-motion:reduce){{.disc,.bars rect,.prog{{animation:none}}}}
</style>
<defs><linearGradient id="eq" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="{DEEP}"/><stop offset="1" stop-color="#B8C4FF"/></linearGradient></defs>
<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="22" fill="{PANEL}" stroke="{LINE}" stroke-width="2"/>
<g class="disc">
<circle cx="{cx}" cy="{cy}" r="{R}" fill="#060B19"/>{grooves}
<path d="M{cx-40} {cy-22} A46 46 0 0 1 {cx-10} {cy-44}" stroke="#ffffff" stroke-opacity=".12" stroke-width="5" fill="none" stroke-linecap="round"/>
<circle cx="{cx-13}" cy="{cy-15}" r="7" fill="{WHITE}"/><circle cx="{cx+13}" cy="{cy-15}" r="7" fill="{WHITE}"/>
<circle cx="{cx}" cy="{cy}" r="21" fill="{WHITE}"/>
<circle cx="{cx-13}" cy="{cy-15}" r="3.2" fill="#C9CCE6"/><circle cx="{cx+13}" cy="{cy-15}" r="3.2" fill="#C9CCE6"/>
<path d="M{cx-10} {cy-3} q3 3 6 0 M{cx+4} {cy-3} q3 3 6 0" stroke="#1B2140" stroke-width="1.8" fill="none" stroke-linecap="round"/>
<ellipse cx="{cx}" cy="{cy+5}" rx="3.4" ry="2.4" fill="#1B2140"/>
<circle cx="{cx-12}" cy="{cy+6}" r="3.5" fill="{BLUSH}" opacity=".6"/><circle cx="{cx+12}" cy="{cy+6}" r="3.5" fill="{BLUSH}" opacity=".6"/>
</g>
<path d="{lab}" fill="{MUTED}"/>
<path d="{t}" fill="{WHITE}"/>
<path d="{a}" fill="{MUTED}"/>
<g class="bars">{"".join(bars)}</g>
<rect x="182" y="128" width="420" height="4" rx="2" fill="{LINE}"/>
<rect class="prog" x="182" y="128" width="420" height="4" rx="2" fill="{BLUE}"/>
</svg>''')

# ---------- tech stack: round buttons, one row per area ----------
# brand colours lifted where the original is too dark on navy
STACK = [
    ("EMBEDDED", [("c", "C", "#A8B9CC"), ("cplusplus", "C++", "#5B9BE0"), ("espressif", "ESP32", "#FF6A5E"),
                  ("arduino", "Arduino", "#2EC5CC"), ("raspberrypi", "Pi", "#E8577A"), ("nvidia", "Jetson", "#76B900"),
                  ("riscv", "RISC-V", "#F2B53A"), ("cmake", "CMake", "#4D8FD6")]),
    ("IOT · BACKEND", [("python", "Python", "#FFD43B"), ("fastapi", "FastAPI", "#1FBFAE"), ("postgresql", "PostgreSQL", "#6F95FF"),
                       ("timescale", "Timescale", "#FDB515"), ("redis", "Redis", "#FF4438"), ("mqtt", "MQTT", "#D65ED6"),
                       ("nodered", "Node-RED", "#E0544F"), ("docker", "Docker", "#2496ED")]),
    ("AI · TOOLS", [("opencv", "OpenCV", "#8F7CFF"), ("huggingface", "Hugging Face", "#FFD21E"), ("mysql", "MySQL", "#6FA6D6"),
                    ("javascript", "JavaScript", "#F7DF1E"), ("ollama", "Ollama", "#EEF0FF"), ("nextdotjs", "Next.js", "#EEF0FF"),
                    ("linux", "Linux", "#FCC624"), ("git", "Git", "#F05032")]),
]
def stack():
    cols, cw, rh, cap = 8, 104, 128, 34; W = cols * cw + 24
    H = len(STACK) * (rh + cap) + 8
    cells = []; i = 0
    for r, (title, items) in enumerate(STACK):
        top = r * (rh + cap)
        tp, _ = text_path(title, 20, top + 22, 12, name="JetBrainsMono", wght=600, spacing=2.4)
        cells.append(f'<path class="cap" d="{tp}" fill="{WHITE}"/><rect class="rule" x="20" y="{top+30}" width="{W-40}" height="1" fill="{LINE}"/>')
        for c, (slug, label, color) in enumerate(items):
            d = re.search(r' d="([^"]+)"', (TOOLS / "logos" / f"{slug}.svg").read_text()).group(1)
            cx = 12 + c * cw + cw / 2; cy = top + cap + 46
            lp, _ = text_path(label, cx, cy + 62, 14, wght=500, anchor="middle")
            cells.append(f'''<g class="b" style="animation-delay:{-i*0.37:.2f}s">
<circle cx="{cx}" cy="{cy+5}" r="34" fill="#050914"/>
<circle cx="{cx}" cy="{cy}" r="34" fill="#131E3D" stroke="#26366A" stroke-width="2"/>
<path d="M{cx-18} {cy-26} a30 30 0 0 1 22 -6" stroke="#ffffff" stroke-opacity=".16" stroke-width="4" fill="none" stroke-linecap="round"/>
<g transform="translate({cx-15} {cy-15}) scale(1.25)"><path d="{d}" fill="{color}"/></g>
<path class="lbl" d="{lp}" fill="{WHITE}"/></g>''')
            i += 1
    write("stack.svg", f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">
<style>
.b{{animation:bob 4s ease-in-out infinite}}
@keyframes bob{{0%,100%{{transform:translateY(0)}}50%{{transform:translateY(-3px)}}}}
@media (prefers-reduced-motion:reduce){{.b{{animation:none}}}}
</style>
{"".join(cells)}
</svg>''')

# ---------- section titles ----------
def title(slug, text):
    W, H = 420, 56
    tp, _ = text_path(text, W / 2, 38, 28, wght=600, anchor="middle")
    write(f"title-{slug}.svg", f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">
<path d="{tp}" fill="{WHITE}"/>
<rect x="{W/2-28}" y="48" width="56" height="3" rx="1.5" fill="{BLUE}"/>
</svg>''')

if __name__ == "__main__":
    banner()
    music(*SONG); stack()
    for slug, text in (("stack", "Tech Stack"), ("hours", "Coding Hours"), ("projects", "Projects")):
        title(slug, text)
