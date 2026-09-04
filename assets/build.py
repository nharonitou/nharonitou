"""Build the profile README artwork.

hero.svg   a pixel-art Acropolis at night: Parthenon, a Medusa bust with swaying
           snakes, a broken column, cypresses, the lights of Athens, a pixel moon.
intro.svg  the spinning pixel Earth (from earth.gif) beside a short description.

Both SVGs are self-contained: no fonts, scripts, or external images.
"""
import base64
import io
import math
import random
from pathlib import Path

from PIL import Image, ImageSequence

OUT = Path(__file__).resolve().parent
GIF = OUT / "earth.gif"

MONO = 'ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, "Liberation Mono", "DejaVu Sans Mono", monospace'

U = 4                      # pixel unit
FG, MUTED, BORDER, PANEL = "#e6edf3", "#8b949e", "#30363d", "#161b22"
SKY_TOP, SKY_MID, SKY_HORIZON = "#04060d", "#0a1430", "#182a5c"
GREEK_BLUE, GREEN, EARTH_BLUE, EARTH_GREEN = "#4d8ee6", "#3fb950", "#0000ff", "#00ff00"
MARBLE_LIGHT, MARBLE_MID, MARBLE_SHADOW = "#f4ead0", "#d9cca9", "#a99c7f"
TRIGLYPH, CELLA, TYMPANUM = "#5a5245", "#4a4338", "#3a3329"
STEP = ["#8f8467", "#b3a685", "#cbbf9f"]
ROCK, ROCK_TOP, ROCK_EDGE, ROCK_STRATA = "#2c2934", "#3d3946", "#1d1a24", "#36323f"
CLIFF_LIT, CLIFF_EDGE = "#5a5062", "#7a6f80"
FAR_HILL = "#0e1528"
CYPRESS, CYPRESS_LIGHT = "#0b2f22", "#155a3c"
FLOOD, CITY = "#ffcf6b", "#f6d78a"
MOON, MOON_CRATER = "#e9e6d6", "#c9c4ad"
SNAKE, SNAKE_HEAD = "#2f9e5a", "#8af0b0"

STYLE = f"""
@keyframes tw {{ 0%,100% {{ opacity:.18 }} 50% {{ opacity:1 }} }}
@keyframes cl {{ 0%,100% {{ opacity:.35 }} 50% {{ opacity:.95 }} }}
@keyframes glow {{ 0%,100% {{ opacity:.6 }} 50% {{ opacity:.9 }} }}
.s {{ animation: tw 3s ease-in-out infinite; }}
.c {{ animation: cl 4s ease-in-out infinite; }}
.g {{ animation: glow 7s ease-in-out infinite; }}
.px {{ image-rendering: pixelated; image-rendering: crisp-edges; }}
"""


def rect(x, y, w, h, fill, extra=""):
    return f'<rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" fill="{fill}"{extra}/>'


def earth_sheet():
    im = Image.open(GIF)
    frames = [f.convert("RGBA").copy() for f in ImageSequence.Iterator(im)]
    w, h = frames[0].size
    sheet = Image.new("RGBA", (w * len(frames), h), (0, 0, 0, 0))
    for i, f in enumerate(frames):
        sheet.paste(f, (i * w, 0))
    pal = sheet.convert("P", palette=Image.ADAPTIVE, colors=8, dither=Image.Dither.NONE)
    buf = io.BytesIO()
    pal.save(buf, "PNG", optimize=True)
    return base64.b64encode(buf.getvalue()).decode(), w, h, len(frames)


def earth(cx, cy, scale, halo_r):
    """The spinning Earth: every GIF frame on one sprite sheet, stepped through with SMIL."""
    b64, fw, fh, n = earth_sheet()
    xs = [-fw / 2 * scale - i * fw * scale for i in range(n)]
    return f'''<g transform="translate({cx},{cy})">
  <circle class="g" r="{halo_r}" fill="url(#halo)"/>
  <g clip-path="url(#earthframe)">
    <image class="px" image-rendering="optimizeSpeed" x="{xs[0]:g}" y="{-fh/2*scale:g}" width="{fw*n*scale:g}" height="{fh*scale:g}" href="data:image/png;base64,{b64}">
      <animate attributeName="x" values="{';'.join(f'{v:g}' for v in xs)}" dur="{n/10}s" calcMode="discrete" repeatCount="indefinite"/>
    </image>
  </g>
</g>''', f'<clipPath id="earthframe"><rect x="{-fw/2*scale:g}" y="{-fh/2*scale:g}" width="{fw*scale:g}" height="{fh*scale:g}"/></clipPath>'


