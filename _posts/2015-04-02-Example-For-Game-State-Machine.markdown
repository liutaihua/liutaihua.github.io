---
title: Example For Game State Machine
layout: post
guid: urn:uuid:dcc0281a-3386-45e8-b31c-94635eb609bf
description: Example For Game State Machine
tags:
  - cpp
  - statemachine
  - object coding
---

游戏的cpp coding中面向对象的部分， 可能最基础的要算是状态机了， 对于一个游戏世界几乎所有物品都能看做是一个对象的实例.生物或玩家都的动作会改变自身的某些状态属性， 同时有些动作又需要玩家处于某个状态下才能进行。有限状态机是一个最基本的实现，玩家或生物等其他需求具有状态的物体都应该拥有一个自己的状态机实例。  
状态机里的状态， 应该是可以互相转换的， 或者说整个状态系统， 是一个闭环。   

一个状态机管理类， 数个状态类， 所有状态类都派生于一个状态基类， 状态机管理类会在实例化的时候初始化一系列的状态类，玩家产生状态变化， 应该使用状态机来记录， 而不是在Player类里面自己记录状态变量，比如死亡：
<pre><code>
Player->Die(); invoke: pStateMachine->Die(); invoke: currentState->Die();  invoke: pPlayer->doDead()
</code></pre>
可以看到，Player自己产生Die， 从状态机绕一圈， 才最终执行自身的doDead。 这过程中，状态机内， 可以根据状态变化，产生某些逻辑， 更清楚的描绘了整个过程， 易于扩展。 比如施法状态， 比如行走状态；  

从代码来大概看看结构和过程：

1, 初始化Player的时候， 初始化一个属于Player的状态机
<pre><code>
Player::Player(int id, std::string name):
    user_id_(id),
    user_name_(name)
{
    move_distance_ = 0;
    move_speed_ = kSpeed;
    play_time_ = 0;
    //user_state_ = STATE_READY;
    hp_ = kMaxHp;
    m_pStateMachine = new StateMachine(this);
}
</code></pre>


<pre><code>
StateMachine::StateMachine(Player* pCreature) :
    m_pOwner(pCreature),
    m_ReadyState(this),
    m_IdleState(this),
    m_MoveState(this),
    m_CastingState(this),
    m_DeadState(this)
{

    m_AllStateMap[STATE_READY]		= &m_ReadyState;
    m_AllStateMap[STATE_IDLE]		= &m_IdleState;
    m_AllStateMap[STATE_MOVE]		= &m_MoveState;
    m_AllStateMap[STATE_CASTING]	= &m_CastingState;
    m_AllStateMap[STATE_DEAD]		= &m_DeadState;

	m_pCurrentState = m_AllStateMap[STATE_READY];
    m_curStateId = STATE_READY;

}
</code></pre>
2，上面代码， 状态机在初始化的时候， 会引用各个状态对象， 并存在自己的一个数组里， 这里的STATE_READY ...等是一个定义在头文件里的枚举：
<pre><code>
enum StateType
{
    STATE_READY = 0,
    STATE_IDLE,						// 正常状态
    STATE_MOVE,						// 移动
    STATE_CASTING,					// 施法
    STATE_STUN,						// 晕
    STATE_DEAD,						// 死亡
    STATE_MOVE_CASTING,             // 移动施法状态
    STATE_COUNT
};
</code></pre>


3， 各个类都会有一个Update方法， 最先是Player在主函数后按帧执行Update， 调用链是:
<pre><code>
Player->Update()  invoke: pStateMachine->Update() invoke: currentState->Update()
</code></pre>
可以在每个状态类的Update方法里， 实现所在这个状态时， 做的某些逻辑， 比如施法状态， Update的时候， 扣除玩家施法某个法术的读条时间等等。

4， 状态类的基类大概是这样：
<pre><code>
class StateMachine;
class Player;

class IState
{
public:
  IState(int type, StateMachine* pStateMachine);
  virtual ~IState() {}
  virtual void Update( uint64 frameCount ) = 0;
  virtual void OnEnter(int stateId/*lastStateId*/) {}
  virtual void OnLeave(int stateId/*nextStateId*/) {}

  // 行为接口
  virtual void MoveTo(int /*position*/) {}
  //virtual void StopAt(const CoVec2& /*position*/, float /*angle*/) {}
  virtual void Cast() {}
  //virtual void OnCasted() {}
  //virtual void Stun() {}
  virtual void Dead() {}
  virtual void Reborn() {}
  //virtual void MoveCast() {}


  // 行为接口
  //virtual void MoveTo(const CoVec2& /*position*/) {}
  //virtual void StopAt(const CoVec2& /*position*/, float /*angle*/) {}

protected:
  StateMachine* m_pStateMachine;
  Player*   m_pCreature;
</code></pre>


5， 状态类的声明大概是这样：
<pre><code>
class DeadState : public IState
{
public:
    DeadState(StateMachine* pStateMachine);
    virtual ~DeadState();

    virtual void OnEnter(int lastStateId);
    virtual void Update( uint64 /*frameCount*/ ) {}
    virtual void Dead();
    virtual void Reborn();

    uint32 KillerId;
};
</code></pre>
整个示例的代码在  https://github.com/liutaihua/gameStateMachine.git ， 在MAC OS 10.10, clang 6.0 xcode6.0下可直接编译通过， 里面包含一些简单的状态改变。按每秒20帧做循环
