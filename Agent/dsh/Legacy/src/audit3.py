import io, glob, re, os

ROOT = r"D:\Projects\HisStory\dsh"
files = []
for pat in ("*.html", "cards/*.html", "heroes/*.html"):
    files += glob.glob(os.path.join(ROOT, pat))

bad = {
    "洗回": [], "军团长": [], "五段": [], "入场即可": [], "唯一突破": [],
    "凑不齐": [], "移动且攻击": [], "不受反击": [], "随机把一张": [],
    "御风六张": [], "18 费的牌，要用过五张红月": [],
}
for f in files:
    s = io.open(f, encoding="utf-8").read()
    for k in bad:
        if k in s:
            bad[k].append(os.path.basename(f))

for k, v in bad.items():
    print(f"{k:10s} {len(v):3d} {v[:4]}")

# card pages checks
cards = glob.glob(os.path.join(ROOT, "cards", "*.html"))
print("cards:", len(cards))
print("no fish:", [os.path.basename(c) for c in cards if "肥鱼碎碎念" not in io.open(c, encoding="utf-8").read()][:3])
print("no 词条:", [os.path.basename(c) for c in cards if "<h4>词条</h4>" not in io.open(c, encoding="utf-8").read()][:3])

# awaken cards buildability
for cid in ("lilia-awaken", "eve-awaken"):
    s = io.open(os.path.join(ROOT, "cards", cid + ".html"), encoding="utf-8").read()
    print(cid, "不可构筑" in s)
