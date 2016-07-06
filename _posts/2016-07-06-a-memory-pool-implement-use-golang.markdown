---
title: a memory pool implement use golang
layout: post
guid: urn:uuid:1ba5ffd0-9113-4a3c-9bb6-3b72e54e5042
description: a memory pool implement use golang
tags:
  - memory pool
  - golang
---


# 用golang实现内存池

用golang做一个预分配的内存池，代码可以很小量做到。   实现细节，主要是一个链表，用来保存内存块.  
定义2个值:  
num 每次需要增长内存池的时候，预分配的内存块数量  
size 预分配时，单个内存块的大小  

一共两个类型：  
Pool  内存池对象，管理grow动作， Get， Put等动作  
Buffer 一个链表

初始化时:  

```go
type Pool struct {
	lock sync.Mutex
	free *Buffer
	max  int
	num  int
	size int
}

// 初始化内存池的时候，调用grow做一次内存预分配
func (p *Pool) init(num, size int) {
	p.num = num
	p.size = size
	p.max = num * size
	p.grow()
}


func (p *Pool) grow() {
	var (
		i   int
		b   *Buffer
		bs  []Buffer
		buf []byte
	)
	buf = make([]byte, p.max)  // 创建一个num * size大小的连续内存
	bs = make([]Buffer, p.num) // 创建链表节点
	p.free = &bs[0]
	b = p.free
	for i = 1; i < p.num; i++ {  // 完成链表节点的首尾相连，引用前面的大内存块中的逐个内存块
		b.buf = buf[(i-1)*p.size : i*p.size]
		b.next = &bs[i]
		b = b.next
	}
	b.buf = buf[(i-1)*p.size : i*p.size]
	b.next = nil  // 这是一个单向链表
	return
}

```

链表对象结构是:

```go
type Buffer struct {
	buf  []byte
	next *Buffer // to next node
}
```

然后就是两个对外的接口, Get 和 Put

```go
// 获取一个内存块
func (p *Pool) Get() (b *Buffer) {
	p.lock.Lock()
	if b = p.free; b == nil {
		p.grow()
		b = p.free
	}
	p.free = b.next
	p.lock.Unlock()
	return
}

// 释放一个内存块
func (p *Pool) Put(b *Buffer) {
	p.lock.Lock()
	b.next = p.free
	p.free = b
	p.lock.Unlock()
	return
}
```

size的大小就是内存块的大小， 因此应根据实际使用场景变化， 比如用在tcp socket 的write buffer上的时候， 那么size就是你希望能buff住的write buffer大小。
