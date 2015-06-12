---
title: single thread mod to load player data
layout: post
guid: urn:uuid:c3c62553-e00f-4853-bbbd-a2d269fcb22a
description: an injection bug with python cpp
tags:
  - thread
  - cpp
  - game
---

## 单线程游戏玩家数据加载方案

我们一直在使用单线程的场景服务器，基本符合由MUDOS发展而来的精简MMO场景服务的模型.
单线程的优点很明显， 安全， 简单， 逻辑清晰， 不会绕死自己的脑细胞， 避免很多多线程下的坑.
但是玩家的数据并不直接由gameserver(也就是scene server, 以下都简称gs）读取， 而是另外一个由python写的服务负责， 这个py服务负责所有玩家需要保存的数据的保存工作， 比如金币， 等级， 各种养成系统。   

客户端在login到gs后， create player的数据， 需要由gs从hades接口获取， 采用短连接， 或unix domain socket减少tcp连接开销。  
由于load player data有一系列的短连接请求， 肯定是不能真的就这么让它阻塞整个线程了， 而且在 new Player之前， playerdata 只是一份不相干数据， 各玩家之前互相都不干扰，因此我们采用新开thread单独做 load player的数据拉取， 之后带着数据回调 PlayerCreationFunc，将这个callback交友主线程完成 player create.  

总结一下这里有：  

两个或多个线程， 其中主线程是游戏的tick线程， 其他线程是 player data loader线程；  


多线程抢一个Queue结构， 暂命名 m_FunctorQueue_1, 主线程在完成login验证后， 将boost bind 一个LoadPlayerDatafunc， 再bind一次PlayerCreationFunction的callback， 最终回调函数比如PlayerLoadingThread 放入Queue_1；  

主线程自己也保持一个Queue， m_FunctorQueue， 主线程将在每个tick， 进行queue.pop(), 获取到 PlayerCreationFunction后， create player；  

data loader线程将获取队列内的LoadPlayerDatafunc执行，data获取完成后， 带着data作为参数， 将 PlayerCreationFunction 放入主线程的队列，等待最终的的player create;    

暂时记录到这里。
