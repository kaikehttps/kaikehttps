"""Gera todos os SVGs do README do perfil (pasta assets/).

Uso, a partir da raiz do repositório:
    pip install -r scripts/requirements.txt
    python scripts/build_assets.py

Os textos dos cards (hero, experiência, stack, projetos, rodapé) ficam neste arquivo:
edite e rode de novo. Fontes (SIL OFL) e ícones (Simple Icons CC0 / Devicon MIT) são
baixados uma única vez para uma pasta de cache temporária. Créditos: assets/CREDITS.md.
"""
import argparse
import base64
import math
import os
import random
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from design import (C, LIGHT, T, Assets, Doc, card_frame, fx, glow_filter, gradient_border, live_dot,  # noqa: E402
                    pill, sparkle_path, stars, tile)

_ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
_ap.add_argument("--repo", default=os.path.dirname(HERE), help="raiz do repositório (padrão: pasta acima de scripts/)")
_ap.add_argument("--cache", default=os.path.join(tempfile.gettempdir(), "kaikehttps-readme-cache"))
_ap.add_argument("--shot", default=os.path.join(HERE, "source", "rotagas-dashboard.jpg"),
                 help="captura do painel do Rotagas embutida no card do projeto")
_ap.add_argument("--pylibs", default=None, help="pasta extra com fonttools/brotli, se não estiverem instalados")
_args = _ap.parse_args()
REPO, SHOT = _args.repo, _args.shot
A = Assets(_args.cache, _args.pylibs)
OUT = os.path.join(REPO, "assets")


def path(*p):
    return os.path.join(OUT, *p)


