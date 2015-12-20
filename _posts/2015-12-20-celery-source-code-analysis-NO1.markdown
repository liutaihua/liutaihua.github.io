---
title: celery source code analysis NO1
layout: post
guid: urn:uuid:8eb843e9-a4ca-4904-9f7d-6f15e87020cf
description: celery source code analysis NO1
tags:
  - celery
  - python
---


# celery source code analysis

最近用celery做了分布式消息队列服务(我们取名hera)， 同时稍微改了一些strategy， celery的一些retry的逻辑， 增加了pause功能，并且为项目封装了一个简单的go-celery， 现在它支持：

1. 自定义strategy， 用于对消息收到后，Request封装前的一些逻辑；
2. 更实效的支持revoke的expire和active times；
3. 重载Task的on\_failure, on\_success等事件回调方法；
4. 新增backend支持：redis-sentinel
5. 新增pause功能(这个暂还不支持针对running状态的task做pause)；
6. 支持etcd配置管理和服务发现；
7. 封装部分任务方法， 以支持golang的任务调用；

celery代码的结构很不错， 等全部整理好， 自己将整理下写出来。
