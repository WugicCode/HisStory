# -*- coding: utf-8 -*-
"""长歌 · 概念图生成（全部为手写 SVG，无外部依赖、无网络资源）"""

import math
import zlib

# ══════════════════════════════ 调色板 ══════════════════════════════

PALETTE = {
    "core-crystal": dict(top="#0a1a24", mid="#123542", low="#1d5566", accent="#9fe0e6", ink="#050b10"),
    "core-guard":   dict(top="#0b1219", mid="#172633", low="#27404f", accent="#cbd6dd", ink="#05080c"),
    "core-field":   dict(top="#140f0a", mid="#2a2118", low="#463726", accent="#d7ad7c", ink="#0a0705"),
    "core-song":    dict(top="#141006", mid="#2c2412", low="#58461f", accent="#f0cf8a", ink="#0a0803"),
    "novian":       dict(top="#080e1c", mid="#152a4a", low="#2d4d7d", accent="#a9c8ef", ink="#04070e"),
    "lilia":        dict(top="#0b0916", mid="#1e1a38", low="#3f3766", accent="#d9d0f5", ink="#060510"),
    "eve":          dict(top="#07120c", mid="#122c1c", low="#2b5738", accent="#b8e0a8", ink="#040a06"),
    "moika":        dict(top="#0d0812", mid="#241630", low="#432b56", accent="#d6a6e8", ink="#070510"),
    "milika":       dict(top="#0e0b06", mid="#26200f", low="#4d4020", accent="#f2e2b0", ink="#080603"),
    "helius":       dict(top="#160b05", mid="#33180a", low="#6b3415", accent="#ffcf8a", ink="#0b0502"),
    "scarlett":     dict(top="#14050a", mid="#2f0b14", low="#5c1626", accent="#ff9aa8", ink="#0a0206"),
    "mophy":        dict(top="#07081a", mid="#151a3c", low="#2b3270", accent="#a8b6f0", ink="#040511"),
}

FACTION_TINT = {
    "通用": ("#0b0f14", "#1d2731", "#cbd2d8"),
    "新的勇者": ("#0a1020", "#1f2f52", "#b9cdf0"),
    "同盟军": ("#160c06", "#3a2110", "#f0c48a"),
    "魔王军": ("#120610", "#39102a", "#e3a6c6"),
}


def _rng(seed):
    return __import__("random").Random(zlib.crc32(seed.encode("utf-8")))


def _num(v):
    """紧凑数字格式"""
    return ("%.2f" % v).rstrip("0").rstrip(".")


# ══════════════════════════════ 基础元素 ══════════════════════════════

def stars(seed, n, w, h, ymax=None, color="#ffffff"):
    r = _rng(seed + "star")
    out = []
    ymax = ymax or h
    for _ in range(n):
        x = r.uniform(0, w)
        y = r.uniform(0, ymax)
        rad = r.choice([0.6, 0.7, 0.8, 1.0, 1.2, 1.6])
        op = r.uniform(0.18, 0.85)
        out.append('<circle cx="%s" cy="%s" r="%s" fill="%s" opacity="%s"/>'
                   % (_num(x), _num(y), _num(rad), color, _num(op)))
    return "".join(out)


def motes(seed, n, w, h, color, ymin=0.2, ymax=0.95):
    r = _rng(seed + "mote")
    out = []
    for _ in range(n):
        x = r.uniform(0, w)
        y = r.uniform(h * ymin, h * ymax)
        rad = r.uniform(0.9, 2.6)
        op = r.uniform(0.08, 0.42)
        out.append('<circle cx="%s" cy="%s" r="%s" fill="%s" opacity="%s"/>'
                   % (_num(x), _num(y), _num(rad), color, _num(op)))
    return "".join(out)


def ridge(seed, w, base_y, amp, step=None, color="#000", opacity=1.0):
    """生成一条山脊折线"""
    r = _rng(seed + "ridge")
    step = step or 70
    pts = []
    x = -40
    y = base_y
    while x < w + 60:
        pts.append((x, y))
        x += r.uniform(step * 0.55, step * 1.5)
        y = base_y - r.uniform(-amp * 0.15, amp)
    pts.append((w + 60, base_y))
    inner = " ".join("%s,%s" % (_num(px), _num(py)) for px, py in pts)
    return ('<polygon points="%s %s,%s -40,%s" fill="%s" opacity="%s"/>'
            % (inner, w + 60, base_y + 400, base_y + 400, color, _num(opacity)))


def crescent(cx, cy, r, fill, opacity=1.0, rot=-24):
    """新月：两圆布尔差"""
    d = r * 0.42
    return ('<g transform="translate(%s %s) rotate(%s)" opacity="%s">'
            '<path d="M0,-%s A%s,%s 0 1,0 0,%s A%s,%s 0 1,1 0,-%s Z" fill="%s"/></g>'
            % (_num(cx), _num(cy), _num(rot), _num(opacity),
               _num(r), _num(r), _num(r), _num(r),
               _num(r), _num(r * 0.86), _num(r), fill))


def sunburst(cx, cy, r1, r2, n, fill, opacity=1.0, spin=0):
    out = ['<g opacity="%s">' % _num(opacity)]
    for i in range(n):
        a = spin + i * 360.0 / n
        a2 = a + (360.0 / n) * 0.34
        p1 = (cx + r1 * math.cos(math.radians(a)), cy + r1 * math.sin(math.radians(a)))
        p2 = (cx + r2 * math.cos(math.radians(a + (360.0 / n) * 0.17)),
              cy + r2 * math.sin(math.radians(a + (360.0 / n) * 0.17)))
        p3 = (cx + r1 * math.cos(math.radians(a2)), cy + r1 * math.sin(math.radians(a2)))
        out.append('<polygon points="%s,%s %s,%s %s,%s" fill="%s"/>'
                   % (_num(p1[0]), _num(p1[1]), _num(p2[0]), _num(p2[1]),
                      _num(p3[0]), _num(p3[1]), fill))
    out.append("</g>")
    return "".join(out)


def rune_ring(cx, cy, r, color, n=24, opacity=0.55, seg=0.55):
    dash = 2 * math.pi * r / n
    return ('<circle cx="%s" cy="%s" r="%s" fill="none" stroke="%s" stroke-width="1.4" '
            'stroke-dasharray="%s %s" opacity="%s"/>'
            % (_num(cx), _num(cy), _num(r), color, _num(dash * seg), _num(dash * (1 - seg)), _num(opacity)))


