"""Design system shared by every generated SVG: tokens, fonts, icons, text helpers."""
import base64
import math
import os
import random
import re
import urllib.request
from xml.sax.saxutils import escape as _xesc

# --------------------------------------------------------------------------- tokens
C = {
    "bg0": "#05060A", "bg1": "#0A0C13", "bg2": "#0D1018",
    "tile": "#10131C", "line": "#1B2030", "line2": "#262D40",
    "text": "#ECEEF4", "text2": "#A6AEC0", "text3": "#7A8396", "text4": "#4E5668",
    "v1": "#C4B5FD", "v2": "#A78BFA", "v3": "#8B5CF6", "v4": "#6D28D9", "v5": "#2E1065",
    "b1": "#93C5FD", "b2": "#60A5FA", "b3": "#3B82F6", "cy": "#38BDF8", "mag": "#C026D3",
}
LIGHT = {"text": "#14161D", "text2": "#424A5C", "text3": "#5B6375", "text4": "#8A92A3",
         "b2": "#2563EB", "v2": "#6D28D9", "v1": "#5B21B6"}

FAM = {
    "SG": "SG,'Space Grotesk','Segoe UI',Roboto,'Helvetica Neue',Arial,sans-serif",
    "JBM": "JBM,'JetBrains Mono',ui-monospace,SFMono-Regular,Menlo,Consolas,monospace",
}
FONT_URLS = {
    ("SG", 500): "https://cdn.jsdelivr.net/npm/@fontsource/space-grotesk@5.2.10/files/space-grotesk-latin-500-normal.woff2",
    ("SG", 700): "https://cdn.jsdelivr.net/npm/@fontsource/space-grotesk@5.2.10/files/space-grotesk-latin-700-normal.woff2",
    ("JBM", 500): "https://cdn.jsdelivr.net/npm/@fontsource/jetbrains-mono@5.2.8/files/jetbrains-mono-latin-500-normal.woff2",
}
SI = "https://cdn.jsdelivr.net/npm/simple-icons@16.33.0/icons/{}.svg"
DV = "https://cdn.jsdelivr.net/gh/devicons/devicon@v2.16.0/icons/{0}/{0}-plain.svg"

REDUCED = "@media (prefers-reduced-motion:reduce){*{animation:none!important}}"


def fx(v, nd=2):
    s = f"{v:.{nd}f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def xesc(s):
    return _xesc(s, {'"': "&quot;"})


# --------------------------------------------------------------------------- cache / fetch
class Assets:
    def __init__(self, cache, pylibs=None):
        self.cache = cache
        os.makedirs(cache, exist_ok=True)
        if pylibs:
            import sys
            sys.path.insert(0, pylibs)
        from fontTools.ttLib import TTFont  # noqa: WPS433
        self.font_b64, self.metrics, self._font_paths, self._subsets = {}, {}, {}, {}
        for key, url in FONT_URLS.items():
            path = self.fetch(url, f"font-{key[0]}-{key[1]}.woff2")
            self._font_paths[key] = path
            raw = open(path, "rb").read()
            self.font_b64[key] = base64.b64encode(raw).decode()
            f = TTFont(path)
            self.metrics[key] = (f.getBestCmap(), f["hmtx"].metrics, f["head"].unitsPerEm)
        self._icons = {}

    def fetch(self, url, name):
        path = os.path.join(self.cache, name)
        if not os.path.exists(path):
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=60) as r:
                data = r.read()
            with open(path, "wb") as fh:
                fh.write(data)
        return path

    # ---- text metrics (advance widths, no kerning: good enough for layout)
    def width(self, s, fam="SG", wt=500, size=14, ls=0.0):
        cmap, hm, upm = self.metrics[(fam, wt)]
        tot = 0
        for ch in s:
            g = cmap.get(ord(ch))
            tot += hm[g][0] if g in hm else upm * 0.55
        return tot * size / upm + ls * len(s)

    def wrap(self, s, maxw, fam="SG", wt=500, size=14, ls=0.0):
        lines, cur = [], ""
        for word in s.split(" "):
            cand = (cur + " " + word).strip()
            if not cur or self.width(cand, fam, wt, size, ls) <= maxw:
                cur = cand
            else:
                lines.append(cur)
                cur = word
        if cur:
            lines.append(cur)
        return lines

    # ---- icons: returns (viewbox, inner markup using currentColor)
    def icon(self, key):
        if key in self._icons:
            return self._icons[key]
        kind, name = key.split(":", 1)
        if kind == "c":
            res = (24, CUSTOM[name])
        else:
            url = SI.format(name) if kind == "si" else DV.format(name)
            raw = open(self.fetch(url, f"{kind}-{name}.svg"), encoding="utf-8").read()
            vb = float(re.search(r'viewBox="0 0 ([\d.]+)', raw).group(1))
            paths = []
            for m in re.finditer(r"<path\b([^>]*)/?>", raw):
                attrs = m.group(1)
                d = re.search(r'\sd="([^"]+)"', attrs).group(1)
                rule = re.search(r'fill-rule="([^"]+)"', attrs)
                paths.append(f'<path d="{d}"' + (f' fill-rule="{rule.group(1)}"' if rule else "") + "/>")
            res = (vb, "".join(paths))
        self._icons[key] = res
        return res


