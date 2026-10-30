import io

p = r"D:\Projects\HisStory\dsh\src\build.py"
s = io.open(p, encoding="utf-8").read()

old = '''    term_map = {t["n"].replace(" ", ""): t for t in M.TERMS}
    seen_kw, kw_rows = set(), []
    for raw in re.findall(r"【([^】]+)】", c["text"]):'''
new = '''    term_map = {t["n"].replace(" ", ""): t for t in M.TERMS}
    seen_kw, kw_rows = set(), []
    marks = re.findall(r"【([^】]+)】", c["text"]) + list(c.get("tags") or [])
    for raw in marks:'''
assert old in s
s = s.replace(old, new)

s = s.replace('<p class="tiny dim" style="margin:0">这张卡面上没有出现规则词条。</p>',
              '<p class="tiny dim" style="margin:0">这张卡面上没有出现规则词条：它的文本只用到通用规则，没有额外词条。</p>')

io.open(p, "w", encoding="utf-8").write(s)
print("ok")
