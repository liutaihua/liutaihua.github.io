---
title: some-note-of-cpp-gameserver
layout: post
guid: urn:uuid:0a6e4503-47d4-4d55-9a44-ecb462036f01
tags:
  - cpp
  - c++
  - game
---


<img src="http://farm4.staticflickr.com/3779/13106561643_5590c06280_c_d.jpg">I just want a drink</img>  

c++通过swig暴露自己的API提供给python调用,  在我们的例子中生成的swig文件是

    data/cnscript/gamelogic.py
    
比如player的SetAttr, GetAttr等接口, 在这里均暴露出, 已提供给python脚本使用.

同时在c++里还有使用Python.h开发, 使用PyObject来调用python的方法, 比如游戏rule里的on_player_entered_map等方法, 在c++里某些逻辑触发时, 会调用这些py方法.

c++里构建一个观察器Observers, 估计是负责监视事件的发生. 当事件发生时(这个不确定, Observers还是EventDispatcher类负责事件), 比如:  

    PyObserver::OnObjectAddedToWorldPostNotify  则会调用某些触发函数,  
但是函数逻辑是写在python脚本里的, 所以在这里触发时, 通过PyObject Call. 当然实际源码里这中间经过一个ScriptManager的类进行的, 但最后都是在使用:  

    <code>
    PyObject *pFunc = _GetPythonFunc(name);
    return _CallPythonObj(pFunc, pTupleArgs);
    </code>
至此c++和py之间的互调逻辑完成.

游戏场景的World:

    Configuration/EnvHolder.cpp   源码里有一个BuildWorldNew的类, 在某个场景进程启动时, 初始化GameWorld时, 会初始化调用  BuildWorldNew,而BuildWorldNew里通过  
    ScriptManager::Instance() -> CallNoRT调用data/cnscript/rule/utils.py里的dress_world_up,  
dress_world_up里会根据启动进程的参数, 为场景加入指定的Ruler类, 比如SingleJJC类.

进程在启动时, GameWorld进行一系列初始化, 包括注册新的事件调度器EventDispatcher,SkillManager,HttpProxy, CreatureObserver， 以及加载WorldObject对象.
GameWorld构建完成之后, 等待用户进入, GameWorld有一系列诸如OnPlayerLogin, login之后进行GameWorld::AddPlayerOrSendLoginFailedAck， 创建玩家数据, 加载玩家各类数据比如宠物, 坐骑, 技能等等.

WorldObject类都是关于场景里物品对象, 碰撞检测, 初始化物品管理器GameItemManager，

Creature生物类, 是包括Player类, Monster类的父类.

EventDispatcher事件调度器

    包含一个EventReceiver事件接收者, Create方法接收一个callback作为回调创建一个事件
    Register方法接收一个receiver作为参数, 把事件接受者加入接受者列表, 
    EventDispatcher也有一个Update方法, 会遍历所有事件, 如果delay时间对了, 则根据receiver回调给于的callback.

GameHolder是游戏外层主循环类, 一个while True进入循环, 每秒20个frame的方式, 对GameHoler自身, GameWorld, WorldObject对象, 进行Update调用, 以更新数据, 触发事件等.  

<pre>
<code>
Configuration/ObjectWebFactory.cpp文件里， ObjectWebFactory类主要进行的是具体是加载玩家数据的逻辑:
    void LoadCharmOf(Player*, const ptree &) const;                             // 获取符文
    void LoadEquipmentsOf(Player*, const ptree &) const;                        // 获取角色装备
    void LoadBagOf(Player*, const ptree &) const;                               // 获取角色背包
    void LoadSkillsOf(Player*, const ptree &) const;                            // 获取角色技能
    void LoadPassiveSkillsOf(Player*, const ptree &) const;
</code>
</pre>

在 void PlayerCreation方法完成后,  方法: PlayerSavingThread会为此场景里的每个玩家创建一个线程,这个线程会用来作为接下来游戏过程中的数据回存或新数据重载.
ObjectWebFactory类里的LoadSkillsOf等方法, 实际是调用Player里的Loadxxx方法:  

    <code>
    void ObjectWebFactory::LoadTechOf(Player* pPlayer, const ptree& ptTech) const
    {
        CnAssert(g_IAmMainThread);
        CnAssert(pPlayer);
        pPlayer->LoadTech(ptTech); ＃这里
    }
    </code>

在Player.cpp里存在方法LoadSkills, 这个方法会根据现有场景World里的 WorldObjectFactory类，通过tcp或者http从hades系统那边获取具体的json格式数据:  

    <code>
    bool Player::LoadTech()
    {
        ptree ptTech;
        bool ok = World()->GetObjectFactory().GetJson("technology/get_tech_attr?userid=" + Crown::ToString(GetUserId()), ptTech);  ＃这里是从hades获取数据
        if (!ok) return false;
        LoadTech(ptTech); #这里是LoadTech的另外一个充载方法， 它会对获取到的数据进行整合,把数值加到Player上.
        return true;
    }
    </code>

GetJson这个方法, 应该是继承或来自于Configuration/ObjectWebFactory.cpp里,  在这里有对GetJson方法进行http改tcp的代码, 而http方式正式游戏以前用的, 后来改成了socket去连接hades了.


暂时到这里.
