import io

p = r"D:\Projects\HisStory\dsh\src\build.py"
s = io.open(p, encoding="utf-8").read()

# bigger faith diamonds so the 1000 fits inside
old = """                 % (cx, cy - 36, cx + 28, cy, cx, cy + 36, cx - 28, cy))"""
new = """                 % (cx, cy - 44, cx + 34, cy, cx, cy + 44, cx - 34, cy))"""
assert old in s
s = s.replace(old, new)

# neutral caption instead of a direction not in the source
old_cap = "'<text class=\"zone-name\" x=\"%d\" y=\"%d\" text-anchor=\"middle\">← 己方推进方向</text>' % (W / 2, H - 14)"
new_cap = "'<text class=\"zone-name\" x=\"%d\" y=\"%d\" text-anchor=\"middle\">示意图 · 五段战场，两端各一座信仰</text>' % (W / 2, H - 14)"
assert old_cap in s
s = s.replace(old_cap, new_cap)

io.open(p, "w", encoding="utf-8").write(s)
print("ok")
