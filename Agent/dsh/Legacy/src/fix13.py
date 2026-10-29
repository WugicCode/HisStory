import io

p = r"D:\Projects\HisStory\dsh\src\meta_rules.py"
s = io.open(p, encoding="utf-8").read()

open_old = '''OPENS = [
    ("〔待确认〕「她的梦想」的『禁锢』", "当前卡池里没有名为「禁锢」的卡牌条目：有「枷锁」这张牌，也有「禁锢」这个状态。"
                                "是改名还是新效果，原典尚未说明，此处照录、不裁定。"),
'''
open_new = '''OPENS = [
'''
assert open_old in s
s = s.replace(open_old, open_new)

chg_old = '"无踪无迹补「激活时，同时」、她的梦想改『禁锢』、绯红之月加【限定】并改「开发一张『红月』」、"'
chg_new = '"无踪无迹补「激活时，同时」、绯红之月加【限定】并改「开发一张『红月』」、"'
assert chg_old in s
s = s.replace(chg_old, chg_new)

add_after = '''    ("溯因", "`dsh/README.md` 记录了两轮修订的逐条对照。本页转录以当前 `CardsDesign.md` 为准。"),'''
add_new = '''    ("误写已改正", "「她的梦想」原稿曾把『枷锁』误写成『禁锢』（卡池里没有名为「禁锢」的牌）。"
              "作者确认这是笔误，已改回『枷锁』——它属错字，不是卡面变更。"),
    ("溯因", "`dsh/README.md` 记录了两轮修订的逐条对照。本页转录以当前 `CardsDesign.md` 为准。"),'''
assert add_after in s
s = s.replace(add_after, add_new)

io.open(p, "w", encoding="utf-8").write(s)
print("ok")
