---
title: Optimization Game
layout: post
guid: urn:uuid:45e7a6c2-4f1d-48fd-ae58-df44f7e1180b
description: Optimization Game
tags:
  - cpp
  - game
  - python
  - thread
---


## 游戏的场景服务和数据服务整合

一直以来都觉的现在运行的游戏后台服务， 实在太多了。  
1,数据服务和场景服务之间的通信， 用的是消息队列zeroMQ来做的， 无形就多了一个消息队列服务， 然后还有一个处理队列任务的mq_worker, 然后数据服务到场景服务的通信.  
2, 需要在每次需要的时候都建立一次本地的socket，就2个服务之间，产生了多余的好多事情。  

目标是将数据服务(python的部分)， 整合到场景服务(c++)的部分里面去， 所有与客户端的通信， 将全部使用场景服务的长连接了，封装一条新的游戏协议，用来处理原来python部分的逻辑。  

cpp的gameHolder里增加一个未login状态时的队列， queue包在map内， 针对每个客户端连击产生一个队列。Player在登陆前的python业务逻辑接口， 将通过这个队列处理。  

队列在主循环内Pop出一条，放入线程执行，需要一个标记位，使得单个客户端的请求串行化。  

现在已经完成整合了， 只是原python逻辑部分与客户端的协议， 返回给客户端的结果是json， 在短连接里json还好， 在长连接里， 它实在太大了，需要做压缩。 也想过用protobuff， 但是原来的python逻辑返回的json数据结构太松散了，如果将json转成pb， 光描述文件，就能耗死人。 而且以后返回说不定就改了某个结构了，初步预计只能用gzip压缩一下json.dumps之后的string。损失部分cpu我想并没有问题。