# --------------------------------------------------------------------------- custom glyphs (24x24)
CUSTOM = {
    "context": (
        '<g fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">'
        '<path d="M12 7.6v3.9M5.6 15.4v-3.9h12.8v3.9M12 11.5v3.9"/></g>'
        '<circle cx="12" cy="5" r="2.6"/><circle cx="5.6" cy="18" r="2.4"/>'
        '<circle cx="12" cy="18" r="2.4"/><circle cx="18.4" cy="18" r="2.4"/>'),
    "rest": (
        '<g fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
        '<path d="M4 8.5h14.5M15 5l3.5 3.5L15 12"/><path d="M20 15.5H5.5M9 12l-3.5 3.5L9 19"/></g>'),
    "wave": (
        '<g fill="none" stroke="currentColor" stroke-width="2.1" stroke-linecap="round">'
        '<path d="M3 10.5v3M6.5 7.5v9M10 4v16M13.5 6.5v11M17 9v6M20.5 11v2"/></g>'),
    "nlp": (
        '<path d="M4 4.5h16a1.5 1.5 0 0 1 1.5 1.5v10a1.5 1.5 0 0 1-1.5 1.5h-9l-4.5 3.8v-3.8H4A1.5 1.5 0 0 1 2.5 16V6A1.5 1.5 0 0 1 4 4.5z"'
        ' fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/>'
        '<path d="M6.5 9h11M6.5 13h7" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>'),
    "llm": (
        '<path d="M10 2.5l1.9 5.4 5.4 1.9-5.4 1.9L10 17.1l-1.9-5.4-5.4-1.9 5.4-1.9z"/>'
        '<path d="M18.5 13.2l1 2.6 2.6 1-2.6 1-1 2.6-1-2.6-2.6-1 2.6-1z" opacity=".75"/>'),
    "bear": (
        '<circle cx="5.6" cy="6.3" r="3.1"/><circle cx="18.4" cy="6.3" r="3.1"/><circle cx="12" cy="13.3" r="8.5"/>'
        '<g fill="#0D1018"><circle cx="8.9" cy="11.8" r="1.15"/><circle cx="15.1" cy="11.8" r="1.15"/>'
        '<ellipse cx="12" cy="15.4" rx="1.6" ry="1.15"/></g>'),
    "linkedin": (
        '<path d="M20.45 20.45h-3.55v-5.57c0-1.33-.03-3.04-1.85-3.04-1.85 0-2.14 1.45-2.14 2.94v5.67H9.35V9h3.41v1.56h.05c.48-.9 1.64-1.85 3.37-1.85 3.6 0 4.27 2.37 4.27 5.46v6.28zM5.34 7.43a2.06 2.06 0 1 1 0-4.13 2.06 2.06 0 0 1 0 4.13zM7.12 20.45H3.56V9h3.56v11.45zM22.22 0H1.77C.79 0 0 .77 0 1.73v20.54C0 23.23.79 24 1.77 24h20.45c.98 0 1.78-.77 1.78-1.73V1.73C24 .77 23.2 0 22.22 0z"/>'),
    "check": (
        '<circle cx="12" cy="12" r="9.2" fill="none" stroke="currentColor" stroke-width="1.8"/>'
        '<path d="M7.8 12.3l2.8 2.8 5.6-5.8" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>'),
    "arrow": (
        '<path d="M7 17L17 7M9 7h8v8" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>'),
    "play": '<path d="M8 5.5v13l10.5-6.5z"/>',
    "code": (
        '<path d="M8.5 7L3.5 12l5 5M15.5 7l5 5-5 5" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>'),
    "globe": (
        '<g fill="none" stroke="currentColor" stroke-width="1.8"><circle cx="12" cy="12" r="9"/>'
        '<path d="M3 12h18M12 3c2.6 2.8 3.8 5.8 3.8 9s-1.2 6.2-3.8 9c-2.6-2.8-3.8-5.8-3.8-9S9.4 5.8 12 3z"/></g>'),
}

