---
title: resource lake code of rabbitmq consumer
layout: post
guid: urn:uuid:887fd09b-04b5-4a8e-9787-10de925032b1
description: resource lake code of rabbitmq consumer
tags:
  - golang
  - rabbitmq
---

# 一次rabbitmq没用好的资源泄露

最近重写的一个使用rabbitmq做borker的服务， 一个go-lang的小服务，支持多节点，很简单就是从mq获得msg， 如果有通过websocket连接上来的client， 那么就push给它。

1. 支持配置多个amqp 地址， 对它们做fail over处理
2. 支持对rabbitmq连接的连接池
3. 支持etcd配置发现更改，etcd里的配置被更新后改变本地内存中的连接地址。

具体的coding设计， 应该是一个client一个queue declare，结果被同事做成了一个连接过来就会新开一个临时的queue，好吧。

然后每次declare的时候都先open channel, 而且没有做好清理工作， 而且由于客户端本身不稳定会经常断线重连， 导致时间一长，造成相当大量的channel和queue, rabbitmq的max processes很快就被挤爆了， 只好临时把rabbitmq的max processes提高。 

改变erlang的 processes的文档： http://www.rabbitmq.com/configure.html， 其实是这样一个环境变量：
```
Unix*: "+K true +A30 +P 1048576 -kernel inet_default_connect_options [{nodelay,true}]"
```

既然找到问题了，就好解决了。针对客户端断开连接之后， 做好相关的资源清理工作。  
其实最好的方式， 应该是一个username一个queue, 而不是这样每次都产生一些临时queue来处理问题。这已有很好的例子了， 比如celery， 应该参照人家优雅的做法， 而不是自己闭门造车.
