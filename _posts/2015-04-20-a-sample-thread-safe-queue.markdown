---
title: a sample thread safe queue
layout: post
guid: urn:uuid:3d0c6dcb-abee-4bff-84f7-398ac89b98ad
description: a sample thread safe queue
tags:
  - cpp
  - queue
---

## 一个自带锁的简单队列， 用单向链表实现：
<pre></code>
template<class T, class LOCK>
class FastQueue
{
	struct node
	{
		T element;
		node * next;
	};
	node * last;
	node * first;
	LOCK m_lock;
public:
	FastQueue()
	{
		last = 0;
		first = 0;
	}
... // 以下暂省略
</code><pre>  

单向链表的node， 包含指向下一个node的指针next，和数据 element.  
初始化队列头尾都是0， 表示空队列。  

要使用这个简单的队列， 需要自带锁，自带锁的方式粒度当然是需要队列调用者控制。m_lock是自带锁的对象实例。  


包含Pop, Push, front, pop_front, hasItems 我们会使用到的方法：  
<pre></code>
	void Push(T elem)
	{
		m_lock.Acquire();
		node * n = new node; //初始化节点
		if(last)
			last->next = n;
		else
			first = n;  
		last = n;       
		n->next = 0;
		n->element = elem;
		m_lock.Release();
	}

	T Pop()
	{
		m_lock.Acquire();
		if(first == 0)
		{
			m_lock.Release();
			return reinterpret_cast<T>(0);  // 空队列返回动态类型转换后的类型T
		}
        
		T ret = first->element;   // 非空队列， 将element提取到变量ret，
		node * td = first;        // td用来接替first， 以便删除回收Pop后的节点
		first = td->next;         // 队列首个节点，转换为Pop后节点的next指向节点
		if(!first)
			last = 0;         // 队列空了
		delete td;
		m_lock.Release();
		return ret;
	}
	T front()   
	{
		m_lock.Acquire();
		if(first == 0)
		{
			m_lock.Release();
			return reinterpret_cast<T>(0);
		}
		T ret = first->element;
		m_lock.Release();
		return ret;
	}

	void pop_front()       // 删除队列最前方节点
	{
		m_lock.Acquire();
		if(first == 0)
		{
			m_lock.Release();
			return;
		}
		node * td = first;
		first = td->next;
		if(!first)
			last = 0;

		delete td;
		m_lock.Release();
	}

	bool HasItems()      // 队列是否为空
	{
		bool ret;
		m_lock.Acquire();
		ret = (first != 0);
		m_lock.Release();
		return ret;
	}
{{% endhighlight %}}  

一个线程安全的Mutex锁：  
<pre></code>
#include <pthread.h>
class  Mutex
{
public:
	Mutex();
	~Mutex();
    inline void Acquire()   // 获取锁， 这是一个同步阻塞操作
	{
		pthread_mutex_lock(&mutex);
	}


    inline void Release()         // 释放，尝试释放一个未被获取的mutex, 不会导致错误
	{
		pthread_mutex_unlock(&mutex);
	}
{{% endhighlight %}}

  FastQueue<ByteBuffer*, Mutex> m_DataQueue;  

创建一个自带线程安全锁的队列 m_DataQueue, 很简单的队列。

