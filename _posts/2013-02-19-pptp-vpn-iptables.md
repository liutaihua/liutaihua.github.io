--
Date: 2013-02-19 11:33 
Title: "pptp做vpn, 连接到内网直接能访问内网IP"
Published: true  
Type: post  
Excerpt: 
--

pptp服务器:

pptp下发下去的ip网段: 10.168.0.0/24 

iptables配置:  (注意打开ip_forward转发):
<pre>
-A FORWARD -s 10.168.0.0/24 -j ACCEPT
-A POSTROUTING -s 10.168.0.0/24 -j MASQUERADE 
</pre>


增加一条路由, 将访问内网172.16.8.0/24的转发到 内网一台已拨pptp到服务器上的一个IP10.168.0.234:    

`route add -net 172.16.8.0/24 gw 10.168.0.234`

在内网这台10.168.0.234的服务器上, 存在另外一个真正的内网网卡IP 172.16.8.213,在这个服务器上启动iptables, 将它当路由器使用来路由网络请求到整个172.16.8.0/24的内网网段:

同样的iptables配置:   (注意打开ip_forward转发)

`-A FORWARD -s 10.168.0.0/24 -j ACCEPT`

`-A POSTROUTING -s 10.168.0.0/24 -j MASQUERADE` 
 

增加一条route:
<pre>
route add -net 10.168.0.0/24  gw 10.168.0.1
</pre>

配置完成, 下面是谁想通过pptp真正连接到内网时, 自己的配置方法:


for linux:

使用pptpsetup程序: 
<pre>
./pptpsetup --create test --server 180.153.136.14 --username test --password defage --encrypt --start
</pre>
然后增加一条路由:

route add -net 172.16.8.0/24 gw 10.168.0.1

若需要访问其他pptp节点, 须增加: route add -net 10.168.0.0/24 gw 10.168.0.1

然后可以直接ping通内网的172.16.8.0/24内任意主机了.





######for mac:

连接VPN后, 打开系统偏好设置==>网络设置 ===> 设定服务顺序, 将VPN拖到最高得位置, 表示网络将优先使用vpn连接.



######for windows:

限制:


由于180.153.136.14服务器的网关 NAT存在针对pptp协议的对点限制,单个出口IP只能有一个client可以连接上180的VPN服务.
