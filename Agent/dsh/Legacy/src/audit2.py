import io, os, re, sys
from pathlib import Path

ROOT = Path(r"D:\Projects\HisStory\dsh")
sys.path.insert(0, str(ROOT / "src"))
import data_cards as D
import meta as M

cards = sorted((ROOT / "cards").glob("*.html"))
heroes = sorted((ROOT / "heroes").glob("*.html"))
print("card pages", len(cards), "hero pages", len(heroes), "cards in data", len(D.CARD_LIST))

no_fish = [p.name for p in cards if "肥鱼碎碎念" not in p.read_text(encoding="utf-8")]
no_rel = [p.name for p in cards if 'class="rels"' not in p.read_text(encoding="utf-8")]
no_kw = [p.name for p in cards if "<h4>词条</h4>" not in p.read_text(encoding="utf-8")]
print("missing fish", len(no_fish), "| missing rels", len(no_rel), "| cards without 词条 panel", no_kw)

# awaken cards must say 不可构筑
for cid in ("lilia-awaken", "eve-awaken"):
    s = (ROOT / "cards" / (cid + ".html")).read_text(encoding="utf-8")
    print(cid, "不可构筑" in s, "觉醒" in s)

# hero pages: talent count in panel
for h in M.HEROES:
    s = (ROOT / "heroes" / (h["id"] + ".html")).read_text(encoding="utf-8")
    m = re.search(r"wordle", s)
    cnt = s.count('class="cface')
    print(h["id"], "talents=", h.get("talents"), "faces=", cnt)

idx = (ROOT / "index.html").read_text(encoding="utf-8")
for kw in ("86", "21", "觉醒", "域外", "特色卡牌"):
    print("index has", kw, kw in idx)
print("archive count text:", "全部 86 张" in (ROOT / "archive.html").read_text(encoding="utf-8"))