def stars(n, w, h, avoid, seed=11, ymax=None):
    rng = random.Random(seed)
    out = []
    for _ in range(n):
        x, y = rng.randint(8, w - 8), rng.randint(6, ymax or h - 6)
        if any(f(x, y) for f in avoid):
            continue
        size = rng.choice([2, 2, 2, 3, 3, 4])
        style = f"animation-duration:{rng.uniform(1.8, 4.5):.2f}s;animation-delay:{-rng.uniform(0, 4.5):.2f}s"
        tint = rng.choice([FG, FG, FG, GREEK_BLUE, EARTH_GREEN])
        if size == 4:
            out.append(f'<g class="s" style="{style}">{rect(x-1, y-3, 2, 6, tint)}{rect(x-3, y-1, 6, 2, tint)}</g>')
        else:
            out.append(rect(x, y, size, size, tint, f' class="s" style="{style}"'))
    return "\n".join(out)


# ---------------------------------------------------------------- the Acropolis


def temple(cx, base_y):
    """Pixel Parthenon. Coordinates in units: x from the centre, y up from the base."""
    out = []

    def R(x, y, w, h, fill):
        out.append(rect(cx + x * U, base_y - (y + h) * U, w * U, h * U, fill))

    R(-48, 0, 96, 2, STEP[0]); R(-46, 2, 92, 2, STEP[1]); R(-44, 4, 88, 2, STEP[2])
    y0, col_h = 6, 20
    R(-40, y0, 80, col_h, CELLA)
    for i in range(8):
        x = -44 + i * 12
        R(x, y0, 2, col_h, MARBLE_LIGHT)
        R(x + 2, y0, 2, col_h, MARBLE_SHADOW)
        R(x - 1, y0 + col_h, 6, 2, MARBLE_LIGHT)
    y1 = y0 + col_h + 2
    R(-44, y1, 88, 3, MARBLE_MID)
    R(-44, y1 + 3, 88, 3, MARBLE_LIGHT)
    for x in range(-44, 44, 6):
        R(x, y1 + 3, 2, 3, TRIGLYPH)
    R(-46, y1 + 6, 92, 1, MARBLE_LIGHT)
    y2 = y1 + 7
    for r in range(13):
        w = 92 - r * 7
        R(-w / 2, y2 + r, w, 1, MARBLE_LIGHT)
        if 1 <= r < 12 and w > 6:
            R(-w / 2 + 2, y2 + r, w - 4, 1, TYMPANUM)
    return "\n".join(out)


SNAKES = [
    # (root x, root y above the head base, pixel offsets from the root going outward)
    (-3, 8, [(0, 0), (0, 1), (-1, 2), (-1, 3), (-2, 4)]),
    (-1, 8, [(0, 0), (0, 1), (0, 2), (-1, 3), (-1, 4)]),
    (1, 8, [(0, 0), (0, 1), (0, 2), (1, 3), (1, 4)]),
    (3, 8, [(0, 0), (0, 1), (1, 2), (1, 3), (2, 4)]),
    (-4, 6, [(0, 0), (-1, 0), (-2, 1), (-3, 1), (-4, 2)]),
    (4, 6, [(0, 0), (1, 0), (2, 1), (3, 1), (4, 2)]),
    (-4, 4, [(0, 0), (-1, 0), (-2, 0), (-3, -1), (-4, -1)]),
    (4, 4, [(0, 0), (1, 0), (2, 0), (3, -1), (4, -1)]),
    (-2, 8, [(0, 0), (-1, 1), (-2, 1), (-3, 2), (-3, 3)]),
    (2, 8, [(0, 0), (1, 1), (2, 1), (3, 2), (3, 3)]),
]