# =============================================================================== HERO
def hero(mobile=False):
    if not mobile:
        W, H, R_ = 846, 360, 22
        P, R = (622, 180), 86
        ring, orbit, tilt = (164, 31), (210, 54), -15
        tx = 46
    else:
        W, H, R_ = 420, 584, 22
        P, R = (210, 150), 64
        ring, orbit, tilt = (124, 24), (170, 42), -15
        tx = 28
    d = Doc(A, W, H, "Kaike Ferreira — desenvolvedor de software. Transformo ideias em produtos digitais, "
                     "da interface à inteligência artificial. Status: construindo a ApexVet e explorando IA.")
    cid = d.uid("clip")
    d.d(f'<clipPath id="{cid}"><rect width="{W}" height="{H}" rx="{R_}"/></clipPath>')
    d.d('<linearGradient id="sky" x1="0" y1="0" x2=".35" y2="1"><stop offset="0" stop-color="#0A0B14"/>'
        '<stop offset="1" stop-color="#040509"/></linearGradient>')
    k = 1 if not mobile else 0.62
    nebulae = [(P[0] - 30 * k, P[1] - 46 * k, 360 * k, "#7C3AED", .52), (P[0] + 170 * k, P[1] + 130 * k, 270 * k, "#2563EB", .36),
               (P[0] - 210 * k, P[1] - 150 * k, 190 * k, "#C026D3", .15), (P[0] + 40 * k, P[1] + 40 * k, 150 * k, "#4F46E5", .25)]
    for i, (x, y, r, c, o) in enumerate(nebulae):
        d.d(f'<radialGradient id="neb{i}" cx="{fx(x)}" cy="{fx(y)}" r="{fx(r)}" gradientUnits="userSpaceOnUse">'
            f'<stop offset="0" stop-color="{c}" stop-opacity="{o}"/><stop offset=".55" stop-color="{c}" stop-opacity="{fx(o * .32)}"/>'
            f'<stop offset="1" stop-color="{c}" stop-opacity="0"/></radialGradient>')
    d.d('<filter id="tex" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" '
        'baseFrequency=".010 .015" numOctaves="4" seed="11"/><feColorMatrix values="0 0 0 0 .66  0 0 0 0 .52  '
        '0 0 0 0 1  0 0 0 1.5 -.62"/></filter>')
    d.d(f'<radialGradient id="texr" cx="{fx(P[0])}" cy="{fx(P[1])}" r="{fx(330 * k + 40)}" gradientUnits="userSpaceOnUse">'
        '<stop offset="0" stop-color="#fff" stop-opacity=".95"/><stop offset="1" stop-color="#fff" stop-opacity="0"/>'
        f'</radialGradient><mask id="texm"><rect width="{W}" height="{H}" fill="url(#texr)"/></mask>')
    d.style("@keyframes breathe{0%,100%{opacity:.82}50%{opacity:1}}.breathe{animation:breathe 9s ease-in-out infinite}")
    d.add(f'<g clip-path="url(#{cid})"><rect width="{W}" height="{H}" fill="url(#sky)"/><g class="breathe">')
    for i in range(len(nebulae)):
        d.add(f'<rect width="{W}" height="{H}" fill="url(#neb{i})"/>')
    d.add(f'</g><rect width="{W}" height="{H}" filter="url(#tex)" mask="url(#texm)" opacity=".30"/>')
    stars(d, W, H, 175 if not mobile else 120, 21 if not mobile else 5, twinkle=26)
    # sparkles
    sp = [(468, 58, 6.5), (806, 300, 5), (790, 54, 4), (394, 326, 3.6), (240, 36, 3.2)] if not mobile else \
        [(54, 58, 5), (372, 250, 4.5), (360, 46, 3.6), (40, 268, 3.2)]
    gid = glow_filter(d, 2.6)
    d.style("@keyframes spk{0%,100%{transform:scale(.72);opacity:.65}50%{transform:scale(1.12);opacity:1}}"
            ".spk{transform-box:fill-box;transform-origin:center;animation:spk 5.5s ease-in-out infinite}")
    for i, (x, y, r) in enumerate(sp):
        delay = f"animation-delay:-{fx(i * 1.3)}s"
        d.add(f'<g class="spk" style="{delay}"><path d="{sparkle_path(x, y, r * 1.9)}" fill="#C7D2FE" opacity=".55" '
              f'filter="url(#{gid})"/><path d="{sparkle_path(x, y, r)}" fill="#F5F3FF"/></g>')
    # shooting star
    d.d('<linearGradient id="shg" x1="1" y1="0" x2="0" y2="0"><stop offset="0" stop-color="#fff"/>'
        '<stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>')
    sx, sy, dx, dy = (190, 22, 250, 104) if not mobile else (60, 20, 170, 70)
    d.style(f"@keyframes shoot{{0%{{transform:translate(0,0);opacity:0}}1.5%{{opacity:1}}"
            f"9%{{transform:translate({dx}px,{dy}px);opacity:0}}100%{{transform:translate({dx}px,{dy}px);opacity:0}}}}"
            f".shoot{{animation:shoot 11s linear infinite;animation-delay:3s}}")
    ang = math.degrees(math.atan2(dy, dx))
    d.add(f'<g class="shoot"><g transform="translate({sx} {sy}) rotate({fx(ang)})">'
          f'<rect x="-86" y="-.7" width="86" height="1.4" rx=".7" fill="url(#shg)"/>'
          f'<circle r="1.6" fill="#fff"/></g></g>')
    # ------------------------------------------------------------- planet system
    d.d('<radialGradient id="pl" cx=".33" cy=".28" r=".92"><stop offset="0" stop-color="#EEE8FF"/>'
        '<stop offset=".12" stop-color="#BBA3FB"/><stop offset=".36" stop-color="#7C3AED"/>'
        '<stop offset=".66" stop-color="#3A1A86"/><stop offset="1" stop-color="#0D0726"/></radialGradient>')
    d.d('<radialGradient id="shade" cx=".8" cy=".84" r="1"><stop offset="0" stop-color="#03020A" stop-opacity=".92"/>'
        '<stop offset=".55" stop-color="#03020A" stop-opacity=".42"/><stop offset="1" stop-color="#03020A" stop-opacity="0"/>'
        '</radialGradient>')
    d.d('<linearGradient id="rim" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#E0E7FF" stop-opacity=".95"/>'
        '<stop offset=".45" stop-color="#818CF8" stop-opacity=".35"/><stop offset="1" stop-color="#60A5FA" stop-opacity=".0"/>'
        '</linearGradient>')
    d.d(f'<radialGradient id="halo" cx="{P[0]}" cy="{P[1]}" r="{fx(R * 1.75)}" gradientUnits="userSpaceOnUse">'
        f'<stop offset=".5" stop-color="#8B5CF6" stop-opacity=".30"/><stop offset="1" stop-color="#8B5CF6" stop-opacity="0"/>'
        f'</radialGradient>')
    rx, ry = ring
    d.d(f'<linearGradient id="ringg" gradientUnits="userSpaceOnUse" x1="{-rx}" y1="0" x2="{rx}" y2="0">'
        '<stop offset="0" stop-color="#A78BFA" stop-opacity="0"/><stop offset=".18" stop-color="#A78BFA" stop-opacity=".85"/>'
        '<stop offset=".5" stop-color="#E0E7FF"/><stop offset=".82" stop-color="#60A5FA" stop-opacity=".85"/>'
        '<stop offset="1" stop-color="#60A5FA" stop-opacity="0"/></linearGradient>')
    d.d('<radialGradient id="moon" cx=".35" cy=".3" r=".8"><stop offset="0" stop-color="#F1F5FF"/>'
        '<stop offset=".6" stop-color="#9AA6C8"/><stop offset="1" stop-color="#3B4260"/></radialGradient>')
    d.d(f'<clipPath id="pc"><circle cx="{P[0]}" cy="{P[1]}" r="{R}"/></clipPath>')
    ag = glow_filter(d, 7 if not mobile else 5)
    tr = f'translate({P[0]} {P[1]}) rotate({tilt})'
    orx, ory = orbit

    def ring_half(front):
        a = (f"M{rx} 0A{rx} {ry} 0 0 1 {-rx} 0" if front else f"M{-rx} 0A{rx} {ry} 0 0 1 {rx} 0")
        s = 0.86
        b = (f"M{fx(rx * s)} 0A{fx(rx * s)} {fx(ry * s)} 0 0 1 {fx(-rx * s)} 0" if front
             else f"M{fx(-rx * s)} 0A{fx(rx * s)} {fx(ry * s)} 0 0 1 {fx(rx * s)} 0")
        o = (f"M{orx} 0A{orx} {ory} 0 0 1 {-orx} 0" if front else f"M{-orx} 0A{orx} {ory} 0 0 1 {orx} 0")
        return (f'<g transform="{tr}" fill="none"><path d="{o}" stroke="#A78BFA" stroke-opacity=".28" '
                f'stroke-dasharray="1.5 5"/><path d="{a}" stroke="url(#ringg)" stroke-width="12" stroke-opacity=".10"/>'
                f'<path d="{a}" stroke="url(#ringg)" stroke-width="2"/><path d="{b}" stroke="url(#ringg)" '
                f'stroke-width="1" stroke-opacity=".55"/></g>')

    def moon(front):
        vals = "1;0" if front else "0;1"
        return (f'<g transform="{tr}"><circle r="{6.5 if not mobile else 5}" fill="url(#moon)">'
                f'<animateMotion dur="28s" repeatCount="indefinite" path="M{orx} 0A{orx} {ory} 0 0 1 {-orx} 0'
                f'A{orx} {ory} 0 0 1 {orx} 0"/><animate attributeName="opacity" values="{vals}" keyTimes="0;.5" '
                f'calcMode="discrete" dur="28s" repeatCount="indefinite"/></circle></g>')

    d.add(f'<circle cx="{P[0]}" cy="{P[1]}" r="{fx(R * 1.75)}" fill="url(#halo)"/>')
    d.add(ring_half(False) + moon(False))
    d.add(f'<circle cx="{P[0]}" cy="{P[1]}" r="{R + 2}" fill="none" stroke="#7C9BFF" stroke-opacity=".45" '
          f'stroke-width="7" filter="url(#{ag})"/>')
    d.add(f'<circle cx="{P[0]}" cy="{P[1]}" r="{R}" fill="url(#pl)"/>')
    dr = fx(R * .16)
    d.style(f"@keyframes drift{{0%,100%{{transform:translateX(-{dr}px)}}50%{{transform:translateX({dr}px)}}}}"
            f".drift{{animation:drift 26s ease-in-out infinite}}")
    bands = [(-.62, .07, "#EDE9FE", .12), (-.36, .05, "#1E1B4B", .30), (-.12, .10, "#DDD6FE", .10),
             (.14, .06, "#1E1B4B", .34), (.36, .09, "#C4B5FD", .10), (.62, .07, "#1E1B4B", .30)]
    band_svg = "".join(f'<ellipse cx="0" cy="{fx(R * y)}" rx="{fx(R * 1.7)}" ry="{fx(R * h)}" fill="{c}" '
                       f'fill-opacity="{o}"/>' for y, h, c, o in bands)
    d.add(f'<g clip-path="url(#pc)"><g transform="{tr}"><g class="drift">{band_svg}</g></g>'
          f'<circle cx="{P[0]}" cy="{P[1]}" r="{R}" fill="url(#shade)"/></g>')
    d.add(f'<circle cx="{P[0]}" cy="{P[1]}" r="{R - .6}" fill="none" stroke="url(#rim)" stroke-width="1.3"/>')
    d.add(ring_half(True) + moon(True))
    # distant planet
    dp = (782, 98, 5.5) if not mobile else (360, 92, 4.2)
    d.d('<radialGradient id="dpl" cx=".35" cy=".3" r=".8"><stop offset="0" stop-color="#BFDBFE"/>'
        '<stop offset="1" stop-color="#1D4ED8"/></radialGradient>')
    d.add(f'<circle cx="{dp[0]}" cy="{dp[1]}" r="{fx(dp[2] * 2.6)}" fill="#3B82F6" opacity=".18" filter="url(#{gid})"/>'
          f'<circle cx="{dp[0]}" cy="{dp[1]}" r="{dp[2]}" fill="url(#dpl)"/>')
    # ------------------------------------------------------------- text
    d.d(f'<linearGradient id="ng" gradientUnits="userSpaceOnUse" x1="{tx}" y1="0" x2="{tx + (300 if not mobile else 250)}" '
        f'y2="0"><stop offset="0" stop-color="#EDE9FE"/><stop offset=".45" stop-color="#A78BFA"/>'
        f'<stop offset="1" stop-color="#60A5FA"/></linearGradient>')
    if not mobile:
        oy, n1, n2, fs, ph, phs, py = 92, 162, 234, 74, [270, 293], 16.5, 314
        phrase = ["Transformo ideias em produtos digitais,", "da interface à inteligência artificial."]
    else:
        oy, n1, n2, fs, ph, phs, py = 302, 362, 422, 60, [460, 483], 16, 512
        phrase = A.wrap("Transformo ideias em produtos digitais, da interface à inteligência artificial.",
                        W - 2 * tx, "SG", 500, 16)
        ph = [460 + 23 * i for i in range(len(phrase))]
        py = ph[-1] + 22
    d.add(f'<rect x="{tx}" y="{oy - 5}" width="18" height="1.4" fill="#60A5FA"/>')
    d.text(tx + 28, oy, "DESENVOLVEDOR DE SOFTWARE", "JBM", 500, 11.5, "#8DB0F7", ls=2.6)
    d.text(tx - 4, n1, "Kaike", "SG", 700, fs, "#F5F6FA", ls=-2)
    d.text(tx - 4, n2, "Ferreira", "SG", 700, fs, "url(#ng)", ls=-2)
    for y, line in zip(ph, phrase):
        d.text(tx, y, line, "SG", 500, phs, "#A9B1C3")
    status = "construindo a ApexVet · explorando IA"
    pw = A.width(status, "JBM", 500, 11.5) + 48
    d.add(f'<rect x="{tx}" y="{py}" width="{fx(pw)}" height="30" rx="15" fill="#60A5FA" fill-opacity=".07" '
          f'stroke="#60A5FA" stroke-opacity=".32"/>')
    live_dot(d, tx + 17, py + 15, "#38BDF8")
    d.text(tx + 32, py + 19.2, status, "JBM", 500, 11.5, "#C7D2FE")
    d.add("</g>")
    d.add(f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="{R_ - .5}" fill="none" stroke="#FFFFFF" '
          f'stroke-opacity=".07"/>')
    d.save(path("hero", "hero-mobile.svg" if mobile else "hero.svg"))


