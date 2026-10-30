# -*- coding: utf-8 -*-
"""patch_world3.py —— 第四轮：人物页公告中性化、阿尔法冲突、大陆待定标注。"""
import io

P = r"D:\Projects\HisStory\dsh\src\meta_world.py"
s = io.open(P, encoding="utf-8").read()

old = '''CAST_CONFLICT = dict(
    title="莫菲：归属已更正",
    body="卡牌设计稿原先把她写在「同盟军」名下，是笔误；作者已确认莫菲属魔王军第七军团长「梦之掌司」。"
         "归档已按魔王军重排她的卡与人物条目——现在两边一致了。",
)'''
new = '''CAST_CONFLICT = dict(
    title="关于莫菲",
    body="莫菲是魔王军目前唯一的卡牌来源：一张 1 费的捕梦网。她在人物表里的身份是梦之掌司，在规则里是一名法师·神官——"
         "两处原典与归档页现在写法一致，不再有需要裁定的分歧。",
)'''
assert old in s
s = s.replace(old, new)

# 阿尔法：两处原典职业不同，加冲突标注
s = s.replace('dict(name="阿尔法", sex="女", race="人类", job="刺客"',
              'dict(name="阿尔法", sex="女", race="人类", job="刺客（Outline 作游侠，两处原典不同，标出待裁）"')
io.open(P, "w", encoding="utf-8").write(s)

# 大陆名：补「名称待定」
P2 = r"D:\Projects\HisStory\dsh\src\meta.py"
t = io.open(P2, encoding="utf-8").read()
n = t.count("魔法大陆")
t = t.replace("魔法大陆", "魔法大陆（名称待定）")
io.open(P2, "w", encoding="utf-8").write(t)
print("ok", n)