def spiral(cx, cy, r, turns, color, width=3, opacity=1.0, rot=0):
    pts = []
    steps = int(turns * 48)
    for i in range(steps + 1):
        t = i / steps
        a = t * turns * 2 * math.pi + math.radians(rot)
        rr = r * (0.12 + 0.88 * t)
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    d = "M" + " L".join("%s,%s" % (_num(x), _num(y)) for x, y in pts)
    return ('<path d="%s" fill="none" stroke="%s" stroke-width="%s" opacity="%s" '
            'stroke-linecap="round"/>' % (d, color, width, _num(opacity)))


def figure(x, y, s=1.0, fill="#05060b", accent=None, kind="cloak"):
    """远景剪影人物（约 70px 高）"""
    g = ['<g transform="translate(%s %s) scale(%s)">' % (_num(x), _num(y), _num(s))]
    if kind == "cloak":
        g.append('<path d="M0,-62 C-9,-58 -12,-44 -11,-26 C-10,-14 -14,-4 -18,2 L18,2 '
                 'C14,-4 10,-14 11,-26 C12,-44 9,-58 0,-62 Z" fill="%s"/>' % fill)
        g.append('<circle cx="0" cy="-66" r="6.4" fill="%s"/>' % fill)
        g.append('<path d="M12,-58 L17,-2" stroke="%s" stroke-width="2.2" opacity="0.9"/>' % fill)
    elif kind == "lance":
        g.append('<path d="M0,-60 C-8,-56 -10,-42 -9,-24 L-6,2 L6,2 L9,-24 C10,-42 8,-56 0,-60 Z" fill="%s"/>' % fill)
        g.append('<circle cx="0" cy="-64" r="6" fill="%s"/>' % fill)
        g.append('<path d="M10,-96 L12,4" stroke="%s" stroke-width="2" />' % fill)
        g.append('<polygon points="12,-96 7,-84 17,-84" fill="%s"/>' % fill)
    elif kind == "bow":
        g.append('<path d="M0,-58 C-7,-54 -9,-40 -8,-22 L-5,2 L5,2 L8,-22 C9,-40 7,-54 0,-58 Z" fill="%s"/>' % fill)
        g.append('<circle cx="0" cy="-62" r="5.6" fill="%s"/>' % fill)
        g.append('<path d="M9,-56 C20,-40 20,-16 9,-2" fill="none" stroke="%s" stroke-width="1.8"/>' % fill)
        g.append('<path d="M9,-56 L9,-2" stroke="%s" stroke-width="0.9" opacity="0.7"/>' % fill)
    if accent:
        g.append('<path d="M0,-62 C7,-58 10,-46 9,-30" fill="none" stroke="%s" '
                 'stroke-width="1.1" opacity="0.45"/>' % accent)
    g.append("</g>")
    return "".join(g)


# ══════════════════════════════ 卡面母题 ══════════════════════════════

def motif_crystal(cx, cy, r, p):
    a = p["accent"]
    out = ['<g transform="translate(%s %s)">' % (_num(cx), _num(cy))]
    pts = "0,%s %s,%s %s,%s 0,%s %s,%s %s,%s" % (
        _num(-r), _num(r * .52), _num(-r * .42), _num(r * .52), _num(r * .50),
        _num(r * .92), _num(-r * .52), _num(r * .50), _num(-r * .52), _num(-r * .42))
    out.append('<polygon points="%s" fill="%s" opacity="0.16"/>' % (pts, a))
    out.append('<polygon points="%s" fill="none" stroke="%s" stroke-width="1.6" opacity="0.85"/>' % (pts, a))
    out.append('<path d="M0,-%s L0,%s M-%s,-%s L0,%s L%s,-%s M0,%s L-%s,%s M0,%s L%s,%s" '
               'stroke="%s" stroke-width="1" opacity="0.5"/>'
               % (_num(r), _num(r * .85), _num(r * .2), _num(r * .2), _num(r * .5),
                  _num(r * .2), _num(r * .2), _num(r * .5), _num(r * .55), _num(r * .85),
                  _num(r * .5), _num(r * .55), _num(r * .85), a))
    out.append("</g>")
    return "".join(out)


def motif_shield(cx, cy, r, p):
    a = p["accent"]
    d = ("M0,-%s C%s,-%s %s,-%s %s,-%s L%s,%s C%s,%s %s,%s 0,%s "
         "C-%s,%s -%s,%s -%s,%s L-%s,-%s C-%s,-%s -%s,-%s 0,-%s Z")
    pts = [_num(r), _num(r * .9), _num(r * .78), _num(r * .95), _num(r * .62),
           _num(r * .9), _num(r * .58), _num(r * .55), _num(r * .9), _num(r * .05),
           _num(r * .35), _num(r * .92), _num(r * .1), _num(r * .95), _num(r * .1),
           _num(r * .35), _num(r * .92), _num(r * .35), _num(r * .55),
           _num(r * .9), _num(r * .58), _num(r * .9), _num(r * .62),
           _num(r * .95), _num(r * .78), _num(r * .9), _num(r * .78)]
    out = ['<g transform="translate(%s %s)">' % (_num(cx), _num(cy))]
    out.append('<path d="%s" fill="%s" opacity="0.14"/>' % (d % tuple(pts), a))
    out.append('<path d="%s" fill="none" stroke="%s" stroke-width="2" opacity="0.85"/>' % (d % tuple(pts), a))
    out.append('<path d="M0,-%s L0,%s M-%s,-%s L%s,-%s" stroke="%s" stroke-width="1.6" opacity="0.55"/>'
               % (_num(r * .52), _num(r * .66), _num(r * .3), _num(r * .06),
                  _num(r * .3), _num(r * .06), a))
    out.append("</g>")
    return "".join(out)


def motif_blade(cx, cy, r, p):
    a = p["accent"]
    out = ['<g transform="translate(%s %s) rotate(8)">' % (_num(cx), _num(cy))]
    N = _num
    blade = ("0,%s %s,%s %s,%s 0,%s %s,%s %s,%s"
             % (N(-r), N(r * .10), N(-r * .55), N(r * .10), N(r * .55),
                N(r * .74), N(-r * .10), N(r * .55), N(-r * .10), N(-r * .55)))
    out.append('<polygon points="%s" fill="%s" opacity="0.16"/>' % (blade, a))
    out.append('<polygon points="%s" fill="none" stroke="%s" stroke-width="1.6" opacity="0.9"/>' % (blade, a))
    out.append('<rect x="%s" y="%s" width="%s" height="6" fill="%s" opacity="0.8"/>'
               % (N(-r * .34), N(r * .58), N(r * .68), a))
    out.append('<rect x="-3" y="%s" width="6" height="%s" fill="%s" opacity="0.7"/>'
               % (N(r * .64), N(r * .3), a))
    out.append('<circle cx="0" cy="%s" r="5" fill="%s" opacity="0.9"/>' % (N(r * .62), a))
    out.append("</g>")
    return "".join(out)


