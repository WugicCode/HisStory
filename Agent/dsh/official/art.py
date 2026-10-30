# -*- coding: utf-8 -*-
"""纸本双色丝网印风格：卡牌图版、人物纹章、概念图。

所有图形均为本文件生成的 SVG，不依赖外部素材。
"""

import hashlib
import math
import random
from pathlib import Path

PAPER = "#f4efe4"
INK = "#171c26"
INK2 = "#1d2430"
GOLD = "#a67c3d"
CRIMSON = "#9e3b3b"
BLUE = "#2f4a6b"
GREEN = "#46624d"
VIOLET = "#5b4a6b"

ACCENTS = {
    "gold": GOLD,
    "crimson": CRIMSON,
    "blue": BLUE,
    "green": GREEN,
    "violet": VIOLET,
}

QUALITY_LABEL = {
    "N": "普通",
    "R": "稀有",
    "E": "史诗",
    "L": "传说",
    "域外": "域外",
    "觉醒": "觉醒",
}

QUALITY_LATIN = {
    "N": "COMMON",
    "R": "RARE",
    "E": "EPIC",
    "L": "LEGEND",
    "域外": "OUTSIDE",
    "觉醒": "AWAKEN",
}


def _seed(text):
    return int(hashlib.md5(text.encode("utf-8")).hexdigest()[:8], 16)


def _rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def _mix(a, b, t):
    ra, ga, ba = _rgb(a)
    rb, gb, bb = _rgb(b)
    return "#%02x%02x%02x" % (
        round(ra + (rb - ra) * t),
        round(ga + (gb - ga) * t),
        round(ba + (bb - ba) * t),
    )


def _esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            .replace('"', "&quot;"))


def _text(x, y, s, size=14, fill=INK, anchor="start", spacing=0, opacity=1, weight=400):
    return (
        f'<text x="{x}" y="{y}" font-family="Noto Serif SC, Songti SC, SimSun, serif" '
        f'font-size="{size}" fill="{fill}" text-anchor="{anchor}" '
        f'letter-spacing="{spacing}" opacity="{opacity}" font-weight="{weight}">{_esc(s)}</text>'
    )


def _latin(x, y, s, size=10, fill=INK, anchor="start", spacing=3, opacity=0.75):
    return (
        f'<text x="{x}" y="{y}" font-family="Georgia, Times New Roman, serif" '
        f'font-size="{size}" fill="{fill}" text-anchor="{anchor}" '
        f'letter-spacing="{spacing}" opacity="{opacity}">{_esc(s)}</text>'
    )


# ---------------------------------------------------------------- fields

def _field(kind, a, f, rng, w=504, h=420):
    """Return the decorative background of the plate's art window."""
    out = []

    if kind == "orb":
        cx, cy = w * 0.5, h * 0.42
        out.append(f'<circle cx="{cx}" cy="{cy}" r="150" fill="none" stroke="{a}" stroke-width="1.1" opacity=".75"/>')
        out.append(f'<circle cx="{cx}" cy="{cy}" r="112" fill="none" stroke="{f}" stroke-width=".8" opacity=".35"/>')
        out.append(f'<circle cx="{cx}" cy="{cy}" r="74" fill="{a}" opacity=".18"/>')
        out.append(f'<circle cx="{cx}" cy="{cy}" r="74" fill="none" stroke="{a}" stroke-width="1.4"/>')
        for i in range(12):
            ang = math.radians(i * 30 + 8)
            x1, y1 = cx + math.cos(ang) * 88, cy + math.sin(ang) * 88
            x2, y2 = cx + math.cos(ang) * 168, cy + math.sin(ang) * 168
            out.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{f}" stroke-width=".6" opacity=".28"/>')
        out.append(f'<line x1="0" y1="{h*0.78:.1f}" x2="{w}" y2="{h*0.78:.1f}" stroke="{f}" stroke-width=".8" opacity=".3"/>')

    elif kind == "arc":
        out.append(f'<path d="M -30 {h*0.9:.0f} Q {w*0.45:.0f} {h*0.05:.0f} {w+30} {h*0.72:.0f}" fill="none" stroke="{a}" stroke-width="1.6" opacity=".85"/>')
        out.append(f'<path d="M -30 {h*0.98:.0f} Q {w*0.45:.0f} {h*0.18:.0f} {w+30} {h*0.82:.0f}" fill="none" stroke="{f}" stroke-width=".8" opacity=".35"/>')
        out.append(f'<circle cx="{w*0.26:.0f}" cy="{h*0.62:.0f}" r="5" fill="{a}"/>')
        for i in range(17):
            t = i / 16
            x = -30 + (w + 60) * t
            y = (1 - t) ** 2 * h * 0.9 + 2 * (1 - t) * t * h * 0.05 + t * t * h * 0.72
            out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="1.6" fill="{f}" opacity=".55"/>')

    elif kind == "split":
        out.append(f'<polygon points="0,0 {w},0 {w},{h*0.55:.0f} 0,{h*0.9:.0f}" fill="{a}" opacity=".14"/>')
        out.append(f'<line x1="-20" y1="{h*0.9:.0f}" x2="{w+20}" y2="{h*0.55:.0f}" stroke="{a}" stroke-width="1.3" opacity=".8"/>')
        out.append(f'<circle cx="{w*0.38:.0f}" cy="{h*0.44:.0f}" r="86" fill="none" stroke="{f}" stroke-width="1.1" opacity=".55"/>')
        out.append(f'<circle cx="{w*0.38:.0f}" cy="{h*0.44:.0f}" r="86" fill="{f}" opacity=".05"/>')
        for i in range(6):
            y = h * 0.12 + i * 34
            out.append(f'<line x1="{w*0.62:.0f}" y1="{y:.0f}" x2="{w-30}" y2="{y-16:.0f}" stroke="{f}" stroke-width=".7" opacity=".35"/>')

    elif kind == "wave":
        for i in range(9):
            y = 36 + i * 42
            amp = 12 + (i % 3) * 7
            d = f"M -20 {y}"
            for x in range(0, w + 40, 20):
                d += f" Q {x+10} {y-amp} {x+20} {y}"
            out.append(f'<path d="{d}" fill="none" stroke="{a if i % 2 == 0 else f}" stroke-width="{1.2 if i % 2 == 0 else .6}" opacity="{.55 if i % 2 == 0 else .25}"/>')
        out.append(f'<circle cx="{w*0.72:.0f}" cy="{h*0.3:.0f}" r="42" fill="{a}" opacity=".16"/>')

    elif kind == "rays":
        cx, cy = w * 0.5, h * 0.38
        out.append(f'<circle cx="{cx}" cy="{cy}" r="54" fill="{a}" opacity=".2"/>')
        out.append(f'<circle cx="{cx}" cy="{cy}" r="54" fill="none" stroke="{a}" stroke-width="1.2"/>')
        for i in range(40):
            ang = math.radians(i * 9 + rng.random() * 3)
            r1 = 68 + rng.random() * 22
            r2 = 170 + rng.random() * 70
            x1, y1 = cx + math.cos(ang) * r1, cy + math.sin(ang) * r1
            x2, y2 = cx + math.cos(ang) * r2, cy + math.sin(ang) * r2
            out.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{f}" stroke-width="{.5 + rng.random()*.6:.2f}" opacity="{.15 + rng.random()*.35:.2f}"/>')
        out.append(f'<line x1="0" y1="{h*0.82:.0f}" x2="{w}" y2="{h*0.82:.0f}" stroke="{f}" stroke-width=".8" opacity=".3"/>')

    elif kind == "grid":
        step = 36
        for x in range(0, w + 1, step):
            out.append(f'<line x1="{x}" y1="0" x2="{x}" y2="{h}" stroke="{f}" stroke-width=".5" opacity=".18"/>')
        for y in range(0, h + 1, step):
            out.append(f'<line x1="0" y1="{y}" x2="{w}" y2="{y}" stroke="{f}" stroke-width=".5" opacity=".18"/>')
        out.append(f'<rect x="{step*4}" y="{step*3}" width="{step*4}" height="{step*4}" fill="{a}" opacity=".16"/>')
        out.append(f'<circle cx="{w*0.55:.0f}" cy="{h*0.48:.0f}" r="98" fill="none" stroke="{a}" stroke-width="1.2" opacity=".8"/>')
        out.append(f'<circle cx="{w*0.55:.0f}" cy="{h*0.48:.0f}" r="98" fill="{PAPER if f == INK else INK}" opacity=".18"/>')

    elif kind == "spiral":
        cx, cy = w * 0.5, h * 0.5
        pts = []
        for i in range(260):
            t = i / 18
            r = 5 + t * 8.2
            ang = t
            pts.append(f"{cx + math.cos(ang) * r:.1f},{cy + math.sin(ang) * r:.1f}")
        out.append(f'<polyline points="{" ".join(pts)}" fill="none" stroke="{a}" stroke-width="1.3" opacity=".85"/>')
        for i in range(18):
            ang = rng.random() * math.tau
            r = 30 + rng.random() * 160
            out.append(f'<circle cx="{cx+math.cos(ang)*r:.1f}" cy="{cy+math.sin(ang)*r:.1f}" r="{1.2+rng.random()*2:.1f}" fill="{f}" opacity=".4"/>')

    elif kind == "ridge":
        layers = [
            (h * 0.86, h * 0.58, a, 0.22),
            (h * 0.92, h * 0.66, f, 0.12),
            (h * 0.98, h * 0.76, a, 0.16),
        ]
        for base, peak, col, op in layers:
            d = f"M 0 {base} L 70 {peak+30} L 150 {peak-20} L 232 {peak+42} L 320 {peak-38} L 408 {peak+26} L 504 {peak-6} L 504 {h} L 0 {h} Z"
            out.append(f'<path d="{d}" fill="{col}" opacity="{op}"/>')
            out.append(f'<path d="{d}" fill="none" stroke="{col}" stroke-width=".8" opacity=".55"/>')
        out.append(f'<circle cx="{w*0.72:.0f}" cy="{h*0.24:.0f}" r="46" fill="{a}" opacity=".18"/>')

    elif kind == "step":
        for i in range(7):
            x = 30 + i * 34
            y = h * 0.82 - i * 36
            out.append(f'<rect x="{x}" y="{y}" width="{w-x-30}" height="{i*36+20}" fill="none" stroke="{a if i%2==0 else f}" stroke-width="{1.1 if i%2==0 else .5}" opacity="{.55 if i%2==0 else .25}"/>')
        out.append(f'<line x1="30" y1="{h*0.9:.0f}" x2="{w-30}" y2="{h*0.9:.0f}" stroke="{f}" stroke-width="1" opacity=".4"/>')

    elif kind == "void":
        out.append(f'<rect width="{w}" height="{h}" fill="{INK2}"/>')
        for _ in range(90):
            x, y = rng.random() * w, rng.random() * h
            out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rng.random()*1.5+.3:.1f}" fill="{f}" opacity="{rng.random()*.55+.08:.2f}"/>')
        out.append(f'<circle cx="{w*0.68:.0f}" cy="{h*0.32:.0f}" r="54" fill="{a}" opacity=".22"/>')
        out.append(f'<circle cx="{w*0.68:.0f}" cy="{h*0.32:.0f}" r="54" fill="none" stroke="{a}" stroke-width="1"/>')
        out.append(f'<path d="M 0 {h*0.82:.0f} L 70 {h*0.74:.0f} L 130 {h*0.8:.0f} L 210 {h*0.7:.0f} L 300 {h*0.79:.0f} L 380 {h*0.72:.0f} L 504 {h*0.8:.0f}" fill="none" stroke="{f}" stroke-width=".7" opacity=".3"/>')

    elif kind == "rain":
        for i in range(48):
            x = rng.random() * w
            y = rng.random() * h * 0.8
            ln = 12 + rng.random() * 34
            out.append(f'<line x1="{x:.1f}" y1="{y:.1f}" x2="{x-5:.1f}" y2="{y+ln:.1f}" stroke="{f}" stroke-width="{.5+rng.random()*.6:.2f}" opacity="{.12+rng.random()*.3:.2f}"/>')
        for i in range(7):
            cx = 40 + i * 70
            out.append(f'<ellipse cx="{cx}" cy="{h*0.86 + (i%2)*10}" rx="{16+rng.random()*18:.0f}" ry="3.2" fill="none" stroke="{a}" stroke-width=".8" opacity=".5"/>')

    else:
        out.append(f'<circle cx="{w/2}" cy="{h/2}" r="120" fill="none" stroke="{a}" stroke-width="1"/>')

    return "\n".join(out)


