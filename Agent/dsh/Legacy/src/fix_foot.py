import io

p = r"D:\Projects\HisStory\dsh\src\build.py"
s = io.open(p, encoding="utf-8").read()

# 1. foot() accepts trailing scripts placed before </body>
old_foot = """def foot(root=\"\"):
    return ('<footer class=\"foot\"><div class=\"wrap\"><div class=\"foot-grid\"><div>'
            '<h4>长歌</h4><p>' + esc(M.FOOTER[\"credit\"]) + '</p>'
            '<p>' + esc(M.FOOTER[\"note\"]) + '</p>'
            '<p>' + esc(M.FOOTER[\"files\"]) + '</p>'
            '</div><div class=\"foot-mark\">月亮升起之前，先把路走完</div></div></div></footer>'
            '<script src=\"' + root + 'assets/js/site.js\"></script></body></html>')"""
new_foot = """def foot(root=\"\", extra=\"\"):
    return ('<footer class=\"foot\"><div class=\"wrap\"><div class=\"foot-grid\"><div>'
            '<h4>长歌</h4><p>' + esc(M.FOOTER[\"credit\"]) + '</p>'
            '<p>' + esc(M.FOOTER[\"note\"]) + '</p>'
            '<p>' + esc(M.FOOTER[\"files\"]) + '</p>'
            '</div><div class=\"foot-mark\">月亮升起之前，先把路走完</div></div></div></footer>'
            '<script src=\"' + root + 'assets/js/site.js\"></script>' + extra + '</body></html>')"""
assert old_foot in s
s = s.replace(old_foot, new_foot)

# 2. archive page script moves into foot()
old_a = """        '</div></div></section>' + foot(\"\") +
        '<script src=\"assets/js/archive.js\"></script>'"""
new_a = """        '</div></div></section>' + foot(\"\", '<script src=\"assets/js/archive.js\"></script>')"""
assert old_a in s
s = s.replace(old_a, new_a)

# 3. sandbox page script moves into foot()
old_b = """        '</div></section>' + foot(\"\") +
        '<script src=\"assets/data/cards.js\"></script><script src=\"assets/js/sandbox.js\"></script>'"""
new_b = """        '</div></section>' + foot(\"\",
            '<script src=\"assets/data/cards.js\"></script><script src=\"assets/js/sandbox.js\"></script>')"""
assert old_b in s
s = s.replace(old_b, new_b)

io.open(p, "w", encoding="utf-8").write(s)

m = io.open(r"D:\Projects\HisStory\dsh\src\meta.py", encoding="utf-8").read()
m = m.replace(
    'note="本页由 DSH 生成；除修正少量笔误外，未改动 dsh 目录以外的任何文件结构。"',
    'note="本页由 DSH 生成。经作者同意，改正了原典中的少量笔误（Outline.md、HisStory-Game/Outline.md、HisStory-Game/CardsDesign.md），除此之外没有改动 dsh 目录以外的文件。"')
m = m.replace(
    'files="原典：README.md · Outline.md · HisStory-Game/Outline.md · HisStory-Game/CardsDesign.md"',
    'files="原典：README.md · Outline.md · HisStory-Game/Outline.md · HisStory-Game/CardsDesign.md · dsh/memo.md"')
io.open(r"D:\Projects\HisStory\dsh\src\meta.py", "w", encoding="utf-8").write(m)
print("patched")
