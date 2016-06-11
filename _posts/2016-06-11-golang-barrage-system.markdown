---
title: golang barrage system
layout: post
guid: urn:uuid:b62abd8b-1d23-495a-932f-93fde8f91e67
description: golang barrage system
tags:
  - golang
  - im
---



<a href="https://github.com/Terry-Mao/goim">goim</a>a>是B站开源的一个方便横向扩容的im系统，用来做聊天室系统非常合适，代码质量也非常不错。
组件 router, logic, comet, job 

主要是 logic, comet

两个对外的服务 

logic 是一个消息发生上行服务， 广告过滤系统集成在里面 

comet 是一个支持ws和tcp协议的消息下发服务

job, router对内 

job只是负责从kafka中获取msg， 根据策略，将消息rpc call 到comet 

router 是一个状态保持服务， 设计原意是为了保存 uid --\> comet, 达到可以发消息给指定uid的功能 

内部使用rpc方式做调用

* logic --> router的访问负载中， 用hashRing方式做一致性hash代替普通hash方式， 来让uid分布到各个router 

* 我们自己把广告过滤集成在里面， 是采用一个全局的manager 管理所有filter， 进程起来的时候， 初始化这些filter， filter跑在线程里， 可配置一个缓冲区长度， 

* 为每个请求产生一个Msg的struct对象， 结果和回调函数， 绑定在对象上， 在channel中传递，过滤完成后，产生kafka消息， 和redis消息。 

comet 
个人已修复或完善了这些内容：  
* 支持ws协议，不过B站自己没有使用， 测试也比较随意。更推荐是使用tcp的方式， ws发生text类型，冗余太多，耗流量， 且每条产生一个syscall，系统负担较大.

* 丢失消息的bug， 很容易重现 

* 单个msgProto的body内， 有包含多个儿子msgProto的对象， 没办法支持ws message文本方式下发消息的方式。逐个把原设计中的大包， 拆成小包，再给ws下发. 同时也让它支持batch的方式

* 内存泄露的问题， 不只是ws协议下， tcp下应该也有。 闭包的问题导致连接对象的引用被hold住， 理论上是存在释放的机会的， 取决于timer的配置大小。 


#### 好的设计

* tcp方式下， 使用了自分配内存池， 预申请， 之后用这片内存池做readBuff和WriteBuff：

 * 主要是由Buffer对象组成的一个链表结构， 每个Buffer对象内是一个[]byte数组，不过它只是Pool对象内buf数组的引用， Pool的大小是 num * size个byte， Pool的grow()完成malloc， 

  * 每个连接建立后会去Pool内拿内存， 创建一个自己的Writer， Writer也是经过封装的，这个Writer相当于在conn.Writer上层做了一次包装，缓冲一下，减少系统调用， 具体缓冲多少，是由Pool设置中的size来决定的。


  * job到comet调用过程中的buffer设计， 缓存短时间片内的房间消息， 防止频率过高的调用，但是buf每次都重新产生， 略有点耗。 

  * comet中heartbeat协议侦的方式， 是用Ring buffer算法， 复用heartbeat对象，免去重复创建。 

  * 封装的timer，做tick或是timeout callback，一样为了在高频率情况下，复用timer对象， 方便让上层调用者保持简洁的代码。 

  * comet结构是 Bucket->room->Channel, 简化消息传递的时候， 寻找的复杂度。 广播类型， 直接走所有Bucket中的chs，到达最终连接， 

  room广播时， 先到Bucket的一个chan， 有多个线程处理将消息交给最终的room， 到达room下的所有连接。 

  * 有不少的地方， 使用map，代替array，比如 一个 []string的方式能实现了， 用 map[string]struct{}， map的查找，插入，删除均是O(1), 而array的插入和删除是O(n)，会涉及内存拷贝。

  PS 关于golang的map性能， 官方是说不确保map一定在哪个性能， 似乎是个树实现， 而不是hashtable， 所以不一定是O(1)， 可能是O(logN)
