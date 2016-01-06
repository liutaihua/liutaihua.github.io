---
title: saltstack DSL
layout: post
guid: urn:uuid:8bab8376-2cd3-4450-886a-9587514df0e5
description: saltstack DSL
tags:
  - saltstack
  - DSL
---

 # saltstack DSL

用salt很多人都在用，我们也在用，用的还算较多，现在所有服务，自定义服务，常用系统服务，包安装，git库更新等都进入salt管理了

salt默认采用的是yaml jinja模版做sls的语法渲染，可以自定义macro, 可在pillar里根据每个minion不同来定义不同的lib，然而这些都不是今天的重点

重点是用yaml或jinja语法写salt，写macro稍微复杂点， 很容易绕进模版里， 比较费脑力，不着急， 已经有人撸出了DSL语法了， 而且salt已经merge了这个特性了

写sls的时候，这样子， 就可以做到了：

```python
#!pydsl

for i in range(10):
    i = str(i)
    for ii in range(5):
        ii = str(i) + str(ii)
        state(ii).cmd.run('echo '+i, cwd='/')
        
mod = include('service.my_pydsl_reuse_func_list', delayed=True)
mod.my_func(1, 2, 'three')
```

这里展开以后就是50个活生生的salt state， 因为是pythonic的， 所以你可以用python来干出任何事情了， 想想都觉得好可怕， 以后可以和繁琐的宏调用say 拜拜了.

附上官方文档地址 在<a href="https://docs.saltstack.com/en/latest/ref/renderers/all/salt.renderers.pydsl.html">这里</a>
