---
title: an injection bug with python cpp
layout: post
guid: urn:uuid:c3c62553-e00a-4856-bbbd-a2d269fcb99a
description: an injection bug with python cpp
tags:
  - 漏洞
  - python
  - game
---

## 一次悲惨的PY注入式漏洞

在前一篇里讲过的使用cpp和python互相调用方法的结构。 这两天就有一个相关漏洞被人利用了， 异常悲惨。  

我们的场景服务对每一个GameWorld都有一个PyTermWorld， 是用来接受数据服务发送过来的连接信息的， 比如可以通过协议连接socket到PyTermWorld， 发送LevelUp, 发送 AddExp等， 也有其他命令是通知PyTermWorld调用相关Python函数的， 比如send_cmd(cmd='import notify;notify.test(xxx,yyyy)') 这样的命令， 这里面的cmd会带上具体的脚本模块以及具体的python方法名称，  


问题出在， 我们在某一出代码里， 接受客户端的一个参数， 之后直接将这个参数内容作为了send_cmd中cmd的某个内容， 导致被人利用，参数直接写了一整条的python exec语句， cpp在调用py函数的时候， 同时会把参数解析， 导致注入成功。  

漏洞直接导致玩家可以修改任意数据， 幸好未在大规模被使用前，找到并修复了。 实在很坑， 利用漏洞的朋友本身有一定实力， 另外客户端被他反编译了， 基本上来说客户端代码已经对他开源了， 目前反编译真是无解。 估计也是有了客户端代码， 才更容易的利用上了漏洞。  



