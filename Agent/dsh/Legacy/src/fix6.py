import io

def rep(p, pairs):
    s = io.open(p, encoding="utf-8").read()
    for a, b in pairs:
        n = s.count(a)
        s = s.replace(a, b)
        print(p, "subs", n, a[:24])
    io.open(p, "w", encoding="utf-8").write(s)

rep(r"D:\Projects\HisStory\dsh\src\build.py",
    [("新的勇者、七位大贤者、魔王军七军团长。", "新的勇者、七位大贤者、魔王军七位领袖。")])
rep(r"D:\Projects\HisStory\dsh\src\meta.py",
    [('tag="军团长 · 施工中"', 'tag="领袖 · 施工中"')])
rep(r"D:\Projects\HisStory\dsh\src\meta_rules.py",
    [("下图为五段式示意，不是规则。", "下图为示意，不是规则。")])
