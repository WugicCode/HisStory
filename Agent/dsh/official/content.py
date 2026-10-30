# -*- coding: utf-8 -*-
"""合并六组卡页内容，并做结构校验。"""

from content_general import CARDS as GENERAL
from content_novian import CARDS as NOVIAN
from content_lilia import CARDS as LILIA
from content_eve import CARDS as EVE
from content_moika import CARDS as MOIKA
from content_rest import CARDS as REST

GROUPS = [
    ("general", GENERAL),
    ("novian", NOVIAN),
    ("lilia", LILIA),
    ("eve", EVE),
    ("moika", MOIKA),
    ("rest", REST),
]

ALL = {}
for _name, _cards in GROUPS:
    for _cid, _card in _cards.items():
        if _cid in ALL:
            raise SystemExit("duplicate content id: %s" % _cid)
        ALL[_cid] = _card

RELATIONS = {
    "前置", "后续", "生成", "来源", "被生成", "转换", "转换自",
    "检索", "被检索", "强化", "被强化", "被配套", "配套",
    "条件", "关联", "同族", "对照",
}

INVERSE = {
    "前置": "后续", "后续": "前置",
    "生成": "来源", "来源": "生成", "被生成": "生成",
    "转换": "转换自", "转换自": "转换",
    "检索": "被检索", "被检索": "检索",
    "强化": "被强化", "被强化": "强化",
    "配套": "被配套", "被配套": "配套",
    "条件": "条件", "关联": "关联",
    "同族": "同族", "对照": "对照",
}

FIELDS = {"orb", "arc", "split", "wave", "rays", "grid", "spiral", "ridge", "step", "void", "rain"}
TONES = {"gold", "blue", "crimson", "green", "violet"}


def validate():
    from cardsource import load_cards
    cards = {c["id"]: c for c in load_cards()}
    errors = []
    if len(cards) != 86:
        errors.append("cardsource: expected 86 cards, got %d" % len(cards))
    missing = sorted(set(cards) - set(ALL))
    extra = sorted(set(ALL) - set(cards))
    if missing:
        errors.append("missing content: %s" % ", ".join(missing))
    if extra:
        errors.append("unknown content: %s" % ", ".join(extra))
    for cid, c in ALL.items():
        for key in ("role", "axes", "art", "links", "note"):
            if key not in c:
                errors.append("%s: missing %s" % (cid, key))
        art = c.get("art", {})
        if art.get("field") not in FIELDS:
            errors.append("%s: bad art field %r" % (cid, art.get("field")))
        if art.get("tone") not in TONES:
            errors.append("%s: bad tone %r" % (cid, art.get("tone")))
        if not isinstance(art.get("motifs"), list) or not 2 <= len(art["motifs"]) <= 4:
            errors.append("%s: motifs must be 2-4 items" % cid)
        if not isinstance(c.get("note"), list) or not 2 <= len(c["note"]) <= 5:
            errors.append("%s: note must be 2-5 paragraphs" % cid)
        for link in c.get("links", []):
            if len(link) != 3:
                errors.append("%s: bad link tuple %r" % (cid, link))
                continue
            target, rel, _desc = link
            if target not in cards:
                errors.append("%s: link to unknown %s" % (cid, target))
            if target == cid:
                errors.append("%s: self link" % cid)
            if rel not in RELATIONS:
                errors.append("%s: bad relation %r" % (cid, rel))
    if errors:
        raise SystemExit("\n".join(errors))
    print("content ok: %d cards, %d links" % (len(ALL), sum(len(c["links"]) for c in ALL.values())))


if __name__ == "__main__":
    validate()
