---
title: single Threading of epoll server
layout: post
guid: urn:uuid:e6bbfe97-9d1b-4a54-bdbb-281feda89d48
description: single Threading of epoll server
tags:
  - cpp
  - epoll event
  - game
  - network framework
---

## 一个单线程的epoll server示例
这个示例是一个echo server， 将回显client端send的64字节.

## epoll的几个基本小知识：
1, event struct结构：  
struct epoll_event {
    uint32_t     events;      /* Epoll events */
    epoll_data_t data;        /* User data variable */
};  

