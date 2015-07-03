---
title: a simple traceAI design
layout: post
guid: urn:uuid:eb1e5b61-2b76-42d2-8578-803ea449b485
description: a simple traceAI design
tags:
  - atan
  - cos
  - angle
  - ai
---

##AITrace的基本路数  

先记录几个经常用到和碰到的三角函数和向量点计算时用到的tips:  

<pre>
有二维向量 A(x, y),  B(x, y)
1,  向量的模， 可以看做是向量点在x,y坐标系下的向量长度,  记作 |A| = sqrt(A.x*A.x + A.y*A.y);
2,  向量相减产生一个新的Vector point， A - B = (A.x-B.x, A.y-B.y), 一个新的Vec point;
3,  相减后的new point，计算出模， 可以看做是A 点与 B点的距离差额（暂时理解如此）;
4,  点积， 也就是相乘，A*B = A.x * B.x + A.y * B.y,  点积有个三角函数相关的公式是:  A*B = |A|*|B|*cos(angle) ,
点积如果大于0， 向量间的夹角是一个锐角， =0是垂直的， <0则是钝角， 
另外可以从这个公式推出:  angle = acos(A*B / |A|*|B|)  acos是反余弦；acos返回的是弧度值， 
具体角度为： angle = angle * 180 / M_PI; 

5， diff_AB_point == A - B == (A.x-B.x, A.y-B.y)  
    有 atan2(diff_AB_point) 等于A减B产生的点diff_AB_point 它到x轴的弧度， 
    
    同时相关的还有：  
    The (directed) angle from vector1 to vector2 can be computed as：
    angle = atan2(vector2.y, vector2.x) - atan2(vector1.y, vector1.x);
这里有一个讨论两点夹角相关的： <a href=http://stackoverflow.com/questions/21483999/using-atan2-to-find-angle-between-two-vectors>点击</a>
</pre>

AITrace  

###包含的属性和方法有
* Monster& AIBase::GetMonster() const 返回在使用aitrace的怪物对象
* TraceState， IdleState， PatrolState等几个状态机类型， 直接定义在AITrace的名字空间内；
* void SetTargetId(uint32 targetId); 设定目标；
* bool TryNextStep(CoVec2& candidate, float initialAngle); 尝试前往下一个目的坐标；
* float GetDistanceFromStart() const; 提供给巡逻状态时，现在所在位置到初始位置的距离;
* 每个状态机均有几个来自状态机基类的虚函数，entry，update等;
* bool AITargetedBase::ProgressiveSearch() 搜寻周围是否有可攻击对象;


大概逻辑是：  

gameWorld在update时， 会调用world内的creature包含monster（monster本身是creature的派生）的update方法， monster开始做update， monster会调用所绑定的AI->Update, 这里就是AITrace。 AITrace 初始状态是IdleState, AITrace开始调用GetCurrentState()->Update(frameCount);进入状态机更新， 根据灵敏程度， IdleState将会决定是继续处于idle状态， 还是进入巡逻状态， 如果已有targetId， 那么进入攻击状态， 当然还要先计算自己与目标的距离，期间会调用traceState跟踪， 直到进入可攻击范围内， 开始攻击， 如果目标跑出警戒距离或追赶距离，进入GoBackState状态， 返回初始坐标， 再次进入IdelState。



