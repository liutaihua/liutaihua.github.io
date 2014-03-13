--
layout: post
Title: "为hubot机器人脚本增加python扩展"
Date: 2013-04-27 13:33
comments: true
categories: notes
--


为hubot机器人脚本增加python扩展

昨天顺利把hubot跑起来了, 能回答了. 也通过nodejs的exec命令执行shell的方式, 将消息以参数的形式传给process.py处理, 以形成用py写脚本的形式.  
不过上面方式有缺陷:  
1, nodejs不是真正的调用py, 同时py执行的返回或直接print或写stdout(print在某种程度上就是stdout), 然后nodejs什么都不用干, 就直接相当于把stdout使用msg.send回复给gtalk了.  
2, 整体结构不优美, nojs跟py还得靠exec执行shell的形式, 这种调用方式挺丑陋.  

在github上找到一个脚本, 也是为了用python来写hubot的脚本, 实现方式也是用stdout和stdin结合, 达到nodejs收到gtalk消息后, 将消息传给py处理. 拿来后, 又做了一些修改, 具体过程是:  

*** 封装一个Python 类, 接收stdin, 输出stdout.  
* 在nodejs里启动这个py类的listen监听stdin, robot收到消息时write到stdin,   
* py从stdin中读到消息, 交给指定的handler  
* handler处理完成后, 输出stdout, 同时触发nodejs的event, 读取stdout通过robot发送回馈信息.  **


pyscript.coffee脚本如下: 
<pre>
class PythonScript

    pyScriptPath = __dirname + '/test.py'
    python_script = require('child_process').spawn('python', [pyScriptPath])
    python_script.stdout.on 'data', (data) =>
        receive_from_python(data.toString())

    module.exports = (robot) ->
        @robot = robot
        #robot.respond /(.*)/i, (msg) ->
        #    newRegex = new RegExp("^[@]?#{robot.name}[:,]? ?(.*)", 'i')
        #    match = newRegex.exec msg.message.text
        #    send_to_python(match[1], msg.message.room, 'respond')
        #    @robot.msg = msg

        robot.hear /(.*)/i, (msg) ->
            send_to_python(msg.message.text, msg.message.room, 'hear')
            @robot.msg = msg

    send_to_python = (message, room, method) ->
        dict =
            type : method,
            message : message,
            room : room
        python_script.stdin.write(JSON.stringify(dict) + '\n')
        console.log JSON.stringify(dict)

    receive_from_python = (json) ->
        data = JSON.parse(json)
        #@robot.messageRoom data.room, data.message # 恶心的问题, data.room在send_to_python调用传的参数msg.message.room是undefined, 导致这里不能这样用
        @robot.msg.send data.message   # 于是在入口的地方直接把msg对象赋给@robot里的, 在这里就能夸函数调用msg.send了.

</pre>



PythonScript类封装如下: hubot_script.py  

<pre>
handlers = [
    (r'/hubot/sys/(.*)', syscmdhandler),
    (r'/hubot/chat/(.*)', chathandler),
]

class HubotScript:
    def __init__(self):
        self.start_listening()

    # 创建一个listen, 监听标准输入, 有输入时执行后面逻辑
    def start_listening(self):
        while True:
            line = sys.stdin.readline()
            self.receive(line)

    def receive(self, json_str):
        # 这里一定需要捕获错误, 否则出错会直接跳出 start_listening中的循环, 监听就结束了
        try:
            json_dict = json.loads(json_str)
            json_dict['message'] = '/' + '/'.join(json_dict['message'].split(' ')) # 搞成类似url的形式, 方便handlers里的regex匹配
            self.dispatch(json_dict)
        except Exception, e:
            print e

    def send(self, message):
        if message:
            #print json.dumps(message)
            sys.stdout.write(json.dumps(message) + '\n')
            sys.stdout.flush()

    # Message Dispatch
    def dispatch(self, json_dict):
        #msg_type = json_dict['type']
        #if msg_type == 'hear':
        #    self.dispatch_generic(json_dict, _hear_handlers)
        #elif msg_type == 'respond':
        #    self.dispatch_generic(json_dict, _resp_handlers)
        self.dispatch_generic(json_dict, handlers)
        
    def dispatch_generic(self, message, regexes):
        for regex, handler in regexes:
            p = re.match(regex, message['message'])
            if p:
                action = ' '.join(p.groups()[0].split('/'))
                response = message
                #response_text = handler(self, message)
                response_text = handler(self, action)
                if response_text:
                    if len(response_text) > 3000: # nodejs的JSON.parse不能处理太长的str
                        response_text = response_text[:3000]
                    response['message'] = response_text
                    self.send(response)
def hear(regex): # 测试用decorator
    def decorator(handler):
        handlers.append((regex, handler))
    return decorator
</pre>



附带一个测试程序, test.py:  
<pre>
\#coding=utf8
from hubot_script import *

class TestScript(HubotScript):

    @hear('def')
    def test_handler(self, message):
        return 'hear'

    #@respond('abc')
    #def test_handlera(self, message):
    #    return 'respond'

if __name__ == '__main__':
    test = TestScript()
</pre>

**
至此**
**我已经将hubot, gtalk, python集成到一起了, 我的hubot的fork在  
https://github.com/liutaihua/hubot.git
运行方式:  
clone之后, 首先进入hubot:  
`cd hubot && npm install ` 
  
然后得在进入node_modules/hubot-gtalk/为hubot-gtalk这个adapter安装依赖:  
`cd node_modules/hubot-gtalk/ && npm install ` 

最后运行  
`./bin/hubot -a gtalk  `

**完.**

