--
layout: post
Title: "nodejs的机器人hubot集成到gtalk"
Date: 2013-04-26 16:15
comments: true
categories: notes
--




hubot 机器人, 居然今天才去了解了下它, 用nodejs运行, coffee javascrpit写的.  

记录下安装方式  
如果是redhat系列的linux, 使用yum 安装即可, centos6后的nodejs版本已经很新了.
实在不行就搞源码安装.

1, clone代码  
    git clone https://github.com/github/hubot

2, 安装依赖
    cd hubot && npm install

3, 尝试运行  
    ./bin/hubot 
在出现的hubot的console 输入hubot help看看帮助命令吧, 输入pug me命令, 如果正常会返回一个http链接, 打开页面是个可爱的狗狗.

4,  将hubot和gtalk连接  
用./bin/hubot -h可以看到帮助, 其中-a参数表示指定adapter  
git clone git://github.com/atmos/hubot-gtalk.git 获取gtalk的adapter代码, 直接将hubot-gtalk放在hubot的node_modules下, 方便hubot查找库.

关于连接gtalk的文档, 可以查看  https://github.com/github/hubot/wiki/Adapter:-Gtalk  
其实很简单, 设定2个系统环境变量: HUBOT_GTALK_USERNAME, HUBOT_GTALK_PASSWORD
我的做法非常暴力, 我直接编辑 node_modules/hubot-gtalk/src/gtalk.coffee  修改  
    # Client Options
    @options =
      username: 'xxxxx@gmail.com'
      password: 'xxxxxxxxx'

还有一个系统变量需要注意, hubot运行时,比如直接./bin/hubot -a shell默认会监听端口, 而端口值使用的是环境变量PORT, 默认是8080 ,如果被占用, hubot程序启动不了. 所以设定下 export PORT=8989之类的端口.  

前面说道的gtalk这个adapter, 源文件其实就是  node_modules/hubot-gtalk/src/gtalk.coffee, 我在使用过程中发现, 里面有个TextMessage函数在用前没有导入, 会导致运行后, 虽然hubot能连接gtalk, 但是无法响应你的消息,  稍作修改(node_modules/hubot-gtalk/src/gtalk.coffee):  

Adapter       = require '/root/app/hubot/src/adapter'
{TextMessage} = require '/root/app/hubot/src/message'

同时依葫画瓢, 写了一个isAllowUser方法, 用于验证用户, 不能谁都邀请你这个hubot聊天, 然后就向hubot发命令吧, 因为我的hubot里写了一些系统相关的, 怕不安全.
user_list =
  'defage': 'admin'
  'liutaihua2008': 'user'  
  

  isAllowUser: (jid) ->
    name = jid.user
    if user_list[name] == undefined
      return false
    return true

在handlePresence 函数里调用一下, 验证不通过就不进行后面的动作了  
    if not @isAllowUser(jid)
      return



5, 成功连上gtalk之后, 能用了, happy了一会, 可是机器人比较傻, 才懂简单的那么几个示例命令, 下面是自己扩展它的方法:  
在src/scripts/路径下, 是命令脚本, 随便捡一个看一眼, 会发现挺简单, 脚本里有一条注释, 会被用作help命令的输出  

`# Commands:`  
`#   hubot email <user@email.com> -s <subject> -m <message> - Sends email with the <subject> <message> to address <user@email.com>`
就是这行了, 虽然是注释, 不过会被当作hubot help的输出.  

暂时我修改了自带的math.coffee,  计算器么, 原来的居然还跑到google上去来一轮, 然后计算好了返回, 放着现成的eval干吗不用, 危险就危险. 反正我是自己用.  
  
增加了一个cmd.coffee 接收消息里的参数, js我太菜了, 于是就用exec方法, 把命令全部丢给一个写好的process.py, 然后在py里就可以想干吗就干吗了,  需要注意的是, js里读输出读的是stdout, 如果stdout没东西, 使用msg.send sdtout返回消息时, 可能会是空的, 只需要在process.py里稍做注意即可.
下面是这个cmd.coffee脚本内容:
<pre>
</code>
 # Description:
 #   Email from hubot to any address
 #
 # Dependencies:
 #   None
 #
 # Configuration:
 #   None
 #
 # Commands:
 #   hubot email <user@email.com> -s <subject> -m <message> - Sends email with the <subject> <message> to address <user@email.com>
 #
 # Author:
 #   earlonrails
 #
 # Additional Requirements
 #   unix mail client installed on the system

util = require 'util'
child_process = require 'child_process'
exec = child_process.exec

module.exports = (robot) ->
  # email by pmail scripts
  robot.respond /email (.*) -s (.*) -m (.*)/i, (msg) ->
    mailCommand = """python /root/app/hubot/src/scripts/pmail.py -t '#{msg.match[1]}' -s '#{msg.match[2]}' -c '#{msg.match[3]}'"""
    exec mailCommand, (error, stdout, stderr) ->
      msg.send stdout

  # 执行系统命令
  robot.hear /cmd (.*)/i, (msg) ->
    if msg.match[1] == 'top'
      exec 'top -bn 1', (error, stdout, stderr) ->
        msg.send stdout
    exec msg.match[1], (error, stdout, stderr) ->
      msg.send stdout

  robot.hear /defage (.*)/i, (msg) ->
    #term   = "\"#{msg.match[1]}\""
    term = msg.match[1]
    cmd = """python /root/app/hubot/process.py --action '#{term}'"""
    exec cmd, (error, stdout, stderr) ->
      msg.send stdout

</code>
</pre>

robot.hear和robot.respond似乎是一样的, 不过robot.hear看起来更符合机器人聊天.
接下来怎么调教它, 就看你想这么搞了,  以后想到点好玩的, 再给它加上吧. 我的机器人是 robotblabla@gmail.com
