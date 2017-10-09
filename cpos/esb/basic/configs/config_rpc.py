# -*- coding: utf-8 -*-
"""
Descriptions
"""

###############################################################################################################
# Message Queue Settings
MQS_CONNECTION_PARAMETER  = {'host':'46.17.167.239' , 'port':5672 , 'socket_timeout' : 4 ,'connection_attempts': 1}
MQS_CREDENTIAL_DESCRIPTOR =    {  'user_name' :   'sjdev'  ,  'pass_word' :   'sjdev'  }
MQS_DEFAULT_POOL_SIZE = 10           # very much not recommended!!! but for a lazy user
                                    # this can keep the system runing normally.
                                    # in multi thread environment, it should support a producer and a consumer at one time.


# main working queue settings (transaction)
WQS_TRANSACTION =   {   'exchange'  :   'sjesb.trans' , 'queue' : 'q.trans' ,
                        'binding_key' : 'sj.trans' , 'queue_durable':True}
WQS_TRANSACTION_JAVA = {  'exchange'  :   'sjesb.trans_java' , 'queue' : 'q.trans_java' ,
                        'binding_key' : 'sj.trans_java' , 'queue_durable':True}
WQS_TRANSACTION_TIMEOUT = 10 # default timeout time in seconds.


########################################################################################
# application status report , through this mq.
WQS_LOG_APPSTATUS =   {   'exchange'  :   'sjesb.log' , 'queue' : 'q.log.appstatus' ,
                        'binding_key' : 'sj.log.appstatus' , 'queue_durable':False}


########################################################################################
# log , through this mq.
WQS_LOG_DEV =   {   'exchange'  :   'sjesb.log' , 'queue' : 'q.log.dev' ,
                        'binding_key' : 'sj.log.dev' , 'queue_durable':True}
# log , through this mq.
WQS_LOG_INFO =   {   'exchange'  :   'sjesb.log' , 'queue' : 'q.log.info' ,
                        'binding_key' : 'sj.log.info' , 'queue_durable':True}
# log , through this mq.
WQS_LOG_WARNING =   {   'exchange'  :   'sjesb.log' , 'queue' : 'q.log.warning' ,
                        'binding_key' : 'sj.log.warning' , 'queue_durable':True}
# log , through this mq.
WQS_LOG_ERROR =   {   'exchange'  :   'sjesb.log' , 'queue' : 'q.log.error' ,
                        'binding_key' : 'sj.log.error' , 'queue_durable':True}
# log , through this mq.
WQS_LOG_FATAL =   {   'exchange'  :   'sjesb.log' , 'queue' : 'q.log.fatal' ,
                        'binding_key' : 'sj.log.fatal' , 'queue_durable':True}
#########################################################################################


####################### 响应动作进程 #######################################################
WQS_JR =   {   'exchange'  :   'sjesb.jr' , 'queue' : 'q.jr' ,
                            # 主要是为了响应管理端的人工操作，响应失败没有问题
                        'binding_key' : 'sj.jr' , 'queue_durable':False} # Must be False! if a jrs losts connection,the queue must be destroy accordingly.
WQS_JR_TIMEOUT = 5 # default timeout time in seconds.
###############################################################################################
#OCM
WQS_OCM =    {   'exchange'  :   'sjesb.ocm' , 'queue' : 'q.ocm' ,
                        'binding_key' : 'sj.ocm' , 'queue_durable':False}
WQS_OCM_TIMEOUT = 5 # default timeout time in seconds.
