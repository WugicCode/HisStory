import io

p = r"D:\Projects\HisStory\dsh\src\meta_world.py"
s = io.open(p, encoding="utf-8").read()

old = ('body="莫菲是魔王军目前唯一的卡牌来源：一张 1 费的捕梦网。她在人物表里的身份是梦之掌司，在规则里是一名法师·神官——"\n'
       '          "两处原典与归档页现在写法一致，不再有需要裁定的分歧。"')
new = ('body="莫菲是魔王军目前唯一的卡牌来源：一张 1 费的捕梦网。她在人物表里的身份是梦之掌司，在规则里是一名法师·神官——"\n'
       '          "前者是职业，后者是单位类型，两层用词，不必对齐。"')

assert old in s, "not found"
s = s.replace(old, new)
io.open(p, "w", encoding="utf-8").write(s)
print("ok")
