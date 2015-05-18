---
title: cpp swig to run into python
layout: post
guid: urn:uuid:b9164dd7-06cb-40c1-9cb0-deaeb5eddfa3
description: cpp swig to run into python
tags:
  - 
---

## 通过SWIG在Py里调用cpp的方法
## 通过Python.h接口， 在cpp里使用python脚本

经常会做改动的业务逻辑在Py里做， cpp通过SWIG暴露出某些cpp内的对象和方法，给python做调用。 同时cpp内也会有CallNoRT来调用python脚本， 完成类似闭环的调用链。  

SWIG的方法， 网上很多介绍。  

cpp内CallNoRt调用Py的， 大概就是封装Python.h开发的一些接口， 调用时：
{% highlight c++ %}
  ScriptManager::Instance()->CallNoRT("eplObserver.print_recv_data", dynamic_cast<TcpSocket*>(this));
{% endhighlight %}

Instance()的时候， 会先Py_Initialize() 产生一个py虚拟机，之后  PyString_FromString， PyImport_ImportModule 等， 同时自己封装一个 ProcessPythonException 用来处理Py的异常捕获，在ScriptManager.h  构造的时候将Python的sys.stdout和sys.stderr重定向到cpp的std::cout咯: 
{% highlight c++ %}
void PyStdOut(const char* p)
{
    std::cout<<p<<std::endl;
}
{% endhighlight %}  


析构函数里， 回收py虚拟机不要忘记：
{% highlight c++ %}
ScriptManager::~ScriptManager()
{
    Py_Finalize();
}
{% endhighlight %} 

完， 代码在<a href="https://github.com/liutaihua/echoEpollServer/tree/master/Py">我的gitbub</a>
