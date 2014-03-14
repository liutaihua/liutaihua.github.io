--
layout: post
Title: "五一随聊"
Date: 2013-05-01 08:19
comments: true
categories: notes
--

<img src='http://ww1.sinaimg.cn/large/793bee10jw1e47srugr8aj20e509sjsi.jpg'>

五一非常无聊的在家呆着, 最近在google资料时, 查到的一些技术blog, 发现好多都在github里, 也就是好多人都把github当作保存技术文章的的管理器, 然后用比如Markdown等语法形式写, 自己弄个简单的程序读出来, 展示就可以变成一个基本的blog站点了.  
我的这个blog也是这个意思, https://github.com/liutaihua/yyu.me.git, 写好的article放在post目录, 一个tornado的web框架, 读出这些article, 加个html围绕就变成现在这个样子了, 不过我还给它增加了在线编辑器, 是一个Markdown语法的在线编辑器, 可以试试预览Markdown语法.   
鉴于我每次发文章虽然是通过在线编辑器发的, 但是实际我写字却是用另外一个Markdown编辑器, 这个在线editor只是copy进去, 然后设定标题.  
想到一个更简洁点的方法, 有时间就把它实现一下, 就是在blog服务上做个api, 接受post, 然后平常在shell里用vim就可以写blog了, 把写好的article保存, 然后POST到这个api即可, 这样也省得再次打开web编辑器了. 
  
图里机器人是github最近开源的hubot, 挺不错. github已经用它来做运维了, 代码发布等. 我想未来这不失为一个运维的好方向, 传统的服务monitor, 告警, 在小型公司基本就是用一个nagios诸如此类的开源套件做告警, 基本就都是在使用邮件发送告警邮件了. 不过邮件实时性稍差, 如果用robot, 不失为一个好方法.  
虽然nodejs语法跟js有所不同, 不过看起来还挺不错的, 可能因为最近刚看完一本<javascript高级程序设计>, js语法基本了解了一下. hubot在用nodejs写的时候, 很多函数调用, 参数都有一个callback, 真是各种callback传来传去, 和以前接触的确实有所区别, 有点意思.