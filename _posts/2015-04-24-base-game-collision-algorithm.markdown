---
title: base game collision algorithm
layout: post
guid: urn:uuid:0f07fcad-904d-4764-87ef-c5e1c197c4c6
description: base game collision algorithm
tags:
  - game collision
  - vector
---

##游戏服务端碰撞检测 

最近看了一些游戏碰撞检测相关的一些内容，然后开始读了一些我们游戏里关于碰撞检测的代码，我们游戏里现在的碰撞检测按我暂时阅读完的代码， 应该分为2块，相对来说我们基本的碰撞检测算法是比较简单的， 后面也记录一下网上看到的关于分离轴多边形的碰撞检测。

一个是生物与scene世界的碰撞物品， 比如房子墙壁，地图围栏， 地图边界区域，用的是2D坐标的点到线段的距离， 结合点的owner本身的半径， 计算是否在碰撞范围内了。
伪代码
{{% highlight c++ %}}
struct Line {Vec start, end;};
typedef Line Segment;

struct Vec {int x, y;};

Vec a = {x, y};
Vec p1 = {x, y}
Vec p2 = {x, y}
Line line = {p1, p2}

//计算点到线段的距离
//点到线段的最短距离，有时候是点到线段的垂直距离， 有时候却是点到线段某个端口的距离
<img src="static/img/p2.png"></img>
// 网上盗个图来看看
double distance(Vec& p, Segment& s){

    //建立向量的点积， 来判断点是在2个端口的哪一端点区
    Vec v = s.start - s.end;
    Vec startTothisPos = p - s.start;
    Vec endTothisPos = p - s.end;

    //两个向量的点积<0则， 向量形成锐角， 反之则是钝角（>90度）, ＝0则是垂直关系
    if (Vec2Dot(v, startTothisPos) < 0) {return Length(startTothisPos);}
    if (Vec2Dot(v, endTothisPos) > 0) {return Length(endTOthisPos);}
    
    //计算点到线的垂直距离
    //点到线的距离 等于 向量点与线形成的夹角， 夹角形成的平行四边形的面积 除以 线的向量长度 
    return fabs(Vec2Cross(v, startToThisPos)) / Length(startTothisPos);
}

//向量的Length， 是平方根计算  sqrt(x*x + y*y)
double Length(Vec& a) {
    return sqrt(a.x*a.x + a.y*a.y);
    //也可以用点积的平方根表示  return sqrt(Vec2Dot(a, a));
}

//向量的点积：
double Vec2Dot(Vec& a, Vec& b) {
    return (a.x*b.x + a.y*b.y);
}

bool IsColliSion(Vec& a, Segment& s){
    double dx = distance(a, s);
    return dx < GetOwnRadius(a);
}

bool IsCollSionWithObj(Vec& a, Vec& b) {
    //点和点的碰撞， 计算点到点的距离， 再与各自半径比较可以得出
    centerOffset = Length(a - b);
    if (centerOffset - GetOwnerRadius(a) - GetOwnerRadius(b) < 0)
        return true;
    return false;
}

{{% endhighlight %}}

另外一个是生物与生物之间， 做的是检测二维坐标里点与点的距离， 再结合2点所属的owner的Radius， 计算两个点之间是否已经进入碰撞范围。调用 IsCollSionWithObj(a, b)计算。

分离轴的碰撞， 下次再来表。 

