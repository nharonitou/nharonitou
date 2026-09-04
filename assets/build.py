"""Build the profile README assets: hero.svg (space scene with the pixel Earth
and an orbiting ghost) and terminal.svg (self-typing terminal card).
Both SVGs are self-contained: no fonts, scripts, or external images."""
import base64
import io
import random
from pathlib import Path

from PIL import Image, ImageSequence

OUT = Path(__file__).resolve().parent
GIF = OUT / "earth.gif"

MONO = 'ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, "Liberation Mono", "DejaVu Sans Mono", monospace'

# GitHub dark palette plus the two colours the Earth GIF is drawn in.
BG0, BG1 = "#05070f", "#0b1530"
FG, MUTED, BORDER, PANEL = "#e6edf3", "#8b949e", "#30363d", "#161b22"
GREEN, BLUE, EARTH_GREEN, EARTH_BLUE = "#3fb950", "#58a6ff", "#00ff00", "#0000ff"


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


# 12 x 14 pixel ghost. '#' body, 'o' eye, '.' empty.
GHOST = [
    "....####....",
    "..########..",
    ".##########.",
    ".##########.",
    "###oo##oo###",
    "###oo##oo###",
    "############",
    "############",
    "############",
    "############",
    "############",
    "############",
    "##.###.###.#",
    "#...#...#..#",
]


def ghost_svg(px=3):
    rects = []
    for y, row in enumerate(GHOST):
        for x, c in enumerate(row):
            if c == ".":
                continue
            fill = FG if c == "#" else "#0d1117"
            rects.append(f'<rect x="{x*px}" y="{y*px}" width="{px}" height="{px}" fill="{fill}"/>')
    w, h = len(GHOST[0]) * px, len(GHOST) * px
    return f'<g transform="translate({-w/2},{-h/2})">{"".join(rects)}</g>'


def stars(n, w, h, seed=7):
    rng = random.Random(seed)
    out = []
    for i in range(n):
        x, y = rng.randint(8, w - 8), rng.randint(8, h - 8)
        # keep the planet's face clear
        if (x - 900) ** 2 / 190**2 + (y - 200) ** 2 / 180**2 < 1:
            continue
        size = rng.choice([2, 2, 2, 3, 3, 4])
        dur = round(rng.uniform(1.8, 4.5), 2)
        delay = round(-rng.uniform(0, 4.5), 2)
        tint = rng.choice([FG, FG, FG, BLUE, EARTH_GREEN])
        style = f"animation-duration:{dur}s;animation-delay:{delay}s"
        if size == 4:  # four-point pixel star
            out.append(
                f'<g class="s" style="{style}" fill="{tint}">'
                f'<rect x="{x-1}" y="{y-3}" width="2" height="6"/>'
                f'<rect x="{x-3}" y="{y-1}" width="6" height="2"/></g>'
            )
        else:
            out.append(f'<rect class="s" style="{style}" x="{x}" y="{y}" width="{size}" height="{size}" fill="{tint}"/>')
    return "\n".join(out)


