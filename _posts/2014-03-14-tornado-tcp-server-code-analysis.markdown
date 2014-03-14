---
title: tornado-tcp-server-code-analysis
layout: post
guid: urn:uuid:990542dd-6179-4466-9e77-2e9890db311d
tags:
  - 
---


<img src="http://farm8.staticflickr.com/7358/12579444664_c9a86273f1_z_d.jpg">three girls</img>

tornado tcp server流程

tornado除去外层httpserver的封装后, 底下都是教给tcpserver, 因此才可以很容易将http协议的tornado app改造成兼容tcp协议的app.
tcpserver的使用doc:

    server = TCPServer()
    server.listen(8888)
    IOLoop.instance().start()

初始化一个TCPServer实例,  在调用listen的时候:

    def listen(self, port, address=""):
        sockets = bind_sockets(port, address=address)
        self.add_sockets(sockets)


    def add_sockets(self, sockets):
        if self.io_loop is None:
            self.io_loop = IOLoop.current()
        for sock in sockets:
            self._sockets[sock.fileno()] = sock
            add_accept_handler(sock, self._handle_connection,
                               io_loop=self.io_loop)
listen时使用创建bind_sockets一个socket,  bind_sockets主要做一些sock的初始化, 比如sock.setblocking,backlog,ipv4, ipv6等, 返回一个包含socket对象的列表;
socket的列表sockets,  作为参数给add_sockets,  add_sockets会初始化一个当前的ioloop,  最后会将这些socket, 添加到add_accept_handler内,  add_accept_handler函数是增加一个ioloop的事件监听器,它有一个callback参数, 用于处理监听到sock有新连接时, 重要是调用add_accept_handler时, callback参数传的是tcpserver的self._handle_connection,
add_accept_handler会在自己函数内部定义一个闭包函数accept_handler, accept_handler接收fd, events,  这个函数会挂死循环用来connection, address = sock.accept(), 得到connection, address作为callback调用的参数, 

    def add_accept_handler(sock, callback, io_loop=None):
        if io_loop is None:
            io_loop = IOLoop.current()
    
    
        def accept_handler(fd, events):
            while True:
                try:
                    connection, address = sock.accept()
                except socket.error as e:
                    if e.args[0] in (errno.EWOULDBLOCK, errno.EAGAIN):
                        return
                    raise
                callback(connection, address)
        io_loop.add_handler(sock.fileno(), accept_handler, IOLoop.READ)  # 在当前ioloop中注册一个给定事件的监听处理, 当触发时, accept_handler就会被回调,  一路回溯就会回调callback函数,  也就是tcpserver的self._handle_connection函数.
代码中的描述是:

        """Registers the given handler to receive the given events for fd.
        The ``events`` argument is a bitwise or of the constants
        ``IOLoop.READ``, ``IOLoop.WRITE``, and ``IOLoop.ERROR``.
        When an event occurs, ``handler(fd, events)`` will be run.
        """

回到最终被调用的_handle_connection函数, 它属于tcpserver, 记得之前的:

            server = TCPServer()
            server.listen(8888)
            IOLoop.instance().start()
这里在IOLoop.instance().start()之前应该, 有一句 server.handle_stream = app 的, 这个app就是我们应用自己想接收到socket传过来的数据后, 要做的业务逻辑了. 不过我们定义的app函数, 应该要有2个参数, 分别是(stream, address), 是用来提供给后来的iostream的,  这里我们的app例子是:
def app(stream, address):
    callback = functools.partial(process, stream)
    stream.read_until('\n', callback)

回到tcpserver, 在通过handle_stream=app之后, tcpserver的handle_stream已经被函数app替换了, 字面意思就能看出是为了handl  后面的stream流的一个方法, 因此那个app函数才一样需要stream, address这2个参数.
前面说的_handle_connection函数是ioloop检测到对应事件后, 最终的回调函数, 那么_handle_connection具体干了什么呢, 看下面:

    def _handle_connection(self, connection, address):
        if self.ssl_options is not None:
            assert ssl, "Python 2.6+ and OpenSSL required for SSL"
            try:
                connection = ssl_wrap_socket(connection,
                                             self.ssl_options,
                                             server_side=True,
                                             do_handshake_on_connect=False)
            except ssl.SSLError as err:
                if err.args[0] == ssl.SSL_ERROR_EOF:
                    return connection.close()
                else:
                    raise
            except socket.error as err:
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
            app_log.error("Error in connection callback", exc_info=True)
首先会检测是否有使用ssl协议加密, 否的话, 我们就跳过前面那一段代码了. 
后面的代码是初始化一个IOStream的实例,  将调用_handle_connection时给的connnection, 和tcpserver的当前ioloop对象作为参数, 初始化IOStream, 然后将这个stream回传给hand_stream也就是我们的app函数处理,
IOStream提供一个非阻塞的socket read方法,  我们经常会使用到它的read_until, 就像前面我们的app函数是:

    def app(stream, address):
        callback = functools.partial(process, stream)
        stream.read_until('\n', callback)

之后的事情, 都是属于业务逻辑process的了. 框架部分已经基本完成,  需要注意的是process业务逻辑也需要接收stream作为一个参数, 因为业务逻辑完成后, 需要使用stream.write方法来将结果发送给客户端.  
