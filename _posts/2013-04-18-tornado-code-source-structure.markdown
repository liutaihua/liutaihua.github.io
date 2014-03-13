--
layout: post
Title: "tornado源码查看-代码结构和请求流向"
Date: 2013-04-25 13:43
comments: true
categories: notes
--




源码里的结构:
<pre>
<code>
tornado
├── auth.py
├── autoreload.py
├── ca-certificates.crt
├── curl_httpclient.py
├── database.py
├── escape.py
├── gen.py
├── httpclient.py
├── httpserver.py
├── httputil.py
├── __init__.py
├── ioloop.py
├── iostream.py
├── locale.py
├── netutil.py
├── options.py
├── platform
│   ├── auto.py
│   ├── common.py
│   ├── __init__.py
│   ├── interface.py
│   ├── posix.py
│   ├── twisted.py
│   ├── windows.py
├── process.py
├── simple_httpclient.py
├── stack_context.py
├── template.py
│   ├── csv_translations
│   │   └── fr_FR.csv
│   ├── gettext_translations
│   │   └── fr_FR
│   │       └── LC_MESSAGES
│   ├── __init__.py
│   ├── README
│   ├── static
│   │   └── robots.txt
│   ├── templates
│   │   └── utf8.html
├── util.py
├── web.py
├── web.py~
├── websocket.py
├── wsgi.py
</code>
</pre>

花了一些时间,准备看tornado的源码, 下午只看了部分http相关的, 结构理出来, google了部分资料, 然后自己理了理思维, 发现自己理解基本是对的, 在http://ispe54.blogspot.com/2013/04/tornado-1.html这篇文章理解下更加清晰了. 

由简单的hello world程序开始, 看进去源码:

class MainHandler(tornado.web.RequestHandler):
    def get(self):
         return self.finish('hello world')
     
<pre>
<code>
\#初始化一个application类的实例
class Application(tornado.web.Application):
    def __init__(self):
        handlers.append((r'/', MainHandler))
        tornado.web.Application.__init__(self, handlers, **config.web_config.settings)
        self.session_manager = common.session.TornadoSessionManager(config.web_config.settings["session_secret"],
            config.web_config.settings["session_dir"])
        self.db = common.util.get_user_db()
        ….
       
def main():
    http_server = tornado.httpserver.HTTPServer(Application(), xheaders=True)
    http_server.listen(8888)
    tornado.ioloop.IOLoop.instance().start() 

</pre>
</code>

1, 先说Application类, 它和RequestHandler同时位于tornado.web模块内,  它总共没多少代码, 
    Application主要是初始化一些option.settings的参数,  将实例代码中的handlers加入到self.handlers中, 最后重写了__call__函数, 在后面将Application实例传给HTTPServer作为callback,  HTTPServer内会有一系列的方法, 将会调用callback(), 实际就会运行这个__call__:





2, tornado.httpserver.HTTPServer 类只是提供一个基础httpserver的方法, httpserver.py和netutil.py 内的TCPServer,这两个文件主要是实现http协议，解析header 和 body， 生成request，回调给appliaction,  在httpserver.py内有一个HTTPConnection, 实现http协议的连接部分. 对于底层的socket, io缓冲等, 是由TCPServer中, 将ioloop, iostream关联在一起实现的.

源码里说HTTPServer类只是个简单的http协议实现:
    A server is defined by a request callback that takes an HTTPRequest
    instance as an argument and writes a valid HTTP response with
    `HTTPRequest.write`. `HTTPRequest.finish` finishes the request (but does
    not necessarily close the connection in the case of HTTP/1.1 keep-alive
    requests). A simple example server that echoes back the URI you
    requested::

        def handle_request(request):
           message = "You requested %s\n" % request.uri
           request.write("HTTP/1.1 200 OK\r\nContent-Length: %d\r\n\r\n%s" % (
                         len(message), message))
           request.finish()

        http_server = httpserver.HTTPServer(handle_request)



HTTPServer是tornado.netutil.TCPServer的子类,  HTTPServer在构造函数__init_里增加了一些属性, 然后重写了TCPServer的handle_stream:
    def handle_stream(self, stream, address):
        HTTPConnection(stream, address, self.request_callback,
                       self.no_keep_alive, self.xheaders)


handle_stream 这个方法, 会在TCPServer里被_handle_connection方法调用:
    def handle_stream(self, stream, address):
        """Override to handle a new `IOStream` from an incoming connection."""
        raise NotImplementedError()

    def _handle_connection(self, connection, address):
        if self.ssl_options is not None:
            assert ssl, "Python 2.6+ and OpenSSL required for SSL"
            try:
                connection = ssl.wrap_socket(connection,
                                             server_side=True,
                                             do_handshake_on_connect=False,
                                             **self.ssl_options)
            except ssl.SSLError, err:
                if err.args[0] == ssl.SSL_ERROR_EOF:
                    return connection.close()
                else:
                    raise
            except socket.error, err:
                if err.args[0] == errno.ECONNABORTED:
                    return connection.close()
                else:
                    raise
        try:
            if self.ssl_options is not None:
                stream = SSLIOStream(connection, io_loop=self.io_loop)
            else:
                stream = IOStream(connection, io_loop=self.io_loop)
            self.handle_stream(stream, address)
        except Exception:
            logging.error("Error in connection callback", exc_info=True)

而_handle_connection会被add_socket调用, 回到最上层, 其实是hello world程序中的http_server.listen(port) 这句, 发起listen, listen方法内会调用add_socket,  而handle_stream中实现的是调用HTTPConnection来处理一系列http协议中的connection部分. 在HTTPConnection中会处理callback,  这个callback就是Application类的__call__,   最后request数据会传给最终的逻辑处理类web.RequestHandler.

说起来特别费劲, 做了个思维导图(可能需要翻墙):

<img src="http://lh5.ggpht.com/0817hoIHa1WnDSGF0wCk1UuKwEtwl1Iy5P7GfIjkwVX8B76_ZbRcgZAp4VSXq86hPnIPFcYPs3WntKGsN_qt=s1600" >

