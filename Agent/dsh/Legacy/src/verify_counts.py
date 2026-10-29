import io, re, os

ROOT = r"D:\Projects\HisStory\dsh"
for f in ("archive.html", "sandbox.html", "index.html", "world.html", "story.html", "cast.html"):
    p = os.path.join(ROOT, f)
    if not os.path.exists(p):
        print(f, "MISSING"); continue
    s = io.open(p, encoding="utf-8").read()
    tail = s.rstrip()[-110:].replace("\n", " ")
    kick = re.search(r"<small>(.*?)</small>", s)
    lead = re.search(r"全部 (\d+) 张，按([^，]+?)个编组", s)
    cnt = re.search(r'id="fcount">([^<]*)<', s)
    print(f, "| tail:", tail)
    print("    kicker:", kick.group(1) if kick else None)
    print("    lead:", lead.group(0) if lead else None, "| fcount:", cnt.group(1) if cnt else None)