# ---------------------------------------------------------------- motifs

def _motifs():
    return {
        "arrow": '<path d="M18 82 L78 22"/><path d="M56 22 L80 20 L78 44"/><path d="M18 82 L10 90 M18 82 L26 74"/>',
        "banner": '<path d="M28 88 V12"/><path d="M28 18 H78 V54 H28"/><path d="M28 18 L40 30 L28 42"/>',
        "bell": '<path d="M50 16 C28 16 26 42 24 58 H76 C74 42 72 16 50 16 Z"/><path d="M18 58 H82"/><path d="M44 70 C44 80 56 80 56 70"/><circle cx="50" cy="11" r="3"/>',
        "book": '<path d="M12 22 C30 18 42 24 50 34 C58 24 70 18 88 22 V78 C70 74 58 78 50 88 C42 78 30 74 12 78 Z"/><path d="M50 34 V88"/>',
        "bow": '<path d="M26 14 C62 28 70 72 26 88"/><path d="M26 14 L26 88"/><path d="M20 50 H86"/><path d="M76 44 L86 50 L76 56"/>',
        "burst": '<path d="M50 8 V92 M8 50 H92 M20 20 L80 80 M80 20 L20 80"/><circle cx="50" cy="50" r="12"/>',
        "chain": '<ellipse cx="34" cy="50" rx="24" ry="15" transform="rotate(-35 34 50)"/><ellipse cx="66" cy="50" rx="24" ry="15" transform="rotate(-35 66 50)"/>',
        "coin": '<circle cx="50" cy="50" r="34"/><circle cx="50" cy="50" r="25" opacity=".6"/><path d="M50 32 L58 50 L50 68 L42 50 Z"/>',
        "corona": '<circle cx="50" cy="50" r="24"/><path d="M50 6 V18 M50 82 V94 M6 50 H18 M82 50 H94 M19 19 L27 27 M73 73 L81 81 M81 19 L73 27 M27 73 L19 81"/>',
        "crack": '<path d="M18 12 L42 38 L30 48 L56 62 L44 72 L78 90"/>',
        "crimson": '<path d="M14 62 C24 30 44 18 62 24 C78 30 86 48 72 62 C60 74 38 76 22 68 Z" fill="currentColor" fill-opacity=".2"/><path d="M22 66 C36 52 54 40 78 36" opacity=".6"/>',
        "crown": '<path d="M14 74 L22 30 L38 50 L50 22 L62 50 L78 30 L86 74 Z"/><path d="M14 74 H86"/><circle cx="50" cy="40" r="3"/>',
        "crystal": '<path d="M50 8 L78 28 L70 74 L50 92 L30 74 L22 28 Z"/><path d="M50 8 L50 92 M22 28 L50 44 L78 28"/><path d="M30 74 L50 58 L70 74"/>',
        "dagger": '<path d="M50 8 L58 42 L50 52 L42 42 Z"/><path d="M30 54 H70"/><path d="M50 52 V86"/><path d="M44 86 H56"/>',
        "dawn": '<path d="M8 70 H92"/><path d="M22 70 C22 44 38 28 50 28 C62 28 78 44 78 70"/><path d="M50 10 V22 M14 30 L22 38 M86 30 L78 38"/>',
        "dream": '<path d="M20 58 C12 46 20 30 36 30 C40 18 58 14 68 24 C86 22 92 42 80 52 C86 64 72 74 60 68 C50 80 30 74 20 58 Z"/><path d="M36 48 C44 42 56 42 64 48"/><path d="M42 56 C47 60 53 60 58 56"/>',
        "drop": '<path d="M50 8 C50 8 22 42 22 60 C22 76 34 88 50 88 C66 88 78 76 78 60 C78 42 50 8 50 8 Z"/><path d="M38 64 C38 72 44 78 50 78" opacity=".6"/>',
        "eclipse": '<circle cx="42" cy="50" r="30" fill="currentColor" fill-opacity=".2"/><circle cx="58" cy="50" r="30" fill="none"/><path d="M58 20 A30 30 0 0 1 58 80" opacity=".5"/>',
        "engrave": '<circle cx="50" cy="50" r="36"/><path d="M22 38 L78 62 M22 50 L78 74 M22 62 L78 86 M22 26 L78 50" opacity=".35"/><circle cx="50" cy="50" r="16"/>',
        "eye": '<path d="M10 50 C28 22 72 22 90 50 C72 78 28 78 10 50 Z"/><circle cx="50" cy="50" r="15"/><circle cx="50" cy="50" r="6" fill="currentColor"/><path d="M50 8 V20 M50 80 V92"/>',
        "feather": '<path d="M30 84 C34 50 52 20 76 12 C78 42 64 70 30 84 Z"/><path d="M30 84 L62 52 M42 72 L58 36 M50 58 L72 40" opacity=".55"/>',
        "flute": '<rect x="14" y="44" width="72" height="12" rx="6"/><circle cx="30" cy="50" r="2.2"/><circle cx="44" cy="50" r="2.2"/><circle cx="58" cy="50" r="2.2"/><circle cx="72" cy="50" r="2.2"/><path d="M86 50 L94 44 V56 Z" fill="currentColor" fill-opacity=".2"/>',
        "gather": '<circle cx="26" cy="34" r="16"/><circle cx="74" cy="34" r="16"/><circle cx="50" cy="72" r="16"/><path d="M36 44 L46 60 M64 44 L54 60 M42 34 H58"/>',
        "hammer": '<path d="M50 26 V92"/><path d="M22 26 H78 V44 H22 Z"/><path d="M30 18 H70" opacity=".55"/><path d="M20 92 H80"/>',
        "scale": '<path d="M50 12 V84"/><path d="M18 30 H82"/><path d="M18 30 L8 52 H28 Z"/><path d="M82 30 L72 52 H92 Z"/><path d="M34 88 H66"/>',
        "serpent": '<path d="M76 14 C54 14 44 28 52 40 C62 56 46 62 34 54 C22 46 16 58 22 70 C28 82 46 88 66 82"/><circle cx="72" cy="18" r="4"/><path d="M76 22 L86 26"/>',
        "mirror": '<ellipse cx="50" cy="48" rx="30" ry="38"/><path d="M50 14 V82" opacity=".4"/><path d="M30 34 C38 28 44 28 50 34" opacity=".6"/><path d="M18 90 H82"/>',
        "mask": '<path d="M22 26 C34 18 66 18 78 26 C82 46 72 74 50 86 C28 74 18 46 22 26 Z"/><path d="M34 44 C38 40 44 40 48 44 M52 44 C56 40 62 40 66 44"/><path d="M40 64 C46 68 54 68 60 64"/>',
        "shadow": '<path d="M50 12 C42 12 38 20 38 28 C38 34 42 38 44 42 C34 46 28 58 28 74 C28 84 34 90 50 90 C66 90 72 84 72 74 C72 58 66 46 56 42 C58 38 62 34 62 28 C62 20 58 12 50 12 Z" fill="currentColor" fill-opacity=".18"/>',
        "wind": '<path d="M8 34 H66 C80 34 80 16 66 16 C57 16 53 23 53 30"/><path d="M8 50 H82 C96 50 96 32 82 32"/><path d="M8 66 H58 C70 66 70 50 58 50"/><path d="M22 82 H48" opacity=".5"/>',
        "halo": '<ellipse cx="50" cy="34" rx="32" ry="12"/><circle cx="50" cy="58" r="24"/><path d="M50 18 V8"/><path d="M30 58 C34 70 66 70 70 58" opacity=".5"/>',
        "hand": '<path d="M34 84 C26 70 22 52 28 36 C32 26 42 30 42 40 V50 C42 34 48 22 56 26 C62 30 58 44 58 50 C62 38 70 34 74 40 C78 48 70 60 68 70 C64 84 52 90 34 84 Z"/><path d="M34 62 C42 56 58 56 64 64" opacity=".5"/>',
        "hood": '<path d="M50 12 C28 12 18 34 20 56 C22 74 34 88 50 88 C66 88 78 74 80 56 C82 34 72 12 50 12 Z"/><path d="M32 50 C34 36 44 30 50 30 C56 30 66 36 68 50 C60 44 40 44 32 50 Z" fill="currentColor" fill-opacity=".12"/><path d="M20 56 L8 72 M80 56 L92 72"/>',
        "horizon": '<path d="M6 64 H94"/><path d="M28 64 C28 44 36 32 50 32 C64 32 72 44 72 64"/><path d="M50 14 V24 M24 30 L30 36 M76 30 L70 36"/><path d="M14 76 H86" opacity=".4"/>',
        "infinity": '<path d="M50 50 C34 26 10 38 18 56 C24 70 42 64 50 50 C58 36 76 30 82 44 C90 62 66 74 50 50 Z"/>',
        "ivy": '<path d="M20 88 C34 68 30 46 46 30 C58 18 72 18 82 10"/><path d="M38 56 C28 48 28 38 38 34 C46 40 46 50 38 56 Z"/><path d="M50 40 C42 30 46 20 56 18 C62 28 58 38 50 40 Z"/><path d="M62 26 C58 16 64 8 74 8 C78 18 72 26 62 26 Z"/>',
        "key": '<circle cx="32" cy="38" r="18"/><circle cx="32" cy="38" r="7"/><path d="M44 50 L84 90"/><path d="M70 76 L78 68 M78 84 L86 76"/>',
        "laurel": '<path d="M20 86 C40 70 58 44 72 12"/><path d="M36 66 C24 64 20 52 28 46 C36 50 40 58 36 66 Z"/><path d="M46 52 C36 46 36 34 46 30 C52 38 52 46 46 52 Z"/><path d="M56 38 C48 30 52 18 62 16 C66 26 62 34 56 38 Z"/><path d="M66 24 C62 14 68 6 78 6 C80 16 74 22 66 24 Z"/>',
        "leaf": '<path d="M18 82 C26 40 50 18 86 14 C82 50 60 74 18 82 Z"/><path d="M18 82 L66 34 M38 62 L64 58 M48 50 L74 44" opacity=".55"/>',
        "lily": '<path d="M50 86 V42"/><path d="M50 50 C30 48 18 30 24 14 C40 18 50 32 50 50 Z"/><path d="M50 50 C70 48 82 30 76 14 C60 18 50 32 50 50 Z"/><path d="M50 42 C44 24 50 8 58 4 C64 18 60 34 50 42 Z"/>',
        "lock": '<rect x="26" y="46" width="48" height="38" rx="5"/><path d="M36 46 V32 C36 20 64 20 64 32 V46"/><circle cx="50" cy="64" r="4"/><path d="M50 68 V76"/>',
        "meridian": '<path d="M50 6 V94"/><circle cx="50" cy="20" r="5"/><circle cx="50" cy="50" r="5"/><circle cx="50" cy="80" r="5"/><path d="M24 34 C36 28 44 28 50 34 C56 40 66 40 76 34" opacity=".55"/><path d="M24 66 C36 60 44 60 50 66 C56 72 66 72 76 66" opacity=".55"/>',
        "moon": '<path d="M62 10 C38 18 26 38 32 58 C38 76 56 88 76 84 C58 74 50 58 54 42 C57 28 68 16 62 10 Z" fill="currentColor" fill-opacity=".15"/>',
        "net": '<path d="M10 20 L90 80 M10 80 L90 20 M28 10 L28 90 M50 6 L50 94 M72 10 L72 90 M10 32 L90 32 M6 50 L94 50 M10 68 L90 68"/>',
        "note": '<ellipse cx="34" cy="76" rx="14" ry="10"/><path d="M48 76 V18"/><path d="M48 18 C62 18 72 26 76 36 C66 34 56 38 48 46"/>',
        "orb": '<circle cx="50" cy="50" r="36"/><ellipse cx="50" cy="50" rx="36" ry="14" transform="rotate(-25 50 50)" opacity=".6"/><circle cx="38" cy="36" r="7" fill="currentColor" fill-opacity=".2"/>',
        "prism": '<path d="M50 10 L88 82 H12 Z"/><path d="M50 10 L50 82 M50 82 L30 46 M50 82 L70 46"/><path d="M88 82 L96 92 M12 82 L4 92" opacity=".5"/>',
        "ring": '<circle cx="50" cy="50" r="36"/><circle cx="50" cy="50" r="22"/><path d="M50 8 V18 M50 82 V92 M8 50 H18 M82 50 H92"/>',
        "road": '<path d="M40 8 C46 30 28 44 36 62 C42 76 34 84 30 94"/><path d="M56 8 C62 30 44 44 52 62 C58 76 50 84 46 94"/><path d="M44 18 H52 M40 32 H48 M42 48 H50 M38 64 H46 M36 80 H44" opacity=".6"/>',
        "root": '<path d="M50 8 V54"/><path d="M50 30 C36 30 26 40 22 54 M50 36 C64 36 74 46 78 60 M50 54 C40 62 34 74 32 88 M50 54 C60 62 66 74 68 88 M50 54 V92"/>',
        "scroll": '<path d="M20 22 C12 22 10 36 20 36 H74 C84 36 84 22 74 22 H20 Z"/><path d="M20 22 V78 C10 78 10 92 20 92 H74 C84 92 84 78 74 78 V36"/><path d="M30 48 H64 M30 60 H64 M30 72 H54" opacity=".5"/>',
        "seed": '<ellipse cx="50" cy="66" rx="18" ry="24"/><path d="M50 44 V18"/><path d="M50 30 C40 30 34 22 34 14 C44 14 50 20 50 30 Z"/><path d="M50 36 C60 36 66 28 66 20 C56 20 50 26 50 36 Z"/>',
        "shield": '<path d="M50 8 L84 22 V50 C84 74 68 88 50 94 C32 88 16 74 16 50 V22 Z"/><path d="M50 22 V78 M30 44 H70" opacity=".55"/>',
        "smoke": '<path d="M18 82 C30 70 22 58 34 48 C46 38 38 26 50 18 C62 10 70 24 62 34 C54 44 66 54 58 66 C50 78 58 84 68 88" fill="none"/>',
        "spark": '<path d="M50 6 L58 42 L94 50 L58 58 L50 94 L42 58 L6 50 L42 42 Z" fill="currentColor" fill-opacity=".12"/>',
        "star": '<path d="M50 8 L61 38 L92 38 L67 56 L76 88 L50 68 L24 88 L33 56 L8 38 L39 38 Z" fill="currentColor" fill-opacity=".12"/>',
        "stone": '<path d="M22 38 L38 14 L70 10 L88 32 L82 70 L58 90 L26 78 Z"/><path d="M38 14 L48 40 L26 78 M48 40 L70 10 M48 40 L82 70 M48 40 L58 90" opacity=".45"/>',
        "sun": '<circle cx="50" cy="50" r="24"/><path d="M50 6 V17 M50 83 V94 M6 50 H17 M83 50 H94 M19 19 L27 27 M73 73 L81 81 M81 19 L73 27 M27 73 L19 81"/>',
        "sword": '<path d="M50 6 L57 46 L50 56 L43 46 Z"/><path d="M28 62 H72"/><path d="M50 56 V88"/><circle cx="50" cy="90" r="4"/>',
        "thorn": '<path d="M16 86 C30 68 28 46 44 32 C56 20 70 16 86 8"/><path d="M32 60 L18 52 M40 48 L28 34 M50 38 L42 20 M62 28 L58 10"/><path d="M64 22 L78 20 M50 36 L40 46"/>',
        "thread": '<path d="M8 68 C26 68 24 30 42 30 C60 30 58 68 76 68 C90 68 92 46 82 36"/><path d="M8 80 C30 80 30 18 52 18 C72 18 72 80 94 80" opacity=".45"/>',
        "tower": '<rect x="30" y="30" width="40" height="58"/><path d="M24 30 V18 H38 V26 H44 V18 H56 V26 H62 V18 H76 V30"/><rect x="44" y="56" width="12" height="20"/><path d="M30 44 H70 M30 72 H70" opacity=".4"/>',
        "trap": '<path d="M12 64 C24 46 36 38 50 42 C64 38 76 46 88 64"/><path d="M12 64 L22 54 L30 66 L40 56 L50 68 L60 56 L70 66 L78 54 L88 64"/><path d="M50 4 V26" opacity=".5"/>',
        "tree": '<path d="M50 92 V44"/><path d="M50 58 C32 58 22 46 22 32 M50 52 C68 52 78 40 78 26 M50 44 C38 38 34 26 40 16 M50 44 C62 38 66 26 60 16 M50 36 C50 22 56 14 64 10"/>',
        "truth": '<path d="M50 8 L90 82 H10 Z"/><path d="M24 56 C36 44 64 44 76 56 C64 68 36 68 24 56 Z"/><circle cx="50" cy="56" r="7" fill="currentColor" fill-opacity=".2"/>',
        "veil": '<path d="M24 8 C16 34 20 62 12 92 M40 8 C34 34 38 62 30 92 M56 8 C50 34 54 62 46 92 M72 8 C66 34 70 62 62 92"/><path d="M12 72 C32 62 66 62 86 72" opacity=".45"/>',
        "wall": '<path d="M12 24 H88 V88 H12 Z"/><path d="M12 44 H88 M12 66 H88 M36 24 V44 M64 24 V44 M24 44 V66 M52 44 V66 M76 44 V66 M36 66 V88 M64 66 V88"/>',
        "wand": '<path d="M18 84 L70 30"/><path d="M62 22 L70 30 L78 22 L70 14 Z" fill="currentColor" fill-opacity=".15"/><path d="M78 8 L80 16 M88 18 L82 22 M84 34 L78 30" opacity=".55"/>',
        "web": '<path d="M50 50 L50 6 M50 50 L88 26 M50 50 L92 62 M50 50 L70 92 M50 50 L30 92 M50 50 L8 62 M50 50 L12 26"/><path d="M50 22 C66 22 78 34 78 50 C78 66 66 78 50 78 C34 78 22 66 22 50 C22 34 34 22 50 22 Z" opacity=".6"/><path d="M50 36 C58 36 64 42 64 50 C64 58 58 64 50 64 C42 64 36 58 36 50 C36 42 42 36 50 36 Z" opacity=".4"/>',
        "wind": '<path d="M8 34 C30 34 34 18 52 18 C66 18 72 26 72 34 C72 44 60 46 50 46"/><path d="M8 58 C36 58 44 44 62 44 C74 44 82 50 82 58 C82 68 68 70 58 70"/><path d="M18 80 C36 80 44 70 56 70" opacity=".5"/>',
    }


