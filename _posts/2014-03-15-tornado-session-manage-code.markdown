---
title: tornado-session-manage-code
layout: post
guid: urn:uuid:99f95859-65f2-49ba-b46a-8a654db65b44
tags:
  -tornado
  -session
---


<img src="http://farm8.staticflickr.com/7224/7272947338_1949a8026e_c_d.jpg">交错</img>

tornado session 管理
我们在用到的tornado的session方法, 是一个开源的session代码

首先, tornado.web.RequestHandler有2个方法: 

    set_secure_cookie和get_secure_cookie, 
就是set_cookie的加强版, 
set_secure_cookie会通过create_signed_value方法为给定的cookie值和key做加密算法, 加密会结合tornado settings给定的cookie_secret设置来的, 因此tornado.web.Application在初始化的时候, cookie_secret是一定需要的哦.

而session.py要做的就是如何将通过get_secure_cookie取到的安全session value, 通过封装更方便的提供给RequestHandler来使用, 这里这个开源的session.py封装成字典的方式了, session使用时就像使用字典一样方便:

    In your RequestHandler (probably in __init__),
        self.session = session.TornadoSession(self.application.session_manager, self)


    After that, you can use it like this (in get(), post(), etc):
        self.session['blah'] = 1234
        self.save()
        blah = self.session['blah']

接下来是看这个session.py的代码, 具体实现方法:
代码不多, 包括TornadoSessionManager,  TornadoSession两个类, 代码来自于github.
首先在初始化你的Application的时候, 需要指定一下:

    application.session_manager = session.TornadoSessionManager(settings["session_secret"], settings["session_dir"])
也就是常见的这样的代码(这个代码实在是太常见了, 只要是个tornado的应用都应该知道这个):

    class Application(tornado.web.Application):
        def __init__(self):
            settings = dict(cookie_secret="y+iqu2psQRyVqvC0UQDB+iDnfI5g3E5Yivpm62TDmUU=",
                  session_secret='ttesttt',
                  session_dir='sessions',
             )
            tornado.web.Application.__init__(self, handlers, **settings)
            application.session_manager = session.TornadoSessionManager(settings["session_secret"], settings["session_dir"])



    def main(port):
        tornado.options.parse_command_line()
        print "start on port %s..." % port
        http_server = tornado.httpserver.HTTPServer(Application(), xheaders=True)
        http_server.listen(port, address='0.0.0.0')
        tornado.autoreload.start()
        tornado.ioloop.IOLoop.instance().start()
来看session.py里TornadoSessionManager具体的逻辑:  
TornadoSessionManager继承于SessionManager, 它提供2个方法: get和set, 
作用是根据RequestHandler对象, 获取和更新secure_cookie:

    def get(self, requestHandler=None):
        if requestHandler == None:
            return super(TornadoSessionManager, self).get()
        else:
            session_id = requestHandler.get_secure_cookie("session_id")
            hmac_digest = requestHandler.get_secure_cookie("hmac_digest")
            return super(TornadoSessionManager, self).get(session_id, hmac_digest)


    def set(self, requestHandler, session):
        requestHandler.set_secure_cookie("session_id", session.session_id)
        requestHandler.set_secure_cookie("hmac_digest", session.hmac_digest)
        return super(TornadoSessionManager, self).set(session)
它的父类SessionManager的几个方法, 目的是为了当这个requesthandler是第一次产生session时, 产生一个新的对应这个session_id的hmac_digest,  并存储,  
然后返回这个存储, 这个存储的具体逻辑可以自己定义, 比如可以使用序列化后的文件存储在本地的session_dir目录, 也可以使用memcache,  
直接将这个新的session_id和它的hmac_digest存储在一个字典内,然后set进memcache,  我们使用的是后者.  

另外SessionManager还会做一个hmac_digest的校验, 当requestHandler不是None的时候, 当然是通过tornado的get_secure_cookie去取session_id:

    session_id = requestHandler.get_secure_cookie("session_id")
    hmac_digest = requestHandler.get_secure_cookie("hmac_digest")
然后通过取到的session_id和hmac_digest,  通过session_id从存储内取出服务器上次算出的正确的hmac_digest和这里的hmac_digest做比对, 来达到session验证效果.


上面初始化TornadoSessionManager完成, 然后是在RequestHandler里使用它了:

    class  MainHandler(tornado.web.RequestHandler):
         def __init__(self, *argc, **argkw):
              super(BaseHandler, self).__init__(*argc, **argkw)
              self.session = session.TornadoSession(self.application.session_manager, self)
这里重写了tornado.web.RequestHandler的__init__方法.

后面的逻辑是, 初始化一个session.TornadoSession实例,  2个参数分别一个是之前初始化后的session.TornadoSessionManager对象, 和RequestHandler自己本身(self对象)
我们来看TornadoSession类, 它继承了一个叫Session的父类, 这个父类非常简单, 只是个继承于字典类型的类:

    class Session(dict):
        def __init__(self, session_id, hmac_digest):
            self.session_id = session_id
            self.hmac_digest = hmac_digest
来看TornadoSession类里的逻辑, 它通过tornado_session_manager和request_handler初始化, 而后的逻辑是:

    class TornadoSession(Session):
        def __init__(self, tornado_session_manager, request_handler):
            self.session_manager = tornado_session_manager
            self.request_handler = request_handler
            try:
                plain_session = tornado_session_manager.get(request_handler)
            except InvalidSessionException:
                plain_session = tornado_session_manager.get()
    
    
            for i, j in plain_session.iteritems():
                self[i] = j
            self.session_id = plain_session.session_id
            self.hmac_digest = plain_session.hmac_digest
    
    
        def save(self):
            self.session_manager.set(self.request_handler, self)

首先tornado_session_manager也就是之前初始化的TornadoSessionManager, get本request_handler的session存储,  
如果此request_handler里能通过get_secure_cookie取到'session_id', 则会做验证, 验证通过后, 返回这个request_handler的session数据,  
在之前我们用的是存储在memcache里的字典结构;  如果是一个新的session_id则会经过TornadoSessionManager之前的逻辑产生新的hmac_digest, 同时会被(当然需要你执行save session操作时):

    requestHandler.set_secure_cookie("session_id", session.session_id)
    requestHandler.set_secure_cookie("hmac_digest", session.hmac_digest)
以提供给下一次应用请求数据时做session校验.
save方法, 用来更新浏览器的session_id和对应的hmac_digest,  当然,同时也会更新服务器本地存储里的数据.

到此tornado的session就完成了.

