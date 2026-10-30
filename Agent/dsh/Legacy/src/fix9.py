import io

p = r"D:\Projects\HisStory\dsh\src\meta_world.py"
s = io.open(p, encoding="utf-8").read()

start = s.index("CAST_CONFLICT")
seg = s[start:start + 900]
print("OLD:", seg[:700].replace("\n", " "))

old_tail = "——两处原典与归档现况在写法一致，不再有需要裁定的分歧。"
if old_tail in s:
    s = s.replace(old_tail, "——前者是职业，后者是单位类型，两层用词，不必对齐。")
io.open(p, "w", encoding="utf-8").write(s)
print("patched:", old_tail in s)
