---
title: python sorted function for dict
layout: post
guid: urn:uuid:3caa3bc2-a07f-4972-9b93-0612d5c43467
tags:
  - python
  - 排序
---


PY有自己内建的工厂函数sorted用来排序, 它返回一个原地排序后的副本. 采用的是原地排序算法. 这个工厂函数的原型是:    

<pre><code>sort(cmp=None, key=None, reverse=None)  </code></pre>  

在使用sorted的时候, 都是可以根据自己需要指定一个函数给key作为针对数据里具体哪个位置做排序的,  

比如最简单的对字典d={'a': {'s': 1}, 'b': {'s': 2}}的's'字段排序:  


  <pre><code>  sorted(d.items(), key=lambda x:x[1]['s'])</code></pre>  
  
key是一个匿名函数, 匿名函数会逐个接受d.items()后产生的列表里的项作为参数, key的函数的返回就是排序的关键字, sorted工厂函数会在等待所有项返回后, 针对这些项对字典d进行排序.   

这里使用的都是针对单个关键字做排序,  实际遇到很多需要对一个字典数据里的多个关键字进行排序.    

有比较优雅的写法是:  
<pre><code>
def sort_dict_by_key_list(d, key_list, reverse=False):
    def ccmp(data_x, data_y):
        for key in key_list:
            return cmp(data_x[key], data_y[key])
    return sorted(d.iteritems(), key=lambda x:x[1], cmp=ccmp, reverse=reverse)
</code></pre>
上面代码中,写了一个自己的cmp把原生cmp套在里面做返回， 加入多个关键字排序的需求进去， 但是这个似乎没有做到的需求是： 多个关键字排序， 这些关键字中有的需要反序， 有的则需要正序， 因为上面的reverse是全局性的， 要么全部正序, 要么全部反序.  

比如一个字典里包含了每个学生的 本次成绩, 学号, 上次考试成绩, 需要针对这3个关键字做排序, 优先顺序是: 优先排本次成绩, 然后是上次成绩, 再然后就学号.  
当对多个关键字做排序的时候, 一样还需要支持是否reverse, 那么这次给key函数就相对稍微复杂点了:  


<pre><code>
def sortkeypicker(keynames):
    reverse_tuple = set()
    for i, k in enumerate(keynames):
        if k[:1] == '-':
            keynames[i] = k[1:]
            reverse_tuple.add(k[1:])
    def getit(adict):
        adict = adict[1]
        composite = [adict[k] for k in keynames]
        for i, (k, v) in enumerate(zip(keynames, composite)):
            if k in reverse_tuple: #出现在reverse_tuple里的key是需要做reverse的, 这里直接把它负数化.
                composite[i] = -int(v)
        return composite
    return getit

d = {'Mike': {'SN': 100, 'current_score': 88, 'last_score': 80}, 'Pod': {'SN': 101, 'current_score': 90, 'last_score': 89}, 'Lisa': {'SN': 33, 'current_score': 79, 'last_score': 93}}

sorted(d.iteritems(), key=sortkeypicker(['-current_score', '-last_score', 'SN']))
</code></pre>

上面的代码中, sortkeypicker函数作为key函数, 它接受一个列表, 这个列表包含要针对哪几个关键词做排序的关键字列表, 在列表越靠近左边的越优先;  
首先处理一下是否需要reverse反序排序的关键字(依据是给定的关键词前的负号"-"), 然后它会返回一个闭包函数,  这个闭包函数getit, 它接受的函数就是在d.iteritems()时产生的列表里的元素,  
这些元素将逐个被getit函数处理, 返回没一个经过处理元素的结果 composite,  
composite其实是一个列表, 列表里包含的就是 keynames关键字列表里这些关键字所对应的字典d里面的value, 当然这些value会在经过之前是否需要reverse_tuple里的关键字做反序处理,  
这里的操作并不会改变字典d里本身的value大小, 所以才有负数的情况, 负数是为了reverse.
  
  
当d.iteritems()里的元素全部逐个被getit处理完之后,  工厂函数sorted已经拥有了针对所有元素排序的依据, 这个例子中, 这些依据就是一个一个的composite, 它的值大体就是:  

    [-88, -80, 100], [-90, -89, 101], [-79, -93, 33]

也就是说实际上工厂函数sorted是对列表  [[-88, -80, 100], [-90, -89, 101], [-79, -93, 33]] 做排序, 同时它保存有这些结果归属于字典d的对应项目, 然后返回经过排序的列表即可, 由于字典本身不是有序的, 所以sorted返回的并不是字典, 而是一个列表, 列表里的元素是d.items()里的个项(key和value对应的元组)  
至此完成对字典数据里多个关键字的排序.

明白了这些逻辑,  当需要对列表或是其他数据结构做多关键字排序的时候, 只需要对key函数==> sortkeypicker做相应修改, 即可达成目的.  

完!


