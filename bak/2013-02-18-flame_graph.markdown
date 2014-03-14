---
title: "flame graph可视化分析"
layout: post
guid: urn:uuid:b87da13a-a4dd-402f-b06a-cef7eeee2d80
tags:
    - linux
---

FlameGraph的例图,解释如下:

图中每一个方块代表栈里的一个函数。
Y轴代表调用深度，最上面的是当前正在CPU上执行的函数，下面的都是其祖先。每个函数都是由它下方的函数调用的。
X轴不是按照时间先后排列的，它只代表样本数目。方块越宽，代表该函数出现的次数越多。
在有多个并发线程同时被采样，样本总数可能超过采样所用的时间。

配合perf使用的方法,分3步:

>>perf record -a -g -F 1000 sleep 60

>>perf script | ./stackcollapse-perf.pl > out.perf-folded

>>cat out.perf-folded | ./flamegraph.pl > perf-kernel.svg

perf record是使用perf工具采样, -a参数表示对整个系统采样,如果希望只采样指定进程, 那么可以使用-p 参数后跟PID
-g表示记录函数调用桟, -F表示采样频率, 最后的sleep 60表示采样60秒后退出然后生成perf.data文件

perf script 表示 Read perf.data (created by perf record) and display trace output 
这些从perf --help中都能看到帮助信息

最后一步是使用flamergraph.pl生成svg图片


perf工具非常方便, 上述只是为了产生图片形式的利于直观, 即使没有flamegraph, 只用perf也一样能方便看到统计数据:

perf record之后,  使用perf report 即可查看执行record时生成的统计数据了,相对直接vim查看统计数据也时比较直观的.

其中还有pert top  , perf stat等, pert top能实施的统计数据并以top的形式展现.