# =============================================================================== SECTION HEADERS
def header(name, over, title, sub=False):
    for light in (False, True):
        col = dict(C, **LIGHT) if light else C
        W, H = (600, 112) if not sub else (600, 96)
        d = Doc(A, W, H, title)
        cx = W / 2
        d.text(cx, 32, over, "JBM", 500, 11.5, col["b2"], anchor="middle", ls=3.2)
        d.text(cx, 78 if not sub else 70, title, "SG", 700, 36 if not sub else 27, col["text"], anchor="middle", ls=-.8)
        y = H - 10
        lg, rg = d.uid("l"), d.uid("r")
        vc, bc = (C["v3"], C["b3"]) if not light else ("#7C3AED", "#2563EB")
        d.d(f'<linearGradient id="{lg}"><stop offset="0" stop-color="{vc}" stop-opacity="0"/><stop offset="1" '
            f'stop-color="{vc}" stop-opacity=".9"/></linearGradient><linearGradient id="{rg}"><stop offset="0" '
            f'stop-color="{bc}" stop-opacity=".9"/><stop offset="1" stop-color="{bc}" stop-opacity="0"/></linearGradient>')
        span = 150 if not sub else 110
        d.add(f'<rect x="{fx(cx - span)}" y="{y - .6}" width="{span - 16}" height="1.2" fill="url(#{lg})"/>'
              f'<rect x="{fx(cx + 16)}" y="{y - .6}" width="{span - 16}" height="1.2" fill="url(#{rg})"/>')
        gid = glow_filter(d, 2.4)
        d.style("@keyframes rot{0%{transform:rotate(0) scale(.9)}50%{transform:rotate(45deg) scale(1.1)}"
                "100%{transform:rotate(90deg) scale(.9)}}.rot{transform-box:fill-box;transform-origin:center;"
                "animation:rot 7s ease-in-out infinite}")
        sc = "#C4B5FD" if not light else "#7C3AED"
        d.add(f'<g class="rot"><path d="{sparkle_path(cx, y, 10)}" fill="{sc}" opacity=".5" filter="url(#{gid})"/>'
              f'<path d="{sparkle_path(cx, y, 5.6)}" fill="{sc}"/></g>')
        d.save(path("sections", f"{name}{'-light' if light else ''}.svg"))


# =============================================================================== EXPERIENCE
def experience(name, over, title, role, desc, tags, accent, accent2, art, featured=False):
    W, H = 410, 300
    d = Doc(A, W, H, f"{title} — {role}. {desc}")
    card_frame(d, W, H, glow=accent, glow_pos=(.92, .05), seed=len(name) * 7, nstars=26)
    if featured:
        gradient_border(d, W, H, 18, accent, accent2)
    art(d)
    live_dot(d, 28, 36, accent)
    d.text(40, 40, over, "JBM", 500, 10.5, accent2, ls=1.7)
    d.text(24, 128, title, "SG", 700, 27, C["text"], ls=-.5)
    d.text(24, 154, role, "SG", 500, 14.5, accent)
    lines = A.wrap(desc, 360, "SG", 500, 13)
    d.lines(24, 188, lines, 20, fam="SG", wt=500, size=13, fill=C["text2"])
    x = 24
    for t in tags:
        x += pill(d, x, 252, t, accent2 if featured else accent) + 7
    d.save(path("experience", f"{name}.svg"))


def art_ui(d):
    x, y, w, h = 266, 24, 120, 82
    d.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="#0E121C" stroke="#283049"/>'
          f'<path d="M{x} {y + 18}H{x + w}" stroke="#283049"/>')
    for i, c in enumerate(("#F87171", "#FBBF24", "#34D399")):
        d.add(f'<circle cx="{x + 11 + i * 9}" cy="{y + 9}" r="2.3" fill="{c}" opacity=".6"/>')
    d.add(f'<rect x="{x + 10}" y="{y + 28}" width="44" height="7" rx="3.5" fill="{C["v2"]}" opacity=".7"/>'
          f'<rect x="{x + 10}" y="{y + 41}" width="98" height="4" rx="2" fill="#3A4258"/>'
          f'<rect x="{x + 10}" y="{y + 50}" width="76" height="4" rx="2" fill="#3A4258"/>'
          f'<rect x="{x + 10}" y="{y + 62}" width="34" height="12" rx="6" fill="{C["b3"]}" opacity=".85"/>'
          f'<rect x="{x + 50}" y="{y + 62}" width="34" height="12" rx="6" fill="none" stroke="#3A4258"/>')
    d.style("@keyframes blink{0%,49%{opacity:1}50%,100%{opacity:0}}.blink{animation:blink 1.1s step-end infinite}")
    d.add(f'<rect class="blink" x="{x + 56}" y="{y + 27}" width="1.6" height="9" fill="{C["b1"]}"/>')


def art_paw(d):
    pc = (340, 86)
    toes = [(round(pc[0] + 37 * math.sin(math.radians(a)), 1), round(pc[1] + 2 - 37 * math.cos(math.radians(a)), 1))
            for a in (-62, -21, 21, 62)]
    pad = [(323, 91), (331, 77), (349, 77), (357, 91), (349, 103), (331, 103)]
    gid = glow_filter(d, 2.2)
    pts = toes + pad
    lines = [(pad[i], pad[(i + 1) % len(pad)]) for i in range(len(pad))]
    d.add(f'<path d="M{pc[0] - 16} {pc[1] + 4}Q{pc[0]} {pc[1] - 10} {pc[0] + 16} {pc[1] + 4}" fill="none" '
          f'stroke="{C["v2"]}" stroke-opacity=".18"/>')
    d.add("".join(f'<path d="M{a[0]} {a[1]}L{b[0]} {b[1]}" stroke="{C["v2"]}" stroke-opacity=".38" stroke-width="1"/>'
                  for a, b in lines))
    d.add("".join(f'<circle cx="{x}" cy="{y}" r="6.5" fill="none" stroke="{C["v2"]}" stroke-opacity=".22"/>'
                  for x, y in toes))
    d.style("@keyframes tw{0%,100%{opacity:.35}50%{opacity:1}}.tw{animation:tw 4s ease-in-out infinite}")
    rnd = random.Random(4)
    for i, (x, y) in enumerate(pts):
        r = 2.6 if i < 4 else 1.9
        dl = f"animation-delay:-{fx(rnd.uniform(0, 4))}s"
        d.add(f'<g class="tw" style="{dl}"><circle cx="{x}" cy="{y}" r="{fx(r * 2.4)}" fill="{C["v1"]}" opacity=".45" '
              f'filter="url(#{gid})"/><circle cx="{x}" cy="{y}" r="{r}" fill="#F5F3FF"/></g>')
    d.text(386, 124, "constelação veterinária", "JBM", 500, 8.5, C["text4"], anchor="end", ls=.6)


