# -*- coding: utf-8 -*-

######################## 数据库的连接 
DB_CONSTR = dict( dsn = 'ORCL_250' , user = 'tsyw' , password = 'tsyw' )


######################## rpc的连接配置 
MQS_CONNECTION_PARAMETER  = {'host':'127.0.0.1' , 'port':5672 , 'socket_timeout' : 4 ,'connection_attempts': 1}
MQS_CREDENTIAL_DESCRIPTOR =    {  'user_name' :   'sjdev'  ,  'pass_word' :   'sjdev'  }

# ICM的地址，ICP向该IP发送报文
ICM_IP = "46.17.189.106"


######################## 缓存控制 
MEMCACHE_IPS = ['46.17.189.250:5628']

######################## mongodb数据库
MONGODB_IPS = ['46.17.189.250:5625']


###################### 以下内容在LINUX上部署时不需要设置 ########################
######################## OPS的文件目录位置 
OPS_ROOT = r"E:\projects\ZHTSYWPT\cpos.esb.kf\jngt\ops"
# 通过RMQ传输文件时，文件的目录位置
RPC_FILE_ROOT = r"F:\Projects_TEMP\rpc_file"

######################## 日志相关配置 
# 核心日志生成目录
APPLOGPATH = r"F:\Projects_TEMP\syslog"

# 交易日志生成目录，主要是动态加载的代码中使用
DYLOGPATH = r"F:\Projects_TEMP\translog"

# print内容的输出文件
PRINTFILEPATH = r"F:\Projects_TEMP\print.log"

# 连接mongodb时使用的配置
LOG_MAP_DIC = {
    "translog":{"local_file":r'F:\Projects_TEMP', 'dbname':"zhtsyw", 'collection':"translog"} ,
    "syslog":{"local_file":r'F:\Projects_TEMP','dbname':"esbapp", 'collection':"syslog"}
    }

# 调试模式时会打印日志内容到控制台
LOG_ENABLE_CONSOLE = False

# 交易处理环境初始化代码所在路径
TRANS_ENV_INIT = r"E:\projects\ZHTSYWPT\cpos.esb.kf\ops\envinit.py"

# 管理平台提供的代码位置
ZH_MANAGE_PY = r"E:\projects\ZHTSYWPT\cpos.esb.kf\jngt\ops\zh_manage\yw_jkgl_001.py"

# shell文件的生成目录
SBINPATH = r"F:\Projects_TEMP\sjsbin"
##################################### end #####################################

# 这里是为了在本地测试，不使用数据库获得代码，纯挡板
#from cpos.esb.tests.busimodel.callable_source import source_from_db
#API_SOURCE_FROM_DB = source_from_db

