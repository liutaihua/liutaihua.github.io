--
Date: 2013-03-07 15:11
Title: "perf  sched  收集和分析调度相关数据"
Published: true  
Type: post  
Excerpt:   
--



1,通常用到 perf sched  record  收集系统相关的调度数据, 然后使用pert ached   latency  --sort max 来打印出收集到的信息,perf sched  latency  --sort  max 展现的数据中各个column的含义如下:

*  Task: 进程的名字和 pid 
*  Runtime: 实际运行时间
*  Switches: 进程切换的次数
*  Average delay: 平均的调度延迟
*  Maximum delay: 最大延迟

其中最值得关注的是Maxinum delay的数据


2, perf sched reply ,  它试图重放pert.data文件中锁记录的调度场景, pert.data文件是由上面的pert ached record等收集命令产生,  如果是使用pert  record产生的pert.data文件, 那么使用pert  ached reply并无法分析出有用的数据.
下面是一次per  ached reply的结果:

<pre>\#perf sched reply 
run measurement overhead: 173 nsecs
sleep measurement overhead: 53289 nsecs
the run test took 999980 nsecs
the sleep test took 1123326 nsecs
nr_run_events:        33692
nr_sleep_events:      33910
nr_wakeup_events:     16719
target-less wakeups:  40
multi-target wakeups: 30
task      0 (             swapper:         0), nr_events: 38449
task      1 (            qemu-kvm:     21706), nr_events: 479
task      2 (            qemu-kvm:     21705), nr_events: 416
task      3 (            qemu-kvm:     17648), nr_events: 2464
task      4 (            qemu-kvm:     17640), nr_events: 2268
task      5 (         ksoftirqd/0:         4), nr_events: 70
task      6 (            qemu-kvm:     17645), nr_events: 2255
task      7 (            qemu-kvm:     17646), nr_events: 2050
task      8 (            qemu-kvm:     18320), nr_events: 1143
task      9 (            qemu-kvm:     18318), nr_events: 1420
task     10 (            qemu-kvm:     17647), nr_events: 2092
</pre>


其中task 0   swapper占了很大比例的event,  说明我的系统中在进行较大的交换分区使用.








