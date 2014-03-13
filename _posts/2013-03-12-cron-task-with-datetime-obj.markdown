--
layout: post
Title: "使用datetime, 构造一个cron task定期执行给定的函数方法"
Date: 2013-03-12 16:29
comments: true
categories: notes
--

使用datetime, 构造一个cron task定期执行给定的函数方法



一个Plan类, 包含next_datatime, execute, 两个方法, __init__方法指明在实例化的时候,需要给定一个func作为参数, 其他参数可以是时间间隔, 或具体的时间点,

<pre>

class Plan(object):

    def __init__(self, func):

        assert callable(fund)

        self.func = fund



    def excute(self):

        self.func()

</pre>

Plan作基类, 根据需要可以做派生,  比如一个方式是按照指定的时间, 间隔执行func,  派生另外一个是到达指定时刻才执行func:



<pre>

class  FixedIntervalPlan(Plan):    # 间隔指定时间后, 在外调用的时候判断next_datetime来执行方法execute

    def __init__(self, fund, **kwargs):

        super(FixedIntervalPlan, self).__init__(func)

        self.interval = datetime.datetime(**kwargs)



    def next_datetime(self):

        return datetime.datetime.now() + self.interval



class FixedTimePlan(Plan):            

    # 根据指定时刻计算出下一时刻, 调用的时候判断next_datetime来决定是否在这个时刻执行execute方法

    def __init__(self, func, **kwargs):

        super(FixedTimePlan, self).__init__(fund)

        self.time = datetime.time(**kwargs)



    def next_datetime(self):        

        now = datetime.datetime.now()

        if self.time > now.time():

            return datetime.datetime.combine(now.date(), self.time)

        else:

            tomorrow = now + datetime.timedelta(days=1)

            return datetime.datetime.combine(tomorrow.date(), self.time)



</pre>

以下是一个实际例子, 如何使用上面的2个类:

<pre>

cron_task_config = [

    FixedIntervalPlan(match_team, seconds=10),    #  每隔10秒执行match_team

]

</pre>

main函数如下:

<pre>

def main():

    pendding_tasks = []   #  初始化一次已经在cron_task_config配置内的任务实例化

    for plan in cron_task_config:

        # pan.next_datetime(), 计算下次任务什么时候可以执行, 将此时间和实例化的

        pendding_tasks.append((plan.next_datetime(), plan))                           

                                                                                         #  plan一起加入准备执行的列表

    cnt = 0

    while True:

        now = datetime.datetime.now()

        if cnt % 60 == 0:

            print now

        next_pendding_tasks = []

        for task in pendding_tasks:

            trigger_time, plan = task

            if trigger_time < now: # 触发时间就是plan的next_datetime, 如果小于当前时间, 表示可以执行

                plan.execute()

                next_pendding_tasks.append((plan.next_datetime(), plan)) # 本次执行完之后,  再次计算next_datetime(), 以备下次判断

            else:

                next_pendding_tasks.append(task) # 触发时间不符合, 加入下次执行的列表内

        pendding_tasks = next_pendding_tasks

        time.sleep(1)

        cnt += 1

</pre>





疑问是, 需要搞这么复杂么, time.sleep定期执行不就行了?  短时间反复执行是用time.sleep可解决, 不过当需求是需要在某天某时刻精确时执行, 用time.sleep显然不行了.  
