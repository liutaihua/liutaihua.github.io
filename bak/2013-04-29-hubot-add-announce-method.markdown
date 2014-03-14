--
layout: post
Title: "hubot增加announce方式做广播消息"
Date: 2013-04-29 11:40
comments: true
categories: notes
--

hubot的announce通知所有在线联系人

hubot在使用挂接到其他平台时, 是支持room的方式了, 这样就支持了由一个用户发送announce通知所有在线联系人的方式了.  

因为想到以后或许可以使用hubot来作为监控通知, 当你指定的监控项目告警时, 使用hubot把信息发送到所有在线订阅人.  

  

因为对nodejs的这个coffee基本都还在研究阶段, 所以以下说的不能代表完全没错误, 或是最佳的办法..  



robot对象有个robot.brain.data.users方法, 保存的是当前的在线订阅用户, 利用这个, 可以随意的将某条消息发送给所有人, 这里举例是announce.py脚本:  

<pre>

module.exports = (robot) ->



  if process.env.HUBOT_ANNOUNCE_ROOMS

    allRooms = process.env.HUBOT_ANNOUNCE_ROOMS.split(',')

  else

    allRooms = []



  robot.respond /announce (.*)/i, (msg) ->

    announcement = msg.match[1]

    for own key, user of robot.brain.data.users

      user_info = { user: user } # 总之, 为了后面robot和adapter的send方法调用, 多包一层, 否则send取user会取成undefined

      robot.send user_info, announcement 

</pre>

      

上面使用的robot.send方法发送消息,这个方法定义在src/robot.coffee里:  

<pre>

  send: (user, strings...) -> 

    @adapter.send user, strings…  

</pre>    

    

可以看出它实际是调用你启动hubot时所用的具体的adapter的send方法, 这里我用的gtalk这个adapter, 因此可以找到这个send方法最终定义在:  node_modules/hubot-gtalk/src/gtalk.coffee  

<pre>

  send: (envelope, strings...) ->

    for str in strings

      message = new Xmpp.Element('message',

          from: @client.jid.toString()

          to: envelope.user.id

          type: if envelope.room then 'groupchat' else envelope.user.type

        ).

        c('body').t(str)

      # Send it off

      @client.send message

</pre>      

上面代码中, 使用的是envelope.user.id来获取用户id的, 因此才需要在announce.coffee脚本里, 比较傻帽的在user外在包一层{ user: user }, 否则在这里使用envelope.user.id将无法取到用户id(就是gmail邮箱地址), 导致广播消息失败.  





于这个send方法对应的, 还有rely和messageRoom方法, 他们在robot.coffee里定义时最终都是调用adapter.send来发送消息.  



至于以后用什么client方式发送广播告警, 简单的方法是:    

1, 写一个简单的xmpp协议(gtalk协议)的小sdk脚本, 通过它发送announce消息到hubot, 然后hubot广播给所有人.  
2, robot对象有一个针对http的方法, robot.router.post可以获取通过hubot的http接口post上来的数据, 这样如果要发布announce, 只需要post到这个方法上即可, 代码如下:  
<pre>
  robot.router.post "/broadcast/create", (req, res) ->
    for own key, user of robot.brain.data.users
      user_info = { user: user } 
      robot.send user_info, req.body.message
    res.end "Message Sent"
</pre>  
用`curl -X POST -d "message=opopop" http://hubot-server-ip:9898/broadcast/create` 测试看看吧.
  
完.