def hero():
    b64, fw, fh, n = earth_sheet()
    W, H = 1200, 400
    cx, cy = 900, 200
    scale = 2
    xs = ";".join(str(-i * fw) for i in range(n))
    orbit_rx, orbit_ry = 210, 70
    orbit_dur = "11s"
    # left half of the ellipse first (goes over the top = behind the planet), then the bottom (in front)
    path = (
        f"M {-orbit_rx} 0 A {orbit_rx} {orbit_ry} 0 0 1 {orbit_rx} 0 "
        f"A {orbit_rx} {orbit_ry} 0 0 1 {-orbit_rx} 0"
    )
    ghost = ghost_svg()

    def ghost_pass(visible_first_half):
        vals = "1;0" if visible_first_half else "0;1"
        return (
            f'<g opacity="{1 if visible_first_half else 0}">'
            f'<animate attributeName="opacity" values="{vals}" keyTimes="0;0.5" calcMode="discrete" '
            f'dur="{orbit_dur}" repeatCount="indefinite"/>'
            f'<animateMotion dur="{orbit_dur}" repeatCount="indefinite" path="{path}"/>'
            f'<g transform="rotate(-12)">{ghost}</g></g>'
        )

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="nharonitou">
<title>nharonitou</title>
<style>
@keyframes tw {{ 0%,100% {{ opacity:.18 }} 50% {{ opacity:1 }} }}
@keyframes glow {{ 0%,100% {{ opacity:.55 }} 50% {{ opacity:.9 }} }}
.s {{ animation: tw 3s ease-in-out infinite; }}
.g {{ animation: glow 6s ease-in-out infinite; }}
.px {{ image-rendering: pixelated; image-rendering: crisp-edges; }}
</style>
<defs>
  <radialGradient id="bg" cx="{cx}" cy="{cy}" r="760" gradientUnits="userSpaceOnUse">
    <stop offset="0" stop-color="{BG1}"/><stop offset="1" stop-color="{BG0}"/>
  </radialGradient>
  <radialGradient id="halo"><stop offset="0" stop-color="{EARTH_BLUE}" stop-opacity=".55"/><stop offset=".55" stop-color="{BLUE}" stop-opacity=".18"/><stop offset="1" stop-color="{BLUE}" stop-opacity="0"/></radialGradient>
  <linearGradient id="bar" x1="0" x2="1"><stop offset="0" stop-color="{EARTH_BLUE}"/><stop offset="1" stop-color="{EARTH_GREEN}"/></linearGradient>
  <filter id="blur" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="8"/></filter>
  <clipPath id="frame"><rect x="{-fw/2*scale}" y="{-fh/2*scale}" width="{fw*scale}" height="{fh*scale}"/></clipPath>
</defs>
<rect width="{W}" height="{H}" rx="16" fill="url(#bg)"/>
{stars(110, W, H)}
<g transform="translate({cx},{cy})">
  <circle class="g" r="210" fill="url(#halo)"/>
  <g transform="rotate(12)">
    <ellipse rx="{orbit_rx}" ry="{orbit_ry}" fill="none" stroke="{BORDER}" stroke-width="1.5" stroke-dasharray="3 7"/>
    {ghost_pass(True)}
  </g>
  <g clip-path="url(#frame)">
    <image class="px" image-rendering="optimizeSpeed" x="{-fw/2*scale}" y="{-fh/2*scale}" width="{fw*n*scale}" height="{fh*scale}" href="data:image/png;base64,{b64}">
      <animate attributeName="x" values="{';'.join(str(-fw/2*scale + int(v)*scale) for v in xs.split(';'))}" dur="{n/10}s" calcMode="discrete" repeatCount="indefinite"/>
    </image>
  </g>
  <g transform="rotate(12)">{ghost_pass(False)}</g>
</g>
<g font-family='{MONO}'>
  <text x="80" y="188" font-size="68" font-weight="700" fill="{BLUE}" opacity=".45" filter="url(#blur)">nharonitou</text>
  <text x="80" y="188" font-size="68" font-weight="700" fill="{FG}"><tspan fill="{GREEN}">~$</tspan> nharonitou</text>
  <rect x="82" y="206" width="300" height="5" fill="url(#bar)"/>
  <text x="82" y="252" font-size="20" fill="{MUTED}">platform engineering · gitops · kubernetes · security</text>
  <text x="82" y="292" font-size="17" fill="{MUTED}" opacity=".8">the earth is <tspan fill="{EARTH_GREEN}">spinning</tspan>. clusters are <tspan fill="{GREEN}">green</tspan>.</text>