def medusa(cx, base_y):
    """A marble Medusa bust on a pedestal. The snakes sway, the eyes glow."""
    out = []

    def R(x, y, w, h, fill):
        out.append(rect(cx + x * U, base_y - (y + h) * U, w * U, h * U, fill))

    R(-6, 0, 12, 2, STEP[0]); R(-5, 2, 10, 1, STEP[1])            # pedestal
    R(-4, 3, 8, 6, MARBLE_MID); R(-3, 4, 6, 4, MARBLE_SHADOW)
    R(-5, 9, 10, 1, MARBLE_LIGHT)
    y = 10
    R(-5, y, 10, 3, MARBLE_LIGHT); R(2, y, 3, 3, MARBLE_SHADOW)     # shoulders
    R(-2, y + 3, 4, 2, MARBLE_MID)                                  # neck
    hy = y + 5
    for r, w in enumerate([6, 8, 8, 8, 8, 8, 8, 6]):                # head
        R(-w / 2, hy + r, w, 1, MARBLE_LIGHT)
        R(w / 2 - 2, hy + r, 2, 1, MARBLE_SHADOW)
    R(-1, hy + 2, 3, 1, TYMPANUM)                                   # mouth
    R(-3, hy + 5, 2, 1, TYMPANUM); R(1, hy + 5, 2, 1, TYMPANUM)     # brows
    eyes = rect(cx - 3 * U, base_y - (hy + 5) * U, 2 * U, U, EARTH_GREEN) + rect(cx + 1 * U, base_y - (hy + 5) * U, 2 * U, U, EARTH_GREEN)
    out.append(f'<g>{eyes}<animate attributeName="opacity" values="1;.35;1" dur="2.6s" repeatCount="indefinite"/></g>')
    rng = random.Random(9)
    for i, (rx, ry, pts) in enumerate(SNAKES):
        ry += hy
        px, py = cx + rx * U + U / 2, base_y - ry * U - U / 2
        body = "".join(
            rect(cx + (rx + dx) * U, base_y - (ry + dy + 1) * U, U, U, SNAKE_HEAD if j == len(pts) - 1 else SNAKE)
            for j, (dx, dy) in enumerate(pts)
        )
        amp = rng.choice([8, 10, 12])
        dur = rng.uniform(1.3, 2.1)
        out.append(
            f'<g><animateTransform attributeName="transform" type="rotate" values="{-amp} {px:g} {py:g};{amp} {px:g} {py:g};{-amp} {px:g} {py:g}" '
            f'keyTimes="0;.5;1" calcMode="spline" keySplines=".45 0 .55 1;.45 0 .55 1" dur="{dur:.2f}s" begin="{-rng.uniform(0, 2):.2f}s" repeatCount="indefinite"/>{body}</g>'
        )
    return "\n".join(out)


def broken_column(cx, base_y):
    out = []

    def R(x, y, w, h, fill):
        out.append(rect(cx + x * U, base_y - (y + h) * U, w * U, h * U, fill))

    R(-4, 0, 8, 2, STEP[1]); R(-3, 2, 6, 5, MARBLE_MID); R(1, 2, 2, 5, MARBLE_SHADOW)
    R(-3, 7, 4, 1, MARBLE_LIGHT); R(-3, 8, 2, 1, MARBLE_LIGHT)
    R(4, 0, 5, 2, MARBLE_SHADOW); R(5, 2, 3, 1, MARBLE_MID)         # a fallen drum
    return "\n".join(out)