def motif_harp(cx, cy, r, p):
    a = p["accent"]
    out = ['<g transform="translate(%s %s)">' % (_num(cx), _num(cy))]
    out.append('<path d="M-%s,%s C-%s,-%s %s,-%s %s,%s" fill="none" stroke="%s" stroke-width="2.4" '
               'opacity="0.9"/>'
               % (_num(r * .55), _num(r * .85), _num(r * .8), _num(r * .9),
                  _num(r * .8), _num(r * .9), _num(r * .5), _num(r * .8), a))
    for i in range(6):
        t = i / 5.0
        x1 = -r * .5 + t * r * .95
        out.append('<path d="M%s,%s L%s,%s" stroke="%s" stroke-width="1" opacity="%s"/>'
                   % (_num(x1), _num(r * (.8 - .0 * t)), _num(x1 + r * .12),
                      _num(r * (-.62 + .1 * t)), a, _num(.32 + .1 * (1 - t))))
    out.append('<circle cx="%s" cy="%s" r="%s" fill="none" stroke="%s" stroke-width="1.4" opacity="0.6"/>'
               % (_num(r * .78), _num(-r * .7), _num(r * .16), a))
    out.append("</g>")
    return "".join(out)


def motif_moon(cx, cy, r, p):
    a = p["accent"]
    out = ['<g transform="translate(%s %s)">' % (_num(cx), _num(cy))]
    out.append(crescent(0, 0, r * .82, a, opacity=0.9))
    out.append('<circle cx="0" cy="0" r="%s" fill="none" stroke="%s" stroke-width="1" opacity="0.35"/>'
               % (_num(r), a))
    out.append(rune_ring(0, 0, r * 1.12, a, n=18, opacity=0.35))
    out.append("</g>")
    return "".join(out)


def motif_wind(cx, cy, r, p):
    a = p["accent"]
    out = ['<g transform="translate(%s %s)">' % (_num(cx), _num(cy))]
    for i, rr in enumerate((r * .95, r * .68, r * .42)):
        out.append(spiral(0, 0, rr, 2.1, a, width=(2.6 - i * .5), opacity=(0.85 - i * .12), rot=i * 55))
    out.append('<path d="M%s,%s C%s,%s %s,%s %s,%s" fill="none" stroke="%s" stroke-width="1.2" '
               'opacity="0.35"/>'
               % (_num(-r * 1.1), _num(r * .5), _num(-r * .2), _num(r * 1.15),
                  _num(r * .8), _num(r * 1.0), _num(r * 1.15), _num(r * .3), a))
    out.append("</g>")
    return "".join(out)


def motif_mask(cx, cy, r, p):
    a = p["accent"]
    out = ['<g transform="translate(%s %s)">' % (_num(cx), _num(cy))]
    N = _num
    d = ("M0,%s C%s,%s %s,%s %s,%s C%s,%s %s,%s 0,%s "
         "C%s,%s %s,%s %s,%s C%s,%s %s,%s 0,%s Z")
    d = d % (N(-r * .78), N(r * .50), N(-r * .78), N(r * .66), N(-r * .40), N(r * .66), N(r * .05),
             N(r * .66), N(r * .50), N(r * .30), N(r * .80), N(r * .86),
             N(-r * .30), N(r * .80), N(-r * .66), N(r * .50), N(-r * .66), N(r * .05),
             N(-r * .66), N(-r * .40), N(-r * .50), N(-r * .78), N(-r * .78))
    out.append('<path d="%s" fill="%s" opacity="0.14"/>' % (d, a))
    out.append('<path d="%s" fill="none" stroke="%s" stroke-width="1.8" opacity="0.85"/>' % (d, a))
    out.append('<path d="M%s,%s q%s,%s %s,0" fill="none" stroke="%s" stroke-width="2.6" opacity="0.9"/>'
               % (N(-r * .38), N(-r * .06), N(r * .19), N(-r * .16), N(r * .38), a))
    out.append('<path d="M%s,%s q%s,%s %s,0" fill="none" stroke="%s" stroke-width="2.6" opacity="0.9"/>'
               % (N(r * .06), N(-r * .06), N(r * .16), N(r * .16), N(-r * .38), a))
    out.append('<path d="M0,%s L0,%s" stroke="%s" stroke-width="1" opacity="0.55"/>'
               % (N(r * .16), N(r * .48), a))
    out.append("</g>")
    return "".join(out)


def motif_halo(cx, cy, r, p):
    a = p["accent"]
    out = ['<g transform="translate(%s %s)">' % (_num(cx), _num(cy))]
    N = _num
    out.append('<circle cx="0" cy="%s" r="%s" fill="none" stroke="%s" stroke-width="2.2" opacity="0.85"/>'
               % (N(-r * .62), N(r * .34), a))
    out.append(sunburst(0, -r * .62, r * .5, r * .78, 14, a, opacity=0.30))
    diamond = "0,%s %s,%s 0,%s %s,%s" % (N(-r * .18), N(r * .22), N(r * .36), N(r * .72),
                                          N(-r * .22), N(r * .36))
    out.append('<polygon points="%s" fill="%s" opacity="0.16"/>' % (diamond, a))
    out.append('<polygon points="%s" fill="none" stroke="%s" stroke-width="1.6" opacity="0.9"/>'
               % (diamond, a))
    out.append('<path d="M0,%s L0,%s" stroke="%s" stroke-width="1" opacity="0.45"/>'
               % (N(r * .02), N(r * .58), a))
    out.append("</g>")
    return "".join(out)


def motif_sun(cx, cy, r, p):
    a = p["accent"]
    out = ['<g transform="translate(%s %s)">' % (_num(cx), _num(cy))]
    out.append(sunburst(0, 0, r * .42, r * 1.05, 20, a, opacity=0.42))
    out.append('<circle cx="0" cy="0" r="%s" fill="%s" opacity="0.22"/>' % (_num(r * .42), a))
    out.append('<circle cx="0" cy="0" r="%s" fill="none" stroke="%s" stroke-width="1.8" opacity="0.9"/>'
               % (_num(r * .42), a))
    out.append('<path d="M0,%s L0,-%s" stroke="%s" stroke-width="1.4" opacity="0.5"/>'
               % (_num(r * 1.25), _num(r * 1.25), a))
    out.append("</g>")
    return "".join(out)


