import os, re, sys
from pathlib import Path

ROOT = Path(r"D:\Projects\HisStory\dsh")
pages = list(ROOT.glob("*.html")) + list(ROOT.glob("cards/*.html")) + list(ROOT.glob("heroes/*.html"))
pages = [p for p in pages if not p.name.endswith(".pv.html")]
missing = []
checked = 0
for p in pages:
    html = p.read_text(encoding="utf-8")
    for m in re.finditer(r'(?:href|src)="([^"]+)"', html):
        u = m.group(1)
        if u.startswith(("http", "#", "mailto:", "data:", "javascript:")):
            continue
        u = u.split("#")[0]
        if not u:
            continue
        target = (p.parent / u).resolve()
        checked += 1
        if not target.exists():
            missing.append((str(p.relative_to(ROOT)), u))
print("pages", len(pages), "refs", checked, "missing", len(missing))
for a, b in missing[:20]:
    print(" -", a, "->", b)

# preview leftovers
pv = [p for p in ROOT.rglob("*.pv.html")]
print("preview files:", len(pv))
