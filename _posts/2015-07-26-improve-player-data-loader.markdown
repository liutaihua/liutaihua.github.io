---
title: improve player data loader
layout: post
guid: urn:uuid:230974a5-661f-4d17-8253-9334f267aad8
description: improve player data loader
tags:
  - queue
  - game
---


## 玩家数据的loader优化

由于历史原因， 最早的时候玩家数据是在2个独立的服务进程中都存在， 游戏场景服务A, 和游戏数据逻辑服务B， A中的数据来自于B， A服务会根据某些逻辑， 触发数据回存， 将数据回存到B， 达到数据一致性要求， 但是随着游戏过程中， 会积累资源比如金币之类的， 这个积累的数据暂时只会存在场景服务A中，后面的运营过程中证明， 这种数据分两份的做法， 是个非常大的坑， 有很多理论上的机会导致数据不一致， 丢数据的问题。  

运营过程中优化过几次A--> B的数据回存操作， 绝大部分数据已经不再做临时数据了， 比如拾取一个物品， 直接拾取操作从B服务走， 场景服务A只需要在请求完成时得到一份通知，重新从B拉去最新的背包数据。   

游戏中很多类似通知场景服务A做数据更新的操作， 可以叫做dataloader， 问题在于loader是一个同步的阻塞的操作， 由于场景服务的逻辑是一个单线程的服务， 所有战斗， 游戏中的每侦都中这个线程内进行的， 连续多个玩家的dataloader操作，可能会因为B-->A的数据延迟， 造成线程阻塞， 无论是多人场景， 还是单人单world场景， 如果线程阻塞了， 会导致其他玩家有感觉， 延迟严重的， 玩家打怪， 放技能， 本应该事实反馈的伤害数字， 会因为其他玩家的Loader而出现卡顿， 延迟.  

所以决定把loader操作做异步化， 异步之后的缺点是， 如果异步线程稍慢， 会导致玩家在某个操作后， 延迟一点才看到自己界面上的金币等资源的变化， 但是这些资源并不是直接的战斗数值， 因此基本是完全不影响体感的。  

异步化的过程比较简单， 做过两版：

1， 完全异步， 发起的loader， 直接boost:bind 把player的this指针带给异步方法， 放入线程队列中， 这个方法完全异步了player的 data loader操作， 但是异步线程和主线程在共享这一个player指针， 无论怎么做， 都会存在一个理论上的操作空指针的可能，  比如主线程里玩家已经离线， 就清楚了player对象， 造成异步线程player已经不存在了， 当然可以在异步里判断player的存在在做操作， 但是过于繁琐， 对每个player的操作都事先判断下. 或者是主线程不直接做删除， 而是把需要删除的player， 放入一个deleter 线程，设定一个标记位来决定是否删除. 但是改动略大。  

2，就是已经采用的方法， 半异步化。 因为这个 data loader最耗时的其实是从B --> A过程中的一次socket连接开销和数据传输开销， 只需要把这一个子步骤放入异步线程即可， 数据获取全部完成之后， 绑定回调函数， 再放入主线程， 主线程会在world的每侦被Pop一次， 得到执行。 那么整个过程是： 

reqLoadData --> generateLoader(attach a callback: onDataLoaded()) --> put it to threading queue --> Got all data in threading --> bind the callback(onDataLoaded(*data)) --> put callback to main threading --> execute the callback at Update done.

经过测试， 开了100个机器人， 每隔50ms做数据dataload操作， 同战斗场景内玩家杀怪， 不再有卡顿延迟， 体感得到优化。.

