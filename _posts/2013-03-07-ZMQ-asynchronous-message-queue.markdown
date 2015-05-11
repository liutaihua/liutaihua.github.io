---
title: "zmq 异步消息队列"
layout: post
guid: urn:uuid:4b736217-ab1f-11e3-9803-040ccecf359c
tags:
    - move from old blog
---
####zmq  push--pull 方式

**在ZMQ中是淡化服务端和客户端的概念的**:

* 相对的服务端:
* 创建一个SUBer订阅者bind一个端口, 用来接收数据
* 创建一个zmq.PUSH
* 创建一个zmq poller轮询对象,
* 将sub注册到poller, 并赋予zmq.POLLIN意味轮询进来的msg
* 创建sock=poller.poll()开始轮询
* 当有msg发送到suber订阅者的监听端口后, sock.recv()方法将会收到msg,
* 最后使用之前创建的pusher, 使用pusher.send(msg)将消息推送到连接到的puller, 如果无puller, 此msg将被丢弃


**相对的client**:

* 创建zmq.PULL 连接到服务端接收push过来的消息

**消息创建者**:

* 创建一个zmq.PUB对象, 意味着此对象为一个消息发布者: pub = context.socket(zmq.PUB)
* 连接到服务端的suber的监听端口: pub.connect('tcp://%s:%s' % (sub_host, sub_port))
* 最后将需要发送的msg, 使用pub.send(msg)发送给suber订阅者


**代码示例:**

对于服务端:
<pre>
<code>
import zmq
context = zmq.Context()



"""定义一个订阅者, 注意的是,这里的订阅者是从服务端来看, 
这个method是订阅者(从这个角度来说服务端也能看成是客户端了), 
对应的client创建一个发布者(PUB)时, 使用connect连接的就是此服务端的订阅者."""
def create_subscriber(port):
    sub = context.socket(zmq.SUB)
    sub.bind('tcp://*:%s' % port)
    sub.setsockopt(zmq.SUBSCRIBE, '')
    return sub

"""此模式在服务端暂时没用用到"""
def create_publisher(port):
    pub = context.socket(zmq.PUB)
    pub.bind('tcp://*:%s' % port)
    pub.setsockopt(zmq.HWM, 0)
    return pub


"""定义个推送者, 如果有client连上此pusher, 当有新消息时,
client的pull.recv()将会获得msg"""
def create_pusher(port):
    pusher = context.socket(zmq.PUSH)
    pusher.bind('tcp://*:%s' % port)
    return pusher
    
    
def main():
    """初始化函数方法"""
    sub = create_subscriber(args.sub_port)
    pub = create_publisher(args.pub_port)
    pusher = create_pusher(args.push_port)

""" 创建一个Poller初始化， 将sub(订阅者)注册到此Poller, 并使用POLLIN参数, 
在后面的poller.pull()方法中, 将能pull到最新的,从client程序发到sub来的消息,
最后使用pub和pusher将消息send出去"""
    poller = zmq.Poller()
    poller.register(sub, zmq.POLLIN)

    while True:
        socks = poller.poll()  \# 创建socks
        for k, v in socks:
           """ 获取消息,此消息实际是由client程序的pub发送到此server的sub,
           然后经由poller.register, 被poller.poll()实例经由recv方法获取"""
            message = k.recv()   
            
            pub.send(message)
            # FIXME: Use gevent instead.
            try:
                \# 使用pusher将msg推送给client程序的puller.recv, 
                pusher.send(message.split(' ', 1)[-1], zmq.NOBLOCK)
            except:
                pass
</code>
</pre>

**客户端:**
<pre>
<code>
import zmq
context = zmq.Context()



"""创建一个发布者, 发布者连接到server程序的订阅者, 产生msg后send, 
其他语言比如cpp, 也是一样连
接的是上面server程序的sub, 发送mq"""
def pub():
    pub = context.socket(zmq.PUB)
    pub.connect('tcp://%s:%s' % (sub_host, sub_port))
    while True:
        msg = 'abc hello' + str(time.time())
        pub.send(msg)
        print 'sending', msg
        time.sleep(1)


\# 暂时没有用到, 此仅作示例
def sub():
    sub = context.socket(zmq.SUB)
    sub.setsockopt(zmq.SUBSCRIBE, '')
    sub.connect('tcp://%s:%s' % (pub_host, pub_port))

    while True:
        msg = sub.recv()
        print 'Got:', msg


"""创建一个puller, 连接的是server程序中的pusher, server端pusher有新msg时, 会push到此puller"""
def pull():
    pull = context.socket(zmq.PULL)
    pull.connect('tcp://%s:%s' % (pusher_host, pusher_port))

    """一个死循环, 不断pull新msg, 接收到msg后根据msg再进行相关业务逻辑,
    一般msg采用json格式, 能非常方便处理不能语言程序之间, 不同进程之间的通信."""
    while True:
        msg = pull.recv()
        print 'Got: ', msg
</code>
</pre>
