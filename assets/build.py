"""Build hero.svg: a pixel-art Acropolis at night with the spinning Earth as the moon.
Self-contained: no fonts, scripts, or external images."""
import base64
import io
import random
from pathlib import Path

from PIL import Image, ImageSequence

OUT = Path(__file__).resolve().parent
GIF = OUT / "earth.gif"

MONO = 'ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, "Liberation Mono", "DejaVu Sans Mono", monospace'

W, H = 1200, 420
U = 4                      # pixel unit
FG, MUTED = "#e6edf3", "#8b949e"
SKY_TOP, SKY_MID, SKY_HORIZON = "#04060d", "#0a1430", "#182a5c"
GREEK_BLUE, EARTH_BLUE, EARTH_GREEN = "#4d8ee6", "#0000ff", "#00ff00"
MARBLE_LIGHT, MARBLE_MID, MARBLE_SHADOW = "#f4ead0", "#d9cca9", "#a99c7f"
TRIGLYPH, CELLA, TYMPANUM = "#5a5245", "#4a4338", "#3a3329"
STEP = ["#8f8467", "#b3a685", "#cbbf9f"]
ROCK, ROCK_TOP, ROCK_EDGE = "#262532", "#3a3846", "#1a1923"
FAR_HILL = "#0e1528"
CYPRESS, CYPRESS_LIGHT = "#0b2f22", "#155a3c"
FLOOD, CITY = "#ffcf6b", "#f6d78a"


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


def rect(x, y, w, h, fill, extra=""):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}"{extra}/>'


def temple(cx, base_y):
    """Pixel Parthenon. Coordinates in units: x from the centre, y up from the base."""
    out = []

    def R(x, y, w, h, fill):
        out.append(rect(cx + x * U, base_y - (y + h) * U, w * U, h * U, fill))

    # stylobate, three steps
    R(-48, 0, 96, 2, STEP[0]); R(-46, 2, 92, 2, STEP[1]); R(-44, 4, 88, 2, STEP[2])
    y0 = 6
    col_h = 20
    R(-40, y0, 80, col_h, CELLA)                       # cella wall behind the colonnade
    for i in range(8):                                 # eight Doric columns
        x = -44 + i * 12
        R(x, y0, 2, col_h, MARBLE_LIGHT)
        R(x + 2, y0, 2, col_h, MARBLE_SHADOW)
        R(x - 1, y0 + col_h, 6, 2, MARBLE_LIGHT)       # capital
    y1 = y0 + col_h + 2
    R(-44, y1, 88, 3, MARBLE_MID)                      # architrave
    R(-44, y1 + 3, 88, 3, MARBLE_LIGHT)                # frieze
    for x in range(-44, 44, 6):
        R(x, y1 + 3, 2, 3, TRIGLYPH)                   # triglyphs
    R(-46, y1 + 6, 92, 1, MARBLE_LIGHT)                # cornice
    y2 = y1 + 7
    for r in range(13):                                # pediment
        w = 92 - r * 7
        R(-w / 2, y2 + r, w, 1, MARBLE_LIGHT)
        if 1 <= r < 12 and w > 6:
            R(-w / 2 + 2, y2 + r, w - 4, 1, TYMPANUM)
    return "\n".join(out)


