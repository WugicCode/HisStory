# -*- coding: utf-8 -*-
"""从 CardsDesign.md 重建 CARD_LIST，保留旧数据层的 note / links / cluster。"""
import sys, io, re

sys.path.insert(0, r"D:\Projects\HisStory\dsh\src")
import data_cards as D

MD = r"D:\Projects\HisStory\HisStory-Game\CardsDesign.md"
OUT = r"D:\Projects\HisStory\dsh\src\data_cards.py"

HERO_ID = {"诺维安": "novian", "莉莉亚": "lilia", "伊芙格林": "eve", "莫伊卡": "moika",
           "米莉卡": "milika", "赫琉思": "helius", "斯卡琳": "scarlett", "莫菲": "mophy", "人类": None}

NEW_META = {
    ("helius", "（施工中）", 0): dict(
        id="helius-talent-1", cluster="helius", hero="helius",
        tags=["机动", "反击", "施工中"],
        note="弓箭手本来「不会受到也无法造成反击伤害」，这张天赋只把后半句改了：他开始能造成反击。于是「拆盾」之后的每一次交换都变成双向的——他仍然是全场最脆的那类单位，只是现在，谁碰他，也要掉一层皮。面板与花费原典都写着「施工中」，这里不替它补。",
        links=[("helius-light-tip", "联动", "先拆掉防御，再让反击成为真正的威胁"),
               ("helius-blaze", "同源", "都建立在「解除防御」之后的那一次交换上")]),
    ("helius", "（施工中）", 1): dict(
        id="helius-talent-2", cluster="helius", hero="helius",
        tags=["机动", "双伤", "施工中"],
        note="攻击时额外造成等同于攻击力的魔法伤害，等于每一箭射两遍：一遍物理、一遍魔法。对面若把防御堆在物理一侧，这一箭就从缝隙里穿过去。它写的是「攻击时」而不是「攻击后」——这半箭是同一次出手的附赠品，不占另一次行动。",
        links=[("helius-corona", "联动", "日冕把防御当膛压，这张把攻击当倍率"),
               ("helius-light-tip", "条件", "对方的防御越薄，这一箭的魔法附加越难被抵消")]),
}

# ---------- 解析 ----------
lines = io.open(MD, encoding="utf-8").read().splitlines()
entries = []
sec = sub = None
sec_fac = {}
cur = None
FIELDS = ("阵营", "品质", "上限", "花费", "类型", "面板", "描述")


def flush():
    global cur
    if cur and cur.get("描述"):
        entries.append(cur)
    cur = None


for ln in lines:
    s = ln.rstrip()
    if s.startswith("## "):
        flush(); sec, sub = s[3:].strip(), None
    elif s.startswith("### "):
        flush(); sec, sub = s[4:].strip(), None
    elif s.strip() in ("天赋：", "专属魔法："):
        flush(); sub = s.strip().rstrip("：")
    elif s.startswith("- "):
        flush(); cur = {"name": s[2:].strip(), "sec": sec, "sub": sub, "_raw": {}}
    elif cur is not None and "：" in s:
        k, v = s.strip().split("：", 1)
        if k in FIELDS:
            cur[k] = v.strip()
    elif cur is None and "：" in s:
        # 章节级字段（如英雄小节里的「阵营：」），记在所属标题下
        k, v = s.strip().split("：", 1)
        if k == "阵营":
            sec_fac[sec] = v.strip()
flush()

# ---------- 旧数据索引 ----------
old_by = {}
for c in D.CARD_LIST:
    key = (c.get("hero") or "core", c["name"])
    old_by.setdefault(key, []).append(c)


def norm_q(v):
    if not v:
        return None
    v = v.strip()
    if v in ("【域外】", "域外"):
        return "域外"
    return v


def hero_of(e):
    if e["sec"] in ("通用魔法", "通用单位"):
        return "core"
    return HERO_ID.get(e["sec"], "core")


def cat_of(e):
    if e["sub"] == "天赋":
        return "天赋"
    if e["sec"] == "通用单位" or ("类型" in e and "面板" in e):
        return "单位"
    return "魔法"


