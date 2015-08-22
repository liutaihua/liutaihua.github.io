---
title: weak_ptr use for cross threading callbak
layout: post
guid: urn:uuid:bc834883-38d1-44a6-afe7-58085f6b6d2d
description: weak_ptr use for cross threading callbak
tags:
  - weak_ptr
  - shared_ptr
  - cpp
  - threading
  - RAII
---


## 工厂类回收资源和夸线程回调时对象是否还存在判断

虽然大多数逻辑都在单线程里实现， 但是不能避免的是一些IO阻塞类型逻辑， 不得不放入子线程里执行，当IO完成后boost:bind(callback, arg1, arg2 ...) 放入主线程队列内执行callback, 但是问题是，假如callback指向的对象函数的对象， 已经销毁了， 这时候就无法判断对象是否还存在了，不判断就会core dump.

可以用weak_ptr完美解决这里线程回调时对象是否还可用的判断


{{% highlight c++ %}} 
class Foo : public std::shared_from_this<Foo>
{
  public:
    void start() {
        auto callback = boost::bind(&Foo::CB, this, boost::weak_ptr<StockFactory>(shared_from_this()));
        boost::thread(&Foo::DoIO, this, callback);
      
    }
    
    void CB(std::weak_ptr<Foo> pObj) {
        std::shared_ptr<Foo> p(pObj.lock())   //尝试提升weak_ptr， 提升失败则对象已消耗，否则提升成shared_ptr
        if (p)
            printf("cb called");
        else
            printf("Object already Destructe");
    }
    
    void DoIO(std::function<void ()> f)
    {
      //doSomeThing()
      f();
    }
}
{{% endhighlight %}} 
    
类似的用法，还有在工厂方法回收资源使用, 防止被创建的对象早与工厂类对象被析构的时候， 因为反回调清除工厂类中objMap里自己释放资源的时候， 工厂对象已经在这之前析构， coredump.

{{% highlight c++ %}} 
class Factory public boost::enable_shared_from_this<Factory>
{
public:
    shared_ptr<Foo>  get()
    {
        
      shared_ptr<Foo> pFoo;
      weak_ptr<Foo> wkFoo;

      // 传自定的析构方法给shared_ptr在析构的时候调用
      pFoo.reset(new Foo,
        boost::bind(&Factory::weakDeleteCallback,
        boost::weak_ptr<Factory>(shared_from_this()),
        _1));
        // 上面必须强制把 shared_from_this() 转型为 weak_ptr，才不会延长生命期
      wkFoo = pFoo; //shared_ptr降为weak_ptr
      string myKey = doGetMyKey();
      objMap[myKey] = wkFoo;
      return pStock;
    }
    
    static void weakDeleteCallback(std::weak_ptr<Factory> wkFactory,
      Foo* pFoo)
    {
        shared_ptr<Factory> factory(wkFactory.lock()); // 尝试提升
        if (factory) { // 如果 factory 还在，那就清理 objMap
            factory->removeStock(objMap);
        }
      delete stock; // sorry, I lied
    }
    
    void removeStock(Foo* p)
    {
        if (p) {
        objMap.erase(p->key());
    }


privite:
    std::map<string, weak_ptr<Foo> > objMap;
}
{{% endhighlight %}} 
代码不严谨，没经过编译， 仅供自己理解. 学习资料参照 <a href="http://files.cppblog.com/Solstice/dtor_meets_mt.pdf">这里</a>