def motif_eclipse(cx, cy, r, p):
    a = p["accent"]
    out = ['<g transform="translate(%s %s)">' % (_num(cx), _num(cy))]
    out.append('<circle cx="0" cy="0" r="%s" fill="%s" opacity="0.2"/>' % (_num(r), a))
    out.append('<circle cx="0" cy="0" r="%s" fill="none" stroke="%s" stroke-width="2" opacity="0.9"/>'
               % (_num(r), a))
    out.append('<circle cx="%s" cy="0" r="%s" fill="%s" opacity="0.5"/>'
               % (_num(r * .34), _num(r * .82), p["top"]))
    out.append(rune_ring(0, 0, r * 1.2, a, n=30, opacity=0.28, seg=0.35))
    out.append("</g>")
    return "".join(out)


def motif_dream(cx, cy, r, p):
    a = p["accent"]
    out = ['<g transform="translate(%s %s)">' % (_num(cx), _num(cy))]
    out.append('<circle cx="0" cy="0" r="%s" fill="none" stroke="%s" stroke-width="2.2" opacity="0.9"/>'
               % (_num(r * .78), a))
    for i in range(6):
        ang = i * 60
        out.append('<path d="M0,0 L%s,%s" stroke="%s" stroke-width="0.9" opacity="0.4"/>'
                   % (_num(r * .78 * math.cos(math.radians(ang))),
                      _num(r * .78 * math.sin(math.radians(ang))), a))
    out.append('<circle cx="0" cy="0" r="%s" fill="none" stroke="%s" stroke-width="1.2" opacity="0.5"/>'
               % (_num(r * .34), a))
    for i, dx in enumerate((-0.34, 0.0, 0.34)):
        out.append('<path d="M%s,%s C%s,%s %s,%s %s,%s" fill="none" stroke="%s" stroke-width="1" '
                   'opacity="0.55"/>'
                   % (_num(r * dx), _num(r * .78), _num(r * dx * 1.2), _num(r * 1.05),
                      _num(r * dx * .8), _num(r * 1.2), _num(r * dx), _num(r * 1.45), a))
    out.append("</g>")
    return "".join(out)


MOTIFS = {
    "core-crystal": motif_crystal, "core-guard": motif_shield, "core-field": motif_blade,
    "core-song": motif_harp, "novian": motif_blade, "lilia": motif_moon, "eve": motif_wind,
    "moika": motif_mask, "milika": motif_halo, "helius": motif_sun, "scarlett": motif_eclipse,
    "mophy": motif_dream,
}


# ══════════════════════════════ 卡面插画 ══════════════════════════════

def card_art(cid, cluster, kind="spell", w=600, h=380):
    p = PALETTE.get(cluster, PALETTE["core-crystal"])
    r = _rng(cid)
    gid = "g" + str(abs(zlib.crc32(cid.encode("utf-8"))) % 100000)
    N = _num

    s = []
    s.append('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d" '
             'role="img" aria-hidden="true">' % (w, h, w, h))
    s.append("<defs>")
    s.append('<linearGradient id="%s-sky" x1="0" y1="0" x2="0" y2="1">'
             '<stop offset="0" stop-color="%s"/><stop offset="0.52" stop-color="%s"/>'
             '<stop offset="1" stop-color="%s"/></linearGradient>' % (gid, p["top"], p["mid"], p["low"]))
    s.append('<radialGradient id="%s-glow" cx="0.5" cy="0.5" r="0.5">'
             '<stop offset="0" stop-color="%s" stop-opacity="0.50"/>'
             '<stop offset="0.42" stop-color="%s" stop-opacity="0.16"/>'
             '<stop offset="1" stop-color="%s" stop-opacity="0"/></radialGradient>'
             % (gid, p["accent"], p["accent"], p["accent"]))
    s.append('<radialGradient id="%s-disc" cx="0.38" cy="0.34" r="0.68">'
             '<stop offset="0" stop-color="#fdfbf4" stop-opacity="0.96"/>'
             '<stop offset="0.62" stop-color="%s" stop-opacity="0.85"/>'
             '<stop offset="1" stop-color="%s" stop-opacity="0.55"/></radialGradient>'
             % (gid, p["accent"], p["accent"]))
    s.append('<linearGradient id="%s-mist" x1="0" y1="0" x2="0" y2="1">'
             '<stop offset="0" stop-color="%s" stop-opacity="0"/>'
             '<stop offset="0.5" stop-color="%s" stop-opacity="0.30"/>'
             '<stop offset="1" stop-color="%s" stop-opacity="0"/></linearGradient>'
             % (gid, p["top"], p["accent"], p["top"]))
    s.append('<radialGradient id="%s-vig" cx="0.5" cy="0.42" r="0.74">'
             '<stop offset="0.42" stop-color="#000" stop-opacity="0"/>'
             '<stop offset="1" stop-color="#000" stop-opacity="0.66"/></radialGradient>' % gid)
    s.append('<filter id="%s-b" filterUnits="userSpaceOnUse" x="%s" y="%s" width="%s" height="%s">'
             '<feGaussianBlur stdDeviation="16"/></filter>'
             % (gid, N(-w * .2), N(-h * .3), N(w * 1.4), N(h * 1.6)))
    s.append("</defs>")

    s.append('<rect width="%d" height="%d" fill="url(#%s-sky)"/>' % (w, h, gid))
    s.append(stars(cid, int(r.uniform(70, 120)), w, h * 0.66))

    # 星云微光
    s.append('<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="%s" opacity="0.08" '
             'filter="url(#%s-b)" transform="rotate(%s %s %s)"/>'
             % (N(w * r.uniform(.35, .7)), N(h * r.uniform(.18, .34)), N(w * .42), N(h * .12),
                p["accent"], gid, N(r.uniform(-18, -6)), N(w * .5), N(h * .26)))

    # 月：满月或残月
    mx = w * r.uniform(.56, .74)
    my = h * r.uniform(.19, .34)
    mr = r.uniform(46, 78)
    s.append('<circle cx="%s" cy="%s" r="%s" fill="url(#%s-glow)"/>'
             % (N(mx), N(my), N(mr * 3.2), gid))
    if r.random() < 0.3:
        s.append(crescent(mx, my, mr, p["accent"], opacity=.55, rot=r.uniform(-40, 40)))
        s.append('<circle cx="%s" cy="%s" r="%s" fill="none" stroke="%s" stroke-width="1" '
                 'opacity="0.35"/>' % (N(mx), N(my), N(mr), p["accent"]))
    else:
        s.append('<circle cx="%s" cy="%s" r="%s" fill="url(#%s-disc)" opacity="0.42"/>'
                 % (N(mx), N(my), N(mr), gid))
        s.append('<circle cx="%s" cy="%s" r="%s" fill="none" stroke="%s" stroke-width="1" '
                 'opacity="0.45"/>' % (N(mx), N(my), N(mr), p["accent"]))
        s.append('<circle cx="%s" cy="%s" r="%s" fill="%s" opacity="0.10" filter="url(#%s-b)"/>'
                 % (N(mx - mr * .28), N(my + mr * .1), N(mr * .5), p["ink"], gid))

    # 云带
    for i in range(2):
        cy = h * r.uniform(.30, .52)
        s.append('<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="%s" opacity="%s" filter="url(#%s-b)"/>'
                 % (N(w * r.uniform(.3, .72)), N(cy), N(w * r.uniform(.22, .4)), N(h * r.uniform(.014, .028)),
                    p["accent"], N(r.uniform(.10, .20)), gid))

    # 远山两三层
    s.append(ridge(cid + "a", w, h * r.uniform(.66, .73), h * r.uniform(.14, .22), step=r.choice([120, 140, 160]),
                   color=p["ink"], opacity=0.55))
    s.append(ridge(cid + "b", w, h * r.uniform(.76, .82), h * r.uniform(.09, .15), step=r.choice([90, 100, 120]),
                   color=p["ink"], opacity=0.75))

    # 地平线处的薄雾
    s.append('<rect y="%s" width="%d" height="%s" fill="url(#%s-mist)" opacity="0.8"/>'
             % (N(h * .70), w, N(h * .18), gid))

    # 母题
    fn = MOTIFS.get(cluster, motif_crystal)
    mscale = min(w, h) * r.uniform(.19, .27)
    mrot = r.uniform(-9, 9)
    s.append('<g transform="rotate(%s %s %s)">' % (N(mrot), N(w * .60), N(h * .48)))
    s.append('<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="url(#%s-glow)" opacity="0.55"/>'
             % (N(w * .60), N(h * .48), N(mscale * 1.15), N(mscale * 1.15), gid))
    if kind == "talent":
        s.append(rune_ring(w * .60, h * .48, mscale * 1.16, p["accent"], n=20, opacity=.30, seg=.42))
    s.append(fn(w * .60, h * .48, mscale, p))
    s.append("</g>")

    # 前景剪影
    s.append('<rect y="%s" width="%d" height="%s" fill="%s" opacity="0.95"/>'
             % (N(h * .845), w, N(h * .155), p["ink"]))
    s.append('<path d="M0,%s C%s,%s %s,%s %d,%s L%d,%s L0,%s Z" fill="%s"/>'
             % (N(h * .865), N(w * .28), N(h * .845), N(w * .56), N(h * .885),
                w, N(h * .845), w, h, h, p["ink"]))

    nfig = 1 if kind == "talent" else r.choice([1, 1, 2, 3])
    for i in range(nfig):
        fx = w * (0.14 + i * 0.17 + r.uniform(-.02, .02))
        fs = r.uniform(.62, .92) * (1.0 - i * 0.10)
        if i == 0:
            fk = "lance" if kind == "unit" else ("bow" if kind == "archer" else "cloak")
        else:
            fk = r.choice(["cloak", "lance", "bow"])
        s.append(figure(fx, h * (0.895 + i * 0.012), fs, p["ink"], accent=p["accent"], kind=fk))

    # 粒子、光带、暗角
    s.append(motes(cid, int(r.uniform(30, 55)), w, h, p["accent"], 0.10, 0.9))
    s.append('<path d="M%s,%s L%s,%s L%s,%s L%s,%s Z" fill="%s" opacity="0.035"/>'
             % (N(mx - 80), N(my + 30), N(mx + 30), N(my + 30),
                N(mx - 170), h, N(mx - 300), h, p["accent"]))
    s.append('<rect width="%d" height="%d" fill="url(#%s-vig)"/>' % (w, h, gid))
    s.append("</svg>")
    return "".join(s)


