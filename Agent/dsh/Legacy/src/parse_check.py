# -*- coding: utf-8 -*-
import sys, re, json
sys.path.insert(0, r"D:\Projects\HisStory\dsh\src")
import data_cards as D

md = open(r"D:\Projects\HisStory\HisStory-Game\CardsDesign.md", encoding="utf-8").read()
lines = md.splitlines()

cards = []
sec = None          # 通用魔法 / 通用单位 / hero name
sub = None          # 天赋 / 专属魔法
cur = None
FIELDS = ("阵营", "品质", "上限", "花费", "类型", "面板", "描述")

def flush():
    global cur
    if cur and cur.get("name"):
        cards.append(cur)
    cur = None

i = 0
while i < len(lines):
    ln = lines[i].rstrip()
    if ln.startswith("## "):
        flush(); sec = ln[3:].strip(); sub = None
    elif ln.startswith("### "):
        flush(); sec = ln[4:].strip(); sub = None
    elif ln.strip() in ("天赋：", "专属魔法："):
        flush(); sub = ln.strip().rstrip("：")
    elif ln.startswith("- "):
        flush()
        cur = {"name": ln[2:].strip(), "section": sec, "sub": sub, "raw": []}
    elif cur is not None and "：" in ln:
        k, v = ln.strip().split("：", 1)
        if k in FIELDS:
            cur[k] = v.strip()
    i += 1
flush()

print("parsed", len(cards))
old = {c["name"]: c for c in D.CARD_LIST}
print("old", len(old))

new_names = [c["name"] for c in cards if c["name"] not in old]
gone = [n for n in old if n not in {c["name"] for c in cards}]
print("new:", new_names)
print("gone:", gone)

diffs = []
for c in cards:
    o = old.get(c["name"])
    if not o:
        continue
    for f, key in (("品质", "q"), ("上限", "lim"), ("花费", "cost"), ("描述", "text"), ("面板", "stats"), ("类型", "utype"), ("阵营", "fac")):
        nv = c.get(f)
        ov = o.get(key)
        if nv is not None and nv != ov:
            diffs.append((c["name"], key, ov, nv))
for d in diffs:
    print("DIFF", d)
