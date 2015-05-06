---
title: single Threading of epoll server
layout: post
guid: urn:uuid:e6bbfe97-9d1b-4a54-bdbb-281feda89d48
description: single Threading of epoll server
tags:
  - cpp
  - epoll event
  - game
  - network framework
---

## 一个单线程的epoll server示例
这个示例是一个echo server， 将回显client端send的64字节.  

代码在 <a href='https://github.com/liutaihua/echoEpollServer'>echoEpollServer</a> 
在OSX下 gcc 4.6， linux 下编译可用， 默认被写死了监听8886端口.

## epoll的几个基本小知识：
1, event struct结构：  
<pre><code>
struct epoll_event {
    uint32_t     events;      /* Epoll events */
    epoll_data_t data;        /* User data variable */
};  
</code></pre>

2, epoll的几个事件类型：
EPOLLIN: 有新的数据流进来了;  
EPOLLOUT: socket可写。  

包含的组件有：  

1， ServerClientSocket.h 描述单个client 和server之间socket的class；  
2， SocketMgr.h epoll或kqueue（OSX下） event io的class， 负责创建一个singleton实例， 注册新的socket到epoll， 设置event事件，调用已注册到epoll的socket fd的方法， 完成写入和读取数据的；  
3，BaseBuffer.h， StraightBuffer.h 一个简易的buffer，一个socket 读和写的临时缓冲区， 完成诸如约定每次读取64字节数据后， 做回显send回client。
4，ThreadPool.h 线程池，但本示例只用到单线程；  
5，ListenSocket.h，负责服务监听socket的创建的， 创建完毕后， registe到epoll， 当client首次连接时，epoll触发ListenSocket的 OnRead()，OnRead内使用accept从os的连接队列里， 取一个新连接，并建立一个新socket， 之后这个连接之间的数据流就交由这个新socket负责， 使用这个新socket， 生成一个ServerClientSocket实例， 同时把这个socket注册到epoll， 后续连接的事件由epoll来回调ServerClientSocket的OnRead等方法；

6, BaseSocket.h是基类，ListenSocket， TcpSocket是他的子类， ServerClientSocket是它的孙子， -。-
7， 其他的是一些杂项。SocketOps.h是一些设定socket option的一些函数.  

当数据到达 ServerClientSocket的时候， 已经可以进入应用层逻辑了。 可以根据需求扩展了。