cards = []
seen = {}
for e in entries:
    hv = hero_of(e)
    seen[(hv, e["name"])] = seen.get((hv, e["name"]), -1) + 1
    idx = seen[(hv, e["name"])]
    newmeta = NEW_META.get((hv, e["name"], idx))
    olds = old_by.get((hv, e["name"]), [])
    old = olds[idx] if idx < len(olds) else None

    if old is None and newmeta is None:
        print("!! no meta for", hv, e["name"]); continue

    cat = cat_of(e)
    if e["name"] == "【觉醒】":
        cat = "觉醒"
    q = norm_q(e.get("品质")) or (old["q"] if old else ("—" if cat == "天赋" else "N"))
    lim = norm_q(e.get("上限"))
    if lim is None:
        lim = old.get("lim", "") if old else ""
    cost = e.get("花费", old.get("cost", "") if old else "")
    HERO_FAC = {"novian": "新的勇者", "lilia": "新的勇者", "eve": "新的勇者",
                "moika": "新的勇者", "milika": "新的勇者",
                "helius": "同盟军", "scarlett": "同盟军", "mophy": "魔王军"}
    fac = e.get("阵营") or sec_fac.get(e["sec"]) or HERO_FAC.get(hv) or (old["fac"] if old else "通用")

    rec = dict(
        id=(newmeta["id"] if newmeta else old["id"]),
        name=e["name"],
        fac=fac,
        q=q,
        lim=lim,
        cost=cost,
        cat=cat,
        cluster=(newmeta["cluster"] if newmeta else old["cluster"]),
        hero=(newmeta["hero"] if newmeta else old.get("hero")),
        tags=(newmeta["tags"] if newmeta else old.get("tags", [])),
        text=e["描述"],
        note=(newmeta["note"] if newmeta else old["note"]),
        links=(newmeta["links"] if newmeta else [l for l in old.get("links", []) if l[0] in {x["id"] for x in D.CARD_LIST}]),
    )
    if e.get("类型"):
        rec["utype"] = e["类型"]
    elif old and old.get("utype"):
        rec["utype"] = old["utype"]
    if e.get("面板"):
        rec["stats"] = e["面板"]
    elif old and old.get("stats"):
        rec["stats"] = old["stats"]
    cards.append(rec)

# ---------- 写出 ----------
def qs(v):
    return '"' + str(v).replace("\\", "\\\\").replace('"', '\\"') + '"'


out = ['# -*- coding: utf-8 -*-',
       '"""长歌 · 卡牌数据层（归档页 · 第一手转录）',
       '',
       '数据来源：HisStory-Game/CardsDesign.md（原典照录，未改动词义；仅统一了【域外】的写法）。',
       'note 字段 = 「肥鱼碎碎念」：归档者对这张卡的理解与设计解读。',
       'links = 卡牌之间的逻辑/归属关联 (目标id, 关系类型, 说明)。',
       '关系类型：生成 / 转化 / 条件 / 检索 / 同源 / 联动。',
       '"""',
       '',
       'CARD_LIST = [']
for c in cards:
    out.append("    dict(")
    out.append("        id=%s, name=%s, fac=%s, q=%s, lim=%s, cost=%s, cat=%s," %
               (qs(c["id"]), qs(c["name"]), qs(c["fac"]), qs(c["q"]), qs(c["lim"]), qs(c["cost"]), qs(c["cat"])))
    line = "        cluster=%s, hero=%s," % (qs(c["cluster"]), qs(c["hero"]) if c["hero"] else "None")
    out.append(line)
    if c.get("utype"):
        out.append("        utype=%s, stats=%s," % (qs(c["utype"]), qs(c.get("stats", ""))))
    elif c.get("stats"):
        out.append("        stats=%s," % qs(c["stats"]))
    out.append("        tags=%s," % ("[" + ", ".join(qs(t) for t in c["tags"]) + "]"))
    out.append("        text=%s," % qs(c["text"]))
    out.append("        note=%s," % qs(c["note"]))
    if c["links"]:
        out.append("        links=[")
        for tgt, kind, note in c["links"]:
            out.append("            (%s, %s, %s)," % (qs(tgt), qs(kind), qs(note)))
        out.append("        ],")
    else:
        out.append("        links=[],")
    out.append("    ),")
out.append("]")
out.append("")

io.open(OUT, "w", encoding="utf-8", newline="\n").write("\n".join(out))

print("cards written:", len(cards))
print("talent:", sum(1 for c in cards if c["cat"] == "天赋"))
print("unit:", sum(1 for c in cards if c["cat"] == "单位"))
print("ids unique:", len({c["id"] for c in cards}) == len(cards))
