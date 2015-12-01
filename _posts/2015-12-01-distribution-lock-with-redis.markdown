---
title: distribution lock with redis
layout: post
guid: urn:uuid:409a1e1d-5010-4876-9f79-6c9370bbc171
description: distribution lock with redis
tags:
  - redis
  - distribution lock
---

## 再次看redis的分布式锁

话说以前我们也有用到这种需求， 在一个noSql数据库中，利用key的expire功能实现的一个锁，那时候因为memcache支持不是太好， 还是略有些问题，不能在很严苛的环境中使用。

主要是一个解锁时候的问题： 当clientA获得锁之后，进行后续逻辑block在某个地方，如果这个时间足够长，长过锁的有效时间(即set在memcache中的expires时间)， 当clientA完成操作，解锁的时候，如果直接使用del操作， 很有可能就会把clientB刚刚完成的锁操作(set key)给删除掉。
  
解决的方法是在unlock前检查一下clientA自己之前的锁是否还有效， 然后再决定是否执行del. 解决办法可以是比较当前时间里加锁时间的流失时间是否大于锁的有效时间，不过这还是不足够严格， 当时碍于我们代码简单，而且每个客户端请求在全局还有一个超时时间3秒， 锁的过期时间是4秒， 不会出现某个请求超过3秒还去解锁的情况， 因为那时候在网络框架上层已经将这个请求执行中断了。


上两天在微博看到有人分享一个讲座说利用redis做分布式锁的， 文章在<a href="http://blog.jobbole.com/95156/">这里</a> 稍微看了下，作者还是没有很好的解决这个问题.   

今天同事发了一个redis.io上的一个讲redis分布式锁的文档， 里面有个很好的解决方案， 而且算法给的也很详细， 地址在 <a href="http://redis.io/topics/distlock">这里</a>, 大体的思路是：

1. 利用redis的setnx功能，对lockKey进行 SET not-exists-key 检查， 没有这个key的时候， 才能set成功， 另外set的时候带上px参数，表示过期时间(px的单位是毫秒), set的value为当前客户端生成的一串唯一性的字符串
2. 利用redis可以嵌入lua脚本的功能，执行简单的lua命令，做法是，先进行get，如果取到的value == self.val_string， 才认为这个锁确实是自己加的， 可以进行del操作， 否则不做任何事情，lua脚本如下： 

```
    unlock_script = """
    if redis.call("get",KEYS[1]) == ARGV[1] then
        return redis.call("del",KEYS[1])
    else
        return 0
    end"""
```
关于redis的lua支持， 可以google文档查看， redis对lua嵌入脚本的支持是原子性的， 它会保证在同一时间， 只会有一个lua脚本在执行， 很像redis的事务功能watch 和multi语句功能。
这样来避免unlock做del操作的时候， 影响到其他客户的锁。  

同时， 还进行多个redis master的支持. 算法很简单， 就是半数以上master被成功set， 才认为本次lock成功， 在对每个master node做set的时候， 每次都计算一下lost time, 如果超过锁的总有效时间，或最终没有达到半数成功的条件， 那么回滚前面成功的锁。

至此， redis锁很完美了。另外， 推荐不要使用failover的方式来做redis的分布式锁， 这涉及到failover期间， 锁漂移和可能会同时存在两个锁的问题， 因为redis的failover同步算法是异步的. 如果要考虑锁的failover， 可以使用多个master node 的方式来做。  
点击<a href="https://github.com/SPSCommerce/redlock-py">这里</a>是一个python语言的redis分布式锁的实现.
