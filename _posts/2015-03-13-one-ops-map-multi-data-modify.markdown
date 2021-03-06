---
title: one ops map multi data modify
layout: post
guid: urn:uuid:a158ed15-464c-4862-93a9-b53b881ea5a2
description: one ops map multi data modify
tags:
  - programing
  - python
  - class
---

  项目的socket短连接服务， 采用的是MVC模式， 玩家的某个功能对应的就是一个Model， 每个Model之间数据是独立的, 当然这些Model是继承于一个父类.  
  对数据的操作都是在实现的Model里进行,  对数据的保存操作(save)我们都建议是在Controller里进行的,  这么做的好处是显而易见的, 玩家各个功能之间数据安全性得以保证, 同时也保证在某个功能产生bug的时候,  各数据之间互相不污染. 
比如一个连接进来了, 可能会涉及多项Model的数据更改和保存. 在Controller里,  可能会有多行对应各功能Model的  obj.save()操作:  

{{% highlight c++ %}}
a = A()
b = B()
a.save()
b.save()
{{% endhighlight %}}
产生的问题是:  
1,  因为最近对所有save方法, 启用了cas检测(我们obj.save()是将数据写入一个类memcache的NoSQL数据库里).  如果Model B的数据save被cas拦截, 会导致一个问题是:  A Model保存成功了, 但是B失败了, 就算B失败的时候做了raise,  这个请求的一致性也已经被破坏了.  
  放到实际的业务场景中,  可能Model A消耗某个资源, 让玩家得到Model B中某个资源, 这样的不一致性问题会导致玩家消耗了某个资源, 但是却没有得到利益, 反过来也可能产生应该扣除某个资源, 但是没有扣成功(因为数据save失败), 而出现可获利的漏洞被利用.
2,  就算save方法不启用pylibmc的cas检测,  依然理上可能存在此类问题.  
问题原因是我们的单个请求处理后的数据保存操作, 并不是原子的, 当然这个问题,  如果代码狗一起约定好一个规则:  
针对问题2, 比如如果a操作是消费, 就先执行a.save()在a.save()成功的基础上, 才进行b.save() 但这个方法也仅仅是在pylibmc的cas检测关闭时的基础上. 但是让代码书写顺序来保证逻辑正确性, 真的大丈夫?  

问题1暂时还没想到好的解决方法,  最好的方式应该是让数据保存操作原子化.

问题发生的几率目前预测应该还很小, 单个短连接是能保证不重复操作一个Model的初始化的, 但是不能保证外部其他程序在这个时间也在调用这个Model, 比如我们有用到ZMQ做消息队列, 不过这个消息队列里的消息也是玩家在场景内产生的, 实际情况比较不容易碰到时间上非常一致的消息和短连接操作, 所以同时调用Model的可能性就也很小了.    
而且这种可能性, 是随短连接请求处理性能变快, 而几率越小的.    
但摩尔定律, 可能会发生的事情, 是一定会发生的. 