# =============================================================================== STACK PANELS
def panel(name, idx, title, caption, keys, dim=False, accent=None):
    cols, size, top, pitch = 5, 62, 76, 94
    rows = math.ceil(len(keys) / cols)
    W = 410
    H = top + (rows - 1) * pitch + size + 22 + 18
    d = Doc(A, W, H, f"{title} — {caption}: " + ", ".join(T[k][0].replace(chr(10), ' ') for k in keys))
    card_frame(d, W, H, glow=accent or C["v3"], glow_pos=(.95, 0), seed=idx * 13, nstars=18)
    d.add(f'<rect x="22" y="23" width="3" height="18" rx="1.5" fill="{accent or C["v2"]}"/>')
    d.text(34, 38, title, "SG", 700, 17, C["text"])
    d.text(W - 22, 37, f"{idx:02d}", "JBM", 500, 11, C["text4"], anchor="end", ls=1)
    d.text(22, 60, caption, "SG", 500, 11.5, C["text3"])
    gap = (W - 40 - cols * size) / (cols - 1)
    for i, k in enumerate(keys):
        r, c = divmod(i, cols)
        tile(d, 20 + c * (size + gap), top + r * pitch, k, size, dim)
    d.save(path("stack", f"{name}.svg"))


# =============================================================================== API FLOW (POSTMAN)
METHOD = {"GET": "#6BDD9A", "POST": "#FFD166", "PUT": "#74AEF6", "DELETE": "#F79A8E"}


def api_request():
    W, H = 410, 300
    d = Doc(A, W, H, "Postman — requisições de exemplo com rotas reais da HelpDesk API: POST /login, "
                     "GET /chamados com token JWT e PUT /chamados/{id}.")
    card_frame(d, W, H, glow="#FF6C37", glow_pos=(.05, 0), seed=91, nstars=14)
    d.icon("si:postman", 22, 21, 22, "#FF6C37")
    d.text(52, 38, "Postman", "SG", 700, 17, C["text"])
    d.text(W - 22, 37, "REST · JWT", "JBM", 500, 10.5, C["text3"], anchor="end", ls=1)
    d.text(22, 61, "Rotas reais da HelpDesk API (Spring Boot)", "SG", 500, 11.5, C["text3"])
    rows = [("POST", "/login", "credenciais → token JWT no header"),
            ("GET", "/chamados", "Authorization: Bearer ‹token›"),
            ("PUT", "/chamados/{id}", "atualiza status e prioridade")]
    y = 78
    # flow rail with travelling packet
    d.add(f'<path d="M34 {y + 52}V{y + 64}M34 {y + 116}V{y + 128}" stroke="{C["line2"]}" stroke-width="1.5"/>')
    for i, (m, p, sub) in enumerate(rows):
        yy = y + i * 64
        d.add(f'<rect x="22" y="{yy}" width="{W - 44}" height="52" rx="12" fill="#0E1119" stroke="{C["line2"]}"/>')
        mc = METHOD[m]
        mw = A.width(m, "JBM", 500, 10.5, .6) + 16
        d.add(f'<rect x="34" y="{yy + 15}" width="{fx(mw)}" height="22" rx="6" fill="{mc}" fill-opacity=".12" '
              f'stroke="{mc}" stroke-opacity=".45"/>')
        d.text(34 + mw / 2, yy + 30, m, "JBM", 500, 10.5, mc, anchor="middle", ls=.6)
        d.text(34 + mw + 12, yy + 23, p, "JBM", 500, 12.5, C["text"])
        d.text(34 + mw + 12, yy + 40, sub, "SG", 500, 11, C["text3"])
        d.add(f'<g transform="translate({W - 50} {yy + 18})"><rect width="16" height="16" rx="5" fill="#FF6C37" '
              f'fill-opacity=".14"/><path d="M5.5 4.5l6 3.5-6 3.5z" fill="#FF6C37"/></g>')
    d.style("@keyframes pk{0%{transform:translateY(0);opacity:0}8%{opacity:1}92%{opacity:1}100%{transform:translateY(128px);"
            "opacity:0}}.pk{animation:pk 4.5s ease-in-out infinite}")
    d.add(f'<circle class="pk" cx="34" cy="{y + 2}" r="3" fill="#FF6C37"/>')
    d.text(22, H - 22, "montar → enviar → inspecionar → ajustar", "JBM", 500, 10, C["text4"], ls=.4)
    d.save(path("stack", "api-requisicao.svg"))


def api_validation():
    W, H = 410, 300
    items = [("Status HTTP", "2xx de sucesso, 401/403 e 404"),
             ("Autenticação", "token JWT e rotas protegidas"),
             ("Contrato da resposta", "corpo JSON coerente com os DTOs"),
             ("Perfis de acesso", "ADMIN · TÉCNICO · CLIENTE"),
             ("Erros de validação", "mensagens e campos obrigatórios")]
    d = Doc(A, W, H, "O que eu verifico ao testar uma API: " + "; ".join(f"{a} ({b})" for a, b in items))
    card_frame(d, W, H, glow=C["v3"], glow_pos=(.95, 0), seed=77, nstars=14)
    d.icon("c:check", 22, 21, 22, C["v2"])
    d.text(52, 38, "O que eu verifico", "SG", 700, 17, C["text"])
    d.text(W - 22, 37, "CHECKLIST", "JBM", 500, 10.5, C["text3"], anchor="end", ls=1)
    d.text(22, 61, "Pontos que confiro em cada endpoint", "SG", 500, 11.5, C["text3"])
    for i, (a, b) in enumerate(items):
        y = 92 + i * 41
        d.add(f'<circle cx="31" cy="{y - 4}" r="9" fill="{C["v3"]}" fill-opacity=".12" stroke="{C["v2"]}" '
              f'stroke-opacity=".5"/><path d="M27 {y - 4}l2.8 2.8 5-5.2" fill="none" stroke="{C["v1"]}" '
              f'stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>')
        d.text(50, y - 1, a, "SG", 700, 13, C["text"])
        d.text(50, y + 15, b, "JBM", 500, 10.5, C["text3"])
        if i < len(items) - 1:
            d.add(f'<path d="M50 {y + 25}H{W - 22}" stroke="{C["line"]}"/>')
    d.save(path("stack", "api-validacao.svg"))


# =============================================================================== PROJECTS
def tech_chips(d, x, y, keys, maxw, h=22, gap=6):
    cx, cy = x, y
    for k in keys:
        label, ik, col = T[k]
        w = A.width(label, "SG", 500, 10.5) + 12 + 7 + 9 + 8
        if cx + w > x + maxw:
            cx, cy = x, cy + h + gap
        if d is not None:
            d.add(f'<rect x="{fx(cx)}" y="{fx(cy)}" width="{fx(w)}" height="{h}" rx="{h / 2}" fill="#121521" '
                  f'stroke="{C["line2"]}"/>')
            d.icon(ik, cx + 8, cy + (h - 12) / 2, 12, col)
            d.text(cx + 8 + 12 + 6, cy + h / 2 + 3.8, label, "SG", 500, 10.5, C["text2"])
        cx += w + gap
    return cy + h


def caption(d, x, y, text, maxw=330, size=9.5, lh=14):
    lines = A.wrap(text, maxw, "JBM", 500, size)
    d.lines(x, y, lines, lh, fam="JBM", wt=500, size=size, fill=C["text4"])
    return len(lines)


def icon_row(d, x, y, keys, size=30, gap=8):
    for i, k in enumerate(keys):
        label, ik, col = T[k]
        xx = x + i * (size + gap)
        d.add(f'<rect x="{xx}" y="{y}" width="{size}" height="{size}" rx="9" fill="#121521" stroke="{C["line2"]}"/>')
        d.icon(ik, xx + size * .22, y + size * .22, size * .56, col)


