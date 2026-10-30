# -*- coding: utf-8 -*-
"""Parse Game/CardsDesign.md into structured card records.

The markdown is the single source of truth for card text.  This module only
reads it; it never writes back to Game/.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / "Game" / "CardsDesign.md"

HERO_ORDER = ["诺维安", "莉莉亚", "伊芙格林", "莫伊卡", "米莉卡", "赫琉思", "斯卡琳", "莫菲"]
HERO_SLUG = {
    "诺维安": "novian",
    "莉莉亚": "lilia",
    "伊芙格林": "eve",
    "莫伊卡": "moika",
    "米莉卡": "milika",
    "赫琉思": "herseus",
    "斯卡琳": "scarlin",
    "莫菲": "morphy",
}

# Explicit, stable ids.  Keeping them hand-written avoids pinyin ambiguity.
IDS = {
    # 通用魔法
    "英雄水晶": "hero-crystal",
    "传召水晶": "summon-crystal",
    "贤者之石": "sage-stone",
    "咏唱": "chant",
    "伊莲女神的祝福": "blessing",
    "调度": "dispatch",
    "魔力附加": "enchant",
    "我们的歌": "our-song",
    # 通用单位
    "芬特罗德雇佣兵团": "fentro-company",
    "格兰蒂亚守卫军": "grandia-guard",
    "格兰蒂亚结界护卫": "grandia-ward",
    # 诺维安
    "旅途的起点": "novian-start",
    "新的勇者": "novian-hero",
    "贤者的向往": "novian-yearn",
    "勇气": "courage",
    "破空": "skybreak",
    "勇者的长歌": "hero-song",
    "远方的憧憬": "longing",
    "漫漫长路": "long-road",
    "征途": "journey",
    "故事与歌": "story-and-song",
    "未来": "future",
    "新章": "new-chapter",
    # 莉莉亚
    "纯粹学究": "lilia-scholar",
    "真理的钥匙": "lilia-key",
    "苍白百合": "pale-lily",
    "苍白之月": "pale-moon",
    "通向月面的经络": "meridian",
    "月见": "moonview",
    "弥望": "gaze",
    "魔力天球": "mana-orb",
    "苍白天球": "pale-orb",
    "纯粹": "pure",
    "寻真": "seek-truth",
    "凝聚冲击": "impact",
    "纯白冲击": "white-impact",
    "相位移动": "phase-shift",
    "逐月": "month-step",
    "苍白缄默": "pale-silence",
    # 伊芙
    "吹笛人": "eve-piper",
    "荆棘王冠": "eve-crown",
    "与风同在": "eve-wind",
    "狂风呼啸": "gale",
    "引风来": "call-wind",
    "强风骤雨": "storm",
    "长风破袭": "long-wind",
    "永恒的记忆": "eternal-memory",
    "常青藤": "ivy",
    "自然感知": "nature-sense",
    "风之感知": "wind-sense",
    "记忆中的苍翠": "green-memory",
    "苍叶": "pale-leaf",
    "古老生灵": "ancient-being",
    "树人": "treant",
    "大地与年轮的苏醒": "ring-awakening",
    # 莫伊卡
    "兜帽怪盗": "moika-hood",
    "天罗地网": "moika-net",
    "陷阱": "trap",
    "游弋": "roam",
    "天罗结界": "net-barrier",
    "无踪无迹": "no-trace",
    "奇袭": "raid",
    "枷锁": "shackle",
    "她的梦想": "her-dream",
    # 米莉卡
    "大奇迹·超度·英灵颂": "great-miracle",
    # 赫琉思
    "光芒尖端": "light-tip",
    "灼光": "scorch",
    "太阳蚀刻": "sun-etch",
    "普照": "shine",
    "光辉": "radiance",
    "日冕": "corona",
    # 斯卡琳
    "阿波罗经络": "apollo",
    "绯红原质": "crimson-origin",
    "绯红灵究": "crimson-spirit",
    "绯红极限": "crimson-limit",
    "绯红之月": "crimson-moon",
    "红月·凝刻": "moon-etch",
    "红月·无限": "moon-infinite",
    "红月·过载": "moon-overload",
    "红月·凝聚": "moon-gather",
    "绯红的真实": "crimson-truth",
    # 莫菲
    "捕梦网": "dream-net",
}

# Two Herseus talents are both literally "（施工中）".
SPECIAL_IDS = ["herseus-t1", "herseus-t2"]
SPECIAL_NAMES = {"herseus-t1": "无名天赋 · 一", "herseus-t2": "无名天赋 · 二"}


def _quality(raw: str) -> str:
    raw = raw.strip()
    if "域外" in raw:
        return "域外"
    if "觉醒" in raw:
        return "觉醒"
    return raw


def _int(raw: str):
    m = re.search(r"\d+", raw or "")
    return int(m.group()) if m else None


def _panel(raw: str):
    m = re.search(r"(\d+)C\s*/\s*(\d+)A\s*/\s*(\d+)D", raw or "")
    if not m:
        return None
    return {"c": int(m.group(1)), "a": int(m.group(2)), "d": int(m.group(3))}


def load_cards():
    text = SOURCE.read_text(encoding="utf-8")
    lines = text.splitlines()

    section = ""
    hero = ""
    hero_faction = ""
    sub = ""
    cards = []
    cur = None
    unnamed = 0

    def finish():
        nonlocal cur, unnamed
        if cur is None:
            return
        name = cur["name"]
        if name == "【觉醒】":
            cur["id"] = HERO_SLUG[hero] + "-awaken"
            cur["kind"] = "觉醒"
            cur["quality"] = "觉醒"
            cur["name"] = "【觉醒】"
            cur["display"] = "【觉醒】"
        elif name == "（施工中）":
            unnamed += 1
            cur["id"] = SPECIAL_IDS[unnamed - 1]
            cur["display"] = SPECIAL_NAMES[cur["id"]]
        else:
            cur["id"] = IDS[name]
            cur["display"] = name
        cur["hero"] = hero
        cur["group"] = hero or ("通用" if section != "英雄" else "")
        cur["section"] = section
        cur["sub"] = sub
        if cur["faction"] == "":
            cur["faction"] = hero_faction or {"通用魔法": "通用", "通用单位": "通用"}.get(section, "新的勇者")
        cards.append(cur)
        cur = None

    for raw in lines:
        line = raw.rstrip()
        s = line.strip()
        if not s:
            continue
        if s.startswith("## "):
            finish()
            section = s[3:].strip()
            hero = ""
            sub = ""
            continue
        if s.startswith("### "):
            finish()
            hero = s[4:].strip()
            hero_faction = ""
            sub = ""
            continue
        if s in ("天赋：", "专属魔法："):
            finish()
            sub = s[:-1]
            continue
        if s.startswith("- "):
            finish()
            cur = {
                "name": s[2:].strip(),
                "faction": "",
                "quality": "",
                "cost": None,
                "limit": None,
                "kind": "",
                "type_line": "",
                "panel": None,
                "text": "",
                "hero": "",
                "group": "",
                "section": section,
                "sub": sub,
            }
            continue
        if cur is None:
            m = re.match(r"^阵营：(.*)$", s)
            if m and hero:
                hero_faction = m.group(1).strip()
            continue
        m = re.match(r"^(阵营|品质|上限|花费|类型|面板|描述)：(.*)$", s)
        if not m:
            continue
        key, val = m.group(1), m.group(2).strip()
        if key == "阵营":
            cur["faction"] = val
        elif key == "品质":
            cur["quality"] = _quality(val)
        elif key == "上限":
            cur["limit"] = None if "施工" in val else (None if "域外" in val else _int(val))
            cur["limit_raw"] = val
        elif key == "花费":
            cur["cost"] = None if "施工" in val else _int(val)
        elif key == "类型":
            cur["type_line"] = val
        elif key == "面板":
            cur["panel"] = _panel(val)
        elif key == "描述":
            cur["text"] = val
    finish()

    for c in cards:
        if not c["kind"]:
            if c["sub"] == "天赋":
                c["kind"] = "天赋"
            elif c["sub"] == "专属魔法":
                c["kind"] = "魔法"
            elif c["type_line"]:
                c["kind"] = "单位"
            elif c["section"] == "通用单位":
                c["kind"] = "单位"
            else:
                c["kind"] = "魔法"
        if c["type_line"]:
            c["kind"] = "单位"
        c["group"] = c["group"] or "通用"
        c["group_slug"] = HERO_SLUG.get(c["group"], "general")
        c["limit_raw"] = c.get("limit_raw", "")
    return cards


if __name__ == "__main__":
    cards = load_cards()
    print(len(cards))
    from collections import Counter
    print("faction", Counter(c["faction"] for c in cards))
    print("kind", Counter(c["kind"] for c in cards))
    print("quality", Counter(c["quality"] for c in cards))
    print("group", Counter(c["group"] for c in cards))
    for c in cards[:12]:
        print(c["id"], c["display"], c["faction"], c["quality"], c["cost"], c["kind"], c["text"][:30])
