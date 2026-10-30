import io

p = r"D:\Projects\HisStory\dsh\src\build.py"
s = io.open(p, encoding="utf-8").read()

old = ("'<p class=\"tiny dim\" style=\"margin-top:8px\">40 张一组 · 只可含所选阵营与通用 · 同一英雄的天赋只能带一张 · '\n"
       "        '单卡不超过其收藏上限【域外】不可收藏。</p></div>'")
new = ("'<p class=\"tiny dim\" style=\"margin-top:8px\">40 张一组 · 只可含所选阵营与通用 · 同一英雄的天赋只能带一张 · '\n"
       "        '单卡不超过其收藏上限 · 【域外】与【觉醒】不可加入。</p>'\n"
       "        '<p class=\"tiny dim\" style=\"margin-top:6px\">「上限」只约束构筑与战斗外的获得；对局中被生成出来的牌不受它约束。</p></div>'")

assert old in s, "pattern not found"
s = s.replace(old, new)
io.open(p, "w", encoding="utf-8").write(s)
print("ok")
