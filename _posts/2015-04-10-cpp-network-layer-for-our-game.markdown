---
title: cpp network layer for our game
layout: post
guid: urn:uuid:b512122b-4c5f-4008-aac8-631fd340d9c8
description: cpp network layer for our game
tags:
  - cpp
  - epoll
  - event network
  - game
---

## 网络层
一个思维导图

<img src="/static/img/2015-04-10-1.png"></img>

基本模块有：
1,  SocketBase 抽象基类， 定义所有会共性的方法， 基本都是Epoll在回调，比如OnRead, OnWrite分别处理epoll的读写事件， ListenSocket也是继承这个基类.
	m_fd 保存socket的fd属性
	m_readBuffer 和 m_writeBuffer 分别是一个读写的buffer， 类型就是Buffer类

2， ListenSocket继承SocketBase基类，同时它是一个模版类， 它是第一个初始化的Socket，被ClientSocketManager这个连接的全局管理器做初始化， 所有方法都全部做inline， 	一个模版函数来创建ListenSocket， 可以传SClientSocket或TcpSocket作为模版参数T，来具化ListenSocket模版类， 创建 ListenSocket对象之后， 调用Open方法， 进行socket初始化， bind到m_fd,  然后将自己注册到EpollEngine类，等待循环的事件回调， 当有新的连接连上来时， 会由EpollEngine触发ListenSocket的虚函数: OnRead;
	OnRead方法只做一件事， 就是把模版参数T, 也就是模版具化时给的TcpSocket或SClientSocket， 我们是使用业务上层的SClientSocket类做具化， OnRead调用accept系统调用：
        socklen_t len2 = sizeof(sockaddr_in);
       // usleep(20);
        new_fd = accept(m_fd, (sockaddr*)&new_peer, &len2);
        if(new_fd > 0)
        {
            T * s = new T(new_fd, &new_peer);
            s->Finalize();
        }
这里就是调用accept产生新的fd， 用这个new_fd初始化 SClientSocket对象， 之后执行 SClientSocket的Finalize()方法， Finalize方法是在TcpSocket中实现的虚函数，
Finalize方法内， 会将SClientSocket对象自己注册到EpollEngine，同时调用下自身的OnConnect()方法，初始化一些需要ClientSocketManager需要做的连接完成的逻辑， 比如假如ClientSocketManager的管理。
之后便是后续的EpollEngine事件回调处理了.
值得一说的是，SClientSocket对象会在OnRead内完成buffer写入之后， 调用OnRecvData， 进入业务逻辑数据包处理阶段



3,  TcpSocket继承SocketBase基类，实现基类中对应的OnRead, OnWrite等虚函数

4， SClientSocket 继承 TcpSocket， 它是客户端连接时产生的对象类，一些只有业务相关的属性在这个子类里，如gameWrold指针， IsLogin判断， 重写OnConnect和OnDisconnect等方法， 做一些业务逻辑的收尾工作



5， buffer类， 保存从socket read到和执行write准备send的字节， 做offset， m_buffer属性做字节存储，space定义可用空间， written为已写入buffer的字节数
	提供Write方法， 需要写入数据到buffer时调用， 通常就是在poll触发EPOLL_READ事件时，由TcpSocket对象触发调用。数据读入buffer后， 增加对应的已读到的数据大小到written
	提供Read方法， 在上层应用逻辑（对游戏协议包大小做完整包判断的地方）从buffer内读取指定字节数
	着重看一下， 读buffer和写buffer的两个过程：
	Write:  buffer的写入是在TcpSocket的OnRead中进行的， Epoll回调OnRead后， 执行系统调用int bytes = recv(m_fd, (char*)m_readBuffer->GetBuffer(), m_readBuffer->GetSpace(), 0);
