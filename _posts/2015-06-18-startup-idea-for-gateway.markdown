---
title: startup idea for gateway
layout: post
guid: urn:uuid:4cf68d7e-fd45-4f0c-b212-5f2b693808ae
description: startup idea for gateway
tags:
  - cpp
  - gateway
  - socket
  - boost
  - asio
---


## gateway的初步想法
已有一套基于epoll event的框架， 打算gateway在这个基础上， 配合boost::asio做。雏形先做个socket proxy出来.  

TODO:
1，设计一个AsioClient类， 它是gw到后端具体gs的连接封装. AsioClient类想到2个方案：
        a, 在原来的面向玩家的SClientSocket类和AsioClient类之间做friend， asio_write, asio_read, asio_connect的callback中， 回调SClientSocket中的对应Write, Read达到与epoll 事件打通， 因此打通玩家到后端gs的proxy通道;
        b, 在原来的 SClientSocket 类基础上， 再次derive一个类型:AsioSClientSocket, 封装asio_write等几个方法， 这样asio的callback和epoll事件之间的打通， 就变成了子类对基类的方法互相调用, 以此也可以打通玩家到gs的通道， proxy数据;
        
2, 设计一个buffer类型， 存放proxy过程中在AsioClient里需要存放的chunk；因为asio异步的原因， 或许还要处理锁的问题.

3， 增加一项游戏协议， 具体应该是接收一个REQ，会将已登陆在gw上的玩家， 代理到新的后端gs， 并断开当前gs的AsioClient对象连接， 处理一些后续事情， 比如通知原gs销毁玩家数据。

暂时想到这么多， 空闲的时候上手做做看。因为没找到可用的轮子， 只好自己琢磨琢磨得到这个初步的雏形。
