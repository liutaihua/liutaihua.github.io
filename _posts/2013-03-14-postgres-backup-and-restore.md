--
layout: post
Title: "postgres备份和恢复"
Date: 2013-03-14 13:28
comments: true
categories: notes
--

####备份:

在postgres.conf配置里指定:

archive_command = 'cp "%p" /data/postgresql/arch/"%f"'



设定:

wal_level=archive  

 

手工备份操作方式:

psql cli后:

select pg_start_backup(' test backup') 

然后:

select pg_stop_backup() ,stop执行时,就会执行archive_command中定义的backup.



####从wal备份中恢复:

创建一个recovery.conf:

cp /usr/pgsql-9.2/share/recovery.conf.sample recovery.conf



在recovery.conf配置中指定:

restore_command = 'cp /data/postgresql/arch/%f %p'



然后重新启动postgresql, 系统会检查到recovery.conf文件的存在,并执行restore, 然后正常启动后,会自动将recovery.conf文件名改为recovery.conf.done
