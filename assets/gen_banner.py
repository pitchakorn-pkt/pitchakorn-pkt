import random
random.seed(20260819)

W, H = 1000, 340
HZ = 250            # horizon line
out = []
a = out.append

a(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Pitchakorn - Embedded / AIoT Developer">')
a('''<defs>
  <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0%" stop-color="#07040A"/><stop offset="45%" stop-color="#130A1A"/>
    <stop offset="80%" stop-color="#2A1030"/><stop offset="100%" stop-color="#43163F"/>
  </linearGradient>
  <radialGradient id="hglow" cx="50%" cy="100%" r="70%">
    <stop offset="0%" stop-color="#FF7AC6" stop-opacity="0.55"/>
    <stop offset="45%" stop-color="#C77DFF" stop-opacity="0.18"/>
    <stop offset="100%" stop-color="#C77DFF" stop-opacity="0"/>
  </radialGradient>
  <linearGradient id="scrim" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0%" stop-color="#07040A" stop-opacity="0.94"/>
    <stop offset="42%" stop-color="#07040A" stop-opacity="0.62"/>
    <stop offset="75%" stop-color="#07040A" stop-opacity="0.12"/>
    <stop offset="100%" stop-color="#07040A" stop-opacity="0"/>
  </linearGradient>
  <linearGradient id="topfade" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0%" stop-color="#07040A" stop-opacity="0.85"/>
    <stop offset="100%" stop-color="#07040A" stop-opacity="0"/>
  </linearGradient>
  <linearGradient id="nameFill" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0%" stop-color="#FDF6FB"/><stop offset="70%" stop-color="#F0D9EC"/>
    <stop offset="100%" stop-color="#E9A8D9"/>
  </linearGradient>
  <linearGradient id="rule" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0%" stop-color="#FF7AC6"/><stop offset="100%" stop-color="#9B6BFF" stop-opacity="0.05"/>
  </linearGradient>
  <linearGradient id="streakP" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0%" stop-color="#FF7AC6" stop-opacity="0"/><stop offset="100%" stop-color="#FF7AC6" stop-opacity="0.95"/>
  </linearGradient>
  <linearGradient id="streakV" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0%" stop-color="#8FD8FF" stop-opacity="0.9"/><stop offset="100%" stop-color="#8FD8FF" stop-opacity="0"/>
  </linearGradient>
  <linearGradient id="road" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0%" stop-color="#1A0C1E"/><stop offset="100%" stop-color="#08050B"/>
  </linearGradient>
  <filter id="blurFar" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="1.6"/></filter>
  <filter id="soft" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="22"/></filter>
  <filter id="lamp" x="-200%" y="-200%" width="500%" height="500%"><feGaussianBlur stdDeviation="2.4"/></filter>
  <clipPath id="frame"><rect x="4" y="4" width="992" height="332" rx="22"/></clipPath>
  <style type="text/css"><![CDATA[
    @keyframes tw   { 0%,100%{opacity:.15} 50%{opacity:.8} }
    @keyframes win  { 0%,42%{opacity:.85} 50%,92%{opacity:.12} 100%{opacity:.85} }
    @keyframes bcn  { 0%,60%{opacity:1} 61%,100%{opacity:.08} }
    @keyframes carA { 0%{transform:translateX(-260px)} 100%{transform:translateX(1060px)} }
    @keyframes carB { 0%{transform:translateX(1060px)} 100%{transform:translateX(-260px)} }
    @keyframes hz   { 0%,100%{opacity:.8} 50%{opacity:1} }
    @keyframes blink{ 0%,49%{opacity:1} 50%,100%{opacity:0} }
    .tw{animation:tw 4s ease-in-out infinite}
    .hz{animation:hz 9s ease-in-out infinite}
    .carA{animation:carA 5.5s linear infinite}
    .carB{animation:carB 7.5s linear infinite}
    .cur{animation:blink 1.1s steps(1) infinite}
  ]]></style>
</defs>''')

a('<rect x="4" y="4" width="992" height="332" rx="22" fill="url(#sky)"/>')
a('<g clip-path="url(#frame)">')

# stars
for i in range(46):
    x, y = random.uniform(10, 990), random.uniform(12, 190)
    r = random.choice([0.7, 0.9, 1.1])
    if random.random() < .35:
        a(f'<circle class="tw" style="animation-delay:{random.uniform(0,4):.1f}s" cx="{x:.0f}" cy="{y:.0f}" r="{r}" fill="#E7D8F5" opacity=".4"/>')
    else:
        a(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r}" fill="#E7D8F5" opacity="{random.uniform(.12,.35):.2f}"/>')

a(f'<ellipse class="hz" cx="520" cy="{HZ+18}" rx="430" ry="130" fill="url(#hglow)"/>')

win_delay = lambda: f'{random.uniform(0, 9):.1f}s'
WCOL = ["#FF7AC6", "#C77DFF", "#E9A8D9", "#FFD1EC", "#8FD8FF"]

def skyline(y_base, hmin, hmax, wmin, wmax, fill, blur, win_step, win_alpha, lit_p, anim_p, gap=0):
    x = -30
    while x < W + 30:
        bw = random.uniform(wmin, wmax)
        bh = random.uniform(hmin, hmax)
        top = y_base - bh
        a(f'<rect x="{x:.0f}" y="{top:.0f}" width="{bw:.0f}" height="{bh+40:.0f}" fill="{fill}"'
          + (f' filter="url(#{blur})"' if blur else '') + '/>')
        # antenna + beacon on tall ones
        if bh > (hmax * .82) and not blur:
            ax = x + bw / 2
            a(f'<rect x="{ax:.0f}" y="{top-16:.0f}" width="1.6" height="16" fill="#3A2A42"/>')
            a(f'<circle cx="{ax:.1f}" cy="{top-18:.0f}" r="2.2" fill="#FF5FA8" filter="url(#lamp)"'
              f' style="animation:bcn 2.6s steps(1) infinite;animation-delay:{random.uniform(0,2.6):.1f}s"/>')
        # windows
        wy = top + 8
        while wy < y_base - 6:
            wx = x + 5
            while wx < x + bw - 5:
                if random.random() < lit_p:
                    c = random.choice(WCOL)
                    op = random.uniform(*win_alpha)
                    if random.random() < anim_p:
                        a(f'<rect class="w" x="{wx:.0f}" y="{wy:.0f}" width="3" height="4" fill="{c}"'
                          f' style="animation:win {random.uniform(5,11):.1f}s ease-in-out infinite;animation-delay:{win_delay()}" opacity="{op:.2f}"/>')
                    else:
                        a(f'<rect x="{wx:.0f}" y="{wy:.0f}" width="3" height="4" fill="{c}" opacity="{op:.2f}"/>')
                wx += win_step
            wy += win_step + 3
        x += bw + gap + random.uniform(1, 5)

skyline(HZ - 12, 55, 130, 34, 78, "#20112A", "blurFar", 11, (.20, .45), .30, .10)
skyline(HZ + 6,  70, 165, 40, 92, "#150B1D", None,      10, (.35, .75), .38, .16)
skyline(HZ + 26, 40, 105, 46, 104, "#0B0610", None,      10, (.45, .95), .30, .22)

# road
a(f'<rect x="0" y="{HZ+62}" width="{W}" height="{H-HZ-62}" fill="url(#road)"/>')
a(f'<rect x="0" y="{HZ+62}" width="{W}" height="1" fill="#5B2E58" opacity=".55"/>')
for cls, y, grad, h in (("carA", HZ + 70, "streakP", 2.4), ("carB", HZ + 78, "streakV", 1.8),
                        ("carA", HZ + 86, "streakP", 1.6)):
    d = random.uniform(0, 3)
    a(f'<rect class="{cls}" style="animation-delay:{d:.1f}s" x="0" y="{y}" width="230" height="{h}" rx="{h/2}" fill="url(#{grad})" opacity=".85"/>')

# scrims for text legibility
a(f'<rect x="0" y="0" width="{W}" height="{H}" fill="url(#scrim)"/>')
a(f'<rect x="0" y="0" width="{W}" height="120" fill="url(#topfade)"/>')
a('</g>')
a('<rect x="4.5" y="4.5" width="991" height="331" rx="22" fill="none" stroke="#3A2A42"/>')

# ---- foreground text ----
a('''<g font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">
  <text x="58" y="78" font-size="13" letter-spacing="5.5" fill="#C3A8D0">EMBEDDED · AIoT · EDGE</text>
</g>
<g font-family="Inter, 'Helvetica Neue', Helvetica, Arial, sans-serif">
  <text x="56" y="150" font-size="58" font-weight="700" letter-spacing="-1" fill="url(#nameFill)">Pitchakorn</text>
  <text x="58" y="192" font-size="17" fill="#CBB9D4">Computer Engineering @ RMUTT</text>
</g>
<rect x="58" y="216" width="180" height="3" rx="1.5" fill="url(#rule)"/>
<g transform="translate(600,54)">
  <rect x="0" y="0" width="346" height="170" rx="14" fill="#0C0711" fill-opacity="0.82" stroke="#4A3454"/>
  <circle cx="20" cy="20" r="4.5" fill="#FF7AC6" fill-opacity="0.85"/>
  <circle cx="36" cy="20" r="4.5" fill="#9B6BFF" fill-opacity="0.6"/>
  <circle cx="52" cy="20" r="4.5" fill="#3A2A42"/>
  <g font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" font-size="13.5">
    <text x="20" y="60"><tspan fill="#C77DFF">while</tspan><tspan fill="#A794B0"> (</tspan><tspan fill="#F0D9EC">awake</tspan><tspan fill="#A794B0">) {</tspan></text>
    <text x="20" y="86"><tspan fill="#A794B0">  </tspan><tspan fill="#E9A8D9">read</tspan><tspan fill="#A794B0">(sensor);</tspan></text>
    <text x="20" y="112"><tspan fill="#A794B0">  </tspan><tspan fill="#E9A8D9">publish</tspan><tspan fill="#A794B0">(broker);</tspan></text>
    <text x="20" y="138"><tspan fill="#A794B0">}</tspan><tspan fill="#FF7AC6"> // it ships</tspan></text>
  </g>
  <rect class="cur" x="133" y="128" width="8" height="13" fill="#FF7AC6"/>
</g>''')
a('</svg>')

open('/Users/panda/Documents/pitchakorn-pkt/assets/banner.svg', 'w').write('\n'.join(out))
print("elements:", len(out))
