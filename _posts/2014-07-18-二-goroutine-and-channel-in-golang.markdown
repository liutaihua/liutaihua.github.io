---
title: 二 goroutine and channel in golang
layout: post
guid: urn:uuid:10aec03c-0f37-41cb-bff3-ab87f8e67236
description: 二 goroutine and channel in golang
tags:
  - golang
  - goroutine
  - channel
---


上代码:
<pre><code>
package main

import (
	"fmt"
)


func xrange() chan int {
  var ch chan int = make(chan int)
	go func() {
		for i := 2; ; i++ {
			fmt.Printf("xrange about to send %d\n", i)
			ch <- i   //#1
		}
	}()
	return ch
}

func filter(in chan int, number int) chan int {
	out := make(chan int)
	go func() {
		for {
			i := <-in   //#2
			fmt.Printf("filter%d received %d\n", number, i)
			if i%number != 0 {
				out <- i   //#3
			}
		}
	}()
	return out
}

func main() {
	nums := xrange()
	number := <-nums   //#4
	max := 100
	for number <= max {
		fmt.Println(number)
		nums = filter(nums, number)
		number = <-nums    //#5
	}
}
</code></pre>  
也可以直接访问:   http://play.golang.org/p/gB7g_Aq5S8 看代码
上面代码是使用goroutine + chan数据类型, 找出100以内的素数.  

代码包含2个chan数据结构变量 ch和out  
每次调用filter函数, 就会生成一个goroutine,  假设当number=2时调用的filter产生的我们姑且叫它为filter2, 依次就会有filter3 ... filterN  


代码运行之后的过程大概是:  



s1, 生成一个顺序整数序列nums, 类型是channel.  

s2, 读取nums, 被阻塞, 协程跳转到xrange中的生产, 最终第一次读取到整数2, 赋值给number;  

s3, 调用filter方法, 此时number=2;  filter2产生一个goroutine, 由于filter方法的第一个参数就是nums这个信道, 那么在filter2的goroutine里代码执行到  #2位置时, 阻塞, 等待xrange中生产下一个整数:3, 经过计算后, 整数3胜出了, 此时应当是 #5位置的信道读取阻塞, 然后会切换到 #3 等待刚刚胜出的整数3被send进out这个信道;  filter2进入随后继续的循环中, 暂且放下这里的逻辑;   


s4, 当out信道有元素了, #5 位置的读取成功了,  number变量被赋值为3;  3这个素数被找出来了;  同时nums变量所代表的ch这个信道channel,  被filter2中的out信道所重赋值.   

s5, main方法中进入下一个循环,  带着number=3的情况再次调用filter,   产生了一个新的goroutine: filter3,  注意,此时的nums注意,nums已经是filter2中的out了, 有此filter3和filter2被一个信道串起来了, 这个信道究竟是哪个呢, 就是filter2返回的变量out,  由于filter2,  filter3这2个goroutine中涉及到同一个channel信道, 因此对于这个信道的操作会讲filter2, filter3变成串行逻辑;  这里给filter2和filter3之间串起来的信道虚拟一个命名叫做 filter2_pipe_filter3吧;  


s6, 接下来协程应该被执行到了filter3的 #2 位置,  照样进行chan的读取会阻塞, 由于filter2, filter3用同一个信道了, 因此协程跳转到filter2中等待 #3 位置的send,  逻辑重回filter2,  继续开始了之前filter2中未完的循环,  
filter2再次读取一次  <-in  这里的in呢是第一次调用filter时的参数nums,  所以filter2中的 #2 位置中的 <-in操作其实是针对xrange中的ch信道, ch信道生产下一个整数4, 整数4可以被2整除因此它不是一个素数,  filter2继续再次循环, xrange产生整数5, 整数5是素数胜出, 准备写入之前所说的 filter2_pipe_filter3, filter2在 #3 位置阻塞,  协程跳转到filter3中的 #2位置读取, 读到整数5,  整数5对3做计算, 胜出了. 被写入filter3的out信道, 返回给main函数中的调用..    


s7, main中带着number=5的情况, 进入下一个循环,  开启filter5,  而filter5又类似会和filter3返回的out这个信道建立一个串行信道, 我们一样给个虚拟的名字叫做:  filter3_pipe_filter5,  filter5开始 #2 位置 <-in的读取, 被阻塞, 协程回filter3, 3在#2的位置一样会被阻塞, 回filter2,  2的 #2 位置阻塞回 xrange中的#1, xrange产生下一个数字6,  由于6在filter2中被筛选了, 会再次让xrange产生数字7,  7在filter2中胜出, 写入filter2_pipe_filter3, 在filter3中被读到, 再一次在filter3中胜出, 写入filter3_pipe_filter5, 被filter5读到, 最终胜出,  协程返回给main,  main开始带着number=7,  生成filter7,  后续一直循环这个过程...  


end: 最终会生成很多这种 filter(N-1)_pipe_filterN 的串行于2个goroutine之间的桥梁似的信道, X和Y彼此阻塞等待彼此的写入和读取,
filter(N-1)_pipe_filterN  中filterN因为只要一读取就会被阻塞在 #2 位置, 唤醒filter(N-1), filter(N-1)一样在读, 依次 N-2, N-3, N-4 ... 直到xrange产生下一个整数,  这个整数就像一片叶子, 流经这些filter, 被filter拿着它依次除以小于自己的其他数,  只要它在其中任意一个filter点被过滤掉,  那么阻塞会让协程再次进入xrange做再下一次的整数生产...  


整个过程就像一个链表,  链表中单个node的数据结构类似于:  

<pre></code>
type  node struct {
    filter_NO  int
    left  *node(filter_NO-1).right
    right  *node(filter_NO+1).left
}
</code></pre>  

这些node的left和它的上一个节点的right搭在一起形成一个golang的信道, 准确的说上golang的串行信道.  
DONE
