--
layout: post
Title: "进程的smaps内存使用分析"
Date: 2013-04-25 16:09
comments: true
categories: notes
--


2.6.16后的内核, 对于查看进程内存使用分布, 更方便了. 在/proc/{pid} 路径下有一个smaps文件, 记录了进程内存使用情况, 在老的内核系统上, 这个文件是maps或memap , 而且老的内核下maps或memap文件记录的数据真不是人读的.  

现在有了高内核, 当然可以用起来了.

smaps文件内容格式是:
<pre>
<code>
7f4913d8f000-7f4913ddd000 r-xp 00000000 fd:00 791940                     /usr/local/boost149/lib/libboost_python.so.1.49.0
Size:                312 kB
Rss:                  20 kB
Pss:                   2 kB
Shared_Clean:         20 kB
Shared_Dirty:          0 kB
Private_Clean:         0 kB
Private_Dirty:         0 kB
Referenced:           20 kB
Anonymous:             0 kB
AnonHugePages:         0 kB
Swap:                  0 kB
KernelPageSize:        4 kB
MMUPageSize:           4 kB
</code>
</pre>
size：  是进程使用内存空间，并不一定实际分配了物理内存；

Rss：   "Resident Set Size"，实际驻留"在内存中"的内存数. 不包括已经交换出去的页面。RSS还包括了与其它进程共享的内存区域，通常用于共享库；

Pss：   Private Rss， Rss中私有的内存页面；

Shared_Clean：  Rss中和其他进程共享的未改写页面；

Shared_Dirty：  Rss和其他进程共享的已改写页面；

Private_Clean：  Rss中改写的私有页面页面；

Private_Dirty：  Rss中已改写的私有页面页面；

(其中Dirty页面如果没有交换机制的情况下，应该是不能回收的)

网上有仁兄使用的过滤分析此文件内容的perl脚本, 借来用:
<pre>
<code>
#!/usr/bin/perl


# Copyright Ben Maurer
# you can distribute this under the MIT/X11 License


use Linux::Smaps;


my $pid=shift @ARGV;
unless ($pid) {
 print "./smem.pl <pid>/n";
 exit 1;
}
my $map=Linux::Smaps->new($pid);
my @VMAs = $map->vmas;


format STDOUT =
VMSIZE:  @######## kb
$map->size
RSS:     @######## kb total
$map->rss
         @######## kb shared
$map->shared_clean + $map->shared_dirty
         @######## kb private clean
$map->private_clean
         @######## kb private dirty
$map->private_dirty
.


write;

printPrivateMappings ();
printSharedMappings ();


sub sharedMappings () {
    return grep { ($_->shared_clean  + $_->shared_dirty) > 0 } @VMAs;
}


sub privateMappings () {
    return grep { ($_->private_clean  + $_->private_dirty) > 0 } @VMAs;
}


sub printPrivateMappings ()
{
    $TYPE = "PRIVATE MAPPINGS";
    $^ = 'SECTION_HEADER';
    $~ = 'SECTION_ITEM';
    $- = 0;
    $= = 100000000;
    foreach  $vma (sort {-($a->private_dirty <=> $b->private_dirty)}
       privateMappings ()) {
 $size  = $vma->size;
 $dirty = $vma->private_dirty;
 $clean = $vma->private_clean;
 $file  = $vma->file_name;
 write;
    }
}


sub printSharedMappings ()
{
    $TYPE = "SHARED MAPPINGS";
    $^ = 'SECTION_HEADER';
    $~ = 'SECTION_ITEM';
    $- = 0;
    $= = 100000000;

    foreach  $vma (sort {-(($a->shared_clean + $a->shared_dirty)
      <=>
      ($b->shared_clean + $b->shared_dirty))}
     sharedMappings ()) {

 $size  = $vma->size;
 $dirty = $vma->shared_dirty;
 $clean = $vma->shared_clean;
 $file  = $vma->file_name;
 write;


    }
}


format SECTION_HEADER =
@<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
$TYPE
@>>>>>>>>>> @>>>>>>>>>>  @>>>>>>>>>   @<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
"vmsize" "rss clean" "rss dirty" "file"
.


format SECTION_ITEM =
@####### kb @####### kb @####### kb   @<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
$size $clean $dirty $file
.

</code>
</pre>
使用之前需要先安装Linux::Smaps模块:
perl -MCPAN -e 'install Linux::Smaps'

使用之:
<pre>
<code>
[root@211 tmp]# perl p.pl 6490
VMSIZE:     835412 kb
RSS:        274928 kb total
              2880 kb shared
              8112 kb private clean
            263936 kb private dirty
