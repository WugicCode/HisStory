import io, re

def edit(path, pairs):
    s = io.open(path, encoding="utf-8").read()
    for a, b in pairs:
        n = s.count(a)
        s = s.replace(a, b)
        print(path.split("\\")[-1], n, a[:20])
    io.open(path, "w", encoding="utf-8").write(s)

SRC = r"D:\Projects\HisStory\dsh\src"

# 元数据：动词统一为「洗入」
edit(SRC + r"\meta.py", [("洗回卡组", "洗入卡组")])
edit(SRC + r"\meta_rules.py", [("洗回卡组", "洗入卡组")])
# 卡牌关联描述
edit(SRC + r"\data_cards.py", [("共用「洗回自身」的循环结构", "共用「加入自身」的循环结构"),
                               ("加入手牌而非洗回卡组", "加入手牌而非洗入卡组")])
