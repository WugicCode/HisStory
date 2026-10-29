from pathlib import Path
import re, sys

ROOT = Path(r"D:\Projects\HisStory\dsh")
sys.path.insert(0, str(ROOT / "src"))
import data_cards as D
import meta as M

cards = list((ROOT / "cards").glob("*.html"))
heroes = list((ROOT / "heroes").glob("*.html"))
print("card pages", len(cards), "hero pages", len(heroes))

miss_fish = [p.name for p in cards if "肥鱼碎碎念" not in p.read_text(encoding="utf-8")]
miss_rel = [p.name for p in cards if 'class="rels"' not in p.read_text(encoding="utf-8")]
print("missing fish:", miss_fish[:5], "missing rels:", miss_rel[:5])

ids = {c["id"] for c in D.CARD_LIST}
page_ids = {p.stem for p in cards}
print("ids without page:", sorted(ids - page_ids)[:5])
print("pages without id:", sorted(page_ids - ids)[:5])

hmiss = [p.name for p in heroes if "cnode" not in p.read_text(encoding="utf-8")]
print("hero pages without constellation:", hmiss)

idx = (ROOT / "index.html").read_text(encoding="utf-8")
for kw in ("特色卡牌", "关系星图", "战场", "魔力", "肥鱼碎碎念", "归档"):
    print(kw, kw in idx)

print("index size KB", len(idx) // 1024)
