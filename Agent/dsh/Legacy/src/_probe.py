# -*- coding: utf-8 -*-
import io, re
p = r"D:\Projects\HisStory\dsh\src\meta_world.py"
s = io.open(p, encoding="utf-8").read()
i = s.find("CAST_CONFLICT")
print(repr(s[i:i + 320]))
