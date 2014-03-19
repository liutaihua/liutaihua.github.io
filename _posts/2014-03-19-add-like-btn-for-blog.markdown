---
title: add-like-btn-for-blog
layout: post
guid: urn:uuid:c4930dee-5265-4fce-9e77-18b0d25b7bbc
tags:
  - blog
  - like
---


<img src='http://farm4.staticflickr.com/3812/13215290983_4c663cbcb7_c_d.jpg'>地下铁(来自flickr)</img>  


晚上闲来无事, 看了眼blog. 这个blog是fork自lhzhang.com,  
原来他还有个like功能, 看了下源码, 是用一个站外js, js里使用ajax方式将点击like按钮的请求post到他自己的一个后台httpserver, 不过人家已经在代码里注明了, 开源之后我们来使用时, 因为域名cross domain问题, 作者是不对其他站点提供like统计支持的.  

于是就自己随意在vps上弄个简单的httpserver了,  把文章名字, 以及从浏览器里取cookie作为user, POST请求到httpserver上,  httpserver所做的只需要根据文章和user, 把文章是否被这个user  like过, 以及文章自己的liked_count 做incr,  在页面刷新的时候, GET本文章的liked_count和user的is_liked即可.

感谢下blog原作者提供这个简洁的blog模版.

