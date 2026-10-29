import io

p = r"D:\Projects\HisStory\dsh\src\build.py"
s = io.open(p, encoding="utf-8").read()

# 1. index 世界观 lead
old_lead = '"原典只写了三条，第四条是空的。空着的地方就让它空着。"'
new_lead = '"原典写了四条概念、三条定律。魔力学先立住，世界才谈得上运转。"'
assert old_lead in s
s = s.replace(old_lead, new_lead)

# 2. rulebook editor's notes: typos have been corrected with the author's approval
old_notes = """        '<p class="lead">两处原文笔误照录于此，并在下方标注。归档者不改写原典，只加注。</p>'
        '<div class="orig"><em>原文 · 行动 · 攻击</em>「对目标造成等同于攻击力的伤害，同时收到目标攻击力的反击伤害。」</div>'
        '<p class="rb-note">「收到」应为「受到」。归档版正文按「受到」重排，此处保留原字。</p>'
        '<div class="orig"><em>原文 · 卡牌操作 · 转换</em>「使一张卡牌变为另一张卡牌。若为场上的单位，则会接触施加于其上的所有防御，中止自身的蓄能。」</div>'
        '<p class="rb-note">「接触」应为「解除」。归档版正文按「解除」重排，此处保留原字。</p>'
        '<div class="hair"></div><p class="tiny dim">另：原典的世界观条目共四条，第四条为空，其后留白。'
        '本文不代为补写。规则手册中的「结构重排」均为归档者的排版，语义以原典为准。</p></div>'"""
new_notes = """        '<p class="lead">两处笔误已按作者意见直接改正。原字列在这里，只为留下改动的痕迹。</p>'
        '<div class="orig"><em>原字 · 行动 · 攻击</em>「…同时收到目标攻击力的反击伤害。」</div>'
        '<p class="rb-note">「收到」改为「受到」。原典文件已同步改正。</p>'
        '<div class="orig"><em>原字 · 卡牌操作 · 转换</em>「…则会接触施加于其上的所有防御，中止自身的蓄能。」</div>'
        '<p class="rb-note">「接触」改为「解除」。原典文件已同步改正。</p>'
        '<div class="hair"></div><p class="tiny dim">另：世界观一章现在的四条概念、三条定律、以及精灵族／神代／现代三代魔法，'
        '见「世界观」页。规则手册中的「结构重排」均为归档者的排版，语义以原典为准。</p></div>'"""
assert old_notes in s
s = s.replace(old_notes, new_notes)

io.open(p, "w", encoding="utf-8").write(s)
print("ok")
