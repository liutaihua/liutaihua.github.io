---
title: tcp-kernel-net.core.somaxconn-backlog
layout: post
guid: urn:uuid:cd45f762-d157-4a2c-854e-eaa6d4070247
tags:
  -tcp
  -kernel
---


一个新服上线, 玩家人数因推广, 较以前的服在线人数大增,  而且由于物理机器上已经存在以前的几个服, 这次新服上了之后在线人数到一定量就会产生掉线的情况, 很奇怪,  怀疑过sysctl.conf 的range_port设的不够用, 或time_waite过大,  但实际这2个值都应该在正常范围内,  但是还是优化了一下回收time_waite的速度, 以及加大range_port,  最后还是不奏效.

由于我们每个服上,  有2个服务进程之间会使用127.0.0.1产生短连接, 所以有比较大的tcp断开后的未关闭部分, 但是原因并不在此. 

最后查到了net.core.somaxconn  somaxconn这个是os限制单个listen端口的tcp队列长度,  优化之前其实已经改成了1024(系统默认是128),  但是由于新服并发量比较大, 突破这个数字是有可能的,  果断加大了net.core.somaxconn数量到32768, 肯定足够大了, 继续观察.

同时看了下关于tcp的backlog选项, 这个是除了os层的somaxconn外, 应用层在一个socket  listen的时候设定的. 
对于一个listening socket，kernel维护者两个队列：
1.一个未完成连接的队列，此队列维护着那些已收到了客户端SYN分节信息，等待完成三路握手的连接，socket的状态是SYN_RCVD

2.一个已完成的连接的队列，此队列包含了那些已经完成三路握手的连接，socket的状态是ESTABLISHED

backlog参数历史上被定义为上面两个队列的大小之和

Berkely实现中的backlog值为上面两队列之和再乘以1.5



当客户端的第一个SYN到达的时候，TCP会在未完成队列中增加一个新的记录然后回复给客户端三路握手中的第二个分节(服务端的SYN和针对客户端的ACK)，这条记录会在未完成队列中一直存在，直到三路握手中的最后一个分节到达，或者直到超时(Berkeley时间将这个超时定义为75秒)

如果当客户端SYN到达的时候队列已满，TCP将会忽略后续到达的SYN，但是不会给客户端发送RST信息，因为此时允许客户端重传SYN分节，如果返回错误信息，那么客户端将无法分清到底是服务端对应端口上没有相应应用程序还是服务端对应端口上队列已满这两种情况