MOTIFS = {}


def motif(name, x, y, size=100, color=INK, opacity=1.0, rotate=0):
    body = MOTIFS.get(name) or MOTIFS["star"]
    return (
        f'<g transform="translate({x - size/2:.1f} {y - size/2:.1f}) rotate({rotate} {size/2} {size/2}) '
        f'scale({size/100:.4f})" color="{color}" opacity="{opacity}" '
        f'fill="none" stroke="currentColor" stroke-width="2.4" '
        f'stroke-linecap="round" stroke-linejoin="round">{body}</g>'
    )


# ---------------------------------------------------------------- card plate

def card_svg(card, meta, index, total=86):
    q = card.get("quality") or "N"
    accent = ACCENTS.get(meta["art"]["tone"], GOLD)
    dark = q == "域外"
    bg = INK if dark else PAPER
    fg = PAPER if dark else INK
    muted = _mix(fg, bg, 0.45)
    tint = _mix(bg, accent, 0.13 if not dark else 0.18)
    rng = random.Random(_seed(card["id"]))
    W, H = 600, 750

    art_w, art_h = 504, 420
    ax, ay = 48, 92

    field = _field(meta["art"]["field"], accent, fg, rng, art_w, art_h)
    motifs = meta["art"]["motifs"][:3]
    positions = [
        (ax + art_w * 0.27, ay + art_h * 0.34, 132),
        (ax + art_w * 0.73, ay + art_h * 0.28, 104),
        (ax + art_w * 0.55, ay + art_h * 0.70, 118),
    ]
    rng.shuffle(positions)
    motif_svg = []
    for i, m in enumerate(motifs):
        px, py, ps = positions[i]
        col = accent if i % 2 == 0 else fg
        motif_svg.append(motif(m, px, py, ps, col, 0.88 if not dark else 0.9, rotate=(-8 + rng.random() * 16)))

    # quality marks
    extras = []
    if q == "域外":
        extras.append(f'<text x="{W-48}" y="{ay+art_h-18}" font-family="Georgia,serif" font-size="11" letter-spacing="3" fill="{accent}" text-anchor="end" opacity=".85">OUTSIDE / NOT COLLECTIBLE</text>')
    elif q == "觉醒":
        extras.append(f'<polygon points="{ax+art_w-120},{ay} {ax+art_w},{ay} {ax+art_w},{ay+120}" fill="{accent}" opacity=".2"/>')
        extras.append(f'<text x="{ax+art_w-16}" y="{ay+24}" font-family="Georgia,serif" font-size="10" letter-spacing="2" fill="{fg}" text-anchor="end" opacity=".8">AWAKENING</text>')
    elif q == "L":
        extras.append(f'<rect x="{ax}" y="{ay}" width="{art_w}" height="{art_h}" fill="none" stroke="{accent}" stroke-width="2"/>')
        extras.append(f'<rect x="{ax+8}" y="{ay+8}" width="{art_w-16}" height="{art_h-16}" fill="none" stroke="{fg}" stroke-width=".6" opacity=".5"/>')
    elif q == "E":
        for cx, cy in ((ax + 8, ay + 8), (ax + art_w - 8, ay + 8), (ax + 8, ay + art_h - 8), (ax + art_w - 8, ay + art_h - 8)):
            extras.append(f'<path d="M{cx-10} {cy} H{cx+10} M{cx} {cy-10} V{cy+10}" stroke="{accent}" stroke-width="1" opacity=".8"/>')
    elif q == "R":
        for i in range(3):
            extras.append(f'<rect x="{ax+art_w-24}" y="{ay+16+i*9}" width="5" height="5" fill="{accent}" opacity=".8"/>')

    # name band for domain cards
    band = ""
    if dark:
        band = f'<rect x="24" y="512" width="552" height="150" fill="{INK2}"/>'
    elif q == "觉醒":
        band = f'<polygon points="24,512 576,512 576,640 24,662" fill="{accent}" opacity=".12"/>'

    # header / footer
    header = (
        _latin(48, 64, "HIS STORY / CARD ARCHIVE", 9, fg, spacing=3.2, opacity=.7)
        + _latin(552, 64, "PLATE %03d" % index, 9, fg, "end", 2.4, .7)
    )
    footer = (
        _latin(48, 720, "HIS STORY", 9, fg, spacing=3.4, opacity=.55)
        + _latin(552, 720, "%03d / %03d" % (index, total), 9, fg, "end", 2.4, .55)
    )

    # name sizing
    name = card["display"]
    n = max(1, len(name))
    name_size = min(38, int(400 / n * 1.18))
    if name_size > 38:
        name_size = 38

    cost_txt = "—" if card.get("cost") is None else str(card["cost"])
    panel = card.get("panel") or {}
    if panel:
        panel_txt = "C %s · A %s · D %s" % (panel.get("c", "—"), panel.get("a", "—"), panel.get("d", "—"))
    else:
        panel_txt = ""

    q_label = QUALITY_LABEL.get(q, q)
    q_latin = QUALITY_LATIN.get(q, "")
    faction = card.get("faction") or ""
    kind = card.get("kind") or ""
    type_line = card.get("type_line") or ""

    body = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<defs>
  <clipPath id="artclip"><rect x="{ax}" y="{ay}" width="{art_w}" height="{art_h}"/></clipPath>
  <filter id="grain"><feTurbulence type="fractalNoise" baseFrequency="0.85" numOctaves="2" stitchTiles="stitch"/><feColorMatrix type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 0.16 0"/></filter>