# ══════════════════════════════ 英雄档案背景 ══════════════════════════════

def hero_art(hid, cluster, kind="spell", w=1200, h=760):
    p = PALETTE.get(cluster, PALETTE["core-crystal"])
    r = _rng(hid + "-hero")
    gid = "h" + str(abs(zlib.crc32((hid + "-hero").encode("utf-8"))) % 100000)
    N = _num
    s = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d" '
         'role="img" aria-hidden="true">' % (w, h, w, h)]
    s.append("<defs>")
    s.append('<linearGradient id="%s-sky" x1="0" y1="0" x2="0" y2="1">'
             '<stop offset="0" stop-color="%s"/><stop offset="0.55" stop-color="%s"/>'
             '<stop offset="1" stop-color="%s"/></linearGradient>' % (gid, p["top"], p["mid"], p["low"]))
    s.append('<radialGradient id="%s-glow" cx="0.5" cy="0.5" r="0.5">'
             '<stop offset="0" stop-color="%s" stop-opacity="0.55"/>'
             '<stop offset="1" stop-color="%s" stop-opacity="0"/></radialGradient>' % (gid, p["accent"], p["accent"]))
    s.append('<radialGradient id="%s-disc" cx="0.4" cy="0.35" r="0.7">'
             '<stop offset="0" stop-color="#fdfbf4" stop-opacity="0.9"/>'
             '<stop offset="1" stop-color="%s" stop-opacity="0.25"/></radialGradient>' % (gid, p["accent"]))
    s.append('<radialGradient id="%s-vig" cx="0.5" cy="0.42" r="0.78">'
             '<stop offset="0.4" stop-color="#000" stop-opacity="0"/>'
             '<stop offset="1" stop-color="#000" stop-opacity="0.72"/></radialGradient>' % gid)
    s.append('<filter id="%s-b" filterUnits="userSpaceOnUse" x="0" y="0" width="%d" height="%d">'
             '<feGaussianBlur stdDeviation="26"/></filter>' % (gid, w, h))
    s.append("</defs>")

    s.append('<rect width="%d" height="%d" fill="url(#%s-sky)"/>' % (w, h, gid))
    s.append(stars(hid + "-hs", 220, w, h * 0.72))
    s.append('<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="%s" opacity="0.10" filter="url(#%s-b)" '
             'transform="rotate(-9 %s %s)"/>'
             % (N(w * .5), N(h * .3), N(w * .5), N(h * .16), p["accent"], gid, N(w * .5), N(h * .3)))

    # 月
    mx, my, mr = w * .615, h * .30, h * .16
    s.append('<circle cx="%s" cy="%s" r="%s" fill="url(#%s-glow)"/>' % (N(mx), N(my), N(mr * 4.2), gid))
    s.append('<circle cx="%s" cy="%s" r="%s" fill="url(#%s-disc)"/>' % (N(mx), N(my), N(mr), gid))
    s.append('<circle cx="%s" cy="%s" r="%s" fill="none" stroke="%s" stroke-width="1" opacity="0.4"/>'
             % (N(mx), N(my), N(mr), p["accent"]))

    # 云带
    for i in range(3):
        s.append('<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="%s" opacity="%s" filter="url(#%s-b)"/>'
                 % (N(w * r.uniform(.25, .8)), N(h * r.uniform(.28, .5)), N(w * r.uniform(.22, .34)),
                    N(h * r.uniform(.012, .022)), p["accent"], N(r.uniform(.14, .24)), gid))

    # 山脊
    s.append(ridge(hid + "ra", w, h * .64, h * .17, step=190, color=p["ink"], opacity=0.55))
    s.append(ridge(hid + "rb", w, h * .735, h * .12, step=150, color=p["ink"], opacity=0.8))

    # 徽记（低透明度，作为背景纹样）
    fn = MOTIFS.get(cluster, motif_crystal)
    ecol = p["accent"]
    s.append('<g opacity="0.16">' + rune_ring(w * .60, h * .36, h * .24, ecol, n=26, opacity=.5, seg=.5) + '</g>')

    # 前景地面
    s.append('<rect y="%s" width="%d" height="%s" fill="%s" opacity="0.96"/>'
             % (N(h * .855), w, N(h * .145), p["ink"]))
    s.append('<path d="M0,%s C%s,%s %s,%s %d,%s L%d,%d L0,%d Z" fill="%s"/>'
             % (N(h * .872), N(w * .26), N(h * .855), N(w * .58), N(h * .89),
                w, N(h * .858), w, h, h, p["ink"]))

    # 人物
    fk = "lance" if kind == "unit" else "bow" if kind == "archer" else "cloak"
    s.append(figure(w * .265, h * .90, 3.9, p["ink"], accent=p["accent"], kind=fk))
    s.append(figure(w * .475, h * .895, 2.1, p["ink"], accent=p["accent"],
                    kind=r.choice(["cloak", "lance", "bow"])))
    s.append(figure(w * .565, h * .888, 1.6, p["ink"], accent=p["accent"], kind="cloak"))

    # 粒子与暗角
    s.append(motes(hid + "-hm", 80, w, h * .9, p["accent"], 0.06, 0.85))
    s.append('<path d="M%s,%s L%s,%s L%s,%d L%s,%d Z" fill="%s" opacity="0.03"/>'
             % (N(mx - 120), N(my + 60), N(mx + 60), N(my + 60), N(mx - 260), h, N(mx - 420), h, p["accent"]))
    s.append('<rect width="%d" height="%d" fill="url(#%s-vig)"/>' % (w, h, gid))
    s.append("</svg>")
    return "".join(s)


