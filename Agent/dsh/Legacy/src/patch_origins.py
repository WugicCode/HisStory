# -*- coding: utf-8 -*-
"""patch_origins.py —— 第四轮：机制的来历（story 页 + 卡页）、战场说明、CSS。"""
import io, re

B = r"D:\Projects\HisStory\dsh\src\build.py"
s = io.open(B, encoding="utf-8").read()

# ── 1. 卡页：来历区块 ─────────────────────────
old_card = """        '<p class="sig">——归档者，读这张卡的时候</p></div>' +"""
new_card = """        '<p class="sig">——归档者，读这张卡的时候</p></div>' + origin_html +"""
assert old_card in s
s = s.replace(old_card, new_card, 1)

anchor = """    fish_paras = [p for p in re.split(r"\\n+", c["note"]) if p.strip()]"""
if anchor not in s:
    # 找到 fish_paras 的定义行
    m = re.search(r"^.*fish_paras\s*=.*$", s, re.M)
    anchor = m.group(0)
    print("anchor:", anchor[:80])

origin_builder = '''
    _origins = [o for o in R.ORIGINS if cid in o.get("cards", [])]
    origin_html = ""
    if _origins:
        origin_html = ('<div class="origin"><h4>机制的来历 <span class="tag guess">推想</span></h4>' +
                       "".join('<p><b>' + esc(o["k"]) + '</b>　' + esc(o["t"]) + '</p>' for o in _origins) +
                       '<p class="tiny dim">这是归档者读牌时的对应关系，不是原典设定。</p></div>')
'''
s = s.replace(anchor, anchor + "\n" + origin_builder, 1)

# ── 2. 战争史：机制的来历一节 ──────────────────
old_story = """            sec("after", "03", "战后", "AFTER THE WAR", "", '<div class="prose">' + after + '</div>' + aside) +"""
new_story = """            sec("after", "03", "战后", "AFTER THE WAR", "", '<div class="prose">' + after + '</div>' + aside) +
            sec("origins", "04", "机制的来历", "WHERE THE MECHANICS COME FROM", R.ORIGINS_INTRO, origins) +"""
assert old_story in s
s = s.replace(old_story, new_story, 1)

story_anchor = """    aside = ('<div class="aside-box"><h4>'"""
origins_def = '''    origins = ('<div class="origins">' + "".join(
        '<div class="origin reveal" data-d="%d"><h4>%s<span class="tag guess">推想</span></h4>'
        '<p class="or-w">%s</p><p>%s</p><p class="or-c">%s</p></div>' %
        (i % 5 + 1, esc(o["k"]), esc(o["w"]), esc(o["t"]),
         "".join('<a href="cards/%s.html">%s</a>' % (cid, esc(BY[cid]["name"]))
                 for cid in o.get("cards", []) if cid in BY))
        for i, o in enumerate(R.ORIGINS)) + '</div>')

'''
s = s.replace(story_anchor, origins_def + story_anchor, 1)

# ── 3. 首页战场说明 ───────────────────────────
s = s.replace('示意圖固定为五段。原典设定：战区排布由随机地图决定，末端战区必然存在，且不能被对方占领。',
              '原典设定：战区排布由随机地图决定，末端战区必然存在，且不能被对方占领。')
s = re.sub(r"示意图固定为五段。原典设定：战区排布由随机地图决定，末端战区必然存在，且不能被对方占领。",
           "示意图。原典设定：战区排布由随机地图决定，末端战区必然存在，且不能被对方占领。", s)

io.open(B, "w", encoding="utf-8").write(s)
print("build patched")

# ── 4. CSS ────────────────────────────────────
C = r"D:\Projects\HisStory\dsh\assets\css\style.css"
css = io.open(C, encoding="utf-8").read()
css += """
/* ---------- 20. 动词表 / 裁定 / 机制的来历 ---------- */
.rb-sub{margin:32px 0 6px;font-size:.92rem;font-weight:400;letter-spacing:.1em;color:var(--gold-2)}
.rb-sec .rb-sub:first-of-type{margin-top:22px}
.rb-note b{color:var(--gold-2);font-weight:400;letter-spacing:.04em}
.origins{display:grid;grid-template-columns:repeat(2,1fr);gap:1px;background:var(--line);border:1px solid var(--line)}
.origin{background:var(--ink);padding:clamp(20px,3vw,30px)}
.origin h4{font-size:1.02rem;font-weight:400;letter-spacing:.14em;color:var(--gold-2);
  display:flex;align-items:center;gap:10px;margin-bottom:10px}
.origin .or-w{font-size:.74rem;letter-spacing:.08em;color:var(--text-3);margin-bottom:10px}
.origin p{font-size:.84rem;line-height:1.85;color:var(--text-2)}
.origin .or-c{margin-top:14px;display:flex;flex-wrap:wrap;gap:6px 14px}
.origin .or-c a{font-size:.76rem;color:var(--silver);border-bottom:1px solid rgba(154,168,184,.3)}
.origin .or-c a:hover{color:var(--gold-2);border-color:var(--gold)}
.k-前置{--rk:#8fb0c6}
.k-对照{--rk:#9a9384}
@media (max-width:880px){.origins{grid-template-columns:1fr}}
"""
io.open(C, "w", encoding="utf-8").write(css)
print("css patched")