def browser(d, x, y, w, h, url, img_b64):
    bar = 26
    cid = d.uid("bc")
    d.d(f'<clipPath id="{cid}"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12"/></clipPath>')
    gid = glow_filter(d, 18)
    d.add(f'<rect x="{x + 18}" y="{y + 26}" width="{w - 36}" height="{h - 30}" rx="16" fill="#7C3AED" opacity=".42" '
          f'filter="url(#{gid})"/>')
    d.add(f'<g clip-path="url(#{cid})"><rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#0B0D13"/>'
          f'<image href="data:image/jpeg;base64,{img_b64}" x="{x}" y="{y + bar}" width="{w}" height="{fx(w / 1.6)}" '
          f'preserveAspectRatio="xMidYMin slice"/><rect x="{x}" y="{y}" width="{w}" height="{bar}" fill="#11141D"/>'
          f'<path d="M{x} {y + bar}H{x + w}" stroke="{C["line2"]}"/></g>')
    for i, c in enumerate(("#F87171", "#FBBF24", "#34D399")):
        d.add(f'<circle cx="{x + 14 + i * 11}" cy="{y + 13}" r="3" fill="{c}" opacity=".75"/>')
    uw = A.width(url, "JBM", 500, 9.5) + 26
    ux = x + w / 2 - uw / 2
    d.add(f'<rect x="{fx(ux)}" y="{y + 6}" width="{fx(uw)}" height="14" rx="7" fill="#0B0D13" stroke="{C["line2"]}"/>')
    d.text(x + w / 2 + 5, y + 16.4, url, "JBM", 500, 9.5, C["text3"], anchor="middle")
    d.add(f'<circle cx="{fx(ux + 9)}" cy="{y + 13}" r="2.4" fill="none" stroke="{C["text3"]}" stroke-width="1"/>')
    d.add(f'<rect x="{x + .5}" y="{y + .5}" width="{w - 1}" height="{h - 1}" rx="11.5" fill="none" stroke="#2C3347"/>')


def featured_rotagas(mobile=False):
    img = base64.b64encode(open(SHOT, "rb").read()).decode()
    title_alt = ("Rotagas — SaaS para distribuidoras de gás: painel do gerente com mapa ao vivo, alertas operacionais, "
                 "cockpit comercial, app do motoboy e landing page, com dados simulados. React, TypeScript, Tailwind CSS, "
                 "Leaflet, Chart.js, Framer Motion e Vite.")
    keys = ["react", "ts", "tailwind", "leaflet", "chartjs", "framer", "vite"]
    desc = ("Painel do gerente com mapa ao vivo, alertas operacionais, cockpit comercial e app do motoboy — "
            "além da landing page do produto. Demonstração com dados simulados.")
    cap = "React · TypeScript · Tailwind · Leaflet · Chart.js · Framer Motion · Vite"
    head = ("PRODUTO · DEMO AO VIVO", "Rotagas", "SaaS para distribuidoras de gás")
    featured(mobile, "rotagas", title_alt, head, desc, keys, cap, "#34D399", "#86EFAC",
             lambda d, x, y, w, h: browser(d, x, y, w, h, "rotas-navy.vercel.app", img), (C["v3"], C["b3"]))


def featured(mobile, name, alt, head, desc, keys, cap, dot, over_col, visual, border, visual_h=(292, 242),
             title_size=(40, 36), square_dot=False):
    """Featured project card: text column + visual (desktop) / visual on top (mobile)."""
    over, title, sub = head
    if not mobile:
        W, H = 846, 344
        d = Doc(A, W, H, alt)
        card_frame(d, W, H, glow=border[0], glow_pos=(.75, .1), seed=len(name), nstars=30)
        gradient_border(d, W, H, 18, border[0], border[1], .8)
        x0 = 34
        mark(d, x0 + 4, 50, dot, square_dot)
        d.text(x0 + 16, 54, over, "JBM", 500, 10.5, over_col, ls=1.8)
        d.text(x0 - 2, 102, title, "SG", 700, title_size[0], C["text"], ls=-1)
        d.text(x0, 130, sub, "SG", 500, 15.5, C["v1"])
        lines = A.wrap(desc, 318, "SG", 500, 13.5)
        d.lines(x0, 164, lines, 21, fam="SG", wt=500, size=13.5, fill=C["text2"])
        iy = 164 + (len(lines) - 1) * 21 + 22
        icon_row(d, x0, iy, keys, size=30, gap=7)
        caption(d, x0, iy + 50, cap, maxw=330)
        visual(d, 392, 26, 426, visual_h[0])
    else:
        W = 410
        lines = A.wrap(desc, W - 48, "SG", 500, 13.5)
        caps = A.wrap(cap, W - 48, "JBM", 500, 9.5)
        y0 = 20 + visual_h[1] + 38
        dy = y0 + 96 + (len(lines) - 1) * 21
        H = dy + 22 + 30 + 20 + (len(caps) - 1) * 14 + 24
        d = Doc(A, W, H, alt)
        card_frame(d, W, H, glow=border[0], glow_pos=(.5, .1), seed=len(name), nstars=24)
        gradient_border(d, W, H, 18, border[0], border[1], .8)
        visual(d, 20, 20, W - 40, visual_h[1])
        mark(d, 28, y0 - 4, dot, square_dot)
        d.text(40, y0, over, "JBM", 500, 10.5, over_col, ls=1.8)
        d.text(22, y0 + 42, title, "SG", 700, title_size[1], C["text"], ls=-1)
        d.text(24, y0 + 68, sub, "SG", 500, 15, C["v1"])
        d.lines(24, y0 + 96, lines, 21, fam="SG", wt=500, size=13.5, fill=C["text2"])
        icon_row(d, 24, dy + 22, keys, size=30, gap=7)
        caption(d, 24, dy + 22 + 30 + 20, cap, maxw=W - 48)
    d.save(path("projects", f"{name}-mobile.svg" if mobile else f"{name}.svg"))


def mark(d, cx, cy, color, square=False):
    if square:
        d.add(f'<rect x="{cx - 4}" y="{cy - 4}" width="8" height="8" rx="2" fill="{color}"/>')
    else:
        live_dot(d, cx, cy, color)


def node(d, x, y, w, h, ik, col, title, sub, mono_title=True):
    d.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="#0F121B" stroke="{C["line2"]}"/>')
    d.add(f'<rect x="{x + 12}" y="{y + (h - 30) / 2}" width="30" height="30" rx="9" fill="{col}" fill-opacity=".12"/>')
    d.icon(ik, x + 18, y + (h - 18) / 2, 18, col)
    avail = w - 52 - 10
    if A.width(sub, "SG", 500, 10.5) <= avail:
        d.text(x + 52, y + h / 2 - 3, title, "JBM" if mono_title else "SG", 500, 11.5, C["text"])
        d.text(x + 52, y + h / 2 + 13, sub, "SG", 500, 10.5, C["text3"])
    else:
        d.text(x + 52, y + 22, title, "JBM" if mono_title else "SG", 500, 11.5, C["text"])
        d.lines(x + 52, y + 38, A.wrap(sub, avail, "SG", 500, 10)[:2], 13, fam="SG", wt=500, size=10, fill=C["text3"])


