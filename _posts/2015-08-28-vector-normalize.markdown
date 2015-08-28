---
title: vector normalize
layout: post
guid: urn:uuid:c7e48395-eff9-4958-b1bb-4cc7233ba010
description: vector normalize
tags:
  - computer graphics 
  - vector normalize
  - vector point
---

## 向量的归一化

###从起始点A到目标点B的路径上的碰撞检测
常见的一个应用场景：游戏技能里有玩家冲一个地方闪现到另外一个指定点，中间不能有阻挡物， 否则就停在阻挡物那里。  


在几何空间中， A每次移动一个单位长度dir，逐步靠近B，就是A每次增加一个unit vector  
归一化：即将一个向量， 使它的模（length）等于1，并且方向不变， normalize后的向量dir， 就是一个单位向量了  
用做在空间中，向量往前增加一个单位长度, 即 += dir

A, B是两个向量点，实现步骤是：
{{% highlight c++ %}}
1， 计算A到B的距离， 就是向量运算中 C = A - B,  distance = C.length() 也就是C的模。
2， 计算新产生的向量C的单位向量，也就是向量归一化，得到单位向量dir ＝ normalized(C)  
    def nromalized(vec):
        length = vec.length()
        vec.x = vec.x / length
        vec.y = vec.y / length
        return vec
3,  取A点往前增加2个半径长度的点pos， 作为初始点:
    pos = A + dir*(A.radius() + B.radius())
    
4,  以A到B的距离的一半作为最大循环次数：
    loop_count = (A-B).length()
    
5,  以pos点作为圆心，A的半径作为圆半径的圆内， 检测圆内是否有碰撞，如果有碰撞则跳出循环， 每个循环后给pos增加一个单位向量(也就是normalized后得到的dir):
    while loop_count >= 0:
        if CollisionWorld.TestCircle(pos, A.radius()):
            break
        pos += dir
6, 假如中间有碰撞， 则pos为最终发生了碰撞的某个点.
{{% endhighlight %}}

得恶补一下线性代数了，参照文档
<a href="http://www.zhihu.com/question/19951858">zhihu</a>
<a href="http://www.fundza.com/vectors/normalize/">vector normalizing</a>
