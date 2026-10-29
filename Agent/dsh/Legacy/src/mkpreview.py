import os, re, shutil

ROOT = r"D:\Projects\HisStory\dsh"
INJECT = ("<style>"
          ".reveal{opacity:1!important;transform:none!important}"
          ".hero{min-height:600px!important}"
          ".nav{position:absolute!important}"
          ".nav-prog{display:none!important}"
          "*{animation:none!important;transition:none!important}"
          "</style></head>")

targets = [
    "index.html", "archive.html", "sandbox.html", "rulebook.html",
    "heroes/novian.html", "heroes/lilia.html",
    "cards/hero-crystal.html", "cards/lilia-awaken.html",
    "cards/scarlett-truth.html", "cards/our-song.html",
]

made = []
for rel in targets:
    src = os.path.join(ROOT, rel)
    if not os.path.exists(src):
        print("MISS", rel); continue
    html = open(src, encoding="utf-8").read()
    html = html.replace("</head>", INJECT, 1)
    out = src[:-5] + ".pv.html"
    open(out, "w", encoding="utf-8").write(html)
    made.append(out)

print("previews:", len(made))