# ══════════════════════════════ 阵营徽记 ══════════════════════════════

def sigil(faction, size=220):
    c1, c2, acc = FACTION_TINT.get(faction, FACTION_TINT["通用"])
    if faction == "新的勇者":
        inner = (crescent(0, -14, 52, acc, opacity=.95) +
                 '<path d="M0,-96 L0,74" stroke="%s" stroke-width="3" opacity="0.9"/>'
                 '<polygon points="0,-118 14,-96 -14,-96" fill="%s" opacity="0.9"/>'
                 '<path d="M-40,40 C-18,18 18,18 40,40" fill="none" stroke="%s" stroke-width="3" '
                 'opacity="0.85"/>' % (acc, acc, acc))
    elif faction == "同盟军":
        inner = (sunburst(0, 0, 30, 96, 16, acc, opacity=.55) +
                 '<circle cx="0" cy="0" r="30" fill="none" stroke="%s" stroke-width="3"/>'
                 '<circle cx="0" cy="0" r="14" fill="%s" opacity="0.5"/>' % (acc, acc))
    elif faction == "魔王军":
        inner = ('<path d="M0,-92 C36,-92 62,-58 62,-14 C62,52 34,86 0,96 C-34,86 -62,52 -62,-14 '
                 'C-62,-58 -36,-92 0,-92 Z" fill="%s" opacity="0.12"/>'
                 '<path d="M0,-92 C36,-92 62,-58 62,-14 C62,52 34,86 0,96 C-34,86 -62,52 -62,-14 '
                 'C-62,-58 -36,-92 0,-92 Z" fill="none" stroke="%s" stroke-width="2.4" opacity="0.85"/>'
                 '<polygon points="-38,-72 -62,-114 -26,-94" fill="%s" opacity="0.9"/>'
                 '<polygon points="38,-72 62,-114 26,-94" fill="%s" opacity="0.9"/>'
                 '<path d="M0,-50 L-7,-16 L6,14 L-3,52" fill="none" stroke="%s" stroke-width="2.6" '
                 'opacity="0.9"/>'
                 % (acc, acc, acc, acc, acc))
    else:
        inner = (rune_ring(0, 0, 84, acc, n=16, opacity=.5) +
                 '<circle cx="0" cy="0" r="52" fill="none" stroke="%s" stroke-width="2" opacity="0.8"/>'
                 '<path d="M0,-40 L0,40 M-40,0 L40,0" stroke="%s" stroke-width="2" opacity="0.7"/>'
                 % (acc, acc))
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="-130 -130 260 260" width="%d" height="%d" '
            'role="img" aria-label="%s"><defs>'
            '<radialGradient id="sg" cx="0.5" cy="0.5" r="0.5">'
            '<stop offset="0" stop-color="%s" stop-opacity="0.22"/>'
            '<stop offset="1" stop-color="%s" stop-opacity="0"/></radialGradient></defs>'
            '<circle cx="0" cy="0" r="126" fill="url(#sg)"/>'
            '<circle cx="0" cy="0" r="108" fill="none" stroke="%s" stroke-width="1" opacity="0.28"/>'
            '<circle cx="0" cy="0" r="96" fill="none" stroke="%s" stroke-width="0.7" opacity="0.18"/>'
            '<g>%s</g></svg>'
            % (size, size, faction, acc, c2, acc, acc, inner))

# ══════════════════════════════ 主视觉 ══════════════════════════════

