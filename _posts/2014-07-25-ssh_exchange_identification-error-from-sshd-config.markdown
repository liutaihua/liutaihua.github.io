---
title: ssh_exchange_identification error from sshd config
layout: post
guid: urn:uuid:c5cf8844-e797-49d4-8501-8fc403bfcf16
description: ssh_exchange_identification error from sshd config
tags:
  - ssh
  - ssh_exchange_identification
  - sshd_config
---


项目用fabric做代码更新, 大体流程是利用fabric的接口, 登录到指定服务器上, 干一些事情.  
而实际fabric在执行这个过程的时候,  使用的是ssh协议.  奇怪的问题是, 当在批量操作一些更新的时候, 批量是指可能对单个服务器目标同时有多个fabric的ssh连接操作, 此时会报错ssh_exchange_identification, 已经在一次更新中导致个别项目漏了更新.  
仔细google,  已经看到第2页了, 找到的说法几乎都是把 sshd:ALL加入 /etc/hosts.allow中, 但是明显不是我这个问题的答案.  

思来想去, 可能是和sshd某个并发配置有关?  于是直接查sshd的配置项说明文档.    
终于找到一个配置点:  sshd_config中的MaxStartups, 默认是注释状态, 值是10,  直接改大到100, 取消注释,  重启sshd服务.

问题解决.
