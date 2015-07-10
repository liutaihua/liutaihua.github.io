---
title: design custom dynamic_cast
layout: post
guid: urn:uuid:6bb2dee7-24b4-4563-a076-7877cda1df2b
description: design custom dynamic_cast
tags:
  - cpp
  - dynamic_cast
  - design mod
---


## 一个自定的dynamic_cast设计 


一个运行时检查的自设计dynamic_cast转换系统：
- 包含2个预编译宏，CnDeclareRootRTTI 和CnDeclareRTTI， 宏的目的只是为了生成对应的代码， 实际手法和直接在类里码代码是一样意思；
- 一个简单的RTTI类型，每个基类和派生类将会自带一个RTTI的实例属性: ms_RTTI, RTTI类如下:
{% highlight c++ %}
class CnRTTI
{
public:
	CnRTTI (const char* pcName, const CnRTTI* pkBaseRTTI);
	inline const char* GetName() const {return m_pcName;}
	inline const CnRTTI* GetBaseRTTI() const {return m_pkBaseRTTI;}

protected:
	const char* m_pcName;
	const CnRTTI* m_pkBaseRTTI;
};
{% endhighlight %}
直接上脑图， 文字真是描述好费劲。

<img src='static/img/RTTI.png'>RTTI</img>