</g>
</svg>
'''


def terminal():
    W, H = 1200, 340
    fs = 20
    cw = 13          # generous per-character width for the typing clip
    x0, y0, lh = 28, 80, 32
    prompt = "~ $ "

    lines = [
        # (kind, text, start_s, type_s)
        ("cmd", "whoami", 0.4, 0.5),
        ("out", "nharonitou", 1.0, 0),
        ("cmd", "echo $STACK", 1.5, 0.8),
        ("out", "kubernetes · flux · gitops · python · ci/cd", 2.4, 0),
        ("cmd", "kubectl get planets -w", 2.9, 1.3),
        ("hdr", "NAME    STATUS     RESTARTS   AGE", 4.3, 0),
        ("row", "earth   Spinning   0          4.5e9y", 4.6, 0),
        ("end", "", 5.3, 0),
    ]
    body = []
    defs = []
    for i, (kind, text, start, dur) in enumerate(lines):
        y = y0 + i * lh
        if kind == "cmd":
            pw = len(prompt) * cw
            full = pw + len(text) * cw
            defs.append(
                f'<clipPath id="c{i}"><rect x="{x0}" y="{y-fs}" width="0" height="{lh}">'
                f'<animate attributeName="width" from="{pw}" to="{full}" begin="{start}s" dur="{dur}s" fill="freeze"/>'
                f'</rect></clipPath>'
            )
            body.append(
                f'<text x="{x0}" y="{y}" opacity="0" clip-path="url(#c{i})">'
                f'<set attributeName="opacity" to="1" begin="{start}s" fill="freeze"/>'
                f'<tspan fill="{GREEN}">{prompt}</tspan><tspan fill="{FG}">{esc(text)}</tspan></text>'
            )
        elif kind == "end":
            body.append(
                f'<text x="{x0}" y="{y}" opacity="0"><set attributeName="opacity" to="1" begin="{start}s" fill="freeze"/>'
                f'<tspan fill="{GREEN}">{prompt}</tspan></text>'
                f'<rect x="{x0 + len(prompt)*cw - 2}" y="{y - fs + 3}" width="11" height="{fs + 2}" fill="{FG}" opacity="0">'
                f'<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;.5;.5;1" dur="1.1s" begin="{start}s" repeatCount="indefinite"/>'
                f'</rect>'
            )
        else:
            colour = {"out": MUTED, "hdr": FG, "row": MUTED}[kind]
            t = esc(text)
            if kind == "row":
                t = t.replace("Spinning", f'<tspan fill="{BLUE}">Spinning</tspan>').replace("earth", f'<tspan fill="{EARTH_GREEN}">earth</tspan>')
            if kind == "out" and text == "nharonitou":
                colour = FG
            body.append(
                f'<text x="{x0}" y="{y}" fill="{colour}" opacity="0" xml:space="preserve">'
                f'<set attributeName="opacity" to="1" begin="{start}s" fill="freeze"/>{t}</text>'
            )

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="terminal">
<title>terminal</title>
<defs>{"".join(defs)}</defs>
<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="14" fill="#0d1117" stroke="{BORDER}"/>
<path d="M14.5 .5 H{W-14.5} A14 14 0 0 1 {W-.5} 14.5 V40 H.5 V14.5 A14 14 0 0 1 14.5 .5 Z" fill="{PANEL}"/>
<line x1=".5" y1="40.5" x2="{W-.5}" y2="40.5" stroke="{BORDER}"/>
<circle cx="24" cy="20" r="6" fill="#ff5f56"/><circle cx="44" cy="20" r="6" fill="#ffbd2e"/><circle cx="64" cy="20" r="6" fill="#27c93f"/>
<text x="{W/2}" y="25" text-anchor="middle" font-family='{MONO}' font-size="14" fill="{MUTED}">nharonitou@earth: ~</text>
<g font-family='{MONO}' font-size="{fs}" xml:space="preserve">
{chr(10).join(body)}
</g>
</svg>
'''


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


if __name__ == "__main__":
    (OUT / "hero.svg").write_text(hero())
    (OUT / "terminal.svg").write_text(terminal())
    for f in sorted(OUT.iterdir()):
        print(f.name, f.stat().st_size)
