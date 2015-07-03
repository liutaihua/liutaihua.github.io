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

有二维向量 A(x, y),  B(x, y)
1,  向量的模， 可以看做是向量点在x,y坐标系下的向量长度,  记作 |A| = sqrt(A.x*A.x + A.y*A.y);
2,  向量相减产生一个新的Vector point， A - B = (A.x-B.x, A.y-B.y), 一个新的Vec point;
3,  相减后的new point，计算出模， 可以看做是A 点与 B点的距离差额（暂时理解如此）;
4,  点积， 也就是相乘，A*B = A.x * B.x + A.y * B.y,  点积有个三角函数相关的公式是:  A*B = |A|*|B|*cos(angle) ， 点积如果大于0， 向量间的夹角是一个锐角， =0是垂直的， <0则是钝角，  
另外可以从这个公式推出:  angle = acos(A*B / |A|*|B|)  acos是反余弦；acos返回的是弧度值， 
具体角度为： angle = angle * 180 / M_PI; 

5， diff_AB_point == A - B == (A.x-B.x, A.y-B.y)  
    有 atan2(diff_AB_point) 等于A减B产生的点diff_AB_point 它到x轴的弧度， 
    
    同时相关的还有：  
    The (directed) angle from vector1 to vector2 can be computed as：
    angle = atan2(vector2.y, vector2.x) - atan2(vector1.y, vector1.x);

