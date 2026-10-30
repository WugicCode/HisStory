import io

p = r"D:\Projects\HisStory\dsh\src\build.py"
s = io.open(p, encoding="utf-8").read()

old = ("""        for i, t in enumerate(W.TIMELINE)) + '</ul>')
""")
new = ("""        for i, t in enumerate(W.TIMELINE)) + '</ul>'
        '<p class="rb-note" style="margin-top:22px">'
        '<b>〔归档者注 · 非史书〕</b>「如今」一条里的红月，不见于史书正文。'
        '它只出现在牌面与史书之外的那一节的写法里，这里按对照的读法记一句，不当作史实。</p>')
""")

assert s.count(old) == 1, s.count(old)
s = s.replace(old, new)
io.open(p, "w", encoding="utf-8").write(s)
print("ok")
