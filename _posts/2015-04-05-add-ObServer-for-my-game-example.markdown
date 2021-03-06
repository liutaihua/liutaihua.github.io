---
title: add ObServer for my game example
layout: post
guid: urn:uuid:9dc7bcc9-6ec4-4f2e-8908-7df7d43fcca1
description: add ObServer for my game example
tags:
  -c++
  -observer
  -game 
---


游戏里有很多事件， 可能会随玩家， 或场景内某个物品或某个生物体的状态， 来触发这些事件。比如那种跟随主人走动的宠物，可以认为随主人的状态变更为STATE_MOVE来触发宠物的某个事件， 比如跟随主人，宠物类和宠物的AI类， 以及人物类， 均是独立的， 我们需要一个观察器来连接他们之间的关联：  

{{% highlight c++ %}}
```c++
class CreatureObserver
{
public:
    CreatureObserver();
    ~CreatureObserver(){}
    void Observe(Creature *obj);
    fd::delegate<void(Creature*)> SigCreatureMoved; 
private:
    void ObserveCreature(Creature* pCreature);

    void OnCreatureMove(Creature* pCreature);
};
```
{{% endhighlight %}}


这个简化版的observer， 包含2个方法，被观察者注册上来的实现， 大体是这样：
{{% highlight c++ %}}
```c++
Creature::Creature(enum ObjectType objType) :  //生物基类的构造函数
    m_pCreatureObserver(CnNew CreatureObserver)
{
    m_pStateMachine = new StateMachine(this);
    m_pCreatureObserver->Observe(this);
    m_pCreatureObserver->SigCreatureMoved.add(boost::bind(&Creature::OnCreatureMoved, this, _1));
}
```
{{% endhighlight %}}
boost库的bind， 我将它看做是在Python里类似偏函数的一个函数再封装过程。 它被注册到观察器的SigCreatureMoved, 当SigCreatureMoved被调用时， 会触发回调Creature::OnCreatureMoved方法。
m_pCreatureObserver->Observe(this);它调用的实现如下， 意思是会让creatureobserver反向往creature类的SigMoved注册一个回调OnCreatureMove， 在OnCreatureMove会显示运行creatureobserver自己的SigCreatureMoved, 从而将creature和creatureobserver关联起来， 而其他类，如Pet， 如果想通过Observer来依照creature状态，触发事件， 则注册到指定的creatureObserver上， 比如这里是SigCreatureMoved. 
{{% highlight c++ %}}
```c++
void CreatureObserver::Observe(Creature* obj)
{
    ObserveCreature(obj);
}
void CreatureObserver::ObserveCreature(Creature* pCreature)
{
    pCreature->SigMoved.add(boost::bind(&CreatureObserver::OnCreatureMove, this, pCreature));
}

void CreatureObserver::OnCreatureMove(Creature* pCreature)
{
    std::cout<<"CreatureObserver::OnCreatureMove"<<"\n";
    SigCreatureMoved(pCreature);
}
```
{{% endhighlight %}}

{{% highlight c++ %}}
```c++
class Creature
{
    public:
        // ... 省略部分
        fd::delegate<void()> SigMoved;
        // ... 省略部分
{{% endhighlight %}}
```


整个过程还不是很丰满，我会把PetAI是如果根据Pet obj和Player Obj的状态变化，来实现自己的基本AI逻辑一起讲清楚。暂时先到这里了。