def featured_gameshelf(mobile=False):
    alt = ("GameShelf Ceará — monorepo full stack com catálogo, biblioteca pessoal e avaliações de jogos. "
           "Arquitetura: interface React com TanStack Query, API NestJS com JWT e refresh token rotativo, "
           "PostgreSQL via Prisma e CI no GitHub Actions com testes e2e via Testcontainers.")
    keys = ["ts", "nest", "react", "rq", "pg", "prisma", "docker", "actions"]
    desc = ("Catálogo, biblioteca pessoal e avaliações de jogos. API NestJS com JWT e refresh token rotativo, "
            "PostgreSQL via Prisma e testes e2e com Testcontainers rodando no CI.")
    cap = "TypeScript · NestJS · React · TanStack Query · PostgreSQL · Prisma · Docker · GitHub Actions"
    head = ("FULL STACK · MONOREPO", "GameShelf Ceará", "TypeScript de ponta a ponta")
    featured(mobile, "gameshelf", alt, head, desc, keys, cap, C["b2"], C["b1"],
             lambda d, x, y, w, h: arch(d, x, y, w, h), (C["b3"], C["v3"]), visual_h=(292, 292),
             title_size=(36, 32), square_dot=True)


def arch(d, x, y, w, h=286):
    """Architecture diagram: web -> api -> postgres + CI pipeline."""
    d.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" fill="#090B11" stroke="#252B3D"/>')
    # dotted grid
    pid = d.uid("dots")
    d.d(f'<pattern id="{pid}" width="14" height="14" patternUnits="userSpaceOnUse"><circle cx="1" cy="1" r=".8" '
        f'fill="#1F2536"/></pattern>')
    d.add(f'<rect x="{x + 1}" y="{y + 1}" width="{w - 2}" height="{h - 2}" rx="13" fill="url(#{pid})"/>')
    d.text(x + 16, y + 24, "ARQUITETURA", "JBM", 500, 9.5, C["text4"], ls=1.6)
    nw = (w - 32 - 34) / 2
    n1x, n2x, ny = x + 16, x + 16 + nw + 34, y + 40
    node(d, n1x, ny, nw, 62, "si:react", "#61DAFB", "apps/web", "React · TanStack Query")
    node(d, n2x, ny, nw, 62, "si:nestjs", "#EA2845", "apps/api", "NestJS · JWT + refresh")
    node(d, n2x, ny + 92, nw, 62, "si:postgresql", "#6E9BEA", "PostgreSQL", "Prisma · triggers")
    node(d, n1x, ny + 92, nw, 62, "si:swagger", "#85EA2D", "OpenAPI", "documentação Swagger")
    d.style("@keyframes flow{to{stroke-dashoffset:-20}}.flow{animation:flow 1.2s linear infinite}")
    ay = ny + 31
    d.add(f'<path class="flow" d="M{fx(n1x + nw + 4)} {ay}H{fx(n2x - 6)}" stroke="{C["b2"]}" stroke-width="1.6" '
          f'stroke-dasharray="4 6" fill="none"/><path d="M{fx(n2x - 10)} {ay - 4}l5 4-5 4" fill="none" '
          f'stroke="{C["b2"]}" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>')
    d.text(n1x + nw + 17, ay - 8, "HTTP", "JBM", 500, 8.5, C["text3"], anchor="middle")
    vx = n2x + nw / 2
    d.add(f'<path class="flow" d="M{fx(vx)} {ny + 66}V{ny + 86}" stroke="{C["v2"]}" stroke-width="1.6" '
          f'stroke-dasharray="4 6" fill="none"/>')
    d.add(f'<path class="flow" d="M{fx(n2x - 4)} {ny + 123}H{fx(n1x + nw + 6)}" stroke="{C["text4"]}" '
          f'stroke-width="1.3" stroke-dasharray="3 6" fill="none"/>')
    # CI pipeline
    cy = ny + 172
    d.add(f'<rect x="{x + 16}" y="{cy}" width="{w - 32}" height="58" rx="12" fill="#0F121B" stroke="{C["line2"]}"/>')
    d.icon("si:githubactions", x + 28, cy + 10, 16, "#3B95FF")
    d.text(x + 52, cy + 22, "CI · GitHub Actions", "JBM", 500, 10.5, C["text"])
    d.icon("si:docker", x + w - 44, cy + 9, 18, "#2496ED")
    d.text(x + w - 50, cy + 22, "Testcontainers", "JBM", 500, 9, C["text3"], anchor="end")
    steps = ["lint", "tipos", "testes", "e2e", "build"]
    sx = x + 28
    avail = w - 56
    sw = (avail - 4 * 14) / 5
    for i, s in enumerate(steps):
        xx = sx + i * (sw + 14)
        d.add(f'<rect x="{fx(xx)}" y="{cy + 32}" width="{fx(sw)}" height="18" rx="9" fill="{C["v3"]}" fill-opacity=".1" '
              f'stroke="{C["v2"]}" stroke-opacity=".35"/>')
        d.text(xx + sw / 2, cy + 44.5, s, "JBM", 500, 9.5, C["v1"], anchor="middle")
        if i < 4:
            d.add(f'<path d="M{fx(xx + sw + 4)} {cy + 41}h6" stroke="{C["text4"]}" stroke-width="1.2"/>')


