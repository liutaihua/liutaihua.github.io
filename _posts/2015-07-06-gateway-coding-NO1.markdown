---
title: gateway coding NO1
layout: post
guid: urn:uuid:82cb7100-9a6f-46e4-8cf3-7f9af2d191ae
description: gateway coding NO1
tags:
  - cpp
  - gateway
  - socket
---

## 网关编码一

拆了又补， 补了又拆，边拆边想，发现之前用asio socket的方式做gateway， 有不少问题。  
* 1， 如果用asio做连接upstream server的socket， 还需要把byte buffer实现一遍， 虽然已有现成的buffer代码， 不过生搬过去还是显的略繁琐;
* 2,  如果用asio， 下游用的是epoll， 要在asio的async_read_some, 和epoll的 OnRead, OnWrite间穿梭， 感觉好脑残，之前的想法果然傻逼， 当然推翻它重来了;
* 3， 改成都用epoll监听， 方便很多。基本上就是设计一个新类 ProxySClientSocket 继承SClientSocket, 就可以把原有的buffer都用下来啦， 只需要额外增加一个 ConnectTCPSocket模版，针对传进来的类型， 把connect之后的新fd做参数传给T, 创建返回即可，把父类的OnRecvData 改成虚函数， 在ProxySClientSocket里重写；  
*  这样epoll继续回调一样的方法， 注册在epoll上的面向客户端的继承SClientSocket和面向上游游戏服务的ProxySClientSocket， 就可以互不想干的处理socket数据， 在各自的OnRecvData内处理， 之后调用对方的SendPack.  
*  
{% highlight c++ %}
class ProxySClientSocket : public SClientSocket
{

public:
    ProxySClientSocket(SOCKET fd, const sockaddr_in * peer);
    ~ProxySClientSocket();

private:
    char proxySendBuff[MAX_PACK_LEN];
    char proxyRecBuff[MAX_PACK_LEN];

public:
    std::unique_ptr<SClientSocket> m_pPrimeSocket;

    void SetPrimeSocket(SClientSocket* p);
    virtual void OnRecvData();
    SClientSocket* GetPrimeSocket() {return m_pPrimeSocket.get();}
};
{% endhighlight %}

在面向客户端的继承SClientSocket中增加一个m_pProxySocket 指向已建立的，和上游游戏服务的socket；  

在面向上游游戏服务的ProxySClientSocket里m_pPrimeSocket 指向已上面的连接客户端的socket;

数据proxy就完成了。  

这个方案的优点是：  
* 1, 复用了已有的代码， 如果只是单单做前期的转发型简单gateway需求， 几乎没有什么改动;
* 2,  用epoll， 根据虚函数表， 很直观的把upstream socket和downstream socket分开， 更容易理解;
* 3， 转发的颗粒度是游戏协议的单个数据包， 因此可扩展性比较好， 可以在此基础上加入强网关的设计， 已经想到的要加入的有： 客户端在保持当前连接的状态下， 跳转场景服务，跳转动作由gateway断开前一个proxy， 创建一个连接到新场景的proxy;  还可以做其他一些以前设计缺陷的， 不能准确真实的统计在线玩家的.   
* 
日后再谈..
