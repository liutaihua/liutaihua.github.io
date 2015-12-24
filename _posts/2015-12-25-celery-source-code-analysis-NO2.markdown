---
title: celery source code analysis NO2
layout: post
guid: urn:uuid:33f83e71-6cc7-4b89-97aa-f7608e4a3306
description: celery source code analysis NO2
tags:
  - celery
  - amqp
---


# celery 初始化过程

consumer初始过程：

这些步骤都是celery/bootsteps.py中 StartStopStep的子类，Gossip例外， 它是ConsumerStep的子类；

他们被封装在Blueprint (蓝图？)中，

```python
    class Blueprint(bootsteps.Blueprint):
        name = 'Consumer'
        default_steps = [
            'celery.worker.consumer:Connection',
            'celery.worker.consumer:Mingle',
            'celery.worker.consumer:Events',
            'celery.worker.consumer:Gossip',
            'celery.worker.consumer:Heart',
            'celery.worker.consumer:Control',
            'celery.worker.consumer:Tasks',
            'celery.worker.consumer:Evloop',
            'celery.worker.consumer:Agent',
        ]
```

在Consumer的\_\_init\_\_中会对Blueprint初始化：

```python
        self.blueprint = self.Blueprint(
            app=self.app, on_close=self.on_close,
        )
        self.blueprint.apply(self, **dict(worker_options or {}, **kwargs))
  # apply调用会对blueprint里的steps这个set中的module，做类似module_import，将set内的字符串表示的module作import
  
  #...
  
  # 然后用parent, 也就是传给apply调用的 self, self也就是Consumer对象，对每个setp module生成对象实例，之后都存中blueprint对象的self.steps字典中，字典key是module字符名字
  
        order = self.order = []
        steps = self.steps = self.claim_steps()

        self._debug('Building graph...')
        for S in self._finalize_steps(steps):
            step = S(parent, **kwargs)
            steps[step.name] = step
            order.append(step)
        self._debug('New boot order: {%s}',
                    ', '.join(s.alias for s in self.order))
        for step in order:
            step.include(parent)
```

到这里完成了各个step对象实例化。



Consumer的start方法， 应该是提供给它的上层调用者， 调用开始一个Consumer的， 在start方法中，会调用blueprint的 start， blueprint的start会将封装在自己的self.steps中的step， 全部执行 step.start(parent), parent就是Consumer的对象实例：

```python
    # Consumer的start 开始
    def start(self):
        blueprint = self.blueprint
        while blueprint.state != CLOSE:
            self.restart_count += 1
            maybe_shutdown()
            try:
                blueprint.start(self)   # 启动blueprint 开始逐个step的初始化
            except self.connection_errors as exc:
              # ....
              # 省略
              
    # Blueprint的start          
    def start(self, parent):
        self.state = RUN
        if self.on_start:
            self.on_start()
        for i, step in enumerate(s for s in parent.steps if s is not None):
            self._debug('Starting %s', step.alias)
            self.started = i + 1
            step.start(parent)
            debug('^-- substep ok')          
```

接下来就是最上述的那些 step 对象的初始化了，他们全部都定义在 worker/consumer.py文件中， 先看Connect， 因为step.start实际就是调用每个step对象的start方法：

```python
    # Connection的start
    # 可以看出， 之所以叫 step， 确实是名副其实， 其实就是将Consumer的初始化过程，封装成一个一个，串行的步骤，第一步是Connection
    # 这里的c， 就是start传来的parent, 那么它其实就是 Consumer对象本身
    def start(self, c):
        c.connection = c.connect()
    # 那么这里调用了Consumer的connect方法， 连接amqp，以及一些和连接相关的逻辑
    
    
    # Mingle step是进行 searching neighbors，来发现其他节点, 如果发现了node， 会和对方同步一下revoked数据
    
    # Event step会初始化事件调度器，代码里面经过一顿绕来绕去的， 它其实定义在 events/__init__.py里的 EventDispatcher
    # 这里是Event step的start方法：
    def start(self, c):
        # flush events sent while connection was down.
        prev = self._close(c)
        # 使用Consumer的connect返回的conn， 和本节点hostname初始化 Dispatcher对象, 这样Consumer.event_dispatcher完成初始化
        dis = c.event_dispatcher = c.app.events.Dispatcher(
            c.connect(), hostname=c.hostname,
            enabled=self.send_events, groups=self.groups,
        )
        if prev:
            dis.extend_buffer(prev)
            dis.flush()
            
    # Gossip step 初始化amqp Channel，通过自己的get_consumer初始化kombu.Consumer(amqp协议的consumer)
    # self.Receiver其实是 events/__init__.py内的 EventReceiver类， 那么就是初始化这个事件接收者类， routing_key这里是直接写死的
    # EventReceiver这里用做的是consumer节点之间的消息事件调度，
    # 它通过订阅routing_key是 ‘worker.#’这个topic类型的exchange type，来订阅调度消息
    # 初始化的amqp协议的consumer最终，存储在Gossip的self.consumers中
    # 在初始化kombu.Consumer的地方， 设置了mq消息的回调方法，就是 Gossip的on_message
    # 发现Gossip居然做的是election之类的事，好神奇，还没看到celery有什么election方面的功能，表示没明白是干吗的， 以后再吧
    def get_consumers(self, channel):
        self.register_timer()
        ev = self.Receiver(channel, routing_key='worker.#')
        return [kombu.Consumer(
            channel,
            queues=[ev.queue],
            on_message=partial(self.on_message, ev.event_from_message),
            no_ack=True
        )]
        
        
    # Heart step 是初始化一个heartbeat, 用于node节点之间的心跳检查
    def start(self, c):
        c.heart = heartbeat.Heart(
            c.timer, c.event_dispatcher, self.heartbeat_interval,
        )
        c.heart.start()
        
    
    # Control 用于 CELERY_ENABLE_REMOTE_CONTROL 方面的
    
    # Tasks step 是初始化 amqp的consumer， 是TaskConsumer, 最终这个amqp的consumer存储在 Consumer.task_consumer中
        c.task_consumer = c.app.amqp.TaskConsumer(
            c.connection, on_decode_error=c.on_decode_error,
        )
        
    # Evloop step 初始化事件循环器，这是consumer事件循环的关键:
    # 这里最终会运行的loop 是 self.loop = loops.asynloop if hub else loops.synloop
    # 也就是异步方式还是同步方式， 基于celery使用的方式而不同， 比如用 eventlet 或是 fork 模式
    def loop_args(self):
        return (self, self.connection, self.task_consumer,
                self.blueprint, self.hub, self.qos, self.amqheartbeat,
                self.app.clock, self.amqheartbeat_rate)    # loop调用的时候用这些args
    def start(self, c):
        self.patch_all(c)
        c.loop(*c.loop_args())

    def patch_all(self, c):
        c.qos._mutex = DummyLock()  
    
    # loop最终是定义在 worker/loop.py中
    # loop函数最终使用的是kombu模块的async/hub.py中的Hub对象，来完成异步的事件模型， Hup对象是在上层中初始化的
    # Consumer的self.hub，是由上层调用初始化的，其实就是上层的WorkController类， 后面来说这个
    # 它会回调具体的callback
        
```

