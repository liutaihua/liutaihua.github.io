---
title: 一则内存泄露
layout: post
guid: urn:uuid:4b1a6a5e-38e3-4e62-b5b1-fb70786d6061
description: a memory leak with python
tags:
  -python
  -memory leak
---

上段时间组内解决的一个奇葩内存泄露问题, 找到最终原因时发现真是奇坑无比的一个原因.
一开始怀疑某个逻辑会导致dict引用数一直增加, 或是其他对象始终不释放, 导致内存一直在涨, 期间开启gc collect也没用.
使用memory grapher 等内存泄露工具检测, 打印出一段时间对象的增长量,  dict, list等数据结构的增长量, 从打印信息看虽然有一定问题, 但是确实不可能会导致那么严重的内存泄露, 我们某个游戏服有时甚至会突然从300MB进程内存, 很快就上涨到3GB.
最后只好从业务层面,  把那些请求量大的接口, 逐个拿来测试, 排除法,  但是居然无论是哪个接口, 排除到最后即使一个非常简单的逻辑, 同样会有内存泄露, 简直无法相信自己的眼镜.
最后的最后,  发现在框架的最外围代码里,  有一处gsignal(signal.SIGTERM, exit, server) 代码, 当时应该是为了方便测试, 捕获ctrl+c等信号, 以便快速使各coroutine迅速退出.
但是问题在于这3行signal代码, 写在app中, 就是gevent的 StreamServer构造好之后, 每次有请求来都会回掉的那个主入口函数.

<p><code>
server = StreamServer(('0.0.0.0', port), apps, spawn=pool)

....

def apps(socket, address):
    # this handler will be run for each incoming connection in a dedicated greenlet
    # using a makefile because we want to use readline()
    gsignal(signal.SIGTERM, exit, server)
    gsignal(signal.SIGQUIT, exit, server)
    gsignal(signal.SIGINT, exit, server)
    socket.setsockopt(origin_socket.IPPROTO_TCP, origin_socket.TCP_NODELAY, 1)
    port = int(sys.argv[1])

...

</code></p>

这段代码会导致只要有socket回调, 就创建3个信号处理标记, 对象是只增不减. 没想到当初随便的一记只为测试方便的代码, 导致后来一直的内存泄露. 
