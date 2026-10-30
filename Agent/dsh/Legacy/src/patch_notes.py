# -*- coding: utf-8 -*-
"""patch_notes.py —— 第四轮：按「生成/移动」语义与作者裁定重写卡牌碎碎念、修关系标签。"""
import io, sys

sys.path.insert(0, r"D:\Projects\HisStory\dsh\src")
import data_cards as D

NOTES = {
 "hero-crystal": "2 费、上限 4，抽一张牌，再「加入卡组」一张自身。按动词表，加入是印制新卡，所以它不是「循环」而是自我复制：每用一次，牌库里就多一张英雄水晶。开局用它把天赋抽出来，再让传召水晶吃掉手里的专属魔法——两枚水晶越洗越多，牌库会变成一台只产专属牌的机器。",
 "summon-crystal": "2 费，选一张手里的专属魔法送回卡组，再「加入卡组」一张自身。同一张牌上两个动词并存，正好演示区别：送回去的那张是旧牌（洗入＝移动），多出来的是新牌（加入＝生成）。它要求手里先有专属魔法才能启动，所以通常晚于英雄水晶。",
 "philosopher-stone": "6 费，二选一：换 8 点魔力，或者 6 点魔力 + 抽一张 + 把自身加入卡组。后者是生成，所以这张上限 1 的孤本永远不会真正用完；代价是每回合多花 6 点，收益是它一直留在牌库里。前者则意味着永远失去它。上限 1、史诗、通用——三样都指向一件没有归属的未竟之作。",
 "novian-future": "1 费，永久让诺维安可攻可防并减一行动花费，同时把一张「新章」加入卡组。加入是生成，所以不是「埋一张牌」，而是每打出一次就多一张。1 费说明作者不想让玩家犹豫：这是转型点，不是选择题。",
 "lilia-awaken": "觉醒面板不是第四张天赋，带不进卡组。触发它的不是「蓄能两次」本身，而是用掉一张「苍白之月」——苍白百合的蓄能只是递来那张月。苍白之月是传说、上限 2、可以构筑携带，所以三张天赋都能直接走这条路。觉醒之后：己方魔法减一费、入场给「经络」、蓄能产出减费与「苍白缄默」、防御带抽牌。",
 "lilia-pale-moon": "2 费，三件事：递一张「经络」、让莉莉亚觉醒，或者（已觉醒时）复制一张专属魔法洗入卡组。最后半句是「洗入」——复制出来的是一张新牌，但动词照原典写作移动的那一个。它是唯一直接写「使莉莉亚觉醒」的牌，也是对手最该提防的信号。",
 "lilia-meridian": "1 费的「三态牌」：在卡组就抽莉莉亚，在手牌就让她入场，在场上就给一张单位或英雄。抽是检索、入场是打出，两者都不生成任何东西——它不污染牌库。",
 "lilia-impact": "4 费一记魔法伤害，击杀则把自身加入卡组。加入是生成：只要每次都能打死，牌库里的它就用不完，是全卡池最直白的「生成即续航」。条件叠着【限定】，实际要求先养出一个够大的莉莉亚。",
 "lilia-white-impact": "5 费，击杀后加入卡组并额外给 2 点魔力。比原版贵 1 费，换来的是把生成与回本放在一起：每打死一个单位，就多一张冲击、多两点魔力。觉醒后的莉莉亚不再靠攒，而是靠打。",
 "lilia-silence": "9 费，除莉莉亚外双方无法造成魔法伤害。它由觉醒后的蓄能产出，是觉醒的奖励，不是可以直接构筑的答案——也意味着它出现时，对手的魔法伤害通常已经铺开了。",
 "lilia-gaze": "唯一能在被禁锢时使用的牌：解锁、强化，再开发一张专属魔法。开发是生成，因此它同时是成本与收益——被控得越死，这张牌越像一次反击。",
 "lilia-pure": "2 费：1 点魔力 + 抽一。觉醒后转为「寻真」（2 点魔力 + 开发一张专属魔法）。四张上限说明它本来就是填充牌，觉醒把它换成了引擎。",
 "lilia-truth-seeking": "觉醒后的「纯粹」：2 点魔力换 1 点，外加开发一张专属魔法。它把「觉醒」这件事直接兑换成资源。",
 "moika-hooded-thief": "2 费、0 行动花费、50 攻、150 防，唯一的负面是「防御具有加一花费」。0 行动花费不等于【机动】，它入场当回合仍然不能行动；游侠的定义是「一回合内可以移动且攻击」，那是另一回事。它的价值在【返场】：被消灭后加入手牌而非洗回卡组——加入是生成，所以每次返场都是一张新牌。",
 "milika-miracle": "12 费。本场战斗每有过一个己方单位被消灭，就造成两次 25 点，按阵亡数累加——死五个就是 250 点，不是死得越多越轻。除英雄外一个己方单位都没死过时，改为对敌方信仰造成 1000 点：信仰没有反击面板，这一发几乎等于斩杀。两条支路互斥，等于两副不同的卡组。12 费在可收藏的牌里与日冕并列最贵。",
 "helius-shine": "2 费，对所有敌方目标打 50 点并抽一，然后把一张「光辉」加入卡组。加入是生成：它不是在牌库里埋一张 4 费牌当代价，而是每打一次就多一张光辉——链条只会变长。",
 "helius-radiance": "4 费，5 次 50 点，优先打防御最高的敌方单位，结算后把「日冕」加入卡组。打得越厚，日冕越多；敌方没有单位时转向信仰，这条兜底让它不浪费。",
 "scarlett-crimson-moon": "7 费，+3 魔力上限，【限定】，「开发」一张『红月』——开发是从三张额外的牌里选一张，属于生成。若已觉醒，还会随即将一张『红月』加入手牌。它是红月体系的终点，也是唯一能靠转化在卡组里凑出第二张的牌。",
 "mophy-dreamcatcher": "1 费，禁锢一个战区的所有单位。魔王军的卡池尚未展开，捕梦网是目前唯一的机制声明：在「战区」这个维度上做群体控制。强度取决于单张地图上战区的单位密度——挤得越满越值；战场几段、每段几人，原典留白。",
}