</defs>
<rect width="{W}" height="{H}" fill="{bg}"/>
<rect width="{W}" height="{H}" fill="{fg}" filter="url(#grain)" opacity=".16"/>
<rect x="24" y="24" width="552" height="702" fill="none" stroke="{fg}" stroke-width="1.1" opacity=".55"/>
<rect x="36" y="36" width="528" height="678" fill="none" stroke="{accent}" stroke-width=".8" opacity=".5"/>
<path d="M24 50 V24 H50 M550 24 H576 V50 M576 700 V726 H550 M50 726 H24 V700" fill="none" stroke="{accent}" stroke-width="1.4" opacity=".85"/>
{header}
{band}
<g clip-path="url(#artclip)">
  <rect x="{ax}" y="{ay}" width="{art_w}" height="{art_h}" fill="{tint}"/>
  <g transform="translate({ax} {ay})">{field}</g>
  {''.join(extras)}
  <text x="{ax+art_w-18}" y="{ay+art_h-28}" font-family="Georgia, serif" font-size="168" fill="{fg}" opacity=".07" text-anchor="end">{index:02d}</text>
  {''.join(motif_svg)}
</g>
<rect x="{ax}" y="{ay}" width="{art_w}" height="{art_h}" fill="none" stroke="{fg}" stroke-width="1" opacity=".55"/>
<rect x="{ax+7}" y="{ay+7}" width="{art_w-14}" height="{art_h-14}" fill="none" stroke="{fg}" stroke-width=".5" opacity=".22"/>
<circle cx="78" cy="584" r="29" fill="{accent}" opacity=".14"/>
<circle cx="78" cy="584" r="29" fill="none" stroke="{accent}" stroke-width="1.2"/>
<text x="78" y="598" font-family="Georgia, serif" font-size="30" fill="{fg}" text-anchor="middle">{cost_txt}</text>
{_text(126, 594, name, name_size, fg, weight=500)}
{_text(126, 624, type_line or kind, 14, muted)}
{_text(126, 648, meta["role"], 12, accent)}
{_text(126, 674, (faction + " · " + q_label).strip(" · "), 12, muted)}
{_latin(552, 648, q_latin, 9, accent, "end", 2)}
{_latin(552, 674, panel_txt, 9, muted, "end", 1.2)}
<line x1="48" y1="694" x2="552" y2="694" stroke="{fg}" stroke-width=".6" opacity=".28"/>
<text x="574" y="380" font-family="Noto Serif SC, Songti SC, serif" font-size="12" fill="{fg}" opacity=".35" transform="rotate(90 574 380)" text-anchor="middle">长歌 · 卡牌档案</text>
{footer}
</svg>'''
    return body


# ---------------------------------------------------------------- sigil

def sigil_svg(latin, motifs, tone, numeral, size=360, subtitle=""):
    accent = ACCENTS.get(tone, GOLD)
    rng = random.Random(_seed(latin + numeral))
    c = size / 2
    r = size * 0.36
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 {size} {size}">',
        f'<rect width="{size}" height="{size}" fill="{PAPER}"/>',
        f'<rect width="{size}" height="{size}" fill="{INK}" opacity=".035"/>',
        f'<circle cx="{c}" cy="{c}" r="{r+30}" fill="none" stroke="{INK}" stroke-width=".7" opacity=".35"/>',
        f'<circle cx="{c}" cy="{c}" r="{r+18}" fill="none" stroke="{accent}" stroke-width=".8" opacity=".6"/>',
        f'<circle cx="{c}" cy="{c}" r="{r}" fill="{accent}" opacity=".08"/>',
        f'<circle cx="{c}" cy="{c}" r="{r}" fill="none" stroke="{INK}" stroke-width="1.1"/>',
    ]
    for i in range(24):
        ang = math.radians(i * 15)
        r1 = r + 20
        r2 = r + (26 if i % 3 == 0 else 22)
        out.append(f'<line x1="{c+math.cos(ang)*r1:.1f}" y1="{c+math.sin(ang)*r1:.1f}" x2="{c+math.cos(ang)*r2:.1f}" y2="{c+math.sin(ang)*r2:.1f}" stroke="{accent}" stroke-width=".6" opacity=".55"/>')
    m1, m2 = (motifs + ["star", "ring"])[:2]
    out.append(motif(m1, c - r * 0.33, c - r * 0.1, r * 0.62, INK, .9, rotate=-8))
    out.append(motif(m2, c + r * 0.33, c + r * 0.12, r * 0.46, accent, .9, rotate=10))
    out.append(_latin(c, c + r + 44, latin.upper(), 9, INK, "middle", 3.2, .65))
    out.append(f'<text x="{c}" y="{c - r - 12}" font-family="Georgia,serif" font-size="11" letter-spacing="3" fill="{accent}" text-anchor="middle">{numeral}</text>')
    out.append('</svg>')
    return "\n".join(out)


# ---------------------------------------------------------------- concept plates

def _plate_base(w, h, dark=False, title="", subtitle="", numeral=""):
    bg = INK if dark else PAPER
    fg = PAPER if dark else INK
    accent = CRIMSON if dark else GOLD
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">',
         f'<rect width="{w}" height="{h}" fill="{bg}"/>',
         f'<rect width="{w}" height="{h}" fill="url(#none)" opacity="0"/>']
    s.append(f'<rect x="26" y="26" width="{w-52}" height="{h-52}" fill="none" stroke="{fg}" stroke-width=".8" opacity=".4"/>')
    s.append(f'<rect x="38" y="38" width="{w-76}" height="{h-76}" fill="none" stroke="{accent}" stroke-width=".6" opacity=".4"/>')
    if numeral:
        s.append(_latin(56, 70, numeral, 10, accent, spacing=3))
    if title:
        s.append(_text(56, 108, title, 26, fg, weight=500))
    if subtitle:
        s.append(_text(56, 136, subtitle, 12, fg, opacity=.6))
    return s, fg, accent


def concept_mana():
    w, h = 1200, 760
    s, fg, a = _plate_base(w, h, False, "魔力、原质与魔能", "THE THREE LAWS OF MAGIC", "PLATE I")
    cx, cy = w * 0.55, h * 0.55
    centers = [(cx, cy - 120, "魔力"), (cx - 135, cy + 80, "原质"), (cx + 135, cy + 80, "魔能")]
    for x, y, label in centers:
        s.append(f'<circle cx="{x}" cy="{y}" r="150" fill="{a}" opacity=".07"/>')
        s.append(f'<circle cx="{x}" cy="{y}" r="150" fill="none" stroke="{a}" stroke-width="1.2" opacity=".8"/>')
        s.append(f'<text x="{x}" y="{y+6}" font-family="Noto Serif SC, Songti SC, serif" font-size="24" fill="{fg}" text-anchor="middle">{label}</text>')
    s.append(f'<path d="M{cx} {cy-120} L{cx-135} {cy+80} L{cx+135} {cy+80} Z" fill="none" stroke="{fg}" stroke-width=".8" opacity=".45"/>')
    s.append(_text(80, h - 100, "第一定律：魔力的流动，实质是原质的重新分布。", 15, fg, opacity=.85))
    s.append(_text(80, h - 70, "第二定律：魔力与原质统一量纲后，总和不变，称为「魔能」。", 15, fg, opacity=.85))
    s.append(_text(80, h - 40, "第三定律：魔能可以与其他能量互相转化，总和不变。", 15, fg, opacity=.85))
    s.append(_latin(w - 56, h - 52, "FUTZE / SCARLIN", 9, a, "end", 2.5, .7))
    s.append('</svg>')
    return "\n".join(s)


def concept_ages():
    w, h = 1200, 760
    s, fg, a = _plate_base(w, h, False, "三代魔法", "THREE AGES OF MAGIC", "PLATE II")
    cols = [("精灵族魔法", "本能 · 环境的原质", "tree", "I"), ("神代魔法", "神谕 · 不可解的奇迹", "dawn", "II"), ("现代魔法", "原质 · 可被教授", "prism", "III")]
    for i, (title, sub, m, num) in enumerate(cols):
        x = 100 + i * 350
        s.append(f'<rect x="{x}" y="190" width="300" height="450" fill="{a}" opacity=".04"/>')
        s.append(f'<rect x="{x}" y="190" width="300" height="450" fill="none" stroke="{fg}" stroke-width=".8" opacity=".4"/>')
        s.append(motif(m, x + 150, 330, 130, a if i == 2 else fg, .9))
        s.append(_text(x + 24, 500, title, 24, fg, weight=500))
        s.append(_text(x + 24, 532, sub, 13, fg, opacity=.65))
        s.append(_latin(x + 24, 590, num, 11, a, spacing=3))
    s.append(_text(100, 710, "现代魔法是唯一被完全理解、可以系统教学的一代；它的代价，是它也被写进了权力的历史。", 14, fg, opacity=.7))
    s.append('</svg>')
    return "\n".join(s)


def concept_redmoon():
    w, h = 1200, 760
    s, fg, a = _plate_base(w, h, True, "红月", "THE RED MOON", "PLATE III")
    rng = random.Random(500)
    for _ in range(120):
        s.append(f'<circle cx="{rng.random()*w:.0f}" cy="{rng.random()*h*.7:.0f}" r="{rng.random()*1.6+.3:.1f}" fill="{PAPER}" opacity="{rng.random()*.5+.1:.2f}"/>')
    s.append(f'<circle cx="{w*0.66:.0f}" cy="{h*0.42:.0f}" r="190" fill="{CRIMSON}" opacity=".22"/>')
    s.append(f'<circle cx="{w*0.66:.0f}" cy="{h*0.42:.0f}" r="190" fill="none" stroke="{CRIMSON}" stroke-width="1.4"/>')
    s.append(f'<circle cx="{w*0.66:.0f}" cy="{h*0.42:.0f}" r="160" fill="none" stroke="{PAPER}" stroke-width=".7" opacity=".35"/>')
    # city silhouette
    x = 80
    rng2 = random.Random(77)
    while x < w - 80:
        bw = 30 + rng2.random() * 55
        bh = 60 + rng2.random() * 150
        s.append(f'<rect x="{x:.0f}" y="{h-110-bh:.0f}" width="{bw:.0f}" height="{bh:.0f}" fill="{INK2}"/>')
        if rng2.random() > .5:
            s.append(f'<path d="M{x:.0f} {h-110-bh:.0f} L{x+bw/2:.0f} {h-140-bh:.0f} L{x+bw:.0f} {h-110-bh:.0f} Z" fill="{INK2}"/>')
        x += bw + 12
    s.append(f'<line x1="26" y1="{h-110}" x2="{w-26}" y2="{h-110}" stroke="{PAPER}" stroke-width=".8" opacity=".35"/>')
    s.append(_text(56, h - 56, "她在愤怒中升起了红月。此后，月亮有了两面。", 15, PAPER, opacity=.8))
    s.append('</svg>')
    return "\n".join(s)


def concept_war():
    w, h = 1200, 760
    s, fg, a = _plate_base(w, h, True, "七贤者", "THE SEVEN SAGES", "PLATE IV")
    names = ["荷珀", "斯卡琳", "克莱斯特", "赫琉思", "阿尔法", "戈伦", "欧若拉"]
    motifs = ["sword", "moon", "stone", "sun", "dagger", "hammer", "dawn"]
    for i, (n, m) in enumerate(zip(names, motifs)):
        x = 90 + i * 148
        s.append(f'<line x1="{x}" y1="190" x2="{x}" y2="600" stroke="{PAPER}" stroke-width="1" opacity=".5"/>')
        s.append(f'<path d="M{x-34} 190 H{x+34} L{x+34} 430 L{x} 470 L{x-34} 430 Z" fill="{CRIMSON}" opacity=".12"/>')
        s.append(motif(m, x, 300, 86, PAPER if i % 2 else CRIMSON, .9))
        s.append(f'<text x="{x}" y="540" font-family="Noto Serif SC, Songti SC, serif" font-size="16" fill="{PAPER}" text-anchor="middle">{n}</text>')
        s.append(_latin(x, 566, "0%d" % (i + 1), 9, CRIMSON, "middle", 2))
    s.append(_text(56, 690, "他们终结了三十年的战争，也把一些问题留给了五百年后。", 15, PAPER, opacity=.75))
    s.append('</svg>')
    return "\n".join(s)


def concept_battlefield():
    w, h = 1200, 760
    s, fg, a = _plate_base(w, h, False, "战场", "A MINIMAL MAP", "PLATE V")
    # minimal structure: five boxes, not a fixed map
    zones = [("末端 · 信仰", "END"), ("战区 II", "II"), ("战区 III", "III"), ("战区 IV", "IV"), ("末端 · 信仰", "END")]
    for i, (label, num) in enumerate(zones):
        x = 70 + i * 216
        s.append(f'<rect x="{x}" y="210" width="196" height="330" fill="{a}" opacity=".04"/>')
        s.append(f'<rect x="{x}" y="210" width="196" height="330" fill="none" stroke="{fg}" stroke-width=".9" opacity=".55"/>')
        s.append(_latin(x + 98, 240, num, 9, a, "middle", 2))
        if i in (0, 4):
            s.append(f'<circle cx="{x+98}" cy="380" r="46" fill="none" stroke="{a}" stroke-width="1.4"/>')
            s.append(f'<path d="M{x+98} 340 V420 M{x+58} 380 H{x+138}" stroke="{a}" stroke-width=".8" opacity=".6"/>')
            s.append(f'<text x="{x+98}" y="386" font-family="Georgia,serif" font-size="16" fill="{fg}" text-anchor="middle">1000</text>')
        else:
            for j in range(2):
                bx = x + 44 + j * 62
                by = 330 + (j % 2) * 62
                s.append(f'<rect x="{bx}" y="{by}" width="46" height="58" fill="none" stroke="{fg}" stroke-width=".8" opacity=".5"/>')
                s.append(f'<circle cx="{bx+23}" cy="{by+22}" r="7" fill="{a}" opacity=".55"/>')
                s.append(f'<line x1="{bx+12}" y1="{by+44}" x2="{bx+34}" y2="{by+44}" stroke="{fg}" stroke-width=".8" opacity=".5"/>')
        s.append(_text(x + 18, 572, label, 12, fg, opacity=.75))
    # arrows
    s.append(f'<path d="M270 620 C360 600 420 620 510 600" fill="none" stroke="{a}" stroke-width="1" marker-end="url(#arrow)"/>')
    s.append(f'<path d="M930 620 C840 600 780 620 690 600" fill="none" stroke="{a}" stroke-width="1"/>')
    s.append(f'<defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="6" refY="4" orient="auto"><path d="M0 0 L8 4 L0 8 Z" fill="{a}"/></marker></defs>')
    s.append(_text(70, 700, "最小结构：战区数量、排布与容量由地图决定；单位从末端加入，再向外移动。", 14, fg, opacity=.7))
    s.append('</svg>')
    return "\n".join(s)


def concept_card():
    w, h = 1200, 760
    s, fg, a = _plate_base(w, h, False, "一张卡的解剖", "ANATOMY OF A CARD", "PLATE VI")
    # schematic card
    x, y, cw, ch = 120, 180, 330, 430
    s.append(f'<rect x="{x}" y="{y}" width="{cw}" height="{ch}" fill="{PAPER}" stroke="{INK}" stroke-width="1.2"/>')
    s.append(f'<rect x="{x+14}" y="{y+14}" width="{cw-28}" height="{ch-28}" fill="none" stroke="{a}" stroke-width=".8"/>')
    s.append(f'<rect x="{x+30}" y="{y+40}" width="{cw-60}" height="210" fill="{a}" opacity=".12"/>')
    s.append(f'<circle cx="{x+cw/2}" cy="{y+145}" r="56" fill="none" stroke="{a}" stroke-width="1"/>')
    s.append(motif("moon", x + cw / 2, y + 145, 90, a, .9))
    s.append(_text(x + 30, y + 300, "卡名", 26, fg, weight=500))
    s.append(_text(x + 30, y + 330, "类型 · 标签", 13, fg, opacity=.6))
    s.append(_text(x + 30, y + 370, "卡文 / 效果", 13, fg, opacity=.75))
    s.append(_text(x + 30, y + 392, "以规则语言写成。", 13, fg, opacity=.55))
    s.append(_text(x + 30, y + 410, "动词与数字都可以被裁定。", 13, fg, opacity=.55))
    # callouts
    call = [(x + cw + 30, y + 60, "图版", "抽象几何与标志性道具"), (x + cw + 30, y + 160, "费用", "左上角的数字"), (x + cw + 30, y + 300, "归属", "英雄 · 阵营 · 品质"), (x + cw + 30, y + 400, "碎碎念", "归档者的读卡笔记")]
    for cx, cy, t, d in call:
        s.append(f'<line x1="{x+cw+12}" y1="{cy}" x2="{cx-12}" y2="{cy}" stroke="{a}" stroke-width=".8" opacity=".6"/>')
        s.append(f'<circle cx="{x+cw+12}" cy="{cy}" r="3" fill="{a}"/>')
        s.append(_text(cx, cy - 4, t, 16, fg, weight=500))
        s.append(_text(cx, cy + 16, d, 12, fg, opacity=.6))
    s.append(_text(56, 700, "卡面是给对手看的；碎碎念是给自己看的。", 14, fg, opacity=.7))
    s.append('</svg>')
    return "\n".join(s)


def concept_road():
    w, h = 1200, 760
    s, fg, a = _plate_base(w, h, True, "", "", "")
    rng = random.Random(1939)
    for _ in range(160):
        s.append(f'<circle cx="{rng.random()*w:.0f}" cy="{rng.random()*h*.75:.0f}" r="{rng.random()*1.5+.3:.1f}" fill="{PAPER}" opacity="{rng.random()*.5+.08:.2f}"/>')
    s.append(f'<circle cx="{w*0.72:.0f}" cy="{h*0.28:.0f}" r="150" fill="{PAPER}" opacity=".9"/>')
    s.append(f'<circle cx="{w*0.72:.0f}" cy="{h*0.28:.0f}" r="150" fill="none" stroke="{PAPER}" stroke-width="1" opacity=".6"/>')
    s.append(f'<circle cx="{w*0.72:.0f}" cy="{h*0.28:.0f}" r="180" fill="{PAPER}" opacity=".05"/>')
    # road
    s.append(f'<path d="M520 760 L610 430 L680 760 Z" fill="{PAPER}" opacity=".06"/>')
    s.append(f'<path d="M548 760 L620 450 M652 760 L636 450" fill="none" stroke="{PAPER}" stroke-width=".8" opacity=".3"/>')
    # figure
    s.append(f'<circle cx="626" cy="486" r="10" fill="{PAPER}" opacity=".85"/>')
    s.append(f'<path d="M626 496 V540 M626 512 L610 528 M626 512 L642 528 M626 540 L612 572 M626 540 L640 572" fill="none" stroke="{PAPER}" stroke-width="3" opacity=".85" stroke-linecap="round"/>')
    s.append(_text(56, 660, "月亮升起之前，先把路走完。", 18, PAPER, opacity=.9))
    s.append(_latin(56, 694, "A ROAD STILL BEING WALKED", 9, CRIMSON, spacing=3))
    s.append('</svg>')
    return "\n".join(s)


def cover_svg(w=1600, h=900):
    rng = random.Random(1029)
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">',
           f'<rect width="{w}" height="{h}" fill="{INK}"/>']
    # faint vertical wash
    out.append(f'<rect width="{w}" height="{h}" fill="url(#wash)" opacity=".7"/>')
    out.append(f'<defs><linearGradient id="wash" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{INK2}"/><stop offset="1" stop-color="{INK}"/></linearGradient></defs>')
    for _ in range(220):
        out.append(f'<circle cx="{rng.random()*w:.0f}" cy="{rng.random()*h*.72:.0f}" r="{rng.random()*1.6+.3:.1f}" fill="{PAPER}" opacity="{rng.random()*.55+.06:.2f}"/>')
    mx, my, mr = w * 0.72, h * 0.30, 190
    out.append(f'<circle cx="{mx}" cy="{my}" r="{mr*1.28:.0f}" fill="{PAPER}" opacity=".04"/>')
    out.append(f'<circle cx="{mx}" cy="{my}" r="{mr}" fill="{PAPER}" opacity=".92"/>')
    out.append(f'<circle cx="{mx}" cy="{my}" r="{mr}" fill="none" stroke="{PAPER}" stroke-width="1" opacity=".55"/>')
    out.append(f'<circle cx="{mx-mr*.18:.0f}" cy="{my-mr*.12:.0f}" r="{mr*.16:.0f}" fill="{INK}" opacity=".035"/>')
    # skyline
    x = -20
    while x < w + 20:
        bw = 26 + rng.random() * 62
        bh = 40 + rng.random() * 190
        out.append(f'<rect x="{x:.0f}" y="{h*.82-bh:.0f}" width="{bw:.0f}" height="{bh:.0f}" fill="{INK2}"/>')
        if rng.random() > .62:
            out.append(f'<path d="M{x:.0f} {h*.82-bh:.0f} L{x+bw/2:.0f} {h*.82-bh-30:.0f} L{x+bw:.0f} {h*.82-bh:.0f} Z" fill="{INK2}"/>')
        x += bw + 9
    out.append(f'<rect x="0" y="{h*.82:.0f}" width="{w}" height="{h*.18:.0f}" fill="{INK2}"/>')
    # road
    out.append(f'<path d="M{w*.46:.0f} {h} L{w*.6:.0f} {h*.55:.0f} L{w*.64:.0f} {h:.0f} Z" fill="{PAPER}" opacity=".05"/>')
    out.append(f'<path d="M{w*.53:.0f} {h} L{w*.605:.0f} {h*.55:.0f}" fill="none" stroke="{PAPER}" stroke-width="1" opacity=".16"/>')
    out.append(f'<path d="M{w*.6:.0f} {h} L{w*.61:.0f} {h*.55:.0f}" fill="none" stroke="{PAPER}" stroke-width="1" opacity=".16"/>')
    # tiny figure
    fx, fy = w * 0.607, h * 0.60
    out.append(f'<circle cx="{fx:.0f}" cy="{fy:.0f}" r="7" fill="{PAPER}" opacity=".8"/>')
    out.append(f'<path d="M{fx:.0f} {fy+7:.0f} V{fy+36:.0f} M{fx:.0f} {fy+16:.0f} L{fx-11:.0f} {fy+27:.0f} M{fx:.0f} {fy+16:.0f} L{fx+11:.0f} {fy+27:.0f} M{fx:.0f} {fy+36:.0f} L{fx-9:.0f} {fy+58:.0f} M{fx:.0f} {fy+36:.0f} L{fx+9:.0f} {fy+58:.0f}" fill="none" stroke="{PAPER}" stroke-width="2.4" opacity=".8" stroke-linecap="round"/>')
    out.append('</svg>')
    return "\n".join(out)


def game_cover_svg(w=1600, h=900):
    """游戏编封面：随机地图的最小结构、几张牌、一轮月。无文字，文字由网页叠上去。"""
    rng = random.Random(1939)
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">',
           f'<rect width="{w}" height="{h}" fill="{INK}"/>',
           f'<defs><linearGradient id="gfade" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{INK}" stop-opacity="0"/><stop offset="1" stop-color="{INK}" stop-opacity=".92"/></linearGradient>'
           f'<linearGradient id="gleft" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{INK}" stop-opacity=".97"/><stop offset=".58" stop-color="{INK}" stop-opacity=".78"/><stop offset="1" stop-color="{INK}" stop-opacity="0"/></linearGradient></defs>']
    for _ in range(210):
        out.append(f'<circle cx="{rng.random()*w:.0f}" cy="{rng.random()*h*.8:.0f}" r="{rng.random()*1.5+.3:.1f}" fill="{PAPER}" opacity="{rng.random()*.5+.04:.2f}"/>')
    mx, my, mr = w * .76, h * .26, 168
    out.append(f'<circle cx="{mx}" cy="{my}" r="{mr*1.38:.0f}" fill="{PAPER}" opacity=".035"/>')
    out.append(f'<circle cx="{mx}" cy="{my}" r="{mr}" fill="{PAPER}" opacity=".88"/>')
    out.append(f'<circle cx="{mx}" cy="{my}" r="{mr}" fill="none" stroke="{PAPER}" stroke-width="1" opacity=".5"/>')
    # five zones
    zone_w, zone_h, gap = 214, 300, 44
    total = zone_w * 5 + gap * 4
    x0 = (w - total) / 2
    y0 = 505
    for i in range(5):
        x = x0 + i * (zone_w + gap)
        edge = i in (0, 4)
        stroke = GOLD if edge else PAPER
        op = ".42" if edge else ".15"
        out.append(f'<rect x="{x:.0f}" y="{y0}" width="{zone_w}" height="{zone_h}" fill="none" stroke="{stroke}" stroke-width="1" opacity="{op}"/>')
        out.append(f'<line x1="{x:.0f}" y1="{y0+26}" x2="{x+zone_w:.0f}" y2="{y0+26}" stroke="{stroke}" stroke-width="1" opacity="{op}"/>')
        out.append(f'<text x="{x+12:.0f}" y="{y0+18}" font-family="Georgia,serif" font-size="10" letter-spacing="3" fill="{PAPER}" opacity=".34">ZONE 0{i+1}</text>')
        if edge:
            # faith diamond
            cx, cy = x + zone_w / 2, y0 + zone_h * .54
            out.append(f'<path d="M{cx:.0f} {cy-24:.0f} L{cx+24:.0f} {cy:.0f} L{cx:.0f} {cy+24:.0f} L{cx-24:.0f} {cy:.0f} Z" fill="none" stroke="{GOLD}" stroke-width="1.2" opacity=".62"/>')
            out.append(f'<circle cx="{cx:.0f}" cy="{cy:.0f}" r="4" fill="{GOLD}" opacity=".62"/>')
        else:
            for j in range(2):
                cw, ch = 74, 100
                cx = x + 26 + j * 92
                cy = y0 + 54 + (18 if j else 0)
                out.append(f'<rect x="{cx:.0f}" y="{cy:.0f}" width="{cw}" height="{ch}" fill="{PAPER}" opacity=".035" stroke="{PAPER}" stroke-width="1" stroke-opacity=".18"/>')
                out.append(f'<circle cx="{cx+cw/2:.0f}" cy="{cy+32:.0f}" r="13" fill="none" stroke="{PAPER}" stroke-width="1" opacity=".2"/>')
                out.append(f'<line x1="{cx+14:.0f}" y1="{cy+76}" x2="{cx+cw-14:.0f}" y2="{cy+76}" stroke="{PAPER}" stroke-width="1" opacity=".14"/>')
    # connecting line behind zones
    out.append(f'<path d="M{x0-40:.0f} {y0+zone_h+38:.0f} C{w*.3:.0f} {y0+zone_h+82:.0f}, {w*.7:.0f} {y0+zone_h+82:.0f}, {x0+total+40:.0f} {y0+zone_h+38:.0f}" fill="none" stroke="{GOLD}" stroke-width="1" opacity=".32"/>')
    out.append(f'<rect x="0" y="0" width="{w*.62:.0f}" height="{h}" fill="url(#gleft)"/>')
    out.append(f'<rect x="0" y="{h*.58:.0f}" width="{w}" height="{h*.42:.0f}" fill="url(#gfade)"/>')
    out.append('</svg>')
    return "\n".join(out)


# ---------------------------------------------------------------- build helpers

def build_all(outdir, cards, contents, total=86):
    outdir = Path(outdir)
    (outdir / "cards").mkdir(parents=True, exist_ok=True)
    (outdir / "heroes").mkdir(parents=True, exist_ok=True)
    (outdir / "concept").mkdir(parents=True, exist_ok=True)
    for i, c in enumerate(cards, 1):
        svg = card_svg(c, contents[c["id"]], i, total)
        (outdir / "cards" / (c["id"] + ".svg")).write_text(svg, encoding="utf-8")
    plates = {
        "mana": concept_mana(),
        "ages": concept_ages(),
        "redmoon": concept_redmoon(),
        "war": concept_war(),
        "battlefield": concept_battlefield(),
        "card": concept_card(),
        "road": concept_road(),
        "cover": cover_svg(),
        "game-cover": game_cover_svg(),
    }
    for k, v in plates.items():
        (outdir / "concept" / (k + ".svg")).write_text(v, encoding="utf-8")
    return len(cards), len(plates)


MOTIFS = _motifs()