PRIVATE MAPPINGS
     vmsize   rss clean   rss dirty   file
  406380 kb     7432 kb   258816 kb   [heap]
    6272 kb        0 kb     3612 kb
    4048 kb       28 kb      364 kb   /terminus/crown/bin/ares
     520 kb       56 kb      216 kb
     604 kb      112 kb      176 kb
     260 kb       20 kb      160 kb
     240 kb       32 kb      128 kb   /usr/lib64/libpython2.6.so.1.0
     260 kb       44 kb       92 kb
     772 kb      236 kb       44 kb
     224 kb        0 kb       44 kb   [stack]
      56 kb        8 kb       40 kb
      80 kb       20 kb       36 kb
      72 kb       12 kb       24 kb   /terminus/crown/bin/ares
     928 kb        0 kb       24 kb   /usr/lib64/libstdc++.so.6.0.13
   10240 kb        0 kb       20 kb
     132 kb        0 kb       16 kb
      20 kb        0 kb       16 kb
    1476 kb        0 kb       16 kb   /usr/lib64/libpython2.6.so.1.0
   10240 kb        0 kb       12 kb
   10240 kb        0 kb        8 kb
      16 kb        0 kb        8 kb   /usr/lib64/python2.6/lib-dynload/datetime.so
       8 kb        0 kb        8 kb   /usr/lib64/libstdc++.so.6.0.13
       4 kb        0 kb        4 kb   /usr/lib64/python2.6/lib-dynload/syslog.so
      16 kb       12 kb        4 kb   /lib64/libc-2.12.so
       4 kb        0 kb        4 kb   /lib64/libc-2.12.so
       4 kb        0 kb        4 kb   /lib64/libm-2.12.so
       4 kb        0 kb        4 kb   /lib64/libm-2.12.so
      28 kb       20 kb        4 kb   /usr/lib64/libstdc++.so.6.0.13
      84 kb        8 kb        4 kb
      92 kb        0 kb        4 kb   /lib64/libpthread-2.12.so
       4 kb        0 kb        4 kb   /lib64/libpthread-2.12.so
       4 kb        0 kb        4 kb   /lib64/libpthread-2.12.so
      16 kb        0 kb        4 kb
      12 kb        4 kb        4 kb   /usr/lib64/libcurl.so.4.1.1
     128 kb        0 kb        4 kb   /lib64/ld-2.12.so
       4 kb        0 kb        4 kb   /lib64/ld-2.12.so
       4 kb        4 kb        0 kb   /usr/lib64/python2.6/lib-dynload/_randommodule.so
       8 kb        8 kb        0 kb   /usr/lib64/python2.6/lib-dynload/timemodule.so
       4 kb        4 kb        0 kb   /usr/lib64/python2.6/lib-dynload/_functoolsmodule.so
       4 kb        4 kb        0 kb   /usr/lib64/python2.6/lib-dynload/_json.so
       4 kb        4 kb        0 kb   /lib64/librt-2.12.so
      16 kb        8 kb        0 kb   /usr/local/boost149/lib/libboost_python.so.1.49.0
       4 kb        4 kb        0 kb   /usr/local/boost149/lib/libboost_system.so.1.49.0
       8 kb        4 kb        0 kb   /usr/local/boost149/lib/libboost_thread.so.1.49.0
      16 kb       16 kb        0 kb   /usr/local/lib/libzmq.so.1.0.0
      12 kb        4 kb        0 kb
       4 kb        4 kb        0 kb   /lib64/ld-2.12.so
       4 kb        4 kb        0 kb

SHARED MAPPINGS
     vmsize   rss clean   rss dirty   file
    4048 kb      948 kb        0 kb   /terminus/crown/bin/ares
    1476 kb      784 kb        0 kb   /usr/lib64/libpython2.6.so.1.0
    1576 kb      448 kb        0 kb   /lib64/libc-2.12.so
     324 kb      172 kb        0 kb   /usr/lib64/libcurl.so.4.1.1
     928 kb      160 kb        0 kb   /usr/lib64/libstdc++.so.6.0.13
     524 kb      104 kb        0 kb   /lib64/libm-2.12.so
     192 kb       76 kb        0 kb   /usr/local/lib/libzmq.so.1.0.0
      64 kb       32 kb        0 kb   /usr/lib64/python2.6/lib-dynload/datetime.so
      72 kb       28 kb        0 kb   /terminus/crown/bin/ares
      92 kb       28 kb        0 kb   /lib64/libpthread-2.12.so
     312 kb       20 kb        0 kb   /usr/local/boost149/lib/libboost_python.so.1.49.0
      12 kb       12 kb        0 kb   /usr/lib64/python2.6/lib-dynload/_json.so
      96 kb       12 kb        0 kb   /usr/local/boost149/lib/libboost_thread.so.1.49.0
     128 kb       12 kb        0 kb   /lib64/ld-2.12.so
       8 kb        8 kb        0 kb   /usr/lib64/python2.6/lib-dynload/syslog.so
      12 kb        8 kb        0 kb   /usr/lib64/python2.6/lib-dynload/_randommodule.so
      12 kb        8 kb        0 kb   /usr/lib64/python2.6/lib-dynload/timemodule.so
       8 kb        8 kb        0 kb   /usr/lib64/python2.6/lib-dynload/_functoolsmodule.so
      28 kb        4 kb        0 kb   /lib64/librt-2.12.so
       8 kb        4 kb        0 kb   /usr/local/boost149/lib/libboost_system.so.1.49.0
       4 kb        4 kb        0 kb   [vdso]

</pre>
</code>
从上面看到rss大小被分成了两个部分: private(私有)和shared(共享).
private rss就是我们最关心的进程实际占用的内存数.