def cypress(x, base_y, h_units, seed):
    rng = random.Random(seed)
    out = []
    for r in range(h_units):
        t = r / h_units
        w = max(1, round((1 - t) * 5 + rng.choice([0, 0, 1]) * (t < 0.8)))
        out.append(rect(x - (w * U) // 2, base_y - (r + 1) * U, w * U, U, CYPRESS))
        if w >= 3 and rng.random() < 0.35:
            out.append(rect(x - (w * U) // 2, base_y - (r + 1) * U, U, U, CYPRESS_LIGHT))
    return "\n".join(out)


def moon(cx, cy, r=9):
    out = [f'<circle class="g" cx="{cx}" cy="{cy}" r="{r*U*2.4:g}" fill="url(#moonhalo)"/>']
    for dy in range(-r, r + 1):
        hw = int(math.sqrt(r * r - dy * dy))
        out.append(rect(cx - hw * U, cy + dy * U, 2 * hw * U, U, MOON))
    for dx, dy, w in [(-4, -3, 2), (2, 1, 3), (-1, 4, 2), (4, -5, 1), (-6, 2, 1)]:
        out.append(rect(cx + dx * U, cy + dy * U, w * U, U, MOON_CRATER))
    return "\n".join(out)


PLATEAU = 38
LEDGES = [38, 37, 36, 32, 31, 30, 26, 25, 24, 22, 21, 20, 20, 20]   # cliff profile, one entry per column


def acropolis_top(xu):
    """Height in units: a flat top, sheer cliffs with ledges, then a scree slope to the city."""
    if 96 <= xu <= 228:
        return PLATEAU
    if 82 <= xu < 96:
        return LEDGES[96 - xu - 1]
    if 228 < xu <= 242:
        return LEDGES[xu - 228 - 1]
    if 34 <= xu < 82:
        return round(20 * ((xu - 34) / 48) ** 1.6)
    if 242 < xu <= 290:
        return round(20 * ((290 - xu) / 48) ** 1.6)
    return 0


def far_hills(xu):
    return 14 + round(6 * math.sin(xu / 17) + 4 * math.sin(xu / 7 + 2) + 3 * math.sin(xu / 3.1))


def ridge(W, H, top_fn, fill, top_fill=None, edge_fill=None, seed=3, jitter=1):
    rng = random.Random(seed)
    out = []
    for xu in range(0, W // U):
        h = top_fn(xu)
        if h <= 0:
            continue
        if h != PLATEAU and jitter:
            h = max(0, h + rng.choice(range(-jitter, jitter + 1)))
        top = H - h * U
        out.append(rect(xu * U, top, U, H - top, fill))
        if top_fill:
            out.append(rect(xu * U, top, U, U, top_fill))
        if edge_fill and rng.random() < 0.15:
            out.append(rect(xu * U, top + U, U, U, edge_fill))
    return "\n".join(out)


def rock(W, H, seed=3):
    """The Acropolis rock: strata, lit cliff faces, crevices, and shrubs on the scree."""
    rng = random.Random(seed)
    out = []
    for xu in range(0, W // U):
        h = acropolis_top(xu)
        if h <= 0:
            continue
        steep = 82 <= xu < 96 or 228 < xu <= 242                # the cliff ledges
        top = H - h * U
        out.append(rect(xu * U, top, U, H - top, ROCK))
        for row in range(h):                                   # strata bands and crevices
            y = top + row * U
            if row % 7 == 3 and rng.random() < 0.8:
                out.append(rect(xu * U, y, U, U, ROCK_STRATA))
            elif rng.random() < 0.05:
                out.append(rect(xu * U, y, U, U, ROCK_EDGE))
        if steep:                                              # floodlit cliff face
            out.append(rect(xu * U, top, U, min(6, h) * U, CLIFF_LIT))
            out.append(rect(xu * U, top, U, U, CLIFF_EDGE))
        else:
            out.append(rect(xu * U, top, U, U, ROCK_TOP))
        if not steep and h < PLATEAU and rng.random() < 0.10:  # shrubs on the slope
            w = rng.choice([2, 3])
            out.append(rect(xu * U, top - U, w * U, U, CYPRESS_LIGHT if rng.random() < .3 else CYPRESS))
            out.append(rect(xu * U + U, top - 2 * U, (w - 1) * U, U, CYPRESS))
    return "\n".join(out)


def city_lights(W, H, n, seed=5):
    rng = random.Random(seed)
    out = []
    for _ in range(n):
        x, y = rng.randint(4, W - 6), rng.randint(372, 412)
        if acropolis_top(x // U) * U > H - y + 2:
            continue
        style = f"animation-duration:{rng.uniform(2.5, 6):.2f}s;animation-delay:{-rng.uniform(0, 6):.2f}s"
        out.append(rect(x, y, 2, 2, CITY, f' class="c" style="{style}"'))
    return "\n".join(out)


def hero():
    W, H = 1200, 420
    plateau_y = H - PLATEAU * U
    temple_cx, statue_x, column_x, moon_x, moon_y = 650, 404, 900, 1010, 90
    avoid = [
        lambda x, y: (x - moon_x) ** 2 + (y - moon_y) ** 2 < 110**2,
        lambda x, y: 440 < x < 860 and y > 60,
        lambda x, y: 350 < x < 460 and y > 140,
    ]
    trees = "\n".join([
        cypress(190, H - acropolis_top(47) * U + 2, 9, 1),
        cypress(246, H - acropolis_top(61) * U + 2, 12, 2),
        cypress(290, H - acropolis_top(72) * U + 2, 13, 3),
        cypress(1000, H - acropolis_top(250) * U + 2, 13, 4),
        cypress(1048, H - acropolis_top(262) * U + 2, 11, 5),
        cypress(1096, H - acropolis_top(274) * U + 2, 8, 6),
    ])
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="The Acropolis at night">
<title>The Acropolis at night</title>
<style>{STYLE}</style>
<defs>
  <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="{SKY_TOP}"/><stop offset=".55" stop-color="{SKY_MID}"/><stop offset="1" stop-color="{SKY_HORIZON}"/>
  </linearGradient>
  <radialGradient id="moonhalo"><stop offset="0" stop-color="{MOON}" stop-opacity=".35"/><stop offset=".5" stop-color="{MOON}" stop-opacity=".08"/><stop offset="1" stop-color="{MOON}" stop-opacity="0"/></radialGradient>
  <radialGradient id="flood" cx=".5" cy="1" r=".5"><stop offset="0" stop-color="{FLOOD}" stop-opacity=".42"/><stop offset=".5" stop-color="{FLOOD}" stop-opacity=".12"/><stop offset="1" stop-color="{FLOOD}" stop-opacity="0"/></radialGradient>
  <clipPath id="card"><rect width="{W}" height="{H}" rx="16"/></clipPath>
</defs>
<g clip-path="url(#card)">
<rect width="{W}" height="{H}" fill="url(#sky)"/>
{stars(150, W, H, avoid, ymax=300)}
{moon(moon_x, moon_y)}
{ridge(W, H, far_hills, FAR_HILL, seed=8, jitter=0)}
<rect x="{temple_cx-460}" y="{plateau_y-320}" width="920" height="330" fill="url(#flood)"/>
{rock(W, H)}
{trees}
{temple(temple_cx, plateau_y + 2)}
{medusa(statue_x, plateau_y + 2)}
{broken_column(column_x, plateau_y + 2)}
{city_lights(W, H, 140)}
<g font-family='{MONO}'>
  <text x="60" y="84" font-size="30" font-weight="700" fill="{GREEK_BLUE}">Καλώς ήρθατε</text>
  <rect x="62" y="96" width="170" height="4" fill="{GREEK_BLUE}" opacity=".6"/>
</g>
</g>
</svg>
'''


# ---------------------------------------------------------------- the intro card

HEADLINE = "Python · APIs · GitOps · Kubernetes"
PILLS = ["K3s", "Flux", "Kyverno", "Flask", "FastAPI", "GitHub Actions", "Prometheus"]


def intro():
    W, H = 1200, 250
    ex, ey = 150, H / 2
    globe, frame = earth(ex, ey, 1.3, 150)
    avoid = [lambda x, y: (x - ex) ** 2 + (y - ey) ** 2 < 125**2, lambda x, y: 300 < x < 1150 and 80 < y < 190]
    pills = []
    x = 320
    for i, label in enumerate(PILLS):
        w = len(label) * 9.4 + 26
        colour = [GREEK_BLUE, GREEN][i % 2]
        pills.append(
            f'<rect x="{x}" y="148" width="{w:g}" height="32" rx="16" fill="{PANEL}" stroke="{BORDER}"/>'
            f'<text x="{x + w/2:g}" y="169" font-size="15" text-anchor="middle" fill="{colour}">{label}</text>'
        )
        x += w + 12
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="intro">
<title>intro</title>
<style>{STYLE}</style>
<defs>
  <radialGradient id="bg" cx="{ex}" cy="{ey}" r="900" gradientUnits="userSpaceOnUse">
    <stop offset="0" stop-color="{SKY_MID}"/><stop offset="1" stop-color="{SKY_TOP}"/>
  </radialGradient>
  <radialGradient id="halo"><stop offset="0" stop-color="{EARTH_BLUE}" stop-opacity=".55"/><stop offset=".55" stop-color="{GREEK_BLUE}" stop-opacity=".18"/><stop offset="1" stop-color="{GREEK_BLUE}" stop-opacity="0"/></radialGradient>
  {frame}
  <clipPath id="card"><rect width="{W}" height="{H}" rx="16"/></clipPath>
</defs>
<g clip-path="url(#card)">
<rect width="{W}" height="{H}" fill="url(#bg)"/>
{stars(90, W, H, avoid, seed=21)}
{globe}
<g font-family='{MONO}'>
  <text x="320" y="120" font-size="32" font-weight="700" fill="{FG}">{HEADLINE}</text>
  {"".join(pills)}
</g>
</g>
</svg>
'''


if __name__ == "__main__":
    for name, fn in (("hero.svg", hero), ("intro.svg", intro)):
        (OUT / name).write_text(fn())
        print(name, (OUT / name).stat().st_size)