这个调用， 会获取read buffer的当前可用空间GetSpace， 从socket stream中读取指定数量的字节到m_readBuffer对象的m_buffer字符数组内， 紧接着调用m_readBuffer->IncrementWritten(bytes);
更新已写入的计数, 也就是增加 written， 写入buffer完成。
写入完成之后， 就直接调用一次SClientSocket对象的OnRecvData方法，通知说有新数据到了，是否读取和读取多少， 由OnRecvData里决定

	业务数据中是协议包， 分成协议头和协议body
	Read:  buffer的读取是在SClientSocket对象的OnRecvData方法里， OnRecvData会循环一个较大的次数， 这里是200次， 尝试读取buffer,。用一个计数器 m_remaining来串行读取逐个过来的协议包，只有当m_remaining等于0， 才开始本次协议包的包头开始读取， 否则肯定是上一次协议包读取尚未完成，m_remaining的字面意思也是这个意思， 表示协议包还剩下多少没有读到，
	接着看， 如果m_remaining等于0， 即本次读取是一个全新的协议包开始读取点，首先读取协议头大小的字节， 如果buffer内数据长度小于协议头， 就直接放弃本次读取，等待后续的字节流写入buffer之后的下一次OnRecvData调用；
	如果足够协议头大小， 那么读取协议头， 同时从协议头数据内得知到本次协议包的body大小，将m_remaining设定为剩余还未读取的协议包大小， 之后再判断一次buffer内大小是否大于m_remaining，否则将返回， 等待socket字节流写入到buffer后的下一次 OnRecvData调用；
	直到buffer内大小超过m_remaining了，在某一次OnRecvData的时候， 就可以整个读取出buffer内m_remaining大小的字节了， 至此一个完整的应用层协议包读取完成了。在这里会把m_remaining重设为0， 让下一次的OnRecvData调用会从协议头开始读起。   之后的都是应用协议的Decode解码和后续的业务层逻辑了
这样整个客户端发数据过来的数据读取完成了。

下面是由服务端send数据到客户端的过程：
TcpSocket除了有 m_ReadBuffer之外， 还有一个m_WriteBuffer，也同样是buffer类对象
在开始写入网络层前， 当然是要对协议包做Encode。
由SClientSocket的Write调用开始，Write实际上是TcpSocket复写的虚函数， Write方法内部首先调用m_WriteBuffer的Write方法， 将需要send的数据先放在本地，之后调用一次EpollEngine类的WantWrite方法， 告诉EpollEngine有数据想要写入socket
	EpollEngine的WantWrite方法， 会先新初始化epoll_event结构， epoll_event的fd指向想要写数据的TcpSocket对象， 之后调用系统调用 epoll_ctl(epoll_fd, EPOLL_CTL_MOD, s->GetFd(), &ev); 尝试产生一个写事件:EPOLLOUT， 这个事件将在下一次epoll_wait中被触发
	当EPOLLOUT事件产生的时候， 回调TcpSocket的OnWrite， 调用完成之后，再做一次 Writable判断， 如果为False， 说明没什么可send的了， 就把Epoll事件ctl到EPOLLIN
模式，切回读模式：
                s->OnWrite(0);
                if(!s->Writable())
                {
                    /* change back to read state */
                    struct epoll_event ev;
                    memset(&ev, 0, sizeof(epoll_event));
                    ev.data.fd = s->GetFd();
                    ev.events = EPOLLIN ;//| EPOLLET;

                    epoll_ctl(epoll_fd, EPOLL_CTL_MOD, s->GetFd(), &ev);
                    --s->m_writeLock;
                }
	为了尽快的完成上层代码提交到m_WriteBuff内的数据send到客户端， 每次在OnRead触发的时候， 还会再显示判断下Writeable， 如果有数据就再切到Epoll的Write 状态：
            else if(events[i].events & EPOLLIN)
            {
                s->OnRead(0);
                if(s->Writable() && !s->m_writeLock)
                {
                    ++s->m_writeLock;
                    WantWrite(s);
                }
            }
这里为了防止两次提交write event， 使用了一个 m_writeLock简单的锁， 声明它为
volatile long m_writeLock 禁用寄存器缓存， 因为这个网络层是单线程的，所以没有线程问题

在TcpSocket的 Write方法里， 调用EpollEngine->WantWrite之前， 先判断 m_writeLock == 0， 否则不做WantWrite调用， 因为 WantWrite可能在epoll触发OnRead的地方，已经被提交过一次了。
m_writeLock 会在 poll触发回调OnWrite完成之后， 切回poll的read state时候做递减
--s->m_writeLock;  表示本次写入完成。

	OnWrite内就是简单的一个系统调用：
	int bytes = send(m_fd, (const char*)m_writeBuffer->GetBufferOffset(), m_writeBuffer->GetSize(), 0);
	读取出WriteBuffer里的所有数据尝试写入socket，然后把返回的成功的字节数，作为参数去删除m_WriteBuffer里的数据： m_writeBuffer->Remove(bytes);
至此数据发送就完成了。


6， ClientSocketManager管理类， 存储TcpSocket