# ----------------------------------------------------------------------------- compact cards + motifs
def motif_rings(d, W):
    cx, cy = 150, 61
    layers = [("interfaces", 50, C["b2"], .05, .35), ("infrastructure", 38, C["b3"], .06, .4),
              ("application", 26, C["v2"], .08, .55), ("domain", 14, C["v1"], .16, .9)]
    for _, r, c, fo, so in layers:
        d.add(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{c}" fill-opacity="{fo}" stroke="{c}" stroke-opacity="{so}"/>')
    d.style("@keyframes orb{to{transform:rotate(360deg)}}.orb{transform-origin:150px 61px;animation:orb 14s linear infinite}")
    d.add(f'<g class="orb"><circle cx="{cx + 50}" cy="{cy}" r="3" fill="{C["b1"]}"/></g>')
    for i, (lab, r, c, _, _) in enumerate(layers):
        yy = 34 + i * 18
        d.add(f'<circle cx="236" cy="{yy - 3.5}" r="3.5" fill="{c}"/>')
        d.text(248, yy, lab, "JBM", 500, 10, C["text2"])


def motif_tickets(d, W):
    gid = glow_filter(d, 10)
    d.add(f'<rect x="130" y="34" width="150" height="56" rx="12" fill="{C["v3"]}" opacity=".25" filter="url(#{gid})"/>')
    for i, (dx, dy, op) in enumerate([(26, 14, .35), (13, 24, .6), (0, 34, 1)]):
        x, y = 128 + dx, 18 + dy
        d.add(f'<g opacity="{op}"><rect x="{x}" y="{y}" width="156" height="58" rx="10" fill="#131725" '
              f'stroke="{C["line2"]}"/><circle cx="{x}" cy="{y + 29}" r="6" fill="#0B0D14"/>'
              f'<circle cx="{x + 156}" cy="{y + 29}" r="6" fill="#0B0D14"/></g>')
    x, y = 128, 52
    d.text(x + 16, y + 21, "chamado", "JBM", 500, 10.5, C["text"])
    d.add(f'<rect x="{x + 16}" y="{y + 31}" width="38" height="16" rx="8" fill="#F472B6" fill-opacity=".14" '
          f'stroke="#F472B6" stroke-opacity=".5"/>')
    d.text(x + 35, y + 42.5, "ALTA", "JBM", 500, 8.5, "#F9A8D4", anchor="middle")
    d.add(f'<rect x="{x + 60}" y="{y + 31}" width="72" height="16" rx="8" fill="{C["b2"]}" fill-opacity=".14" '
          f'stroke="{C["b2"]}" stroke-opacity=".5"/>')
    d.text(x + 96, y + 42.5, "ANDAMENTO", "JBM", 500, 8.5, C["b1"], anchor="middle")
    live_dot(d, x + 140, y + 17, C["cy"], r=3)


def motif_player(d, W):
    cx = 205
    rnd = random.Random(3)
    d.style("@keyframes eq{0%,100%{transform:scaleY(.3)}50%{transform:scaleY(1)}}"
            ".eq{transform-box:fill-box;transform-origin:center bottom;animation:eq 1.2s ease-in-out infinite}")
    for side in (-1, 1):
        for i in range(9):
            h = rnd.uniform(22, 54)
            x = cx + side * (52 + i * 11) - (6 if side < 0 else 0)
            col = C["v2"] if i % 2 else C["b2"]
            dl = f"animation-delay:-{fx(rnd.uniform(0, 1.2))}s;animation-duration:{fx(rnd.uniform(.9, 1.6))}s"
            d.add(f'<rect class="eq" style="{dl}" x="{fx(x)}" y="{fx(92 - h)}" width="6" height="{fx(h)}" rx="3" '
                  f'fill="{col}" opacity="{fx(.85 - i * .07)}"/>')
    d.add(f'<rect x="{cx - 34}" y="14" width="68" height="96" rx="12" fill="#0E1119" stroke="{C["line2"]}"/>')
    ag = d.uid("al")
    d.d(f'<linearGradient id="{ag}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{C["v3"]}"/>'
        f'<stop offset="1" stop-color="{C["b3"]}"/></linearGradient>')
    d.add(f'<rect x="{cx - 24}" y="24" width="48" height="40" rx="7" fill="url(#{ag})"/>'
          f'<rect x="{cx - 24}" y="72" width="48" height="3" rx="1.5" fill="#2A3147"/>'
          f'<rect x="{cx - 24}" y="72" width="28" height="3" rx="1.5" fill="{C["v1"]}"/>'
          f'<circle cx="{cx}" cy="92" r="8" fill="#F5F5F7"/><path d="M{cx - 2.5} 88.5v7l6-3.5z" fill="#0E1119"/>')


def motif_boxes(d, W):
    def cube(x, y, s, top, left, right, op=1):
        h = s * .58
        d.add(f'<g opacity="{op}"><path d="M{x} {y}l{s} {-h}l{s} {h}l{-s} {h}z" fill="{top}"/>'
              f'<path d="M{x} {y}l{s} {h}v{s * 1.05}l{-s} {-h}z" fill="{left}"/>'
              f'<path d="M{x + 2 * s} {y}l{-s} {h}v{s * 1.05}l{s} {-h}z" fill="{right}"/></g>')
    cube(96, 52, 26, "#8B7CF6", "#4C3A9E", "#33276E")
    cube(148, 52, 26, "#6CA6F7", "#2D5DAA", "#1E3F78")
    cube(122, 30, 26, "#B3A1FB", "#5B45B8", "#3E2E85", )
    bars = [("A-01", .82, C["v2"]), ("B-07", .46, C["b2"]), ("C-12", .64, C["v2"]), ("D-03", .18, "#F472B6")]
    for i, (lab, v, c) in enumerate(bars):
        y = 30 + i * 18
        d.text(232, y + 4, lab, "JBM", 500, 9, C["text3"])
        d.add(f'<rect x="266" y="{y - 4}" width="96" height="6" rx="3" fill="#1F2536"/>'
              f'<rect x="266" y="{y - 4}" width="{fx(96 * v)}" height="6" rx="3" fill="{c}"/>')
    d.text(232, 104, "nível de estoque", "JBM", 500, 9, C["text4"], ls=.4)


def compact_height(desc, keys, W=410):
    lines = A.wrap(desc, W - 44, "SG", 500, 12.5)
    return tech_chips(None, 22, 184 + len(lines) * 19 - 4, keys, W - 44) + 22


def compact(name, title, desc, keys, motif, alt, H=None):
    W = 410
    H = H or compact_height(desc, keys)
    d = Doc(A, W, H, alt)
    cid = card_frame(d, W, H, glow=C["v3"], glow_pos=(.5, 0), seed=len(name) * 5, nstars=10)
    # cover band
    cb = d.uid("cb")
    d.d(f'<linearGradient id="{cb}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#111526"/>'
        f'<stop offset="1" stop-color="#0B0D15"/></linearGradient>')
    pid = d.uid("dots")
    d.d(f'<pattern id="{pid}" width="16" height="16" patternUnits="userSpaceOnUse"><circle cx="1" cy="1" r=".8" '
        f'fill="#20263A"/></pattern>')
    d.add(f'<g clip-path="url(#{cid})"><rect width="{W}" height="122" fill="url(#{cb})"/>'
          f'<rect width="{W}" height="122" fill="url(#{pid})"/>')
    motif(d, W)
    d.add(f'<path d="M0 122H{W}" stroke="{C["line2"]}"/></g>')
    # repo hint, aligned with the title row
    hint = "código ↗"
    hw = A.width(hint, "JBM", 500, 9, .9) + 20
    rw = pill(d, W - 22 - hw, 143, hint, C["b1"], h=20, size=9, fill_op=.08, stroke_op=.3, upper=False)
    d.text(22, 158, title, "SG", 700, 20, C["text"], ls=-.3)
    lines = A.wrap(desc, W - 44, "SG", 500, 12.5)
    d.lines(22, 184, lines, 19, fam="SG", wt=500, size=12.5, fill=C["text2"])
    tech_chips(d, 22, 184 + len(lines) * 19 - 4, keys, W - 44)
    d.save(path("projects", f"{name}.svg"))
    return rw


# =============================================================================== BUTTONS
def button(name, key, label, sub, w=200, h=58, sub_size=10):
    lab, ik, col = T[key] if key in T else (label, key, C["text"])
    d = Doc(A, w, h, f"{label}: {sub}")
    card_frame(d, w, h, r=14, glow=col, glow_pos=(0, .5), nstars=0)
    d.add(f'<rect x="12" y="{(h - 34) / 2}" width="34" height="34" rx="10" fill="{col}" fill-opacity=".12"/>')
    d.icon(ik, 19, (h - 20) / 2, 20, col)
    d.text(56, h / 2 - 3, label, "SG", 700, 14, C["text"])
    d.text(56, h / 2 + 13, sub, "JBM", 500, sub_size, C["text3"])
    d.icon("c:arrow", w - 26, 10, 14, C["text4"])
    d.save(path("buttons", f"{name}.svg"))


def link_button(name, ik, col, label, w=196, h=44):
    d = Doc(A, w, h, label)
    card_frame(d, w, h, r=12, glow=col, glow_pos=(0, .5), nstars=0)
    d.icon(ik, 16, (h - 16) / 2, 16, col)
    d.text(42, h / 2 + 4.5, label, "SG", 700, 13, C["text"])
    d.icon("c:arrow", w - 26, (h - 13) / 2, 13, C["text3"])
    d.save(path("buttons", f"{name}.svg"))


# =============================================================================== FOOTER
def footer(mobile=False):
    W, H = (846, 210) if not mobile else (420, 236)
    d = Doc(A, W, H, "Curioso por natureza, construtor por escolha. — Kaike Ferreira (@kaikehttps)")
    cid = d.uid("clip")
    d.d(f'<clipPath id="{cid}"><rect width="{W}" height="{H}" rx="20"/></clipPath>')
    d.d('<linearGradient id="fsky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#05060A"/>'
        '<stop offset="1" stop-color="#0B0D18"/></linearGradient>')
    d.add(f'<g clip-path="url(#{cid})"><rect width="{W}" height="{H}" fill="url(#fsky)"/>')
    stars(d, W, H - 40, 90 if not mobile else 60, 33, twinkle=14)
    R = 1400 if not mobile else 700
    cx, cy = W / 2, H - 46 + R
    d.d(f'<radialGradient id="atm" cx="{fx(cx)}" cy="{fx(H - 46)}" r="{fx(W * .55)}" gradientUnits="userSpaceOnUse">'
        f'<stop offset="0" stop-color="#7C3AED" stop-opacity=".55"/><stop offset=".5" stop-color="#3B82F6" stop-opacity=".16"/>'
        f'<stop offset="1" stop-color="#3B82F6" stop-opacity="0"/></radialGradient>')
    d.add(f'<rect width="{W}" height="{H}" fill="url(#atm)"/>')
    d.d('<linearGradient id="hz" x1="0" x2="1"><stop offset="0" stop-color="#60A5FA" stop-opacity="0"/>'
        '<stop offset=".3" stop-color="#A78BFA"/><stop offset=".5" stop-color="#F5F3FF"/><stop offset=".7" '
        'stop-color="#60A5FA"/><stop offset="1" stop-color="#60A5FA" stop-opacity="0"/></linearGradient>')
    gid = glow_filter(d, 5)
    d.add(f'<circle cx="{fx(cx)}" cy="{fx(cy)}" r="{R}" fill="#06070C"/>'
          f'<circle cx="{fx(cx)}" cy="{fx(cy)}" r="{R}" fill="none" stroke="url(#hz)" stroke-width="6" '
          f'stroke-opacity=".55" filter="url(#{gid})"/>'
          f'<circle cx="{fx(cx)}" cy="{fx(cy)}" r="{R}" fill="none" stroke="url(#hz)" stroke-width="1.4"/></g>')
    if not mobile:
        d.text(W / 2, 84, "Curioso por natureza, construtor por escolha.", "SG", 700, 27, C["text"], anchor="middle",
               ls=-.5)
        d.text(W / 2, 114, "KAIKE FERREIRA  ·  @KAIKEHTTPS", "JBM", 500, 10.5, C["text3"], anchor="middle", ls=2.6)
    else:
        d.text(W / 2, 74, "Curioso por natureza,", "SG", 700, 25, C["text"], anchor="middle", ls=-.5)
        d.text(W / 2, 106, "construtor por escolha.", "SG", 700, 25, C["text"], anchor="middle", ls=-.5)
        d.text(W / 2, 136, "KAIKE FERREIRA · @KAIKEHTTPS", "JBM", 500, 10, C["text3"], anchor="middle", ls=2)
    d.add(f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="19.5" fill="none" stroke="#fff" stroke-opacity=".07"/>')
    d.save(path("footer", "footer-mobile.svg" if mobile else "footer.svg"))


# =============================================================================== RUN
def main():
    hero()
    hero(mobile=True)
    for args in [("sobre", "01 · QUEM SOU", "Sobre mim"), ("experiencia", "02 · TRAJETÓRIA", "Experiência"),
                 ("stack", "03 · FERRAMENTAS", "Stack & ferramentas"), ("projetos", "04 · VITRINE", "Projetos em destaque"),
                 ("atividade", "05 · GITHUB", "Atividade no GitHub"), ("contato", "06 · CONEXÃO", "Vamos conversar?")]:
        header(*args)
    header("apis", "03.1 · POSTMAN", "Como eu valido APIs", sub=True)

    experience("ottolog", "EXPERIÊNCIA ATUAL", "Ottolog Express", "Desenvolvedor Frontend",
               "Desenvolvimento de interfaces e soluções para as aplicações da empresa.",
               ["Frontend", "Interfaces", "Aplicações"], C["b2"], C["b1"], art_ui)
    experience("apexvet", "STARTUP · FUNDADOR", "ApexVet", "Fundador & Tech Lead",
               "Startup que desenvolve tecnologia para modernizar a gestão veterinária, explorando inteligência "
               "artificial para facilitar a rotina dos profissionais.",
               ["Gestão veterinária", "IA aplicada", "Tech Lead"], C["v2"], C["v1"], art_paw, featured=True)

    panel("interface", 1, "Interface & Mobile", "Interfaces web em React e apps em Flutter",
          ["html", "css", "js", "ts", "react", "tailwind", "context", "rq", "flutter", "dart"], accent=C["cy"])
    panel("backend", 2, "Backend & APIs", "APIs REST, autenticação e regras de negócio",
          ["node", "nest", "express", "python", "fastapi", "java", "spring", "csharp", "jwt", "rest"], accent=C["v2"])
    panel("dados", 3, "Dados & Cloud", "Bancos relacionais, ORM e deploy",
          ["pg", "mysql", "prisma", "supabase", "vercel"], accent=C["b2"])
    panel("ia", 4, "IA aplicada", "Explorando IA — ex.: transcrição de áudio com Whisper",
          ["whisper", "nlp", "llm"], accent=C["v1"])
    panel("qualidade", 5, "Qualidade & Workflow", "Testes, documentação, CI e containers",
          ["jest", "vitest", "rtl", "swagger", "postman", "git", "github", "actions", "docker", "vite"], accent=C["b2"])
    T["styled"] = ("styled-\ncomponents", "si:styledcomponents", "#DB7093")
    panel("radar", 6, "No radar", "Tenho contato, mas ainda fora dos meus repositórios públicos",
          ["next", "angular", "styled", "rn", "expo", "redux", "zustand", "firebase"], dim=True, accent=C["text3"])
    T["styled"] = ("styled-components", "si:styledcomponents", "#DB7093")

    api_request()
    api_validation()

    featured_rotagas()
    featured_rotagas(mobile=True)
    featured_gameshelf()
    featured_gameshelf(mobile=True)
    cards = [
        ("library-api", "Library API",
         "API REST de biblioteca — livros, usuários e empréstimos — com Clean Architecture, DDD e padrões "
         "Strategy e Factory Method. Em desenvolvimento.",
         ["node", "express", "prisma", "sqlite", "jest", "swagger"], motif_rings,
         "Library API — API REST de biblioteca com Clean Architecture, DDD, Strategy e Factory Method. "
         "Node.js, Express, Prisma, SQLite, Jest e Swagger."),
        ("helpdesk", "HelpDesk",
         "API de chamados de suporte com técnicos, clientes, prioridade e status. Autenticação e perfis de "
         "acesso com Spring Security e JWT.",
         ["java", "spring", "springsec", "jwt", "mysql"], motif_tickets,
         "HelpDesk — API de chamados com Spring Boot, Spring Security, JWT e MySQL."),
        ("clone-spotify", "Clone Spotify",
         "Clone da interface do Spotify em Flutter, desenvolvido na disciplina de aplicativos móveis.",
         ["flutter", "dart"], motif_player,
         "Clone Spotify — interface do Spotify recriada em Flutter e Dart."),
        ("controle-de-estoque", "Controle de Estoque",
         "Sistema de estoque que eu usava no trabalho, hoje open source para qualquer pessoa usar no próprio "
         "dispositivo.",
         ["react", "vite", "tailwind"], motif_boxes,
         "Controle de Estoque — sistema open source de estoque feito com React, Vite e Tailwind CSS."),
    ]
    for i in range(0, len(cards), 2):
        pair = cards[i:i + 2]
        h = max(compact_height(c[2], c[3]) for c in pair)
        for c in pair:
            compact(*c, H=h)

    link_button("rotagas-painel", "c:play", "#34D399", "Painel ao vivo")
    link_button("rotagas-landing", "c:globe", C["b2"], "Landing page")
    link_button("rotagas-codigo", "si:github", "#F5F5F7", "Código do painel")
    link_button("rotagas-codigo-landing", "si:github", "#F5F5F7", "Código da landing")
    link_button("gameshelf-codigo", "si:github", "#F5F5F7", "Ver código no GitHub", w=230)

    button("github", "github", "GitHub", "@kaikehttps")
    button("linkedin", "linkedin", "LinkedIn", "kaikeferreiraalves")
    button("email", "gmail", "E-mail", "kaikebr208@gmail.com", sub_size=9.5)
    button("instagram", "instagram", "Instagram", "@kaike_alvesz")

    footer()
    footer(mobile=True)
    print("assets ok")


if __name__ == "__main__":
    main()
