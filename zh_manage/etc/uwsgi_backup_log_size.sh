#!/bin/bash

LOGDIR=$LOGSDIR                               #log目录
sourcelogpath="${LOGDIR}/oasj_uwsgi.log"       #log源地址
# 获取当前日志大小
size=`ls -l $sourcelogpath | awk '{ print int($5)/1024 }'`
echo '目前日志大小（KB）：'
echo $size
# 判断大小是否超过最大值
if [ $size > 100 ]
then
    echo '超过规定大小,需要拆分文件'
    touchfile="${LOGDIR}/.touchforlogrotate"       #需要touch的文件
    DATE=`date -d "yesterday" +"%Y%m%d%H%M%S"`    #获取当前日期时间
    destlogpath="${LOGDIR}/oasj_uwsgi.log.${DATE}" #重命名后的文件
    mv $sourcelogpath $destlogpath
    touch $touchfile                              # 更新文件时间戳
else
    echo '未超过规定大小'
fi
