---
title: Transfer coding of our RPG game
layout: post
guid: urn:uuid:4e3bf3c1-3ab3-4e56-93ee-3953cfb20625
description: Transfer coding of our RPG game
tags:
  - game
  - c++
  - network layer
  - transfer layer
---


首先， 单个socket是面向玩家的， 以此展开的会有，这个玩家，也就是说这个socket，会拥有一个gameWorld, 以及在玩家login之前， 所有玩家都面向的gameHolder， Holer处理登陆， 已登陆玩家数据网络层将推送给Player类处理。
transfer和gameHoler, gameWorld， Player之间，各使用3个线程安全的数据队列m_DataQueue.
m_DataQueue的类型是 FastQueue<ByteBuffer*, Mutex> m_DataQueue; 它的原型是：
<pre><code>
template<class T, class LOCK>
class FastQueue
{
	struct node
	{
		T element;
		node * next;
	};

	node * last;
	node * first;
	LOCK m_lock;
public:

	FastQueue()
	{
		last = 0;
		first = 0;
	}

	~FastQueue()
	{
		Clear();
	}
	void Push(T elem)
	{
	}

	T Pop()
	{
		}
// 一些其他方法， 这里略去

	bool HasItems()
	{
		bool ret;
		m_lock.Acquire();
		ret = (first != 0);
		m_lock.Release();
		return ret;
	}
};
</code></pre>

玩家和server的socket建立后， 放入socketManager: g_SocketsManager->AddServerSocket(this); socket的数据epoll事件通知，下次再看， 先略过。 基本概念就是socket会在收到数据的时候。  


gameHoler, gameWorld, Player在初始化的时候生成各自的m_DataQueue. 登陆的过程大体是这样子：
1. client send LOGIN REQ
2. socket收到，分析是属于LOGIN REQ发给gameHoler->m_DataQueue:  
    
    case LOGIN:
        ((GameHolder*)m_pGameHolder)->m_DataQueue.Push(pck);
3. gameHodler上如何收到这个数据请求并开始处理的呢，gameHoler每秒20帧的速度循环update， 它会在自己的update里检查自己的m_DataQueue队列， 并处理。  
gameHoler按需要为玩家分配gameWorldId, 或新建world， 根据玩家连接上来的sessionid， 从g_SocketsManager获取玩家的socket连接， 设置这个连接的几个相关property:
<pre><code>
GameWorld* tempWD=GetPlayerWorld(sessionId,TableId);

BoostSC->IsLogin=true;
BoostSC->m_Player=pNewPlayer;
BoostSC->m_GameWorld=tempWD;
</code></pre>

4. 之后的请求进入Player类处理，socket会在收到数据REQ时， 判断类型，并判断是否 BoostSC->IsLogin：
<pre><code>
            if (IsLogin)
            {
                pck = new ByteBuffer(sizeof(uint32)*2+asize);
                *pck<< m_handle;
                *pck<< msgId;
                pck ->append((char*)pData,asize);
                if (m_Player!=NULL)
                    ((Player*)m_Player)->m_DataQueue.Push(pck);
                else
                    delete pck;
            }
</code></pre>  


同样的， Player也会在自己的Update里检查m_DataQueue队列， 处理客户端的REQ， 不过Player的这个做法是在自己的叫UpdateData方法里， 这个UpdateDat并不是Player在Update里调用， 而是gameWorld在自己的Update里， 遍历world里的所有玩家， 逐个调用Player的UpdateData:
<pre><code>
        WorldObject *tempObj;
        for (auto itor = m_PlayerNetMap.begin(); itor != m_PlayerNetMap.end(); ++itor)
        {
            Player* p = itor->second;
            if (p)
              p->UpdateData();
        }

// ... 下面是Player的UpdateData方法
void Player::UpdateData()
{

    uint32 sessionId;
    uint32 MsgId;
    uint32 asize;
    char Data[MAX_PACK_LEN];
    ByteBuffer * pbuffer=NULL;
    try
    {
        for (auto i=0;i<10;i++)
        {
            pbuffer=m_DataQueue.Pop();
            if (pbuffer)
            {
                memset(Data,0,sizeof(Data));
                *pbuffer>>sessionId;
                *pbuffer>>MsgId;
                asize=pbuffer->size()-pbuffer->rpos();
                pbuffer->read((uint8 *)Data,asize);
                delete pbuffer;
                OnRecvWorld(sessionId,MsgId,Data);
            }
            else
                return;
        }
    }
</code></pre>
Player将Data从m_DataQueue取出， 进入OnRecvWorld处理流程， 诸如客户端点击玩家走动， 施放技能，拾取物品， 完成任务等REQ。
 