# 跨阵营（两个非通用阵营之间）的关系一律降为「对照」
CROSS_TO_CONTRAST = [
    ("lilia-mana-sphere", "scarlett-crimson-moon"),
    ("lilia-pale-sphere", "scarlett-crimson-essence"),
    ("helius-light-tip", "grandia-guard"),
    ("helius-solar-etch", "moika-shackle"),
    ("helius-shine", "lilia-mana-sphere"),
    ("helius-corona", "eve-eternal-memory"),
    ("scarlett-crimson-essence", "lilia-pale-sphere"),
    ("mophy-dreamcatcher", "moika-shackle"),
    ("mophy-dreamcatcher", "moika-barrier"),
]

cards = []
for c in D.CARD_LIST:
    c = dict(c)
    if c["id"] in NOTES:
        c["note"] = NOTES[c["id"]]
    newlinks = []
    for (tid, kind, why) in c["links"]:
        pair = (c["id"], tid)
        if (pair in CROSS_TO_CONTRAST or (tid, c["id"]) in CROSS_TO_CONTRAST) and kind in ("联动", "同源", "条件"):
            kind = "对照"
            why = "分属不同阵营，永不同框；并排读能看出两套设计在比什么" if why.strip() in ("—", "") else why
        newlinks.append((tid, kind, why))
    c["links"] = newlinks
    cards.append(c)

out = ["# -*- coding: utf-8 -*-",
       '"""86 张卡的归档数据（由 gen_cards.py 生成，patch_notes.py 修订）。',
       '字段：id / name / fac / q / lim / cost / cat / cluster / hero / tags / text / note / links"""',
       "", "CARD_LIST = ["]
for c in cards:
    out.append("    dict(")
    for k, v in c.items():
        out.append("        %s=%r," % (k, v))
    out.append("    ),")
out.append("]")
out.append("")
io.open(r"D:\Projects\HisStory\dsh\src\data_cards.py", "w", encoding="utf-8", newline="\n").write("\n".join(out))
print("cards rewritten:", len(cards),
      "| notes changed:", sum(1 for c in cards if c["id"] in NOTES),
      "| contrast links:", sum(1 for c in cards for l in c["links"] if l[1] == "对照"))
