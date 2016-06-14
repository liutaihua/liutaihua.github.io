---
title: distributed rate limiter
layout: post
guid: urn:uuid:184a0408-d155-496a-b9e5-69e3275acb97
description: distributed rate limiter
tags:
  - redis
  - rate limiter
---
# 用redis造一个分布式rate limiter

号称分布式， 其实是装逼了呢。我也潮流用一发高逼格词 ＝。＝ 

场景是： 我有一个服务， 需要对用户请求进行限速， 根据uid或者其他user信息， 服务进程是多节点的

经典的限速方式有很多种， token bucket(令牌桶), leaky bucket(漏桶)， 它们的区别基本是对Burst(突发流量)的限制不一样，token bucket能允许一定突发流量， 具体算法查看wiki描述吧。 

但是， 这些算法， 都是基于本地内存存状态的， 当然， 我懂， 可以把几个主要状态，比如tokens, capacity都存redis里做同步，然后进程节点之间共享， 但它的fill操作，就是增加桶内令牌时， 如果也用redis， 会变成 N \* freq 的数量， N是节点数， 因为每个节点都往里面fill， 导致在横向扩展节点数量的时候， 配置没法很直观的配出需要的桶容量。 

之前用redis也实现过一个不支持Burst的限速， 可是用的是key-value, 而且用了expire， 当大量用户的时候， 过多的key expire检测会导致redis性能过多消耗。

还好， redis有sorted set， 可以用一种简便的方式来完成限速， 不过缺点是不支持Burst。 具体做法是： 

1， 为每个user维护一个sorted set, 当用户请求来时， 先用 ZREMRANGEBYSCORE命令删除本时间片内之前的element 

2， ZCOUNT统计出已有数量， 如果大于阀值认为被限速了，后续处理业务逻辑 

3， 没有达到阀值，那么正常完成请求， 并把ZADD一个element， key和val都是当前时间的毫秒数时间戳。

完成，很简单的过程。

