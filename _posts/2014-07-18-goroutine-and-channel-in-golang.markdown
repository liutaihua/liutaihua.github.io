---
title: goroutine and channel in golang
layout: post
guid: urn:uuid:be23178c-640d-4492-beea-078c8baf6697
description: goroutine and channel in golang
tags:
  -golang
  -goroutine
  -channel
---


Golang
看了几天golang, 蛋疼的把以前一个PY的日志处理程序,用golang重写了, 很简单的一个小程序. 用golang重写涉及到, 一些自有特定的string类型的日志, 先是转换成json, 用到simplejson模块, json, err := simplejson.Loads(subStr),  
后面发现用map类型实现, 会更优雅一点:  
<pre>
<code>
    byt := []byte(subStr)
    var dat map[string]interface{}
    if err:= json.Unmarshal(byt, &dat); err != nil{
        panic(err)
    }
    </code></pre>
第2个需要做的就是, 连接mysql做日志入库  
也换了2个方式, 第一次使用go-sql-driver/mysql库, 由于代码写的不大好, 把db的实例化写在了go func {.......}() 里面了, 导致了大量的db连接,  即使使用db.SetMaxIdleConns(10)并不会起效, 很明显因为本身一个go就开启了一个实例, 导致大量mysql连接.  
也尝试使用channel数据类型构建一个简单的db pool:  

<pre>
<code>
var MySQLPool chan *sql.DB
var MAX_POOL_SIZE = 100

func GetMySQL() *sql.DB {
    if MySQLPool == nil {
        MySQLPool = make(chan *sql.DB, MAX_POOL_SIZE)
    }
    //host := ""
    //port := 3306
    user := "terminus"
    passwd := "daydayup"
    db := "athene"
    //connArgs := user + ":" + passwd + "@/" + db + "?charset=utf8"
    connArgs := user + ":" + passwd + "@unix(/tmp/mysql.sock)/" + db + "?charset=utf8"

    if len(MySQLPool) == 0 {
        go func() {
            for i:=0;i<MAX_POOL_SIZE/2;i++ {
                mysql, err := sql.Open("mysql", connArgs)
                if err != nil{
                    panic(err)
                }
                pushToPool(mysql)
            }
        }()
    }
    return <-MySQLPool
}

func pushToPool(conn *sql.DB) {
    if MySQLPool == nil {
        MySQLPool = make(chan *sql.DB, MAX_POOL_SIZE)
    }
    if len(MySQLPool) == MAX_POOL_SIZE {
        conn.Close()
        return
    }
    MySQLPool <- conn
}  
    </code></pre>
但是如上面所说, 这并不是根本问题,  因为错误的讲db的实例化写在go func {....}()里了, 用什么方式其实都会导致数据库连接过多问题, 很傻逼的做法, 发现后迅速改掉, 连接数已经回正常控制水平了, 用自己写的db pool或者不用都一样,  因为使用golang自带的database/sql模块,  sql.Open('mysql', xxxx)来启动go-sql-driver/mysql时,  sql模块本身已经为玩家们封装了db pool, 因此只需要进行db.SetMaxIdleConns(100) 设置最大连接即可..  

自己写一个db pool也是为了使用看看channel数据类型串行多个goroutine的方式. 
用到的库有:  
database/sql  
github.com/go-sql-driver/mysql  
github.com/likexian/simplejson  
strconv  
encoding/json  
strings

