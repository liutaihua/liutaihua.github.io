---
title: post
layout: post
guid: urn:uuid:4b730ef5-ab1f-11e3-bef0-040ccecf359c
tags:
    - move from old blog
------


有2种方式可以实现backup
1,使用wal backup的方式,配置:


{{% highlight c++ %}}
wal_level = archive

archive_mode = on

archive_command = 'test ! -f /data/postgresql/arch/%f && 

cp %p /data/postgresql/arch/%f'
\#archive_timeout = 600
{{% endhighlight %}}

配置后reload pgmaster进程, 此时可以使用psql连接pg后手工进行:
select pg_start_backup('test');
select pg_stop_backup();
系统会将wal日志备份到配置文件指定的目录, 另外的方式,可以脚本化这个操作,同时将walbackup后的文件压缩打包:

{{% highlight c++ %}}
\#!/bin/sh

if [ "$1" == "" ]; then
    $0 backupname
    exit 1
fi
{{% endhighlight %}}


{{% highlight c++ %}}
mkdir -p /data/postgresql/arch
mkdir -p /data/postgresql/arch_gz

psql -Upostgres << START_BACKUP_END
select pg_start_backup('$1');
\q
START_BACKUP_END

find /data/postgresql/arch/ -print | cpio -o -H crc | gzip -v > /data/postgresql/arch_gz/$1.cpio.gz

psql  -Upostgres<< STOP_BACKUP_END
select pg_stop_backup();
\q
STOP_BACKUP_END
{{% endhighlight %}}

\#put backup file to ftp



2, 第2个方式是直接使用pg_dump命令进行
    pg_dump -Upostgres testdb > testdb.backup.sql


使用wal backup的备份方式的优缺点:

Advantages:
Incremental, the WAL archives include everything necessary to restore the current state of the database
Almost no overhead, copying WAL files is cheap
You can restore the database at any point in time (this feature is called PITR, or point-in-time recovery)
Disadvantages:
More complicated to set up than pg_dump
The full backup will be much larger than a pg_dump because all internal table structures and indexes are included
Doesn't work work well for write-heavy databases, since recovery will take a long time.

