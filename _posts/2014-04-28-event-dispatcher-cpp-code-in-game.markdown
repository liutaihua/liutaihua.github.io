---
title: event dispatcher cpp code in game
layout: post
guid: urn:uuid:051180c0-c49f-415c-841b-52284eb8cca2
tags:
  - cpp
  - event dispatcher
  - game code
  - source code
---


这里记录的是现在所在游戏的cpp代码里的, 关于事件调度和触发的源码分析.
EventDispatcher 是一个事件调度者
Event 事件基类
EventReceiver 所有需要接收世界的对象的基类, 它们都对EventReceiver做继承. 并重写RecieveEvent方法.

当GameWorld在初始化的时候, 会为这个World创建一个调度器EventDispatcher的新实例容器m_pEventDispatcher, World有一个GetEventDispatcher可以获取这个世界调度器.  

继续下面的调用桟, 就是EventDispatcher的初始化过程:  
<code>
class EventDispatcher
{
public:
	EventDispatcher(GameWorld* owner);
	virtual ~EventDispatcher();

    bool Init();
    void UnInit();

	bool Create(uint32 frameDelay, uint32 senderId, uint32 recieverId, ulong arg1, ulong arg2);
	bool Create(uint32 frameDelay, EventReceiver* sender, EventReceiver* receiver, ulong arg1, ulong arg2);
    bool Create(uint32 frameDelay, std::function<void()> callback);
    void Update(uint32 frameCount);

	uint32 EventsCount() const;

	// All the WorldObjects in GameWorld will be taken into account,
	// No registration required.
	void Register(EventReceiver* receiver);
	void Unregister(EventReceiver* receiver);

	CnHashMap<uint32, EventReceiver*>& Receivers() { return m_EventReceivers; }
	EventReceiver* GetReceiverById(uint32 id);

	GameWorld* World() const { return m_World; }  
</code>

事件调度器有几个Create方法, 提供给World调用, 以创建新的事件, 创建事件以framedelay为参数表示这个事件延迟多少个游戏侦触发, 在游戏实际配置里, 我们现在是每秒20侦的频率, 所以这个侦除以20就是时间秒.  
事件创建好之后, 存放在调度器的m_EventContainer容器内.
这几个Create重载方法, 会根据调用的不用, 决定使用哪个Event对象来实例化, 比如EventWithCallback的事件类型. 

调度器具有Update方法, 会在主循环里被调用, 每次Update方法都会检查当前侦的count,  如果符合事件的触发条件, 则触发事件, 调用事件接受者的Trigger方法. reveiver就是来自于Create时创建的.

只要有可能被事件触发的对象方法, 这个对象都应该需要继承EventReceiver类, 这样同时自己也就需要重新Trigger方法, 等待事件触发时, 来对应事件处理自己的逻辑.