def banner(w=2400, h=1400):
    r = _rng("banner-night")
    N = _num
    s = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d" '
         'preserveAspectRatio="xMidYMid slice" role="img" aria-label="长歌·主视觉">' % (w, h, w, h)]

    s.append("<defs>")
    s.append('<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">'
             '<stop offset="0" stop-color="#04050c"/>'
             '<stop offset="0.34" stop-color="#0b0e1f"/>'
             '<stop offset="0.58" stop-color="#1b1a33"/>'
             '<stop offset="0.74" stop-color="#3a3352"/>'
             '<stop offset="0.84" stop-color="#5d5170"/>'
             '<stop offset="0.93" stop-color="#2a2540"/>'
             '<stop offset="1" stop-color="#0d0e18"/></linearGradient>')
    s.append('<radialGradient id="moon" cx="0.40" cy="0.34" r="0.70">'
             '<stop offset="0" stop-color="#fdfbf3"/>'
             '<stop offset="0.52" stop-color="#eceef2"/>'
             '<stop offset="0.85" stop-color="#cdd6e2"/>'
             '<stop offset="1" stop-color="#a9b7c9"/></radialGradient>')
    s.append('<radialGradient id="halo" cx="0.5" cy="0.5" r="0.5">'
             '<stop offset="0" stop-color="#e6edf9" stop-opacity="0.40"/>'
             '<stop offset="0.30" stop-color="#c3d0e6" stop-opacity="0.16"/>'
             '<stop offset="0.62" stop-color="#93a4c2" stop-opacity="0.05"/>'
             '<stop offset="1" stop-color="#7d8dab" stop-opacity="0"/></radialGradient>')
    s.append('<linearGradient id="haze" x1="0" y1="0" x2="0" y2="1">'
             '<stop offset="0" stop-color="#8d84a6" stop-opacity="0"/>'
             '<stop offset="0.5" stop-color="#a79cc0" stop-opacity="0.16"/>'
             '<stop offset="1" stop-color="#6d6485" stop-opacity="0"/></linearGradient>')
    s.append('<linearGradient id="glowband" x1="0" y1="0" x2="0" y2="1">'
             '<stop offset="0" stop-color="#d8c7e6" stop-opacity="0"/>'
             '<stop offset="0.55" stop-color="#e2cfa8" stop-opacity="0.13"/>'
             '<stop offset="1" stop-color="#c9b7a0" stop-opacity="0"/></linearGradient>')
    s.append('<radialGradient id="vig" cx="0.5" cy="0.46" r="0.78">'
             '<stop offset="0.40" stop-color="#000" stop-opacity="0"/>'
             '<stop offset="1" stop-color="#000" stop-opacity="0.76"/></radialGradient>')
    s.append('<filter id="soft40" filterUnits="userSpaceOnUse" x="%s" y="%s" width="%s" height="%s">'
             '<feGaussianBlur stdDeviation="40"/></filter>'
             % (N(-w * .25), N(-h * .25), N(w * 1.5), N(h * 1.5)))
    s.append('<filter id="soft16" filterUnits="userSpaceOnUse" x="%s" y="%s" width="%s" height="%s">'
             '<feGaussianBlur stdDeviation="16"/></filter>'
             % (N(-w * .15), N(-h * .15), N(w * 1.3), N(h * 1.3)))
    s.append('<filter id="soft5" filterUnits="userSpaceOnUse" x="%s" y="%s" width="%s" height="%s">'
             '<feGaussianBlur stdDeviation="5"/></filter>'
             % (N(-w * .05), N(-h * .05), N(w * 1.1), N(h * 1.1)))
    s.append("</defs>")

    # 夜空
    s.append('<rect width="%d" height="%d" fill="url(#sky)"/>' % (w, h))
    s.append(stars("banner-night", 420, w, h * .82, color="#eef3ff"))

    # 银河微光
    s.append('<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="#8f9ec4" opacity="0.07" '
             'filter="url(#soft40)" transform="rotate(-14 %s %s)"/>'
             % (N(w * .55), N(h * .30), N(w * .46), N(h * .13), N(w * .55), N(h * .30)))

    # 月与光晕
    mx, my, mr = w * .535, h * .335, h * .150
    s.append('<circle cx="%s" cy="%s" r="%s" fill="url(#halo)"/>' % (N(mx), N(my), N(mr * 3.4)))
    s.append('<circle cx="%s" cy="%s" r="%s" fill="url(#halo)" opacity="0.7"/>'
             % (N(mx), N(my), N(mr * 1.7)))
    s.append('<circle cx="%s" cy="%s" r="%s" fill="url(#moon)"/>' % (N(mx), N(my), N(mr)))
    for dx, dy, rr, op in ((-.30, -.22, .22, .05), (.24, .10, .16, .045), (.02, .34, .12, .04),
                           (-.20, .26, .09, .035), (.33, -.40, .10, .03), (-.05, -.05, .32, .025)):
        s.append('<circle cx="%s" cy="%s" r="%s" fill="#b6bfcd" opacity="%s" filter="url(#soft16)"/>'
                 % (N(mx + mr * dx), N(my + mr * dy), N(mr * rr), N(op)))

    # 云带（模糊的横向条带，掠过月亮）
    for cx_, cy, rx, ry, op in ((w * .40, h * .315, w * .30, h * .020, .10),
                                (w * .62, h * .395, w * .26, h * .016, .085),
                                (w * .46, h * .475, w * .34, h * .014, .07),
                                (w * .66, h * .545, w * .24, h * .012, .055)):
        s.append('<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="#c8c0d8" opacity="%s" '
                 'filter="url(#soft40)"/>'
                 % (N(cx_), N(cy), N(rx), N(ry), N(op)))

    # 大雁
    for i, (bx, by, bs) in enumerate(((w * .70, h * .20, 1.0), (w * .735, h * .228, .8), (w * .675, h * .245, .7))):
        s.append('<path d="M%s,%s q%s,%s %s,%s q%s,%s %s,%s" fill="none" stroke="#0a0c16" '
                 'stroke-width="2.2" opacity="0.55"/>'
                 % (N(bx - 16 * bs), N(by), N(8 * bs), N(-9 * bs), N(16 * bs), N(0),
                    N(8 * bs), N(9 * bs), N(16 * bs), N(0)))

    # 地平线暖光
    s.append('<rect x="0" y="%s" width="%d" height="%s" fill="url(#glowband)"/>'
             % (N(h * .60), w, N(h * .26)))

    def band(base, amp, color, op, pts=8, blur=None, shift=0.0):
        xs = [w * i / (pts - 1) for i in range(pts)]
        ys = [base + r.uniform(-amp, amp) for _ in xs]
        ys[-1] = base + r.uniform(-amp * .4, amp * .4)
        d = "M%s,%s" % (N(xs[0] + shift * w), N(ys[0]))
        for i in range(1, pts):
            mxp = (xs[i - 1] + xs[i]) / 2
            d += " C%s,%s %s,%s %s,%s" % (N(mxp + shift * w), N(ys[i - 1]), N(mxp + shift * w),
                                          N(ys[i]), N(xs[i] + shift * w), N(ys[i]))
        d += " L%s,%d L%s,%d Z" % (N(w + shift * w), h, N(-w * .1 + shift * w), h)
        flt = ' filter="url(#%s)"' % blur if blur else ''
        s.append('<path d="%s" fill="%s" opacity="%s"%s/>' % (d, color, N(op), flt))

    # 远山（带薄雾）
    band(h * .775, h * .030, "#3b3a5c", .55)
    band(h * .795, h * .026, "#2b2b47", .70, shift=0.0, blur="soft5")
    band(h * .818, h * .024, "#1e1f36", .85)

    # 云海横带
    s.append('<rect x="0" y="%s" width="%d" height="%s" fill="url(#haze)" opacity="0.9"/>'
             % (N(h * .80), w, N(h * .05)))

    # 中景山脊
    band(h * .862, h * .022, "#15172a", .95)

    # 城堡（中景山脊之上）
    cx, cy = w * .615, h * .872
    towers = [(-330, 46, 86, 1), (-268, 34, 132, 1), (-212, 52, 74, 0), (-150, 58, 158, 1),
              (-84, 40, 108, 1), (-26, 64, 214, 1), (44, 42, 148, 1), (106, 56, 96, 0),
              (168, 34, 120, 1), (228, 44, 78, 1), (292, 30, 56, 0)]
    g = ['<g fill="#101123">']
    # 主墙体
    g.append('<rect x="%s" y="%s" width="%s" height="%s"/>'
             % (N(cx - 372), N(cy - 64), N(744), N(80)))
    for dx, tw, th, roof in towers:
        g.append('<rect x="%s" y="%s" width="%s" height="%s"/>'
                 % (N(cx + dx - tw / 2), N(cy - th), N(tw), N(th + 64)))
        if roof:
            rh = tw * 1.15
            g.append('<polygon points="%s,%s %s,%s %s,%s"/>'
                     % (N(cx + dx - tw / 2 - 4), N(cy - th), N(cx + dx + tw / 2 + 4), N(cy - th),
                        N(cx + dx), N(cy - th - rh)))
    # 城墙垛口
    for i in range(22):
        bx = cx - 368 + i * 34
        g.append('<rect x="%s" y="%s" width="%s" height="%s"/>' % (N(bx), N(cy - 76), N(16), N(16)))
    g.append("</g>")
    s.append("".join(g))

    # 窗火
    for i in range(70):
        wx = cx + r.uniform(-350, 350)
        wy = cy - r.uniform(16, 210)
        s.append('<rect x="%s" y="%s" width="%s" height="%s" fill="#f4c684" opacity="%s"/>'
                 % (N(wx), N(wy), N(r.uniform(2, 4.5)), N(r.uniform(4, 10)),
                    N(r.uniform(.18, .68))))
    s.append('<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="#f0b46e" opacity="0.10" '
             'filter="url(#soft40)"/>' % (N(cx), N(cy - 80), N(360), N(160)))

    # 近景山脊与地面
    band(h * .905, h * .016, "#0a0b14", 1.0)
    s.append('<path d="M0,%s C%s,%s %s,%s %s,%s L%d,%d L0,%d Z" fill="#05060c"/>'
             % (N(h * .945), N(w * .12), N(h * .925), N(w * .24), N(h * .958),
                N(w * .30), N(h * .938), w, h, h))

    # 山崖上的骑士与旗
    kx, ky, ks = w * .295, h * .952, 2.35
    s.append('<g transform="translate(%s %s) scale(%s)">' % (N(kx), N(ky), N(ks)))
    s.append('<ellipse cx="6" cy="4" rx="54" ry="9" fill="#000" opacity="0.45"/>')
    s.append('<path d="M0,-58 C-13,-54 -18,-40 -17,-22 C-16,-9 -22,1 -27,4 L27,4 C22,1 16,-9 17,-22 '
             'C18,-40 13,-54 0,-58 Z" fill="#04050a"/>')
    s.append('<path d="M0,-58 C13,-54 18,-40 17,-22 C16,-9 22,1 27,4" fill="none" stroke="#c9d6e8" '
             'stroke-width="1.5" opacity="0.30"/>')
    s.append('<circle cx="0" cy="-63" r="7" fill="#04050a"/>')
    s.append('<path d="M-10,-68 L10,-66 L8,-71 L-9,-72 Z" fill="#04050a"/>')
    s.append('<path d="M15,-98 L19,6" stroke="#080b13" stroke-width="3"/>')
    s.append('<polygon points="15,-98 8,-81 22,-81" fill="#080b13"/>')
    s.append('<path d="M-14,-92 C-54,-84 -78,-56 -82,-24 C-60,-33 -38,-37 -14,-40 Z" fill="#0b0d18"/>')
    s.append('<path d="M-14,-92 C-54,-84 -78,-56 -82,-24" fill="none" stroke="#c8a86a" stroke-width="1.1" '
             'opacity="0.30"/>')
    s.append("</g>")

    # 右前景枯树
    s.append('<g fill="none" stroke="#04050a" stroke-width="3" opacity="0.95" stroke-linecap="round">'
             '<path d="M%s,%s C%s,%s %s,%s %s,%s"/>'
             '<path d="M%s,%s C%s,%s %s,%s %s,%s"/>'
             '<path d="M%s,%s C%s,%s %s,%s %s,%s"/>'
             '<path d="M%s,%s C%s,%s %s,%s %s,%s"/></g>'
             % (N(w * .875), h, N(w * .885), N(h * .96), N(w * .872), N(h * .90), N(w * .892), N(h * .845),
                N(w * .892), N(h * .878), N(w * .925), N(h * .862), N(w * .948), N(h * .830),
                N(w * .905), N(h * .842), N(w * .902), N(h * .808), N(w * .878), N(h * .792),
                N(w * .902), N(h * .808), N(w * .930), N(h * .790), N(w * .958), N(h * .800),
                N(w * .890), N(h * .905), N(w * .862), N(h * .886), N(w * .846), N(h * .860)))

    # 前景草
    for i in range(120):
        gx = r.uniform(-20, w + 20)
        gh = r.uniform(8, 30)
        s.append('<path d="M%s,%s q%s,-%s %s,-%s" fill="none" stroke="#04050b" stroke-width="%s" '
                 'opacity="0.85"/>' % (N(gx), N(h), N(r.uniform(-6, 6)), N(gh * .55),
                                       N(r.uniform(-5, 5)), N(gh), N(r.uniform(1.1, 2.2))))

    # 萤火
    s.append(motes("banner-night", 110, w, h, "#f4d9a2", 0.52, 0.99))
    s.append('<rect width="%d" height="%d" fill="url(#vig)"/>' % (w, h))
    s.append("</svg>")
    return "".join(s)
