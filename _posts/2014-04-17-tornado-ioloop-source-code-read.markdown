---
title: tornado ioloop source code read
layout: post
guid: urn:uuid:e37fc1a8-3fe8-407a-8a00-fed282eea034
tags:
  - tornado
  - ioloop
  - source code
---

重新翻看看ioloop的源码， 以前只读到ioloop是tornado所有网络服务的基础，比如tcpserver, iostream都是将自己对应的callback通过ioloop挂载在对应的epoll事件上，
以达到非阻塞的效果。
这里总结下ioloop类的构建过程。  
ioloop它有一个基类: Configurable定义在util.py文件内，这个Configurable类重定义了__new__工厂函数, 据源码里的描述是为了形成一个使用__new__函数来作为构造函数基类,
看这个__new__方法代码

    def __new__(cls, **kwargs):
        base = cls.configurable_base()
        args = {}
        if cls is base:
            impl = cls.configured_class()
            if base.__impl_kwargs:
                args.update(base.__impl_kwargs)
        else:
            impl = cls
        args.update(kwargs)
        instance = super(Configurable, cls).__new__(impl)
        # initialize vs __init__ chosen for compatiblity with AsyncHTTPClient
        # singleton magic.  If we get rid of that we can switch to __init__
        # here too.
        instance.initialize(**args)
        return instance
这段代码会在Configurable或它的子类也就是IOLoop在实例化的时候, 被执行, 它获取当前实例:impl,  
将这个impl连同在实例化时传给__init__的参数, 一起作为参数args传给实例的initialize方法来做IOLoop的初始化.  
这个过程里重要的2个方法是, configurable_base和 configured_class, 还有configurable_default,  
ioloop重写了父类的 configurable_base方法, 它直接返回IOLoop类自己本身:
    @classmethod
    def configurable_base(cls):
        return IOLoop
再看上面的__new__里, 对当前类cls与这个返回比较, 如果是同一个对象, 也就是说如果当前对象是IOLoop,  则执行configured_class:
    @classmethod
    def configured_class(cls):
        """Returns the currently configured class."""
        base = cls.configurable_base()
        if cls.__impl_class is None:
            base.__impl_class = cls.configurable_default()
        return base.__impl_class
这里会判断静态变量__impl_class是否已被赋值, 如果None, 则执行configurable_default方法,  
获得最终需要的对象实例, 绕了这么久这里才是关键, 因为这个configurable_default方法里,  
根据平台不同,会选择epoll, kqueue, select 其中的1个作为事件触发.
    @classmethod
    def configurable_default(cls):
        if hasattr(select, "epoll"):
            from tornado.platform.epoll import EPollIOLoop
            return EPollIOLoop
        if hasattr(select, "kqueue"):
            # Python 2.6+ on BSD or Mac
            from tornado.platform.kqueue import KQueueIOLoop
            return KQueueIOLoop
        from tornado.platform.select import SelectIOLoop
        return SelectIOLoop
这里的对epoll, kqueue, select的选择过程, 返回的EPollIOLoop其实也是IOLoop的子类,  代码在platform/epoll.py里:  

    from tornado.ioloop import PollIOLoop
    class EPollIOLoop(PollIOLoop):
        def initialize(self, **kwargs):
            super(EPollIOLoop, self).initialize(impl=select.epoll(), **kwargs)
这里可以看出, EPollIOLoop继承于PollIOLoop,  PollIOLoop是IOLoop的子类, 源码就是ioloop.py里,  
可以看到IOLoop类本身基本只是根据不同的平台, 最终在访问IOLoop.instance变量的时候,  
返回不同平台下的不同的IOLoop子类, 比如linux下IOLoop.instance其实就是PollIOLoop的epool实例,  
PollIOLoop类的初始化函数initialize需要一个impl参数, 而这个参数就是子类EPollIOLoop传进来的select.epoll()实例:  
    super(EPollIOLoop, self).initialize(impl=select.epoll(), **kwargs)
到此就完成了IOLoop的平台选择....

