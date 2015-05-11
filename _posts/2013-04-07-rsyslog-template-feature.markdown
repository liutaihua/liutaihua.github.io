---
title: "使用rsyslog的template功能"
layout: post
guid: urn:uuid:4b73b78c-ab1f-11e3-b438-040ccecf359c
tags:
    - move from old blog
---
#####rsyslog的一个高级点的用法, 根据programname做日志文件分离, 使用template功能根据系统时间切割日志文件:

<pre>
<code>
*.info;mail.none;authpriv.none;cron.none;!local1;!local3;!local2;               /var/log/messages

$SystemLogRateLimitInterval 2
$SystemLogRateLimitBurst 500

#$out  log_rotation, /terminus/gamelog/hades.log, 1024, /etc/./log_rotation_script


$template hades, "[%PROGRAMNAME%]%MSG:::sp-if-no-1st-sp%%MSG:::drop-last-lf%\n"
$template hadesfile, "/terminus/gamelog/hades_%$YEAR%-%$MONTH%-%$DAY%-%$HOUR%.log"
$template profilefile, "/terminus/gamelog/profile_attr_%$YEAR%-%$MONTH%-%$DAY%-%$HOUR%.log"
$template questfile, "/terminus/gamelog/quest_%$YEAR%-%$MONTH%-%$DAY%-%$HOUR%.log"
$template packagefile, "/terminus/gamelog/package_%$YEAR%-%$MONTH%-%$DAY%-%$HOUR%.log"

if $programname startswith 'hades' then                 ?hadesfile;hades
if $programname startswith 'profile' then                 ?profilefile;hades
if $programname startswith 'quest' then                 ?questfile;hades
if $programname startswith 'package' then                 ?packagefile;hades

</code>
</pre>