# --------------------------------------------------------------------------- technologies
# key: (label, icon, color tuned for dark tiles)
T = {
    "html": ("HTML5", "si:html5", "#E34F26"),
    "css": ("CSS", "si:css", "#9B6CF0"),
    "js": ("JavaScript", "si:javascript", "#F7DF1E"),
    "ts": ("TypeScript", "si:typescript", "#3B8BEB"),
    "react": ("React", "si:react", "#61DAFB"),
    "tailwind": ("Tailwind CSS", "si:tailwindcss", "#38BDF8"),
    "context": ("Context API", "c:context", "#7DD3FC"),
    "rq": ("React Query", "si:reactquery", "#FF4154"),
    "flutter": ("Flutter", "si:flutter", "#47C5FB"),
    "dart": ("Dart", "si:dart", "#2FB4F0"),
    "node": ("Node.js", "si:nodedotjs", "#6CC24A"),
    "nest": ("NestJS", "si:nestjs", "#EA2845"),
    "express": ("Express", "si:express", "#E5E7EB"),
    "python": ("Python", "si:python", "#5B9BD5"),
    "fastapi": ("FastAPI", "si:fastapi", "#14B8A6"),
    "java": ("Java", "dv:java", "#F89820"),
    "spring": ("Spring Boot", "si:springboot", "#6DB33F"),
    "springsec": ("Spring Security", "si:springsecurity", "#6DB33F"),
    "csharp": ("C#", "dv:csharp", "#A179DC"),
    "jwt": ("JWT", "si:jsonwebtokens", "#FB3B7E"),
    "rest": ("REST", "c:rest", "#A78BFA"),
    "pg": ("PostgreSQL", "si:postgresql", "#6E9BEA"),
    "mysql": ("MySQL", "si:mysql", "#5E9DD0"),
    "prisma": ("Prisma", "si:prisma", "#E2E8F0"),
    "supabase": ("Supabase", "si:supabase", "#3FCF8E"),
    "sqlite": ("SQLite", "si:sqlite", "#44A6E0"),
    "redis": ("Redis", "si:redis", "#FF4438"),
    "vercel": ("Vercel", "si:vercel", "#F5F5F7"),
    "jest": ("Jest", "si:jest", "#E0414F"),
    "vitest": ("Vitest", "si:vitest", "#7CD951"),
    "rtl": ("Testing Library", "si:testinglibrary", "#F0484A"),
    "swagger": ("Swagger", "si:swagger", "#85EA2D"),
    "postman": ("Postman", "si:postman", "#FF6C37"),
    "git": ("Git", "si:git", "#F05032"),
    "github": ("GitHub", "si:github", "#F5F5F7"),
    "actions": ("GitHub Actions", "si:githubactions", "#3B95FF"),
    "docker": ("Docker", "si:docker", "#2496ED"),
    "vite": ("Vite", "si:vite", "#A66BFF"),
    "whisper": ("Whisper", "c:wave", "#E5E7EB"),
    "nlp": ("NLP", "c:nlp", "#60A5FA"),
    "llm": ("LLMs", "c:llm", "#A78BFA"),
    "next": ("Next.js", "si:nextdotjs", "#F5F5F7"),
    "angular": ("Angular", "si:angular", "#E8395E"),
    "styled": ("styled-components", "si:styledcomponents", "#DB7093"),
    "rn": ("React Native", "si:react", "#61DAFB"),
    "expo": ("Expo", "si:expo", "#F5F5F7"),
    "redux": ("Redux", "si:redux", "#9370DB"),
    "zustand": ("Zustand", "c:bear", "#D4A373"),
    "firebase": ("Firebase", "si:firebase", "#FFA611"),
    "leaflet": ("Leaflet", "si:leaflet", "#46C13A"),
    "chartjs": ("Chart.js", "si:chartdotjs", "#FF6384"),
    "framer": ("Framer Motion", "si:framer", "#5B93FF"),
    "instagram": ("Instagram", "si:instagram", "#F2577E"),
    "gmail": ("E-mail", "si:gmail", "#EA4335"),
    "linkedin": ("LinkedIn", "c:linkedin", "#3B8FE0"),
}