def cypress(x, base_y, h_units, seed):
    """A pixel cypress: narrow stacked rows, widest near the base."""
    rng = random.Random(seed)
    out = []
    for r in range(h_units):
        t = r / h_units                                # 0 at base, 1 at tip
        w = max(1, round((1 - t) * 5 + rng.choice([0, 0, 1]) * (t < 0.8)))
        out.append(rect(x - (w * U) // 2, base_y - (r + 1) * U, w * U, U, CYPRESS))
        if w >= 3 and rng.random() < 0.35:
            out.append(rect(x - (w * U) // 2, base_y - (r + 1) * U, U, U, CYPRESS_LIGHT))
    return "\n".join(out)


def ridge(top_fn, fill, top_fill=None, edge_fill=None, seed=3, jitter=1):
    """Fill everything below top_fn(x_unit) (in units from the bottom) column by column."""
    rng = random.Random(seed)
    out = []
    for xu in range(0, W // U):
        h = top_fn(xu)
        if h <= 0:
            continue
        if h != 38:                                    # keep the plateau flat under the temple
            h = max(0, h + rng.choice(range(-jitter, jitter + 1)))
        top = H - h * U
        out.append(rect(xu * U, top, U, H - top, fill))
        if top_fill:
            out.append(rect(xu * U, top, U, U, top_fill))
        if edge_fill and rng.random() < 0.15:
            out.append(rect(xu * U, top + U, U, U, edge_fill))
    return "\n".join(out)


def acropolis_top(xu):
    """Height (units) of the Acropolis rock: a plateau with stepped slopes."""
    plateau = 38
    if 96 <= xu <= 226:
        return plateau
    if 40 <= xu < 96:
        return round(plateau * ((xu - 40) / 56) ** 0.8)
    if 226 < xu <= 284:
        return round(plateau * ((284 - xu) / 58) ** 0.8)
    return 0


def far_hills(xu):
    import math
    return 14 + round(6 * math.sin(xu / 17) + 4 * math.sin(xu / 7 + 2) + 3 * math.sin(xu / 3.1))


def stars(n, seed=11):
    rng = random.Random(seed)
    out = []
    for _ in range(n):
        x, y = rng.randint(8, W - 8), rng.randint(6, 300)
        if (x - 1040) ** 2 / 150**2 + (y - 118) ** 2 / 140**2 < 1:   # keep the moon clear
            continue
        if 480 < x < 900 and y > 60:                                   # keep the temple clear
            continue
        size = rng.choice([2, 2, 2, 3, 3, 4])
        style = f"animation-duration:{rng.uniform(1.8, 4.5):.2f}s;animation-delay:{-rng.uniform(0, 4.5):.2f}s"
        tint = rng.choice([FG, FG, FG, GREEK_BLUE, EARTH_GREEN])
        if size == 4:
            out.append(f'<g class="s" style="{style}" fill="{tint}">{rect(x-1, y-3, 2, 6, tint)}{rect(x-3, y-1, 6, 2, tint)}</g>')
        else:
            out.append(rect(x, y, size, size, tint, f' class="s" style="{style}"'))
    return "\n".join(out)


def city_lights(n, seed=5):
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
    b64, fw, fh, n = earth_sheet()
    mx, my, scale = 1040, 118, 1.4
    frame_x = [-fw / 2 * scale - i * fw * scale for i in range(n)]
    temple_cx, plateau_y = 700, H - 38 * U
    trees = "\n".join([
        cypress(214, H - acropolis_top(53) * U + 2, 11, 1),
        cypress(262, H - acropolis_top(65) * U + 2, 14, 2),
        cypress(318, H - acropolis_top(79) * U + 2, 12, 3),
        cypress(956, H - acropolis_top(239) * U + 2, 13, 4),
        cypress(1004, H - acropolis_top(251) * U + 2, 10, 5),
        cypress(1052, H - acropolis_top(263) * U + 2, 8, 6),
    ])
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="nharonitou">
<title>nharonitou</title>
<style>
@keyframes tw {{ 0%,100% {{ opacity:.18 }} 50% {{ opacity:1 }} }}
@keyframes cl {{ 0%,100% {{ opacity:.35 }} 50% {{ opacity:.95 }} }}
@keyframes glow {{ 0%,100% {{ opacity:.6 }} 50% {{ opacity:.9 }} }}
.s {{ animation: tw 3s ease-in-out infinite; }}
.c {{ animation: cl 4s ease-in-out infinite; }}
.g {{ animation: glow 7s ease-in-out infinite; }}
.px {{ image-rendering: pixelated; image-rendering: crisp-edges; }}
</style>
<defs>
  <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="{SKY_TOP}"/><stop offset=".55" stop-color="{SKY_MID}"/><stop offset="1" stop-color="{SKY_HORIZON}"/>
  </linearGradient>
  <radialGradient id="moonhalo"><stop offset="0" stop-color="{EARTH_BLUE}" stop-opacity=".5"/><stop offset=".6" stop-color="{GREEK_BLUE}" stop-opacity=".15"/><stop offset="1" stop-color="{GREEK_BLUE}" stop-opacity="0"/></radialGradient>
  <radialGradient id="flood" cx=".5" cy="1" r=".5"><stop offset="0" stop-color="{FLOOD}" stop-opacity=".42"/><stop offset=".5" stop-color="{FLOOD}" stop-opacity=".12"/><stop offset="1" stop-color="{FLOOD}" stop-opacity="0"/></radialGradient>
  <linearGradient id="bar" x1="0" x2="1"><stop offset="0" stop-color="{GREEK_BLUE}"/><stop offset="1" stop-color="{FG}"/></linearGradient>
  <filter id="blur" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="8"/></filter>
  <clipPath id="frame"><rect x="{-fw/2*scale}" y="{-fh/2*scale}" width="{fw*scale}" height="{fh*scale}"/></clipPath>
  <clipPath id="card"><rect width="{W}" height="{H}" rx="16"/></clipPath>
</defs>
<g clip-path="url(#card)">
<rect width="{W}" height="{H}" fill="url(#sky)"/>
{stars(150)}
<g transform="translate({mx},{my})">
  <circle class="g" r="170" fill="url(#moonhalo)"/>
  <g clip-path="url(#frame)">
    <image class="px" image-rendering="optimizeSpeed" x="{frame_x[0]}" y="{-fh/2*scale}" width="{fw*n*scale}" height="{fh*scale}" href="data:image/png;base64,{b64}">
      <animate attributeName="x" values="{';'.join(f'{v:g}' for v in frame_x)}" dur="{n/10}s" calcMode="discrete" repeatCount="indefinite"/>
    </image>
  </g>
</g>
{ridge(far_hills, FAR_HILL, seed=8, jitter=0)}
<rect x="{temple_cx-460}" y="{plateau_y-320}" width="920" height="330" fill="url(#flood)"/>
{ridge(acropolis_top, ROCK, ROCK_TOP, ROCK_EDGE, seed=3)}
{trees}
{temple(temple_cx, plateau_y + 2)}
{city_lights(140)}
<g font-family='{MONO}'>
  <text x="60" y="118" font-size="60" font-weight="700" fill="{GREEK_BLUE}" opacity=".5" filter="url(#blur)">nharonitou</text>
  <text x="60" y="118" font-size="60" font-weight="700" fill="{FG}">nharonitou</text>
  <rect x="62" y="134" width="240" height="5" fill="url(#bar)"/>
  <text x="62" y="176" font-size="22" fill="{GREEK_BLUE}">Καλώς ήρθατε</text>
  <text x="62" y="206" font-size="16" fill="{MUTED}">platform engineering · gitops · kubernetes</text>
</g>
</g>
</svg>
'''


if __name__ == "__main__":
    (OUT / "hero.svg").write_text(hero())
    print("hero.svg", (OUT / "hero.svg").stat().st_size)