至此Consumer的初始化完成了， 值得一提的是， Consumer的 create\_task\_handler 方法是创建app/task.py中Task的地方，

这个Task也就是我们在使用celery的时候， 用继承也好， 用装饰器也好，生成的具体的业务task了， 

我们可以为每个task设置不同strategy策略

```python
# 这是Consumer的 绑定task name和 strategy 函数的地方
# WorkController会调用这个update_strategies方法
# Consumer的self.strategies属性中， 会存储字典， 它是task name和 strategy的对应
    def update_strategies(self):
    loader = self.app.loader
        for name, task in items(self.app.tasks):
            self.strategies[name] = task.start_strategy(self.app, self)    # 这里最终返回的是strategy函数里的闭包函数: task_message_handler
            task.__trace__ = build_tracer(name, task, loader, self.hostname,
                                      app=self.app)
                                      
    # 在create_task_handler方法中， 会用到self.strategies， 根据amqp过来的body里的task字段获取到task name， 然后招到strategy调用
    def create_task_handler(self):
        strategies = self.strategies
        on_unknown_message = self.on_unknown_message
        on_unknown_task = self.on_unknown_task
        on_invalid_task = self.on_invalid_task
        callbacks = self.on_task_message

        # on_task_received会通过loops.py中对应的loop函数，和Hup的事件循环， 注册在Consumer.task_consumer的callbacks中
        def on_task_received(body, message):          
            try:
                name = body['task']
            except (KeyError, TypeError):
                return on_unknown_message(body, message)

            try:
                strategies[name](message, body,
                                 message.ack_log_error,
                                 message.reject_log_error,
                                 callbacks)
            except KeyError as exc:
                on_unknown_task(body, message, exc)
            except InvalidTaskError as exc:
                on_invalid_task(body, message, exc)

        return on_task_received           

```

这样对worker/job.py中的Request的初始化前， 可以做一些事情了, 而且可以为每个任务定义不同的策略, 策略函数task\_message\_handler是on\_task\_received触发后第一个调用的方法：

```python
    # 这里是承接上面代码中的 strategies[name](....) 调用
    def task_message_handler(message, body, ack, reject, callbacks,
                             to_timestamp=to_timestamp):
        req = Req(body, on_ack=ack, on_reject=reject,
                  app=app, hostname=hostname,
                  eventer=eventer, task=task,
                  connection_errors=connection_errors,
                  message=message)
        # ...省略
    # 需要注意的是此处的Request的实例req， 和app/task.py的Task对象的request属性， 并不是一个东西，不要混淆    
        
    # 这里的Req是worker/job.py中的Request对象， 或者也可以自己利用Request对象继承后，做一些重载形成自己的Request类，在这里使用 
    # 另外， 业务的Task的在Request的 self.task = task or self.app.tasks[name]中
    # Request中的execute_using_pool方法会最终调用self.tasks， 当然看方法名就知道它并不是直接调用， 是一个池
    # execute_using_pool方法是在 WorkController 中被调用的：
    
    # worker/__init__.py中的WorkController的方法至于谁触发的 _process_task，需要再往上层跟才知道了
    def _process_task(self, req):
        """Process task by sending it to the pool of workers."""
        try:
            req.execute_using_pool(self.pool)
        except TaskRevokedError:
            try:
                self._quick_release()   # Issue 877
            except AttributeError:
                pass
        except Exception as exc:
            logger.critical('Internal error: %r\n%s',
                            exc, traceback.format_exc(), exc_info=True)    
```





WorkController 的初始化， 采用的方式是和Consumer一样的， 通过Blueprint来逐个步骤的执行 

    它会完成：

    这些组件的初始化， 其中就是Hub和amqp的Queue，还有对上面分析的Consumer调用

```python
default_steps = set([
    'celery.worker.components:Hub',
    'celery.worker.components:Queues',
    'celery.worker.components:Pool',
    'celery.worker.components:Beat',
    'celery.worker.components:Timer',
    'celery.worker.components:StateDB',
    'celery.worker.components:Consumer',
    'celery.worker.autoscale:WorkerComponent',
    'celery.worker.autoreload:WorkerComponent',

])
```

下次再跟进去看这个。

完！

