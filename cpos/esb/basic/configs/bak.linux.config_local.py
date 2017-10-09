# -*- coding: utf-8 -*-

######################## 数据库的连接 -------（ 数据库主机ip ）
DB_CONSTR = dict( dsn = '46.17.189.250:1521/orcl' , user = 'tsyw' , password = 'tsyw' )


######################## rpc的连接配置 ------（ 管理主机ip和用户名：密码 ）
MQS_CONNECTION_PARAMETER  = {'host':'46.17.189.250' , 'port':5672 , 'socket_timeout' : 4 ,'connection_attempts': 1}
MQS_CREDENTIAL_DESCRIPTOR =    {  'user_name' :   'sjdev'  ,  'pass_word' :   'sjdev'  }


# ICM的地址，ICP向该IP发送报文--------------（通讯主机ip）
ICM_IP = "46.17.189.250"


######################## 缓存控制 -----------（业务主机ip）
MEMCACHE_IPS = ['46.17.189.250:5628']


######################## mongodb数据库------（数据库主机ip）
MONGODB_IPS = ['46.17.189.250:5625']


# 注意如果是测试阶段想实时查看核心代码sjesbapp.log时，只需要将下列代码第一层注释取消即可
#import os
#userhome = os.environ.get('HOME','')
## 调试模式时会打印日志内容到控制台，也可以设置一个文件全路径，作为log的输出目录
#LOG_ENABLE_CONSOLE = '%s/log/sjesbapp.log'%(userhome)
##LOG_ENABLE_CONSOLE = False