# --------------------------------------------------------------------------- SVG document
SAFE_CHARS = ("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789 .,;:!?-–—()[]'\"/&@#%+*=_·•→↗‹›…"
              "áàâãéêíóôõúüçÁÀÂÃÉÊÍÓÔÕÚÜÇ")


def subset_font(A, key, chars):
    """WOFF2 subset with the glyphs actually used plus a safety set (letters, digits, PT accents)."""
    from fontTools import subset  # noqa: WPS433
    text = "".join(sorted(set(chars) | set(SAFE_CHARS)))
    ck = (key, text)
    if ck in A._subsets:
        return A._subsets[ck]
    opts = subset.Options()
    opts.flavor = "woff2"
    opts.layout_features = ["kern", "liga", "calt"]
    opts.name_IDs = ["*"]
    opts.notdef_outline = True
    font = subset.load_font(A._font_paths[key], opts)
    sub = subset.Subsetter(opts)
    sub.populate(text=text)
    sub.subset(font)
    import io
    buf = io.BytesIO()
    subset.save_font(font, buf, opts)
    A._subsets[ck] = base64.b64encode(buf.getvalue()).decode()
    return A._subsets[ck]


class Doc:
    def __init__(self, A, w, h, title, theme="dark"):
        self.A, self.w, self.h, self.title, self.theme = A, w, h, title, theme
        self.defs, self.css, self.parts, self.fonts = [], [], [], set()
        self.chars = {}
        self.n = 0

    def uid(self, p="i"):
        self.n += 1
        return f"{p}{self.n}"

    def add(self, s):
        self.parts.append(s)

    def d(self, s):
        self.defs.append(s)

    def style(self, s):
        if s not in self.css:
            self.css.append(s)

    def text(self, x, y, s, fam="SG", wt=500, size=14, fill=None, anchor="start", ls=0, op=None,
             cls=None, style=None):
        self.fonts.add((fam, wt))
        self.chars.setdefault((fam, wt), set()).update(s)
        a = [f'x="{fx(x)}"', f'y="{fx(y)}"', f'font-family="{FAM[fam]}"', f'font-weight="{wt}"',
             f'font-size="{fx(size)}"', f'fill="{fill or C["text"]}"']
        if anchor != "start":
            a.append(f'text-anchor="{anchor}"')
        if ls:
            a.append(f'letter-spacing="{fx(ls)}"')
        if op is not None:
            a.append(f'opacity="{fx(op)}"')
        if cls:
            a.append(f'class="{cls}"')
        if style:
            a.append(f'style="{style}"')
        self.add(f"<text {' '.join(a)}>{xesc(s)}</text>")

    def lines(self, x, y, lines, lh, **kw):
        for i, ln in enumerate(lines):
            self.text(x, y + i * lh, ln, **kw)

    def icon(self, key, x, y, size, color, op=None, extra=""):
        vb, inner = self.A.icon(key)
        o = f' opacity="{fx(op)}"' if op is not None else ""
        self.add(f'<g transform="translate({fx(x)} {fx(y)}) scale({fx(size / vb, 5)})" color="{color}" '
                 f'fill="{color}"{o}{extra}>{inner}</g>')

    def svg(self):
        faces = "".join(
            "@font-face{font-family:%s;font-weight:%d;font-style:normal;font-display:block;"
            "src:url(data:font/woff2;base64,%s) format('woff2')}"
            % (fam, wt, subset_font(self.A, (fam, wt), self.chars.get((fam, wt), "")))
            for fam, wt in sorted(self.fonts))
        css = faces + "".join(self.css) + REDUCED
        return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{fx(self.w)}" height="{fx(self.h)}" '
                f'viewBox="0 0 {fx(self.w)} {fx(self.h)}" role="img" aria-labelledby="title">'
                f'<title id="title">{xesc(self.title)}</title><style>{css}</style>'
                f'<defs>{"".join(self.defs)}</defs>{"".join(self.parts)}</svg>\n')

    def save(self, path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(self.svg())
        return path


# --------------------------------------------------------------------------- shared drawing helpers
TWINKLE = "@keyframes tw{0%,100%{opacity:.12}50%{opacity:1}}.tw{animation:tw 4s ease-in-out infinite}"
PULSE = ("@keyframes pulse{0%{transform:scale(1);opacity:.7}100%{transform:scale(3.2);opacity:0}}"
         ".pulse{transform-box:fill-box;transform-origin:center;animation:pulse 2.4s ease-out infinite}")


def sparkle_path(cx, cy, r):
    return (f"M{fx(cx)} {fx(cy - r)}Q{fx(cx)} {fx(cy)} {fx(cx + r)} {fx(cy)}Q{fx(cx)} {fx(cy)} {fx(cx)} {fx(cy + r)}"
            f"Q{fx(cx)} {fx(cy)} {fx(cx - r)} {fx(cy)}Q{fx(cx)} {fx(cy)} {fx(cx)} {fx(cy - r)}Z")


def glow_filter(doc, std=4, fid=None):
    fid = fid or doc.uid("g")
    doc.d(f'<filter id="{fid}" x="-80%" y="-80%" width="260%" height="260%">'
          f'<feGaussianBlur stdDeviation="{fx(std)}"/></filter>')
    return fid


def stars(doc, w, h, n, seed, twinkle=0, op=(0.18, 0.75), sizes=(0.45, 0.55, 0.7, 0.85, 1.05, 1.3),
          weights=(5, 5, 4, 3, 2, 1), avoid=None, colors=("#FFFFFF", "#E0E7FF", "#C4B5FD", "#BFDBFE")):
    rnd = random.Random(seed)
    out = []
    tw_count = 0
    for _ in range(n):
        x, y = rnd.uniform(4, w - 4), rnd.uniform(4, h - 4)
        if avoid and any(ax <= x <= ax + aw and ay <= y <= ay + ah for ax, ay, aw, ah in avoid):
            continue
        r = rnd.choices(sizes, weights)[0]
        o = rnd.uniform(*op)
        col = rnd.choice(colors)
        extra = ""
        if tw_count < twinkle and r >= 0.7:
            tw_count += 1
            extra = (f' class="tw" style="animation-duration:{fx(rnd.uniform(2.6, 6.5))}s;'
                     f'animation-delay:-{fx(rnd.uniform(0, 6))}s"')
        out.append(f'<circle cx="{fx(x, 1)}" cy="{fx(y, 1)}" r="{fx(r)}" fill="{col}" opacity="{fx(o)}"{extra}/>')
    if twinkle:
        doc.style(TWINKLE)
    doc.add("".join(out))


def card_frame(doc, w, h, r=18, glow=None, glow_pos=(0.85, 0.0), border=None, seed=3, nstars=22,
               bg=("#0C0F17", "#08090F")):
    """Rounded dark card with subtle starfield; returns the clip id."""
    cid, gid = doc.uid("clip"), doc.uid("bg")
    doc.d(f'<clipPath id="{cid}"><rect width="{fx(w)}" height="{fx(h)}" rx="{r}"/></clipPath>')
    doc.d(f'<linearGradient id="{gid}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{bg[0]}"/>'
          f'<stop offset="1" stop-color="{bg[1]}"/></linearGradient>')
    hid = doc.uid("hl")
    doc.d(f'<linearGradient id="{hid}" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/>'
          f'<stop offset=".5" stop-color="#fff" stop-opacity=".09"/><stop offset="1" stop-color="#fff" stop-opacity="0"/>'
          f'</linearGradient>')
    doc.add(f'<g clip-path="url(#{cid})"><rect width="{fx(w)}" height="{fx(h)}" fill="url(#{gid})"/>')
    if glow:
        rg = doc.uid("rg")
        doc.d(f'<radialGradient id="{rg}" cx="{fx(glow_pos[0] * w)}" cy="{fx(glow_pos[1] * h)}" r="{fx(max(w, h) * 0.62)}" '
              f'gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="{glow}" stop-opacity=".16"/>'
              f'<stop offset="1" stop-color="{glow}" stop-opacity="0"/></radialGradient>')
        doc.add(f'<rect width="{fx(w)}" height="{fx(h)}" fill="url(#{rg})"/>')
    if nstars:
        stars(doc, w, h, nstars, seed, op=(0.08, 0.35))
    doc.add(f'<rect x="{fx(w * .12)}" y="0" width="{fx(w * .76)}" height="1" fill="url(#{hid})"/></g>')
    stroke = border or C["line"]
    doc.add(f'<rect x=".5" y=".5" width="{fx(w - 1)}" height="{fx(h - 1)}" rx="{fx(r - .5)}" fill="none" '
            f'stroke="{stroke}"/>')
    return cid


def gradient_border(doc, w, h, r, c1, c2, op=0.9):
    gid = doc.uid("gb")
    doc.d(f'<linearGradient id="{gid}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{c1}" stop-opacity="{op}"/>'
          f'<stop offset=".45" stop-color="{C["line2"]}" stop-opacity=".9"/><stop offset="1" stop-color="{c2}" stop-opacity="{op}"/>'
          f'</linearGradient>')
    doc.add(f'<rect x=".75" y=".75" width="{fx(w - 1.5)}" height="{fx(h - 1.5)}" rx="{fx(r - .75)}" fill="none" '
            f'stroke="url(#{gid})" stroke-width="1.5"/>')


def pill(doc, x, y, label, color, h=22, size=9.5, fam="JBM", ls=0.9, fill_op=0.08, stroke_op=0.32, upper=True):
    s = label.upper() if upper else label
    w = doc.A.width(s, fam, 500, size, ls) + 20
    doc.add(f'<rect x="{fx(x)}" y="{fx(y)}" width="{fx(w)}" height="{h}" rx="{h / 2}" fill="{color}" '
            f'fill-opacity="{fill_op}" stroke="{color}" stroke-opacity="{stroke_op}"/>')
    doc.text(x + w / 2, y + h / 2 + size * 0.36, s, fam, 500, size, color, anchor="middle", ls=ls)
    return w


def live_dot(doc, cx, cy, color, r=3.4):
    doc.style(PULSE)
    doc.add(f'<circle class="pulse" cx="{fx(cx)}" cy="{fx(cy)}" r="{fx(r)}" fill="{color}"/>'
            f'<circle cx="{fx(cx)}" cy="{fx(cy)}" r="{fx(r)}" fill="{color}"/>')


def tile(doc, x, y, key, size=62, dim=False, label_color=None):
    label, ik, col = T[key]
    tid = "tileg"
    if not any(f'id="{tid}"' in d for d in doc.defs):
        doc.d(f'<linearGradient id="{tid}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#131723"/>'
              f'<stop offset="1" stop-color="#0D1018"/></linearGradient>')
    dash = ' stroke-dasharray="3 3"' if dim else ""
    doc.add(f'<rect x="{fx(x)}" y="{fx(y)}" width="{size}" height="{size}" rx="14" fill="url(#{tid})" '
            f'stroke="{C["line2"] if not dim else "#2E3548"}"{dash}/>')
    gid = doc.uid("tg")
    doc.d(f'<radialGradient id="{gid}"><stop offset="0" stop-color="{col}" stop-opacity="{".2" if not dim else ".1"}"/>'
          f'<stop offset="1" stop-color="{col}" stop-opacity="0"/></radialGradient>')
    cx, cy = x + size / 2, y + size / 2
    doc.add(f'<circle cx="{fx(cx)}" cy="{fx(cy)}" r="{fx(size * .48)}" fill="url(#{gid})"/>')
    isz = 28
    doc.icon(ik, cx - isz / 2, cy - isz / 2, isz, col, op=0.78 if dim else None)
    lc = label_color or (C["text3"] if dim else C["text2"])
    parts = label.split("\n")
    for i, p in enumerate(parts):
        doc.text(cx, y + size + 16 + i * 12, p, "SG", 500, 10.5 if len(parts) == 1 else 10, lc, anchor="middle")
