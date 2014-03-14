import os
import uuid

temp_str = """---
title: %s
layout: post
guid: urn:uuid:%s
tags:
    - move from old blog
---"""

for file in os.listdir('./_posts'):
    print file
    f = open('./_posts/%s'%file, 'r')
    s = f.readlines()
    title_str = s[2].split(':')[-1].strip()
    content = temp_str % (title_str, str(uuid.uuid1()))
    s = s[7:]
    s = ''.join(s)
    content += s
    print content
    f.close()
    ff = open('./_posts/%s'%file, 'w')
    ff.write(content)
