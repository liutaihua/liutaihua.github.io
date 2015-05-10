---
title: event dispatcher mod in Game
layout: post
guid: urn:uuid:bcc01dd4-7f30-4af6-88ec-2e06bae8513a
description: event dispatcher mod in Game
tags:
  - game
  - cpp
  - dispatcher mod
---


## 事件调度器模块
记录下我们游戏里事件调度器模块， 用处， 代码结构。  

我们用来注册一些事件到调度器， 调度器在做update的时候， 会检查容器内的事件， 事件的封装， 包含senderObj, receiveObj, id, delayFrameCount等等。  如果当前帧已经符合delayFrameCount的要求了， 就执行receiveObj.RecieveEvent()方法，将senderObj注册事件时的参数等， 带入RecieveEvent方法执行。

主要包含3个类：

1, Event.h    提供事件的封装
2, EventReceiver.h    一个简单的抽象基类，纯虚函数RecieveEvent接口， 它的派生类都要实现它， 用来接收事件。
3, EventDispatcher.h  全局的事件调度器，每个game world都将创建一个eventdispatch， 使用World()->GetDispatcher()获取当前world的eventdispatch。  

EventDispatcher只有几个简单的接口， Create, Register, Update:  
Create 提供给需要创建事件使用， 2个重载函数, 原型如下：  
<pre><code>
  // 创建带args，调度器Update时，将使用这些args，执行事件接受者的ReceiveEvent方法
	bool Create(uint32 frameDelay, EventReceiver* sender, EventReceiver* receiver, ulong arg1, ulong arg2);
	
	// 创建一个callback类型的事件， Update时，将直接执行callback
  bool Create(uint32 frameDelay, std::function<void()> callback);
</code></pre>


Dispatcher的Create会首先使用对象池alloc一个Event对象， 因为Event.h类型是个足够抽象的类型， 我们不需要每次都生成一个重复的Event对象实例， 比如一个事件它有相同的sender， 一样的receiver， 一样的args， 那么就不用重复初始化实例了， 我们使用自己构造的ObjectPool容器来初始化和free一个实例：
<pre><code>
bool EventDispatcher::Create(uint32 frameDelay, uint32 senderId, uint32 receiverId, ulong arg1, ulong arg2)
{
    CnVerify(GetReceiverById(receiverId));

    uint32 targetFrame = m_FrameCount + frameDelay;
    CnVerify(targetFrame > m_FrameCount);

    // 利用m_EventPool对象池， 分配一个Event实例， 然后将event放入调度器容器， 以供接下来的Update迭代器访问事件
    Event* event = m_EventPool.Alloc(this, senderId, receiverId, arg1, arg2);
    m_EventContainer.insert(EventMap::value_type(targetFrame, event));
    return true;
}


void EventDispatcher::Update(uint32 frameCount)
{
    m_FrameCount = frameCount;
    uint32 count = m_EventContainer.count(frameCount);
    auto range = m_EventContainer.equal_range(frameCount);
    auto itor = range.first;

    if(m_FrameEvents.size() < count)
        m_FrameEvents.resize(count);

    //Event* events[count];
    for(uint32 i = 0; i < count; ++i)
    {
        m_FrameEvents[i] = itor->second;
        ++itor;
    }

    // m_EventContainer maybe changed during the loop.
    for(uint32 i = 0; i < count; ++i)
    {
        // 调用Event类的Trigger触发器， 触发事件， 具体receiver的ReceiveEvent方法在Event->Trigger()内被调用
        m_FrameEvents[i]->Trigger(frameCount);
        
        // 使用完Event实例， 将它释放回ObjectPool
        m_EventPool.Free(m_FrameEvents[i]);
    }
    m_EventContainer.erase(frameCount);
}

void Event::Trigger(uint32 frameCount)
{
    if (!GameWorld::CurrentInstance()) return;

    EventReceiver* obj = nullptr;
    (obj = Dispatcher()->Receivers()[m_RecieverId])
    || (obj = GameWorld::CurrentInstance()->GetObjectById(m_RecieverId));
	if (obj != nullptr)
	  // 调用具体的receiverObject 完成事件的接收
		obj->RecieveEvent(frameCount, m_Arg1, m_Arg2);
}
</code></pre>

所有需要接收事件的Object， 比如Creature,  SKillManager等， 都需要继承EventReceiver类，并提供RecieveEvent接口。
技能释放操作就使用到了EventDispatcher, 当客户端向后端发起一个skill cast， 经过业务逻辑后， 并不会立马在当前帧执行具体的Battle计算， 而是SkillManager创建一个Event， 同时接受者也是SKillManager自己， 对某些技能做成delayToNextCast方式， 比如需要读秒的技能， 需要蓄力过程的技能, 他们并不会立马释放技能， 而且一个延迟释放，这时候就用到了这个事件调度器。

技能模块都是独立与生物类的， SkillManager下次再做分析。  


