# -*- coding: utf-8 -*-
from cpos.esb.basic.rpc import rpc
from cpos.esb.basic.config import settings
wqs_log_appstatus = settings.WQS_LOG_APPSTATUS
wqs_log_dev = settings.WQS_LOG_DEV
wqs_log_info = settings.WQS_LOG_INFO
wqs_log_warning = settings.WQS_LOG_WARNING
wqs_log_error = settings.WQS_LOG_ERROR
wqs_log_fatal = settings.WQS_LOG_FATAL


def start_log_server (cb = None ,cp = None):
    return rpc.start_server(cb,cp,wqs_list = [  wqs_log_appstatus,
                                                wqs_log_dev,
                                                wqs_log_info,
                                                wqs_log_warning,
                                                wqs_log_error,
                                                wqs_log_fatal] )

def send_appstatus (content):
    if not( isinstance(content, dict) or isinstance(content,str) ):
        raise TypeError('send_appstatus expects dict or str')
    r = rpc.req( content , wqs_log_appstatus, 0)
    rpc.noreply_rpc([r ])

def send_log (content,level = 'dev'):
    if not( isinstance(content, dict) or isinstance(content,str) ):
        raise TypeError('send_log expects dict or str')
    log_wqs = {'dev':wqs_log_dev , 'info':wqs_log_info, 'warning':wqs_log_warning , 'error':wqs_log_error, 'fatal':wqs_log_fatal}
    wqs = log_wqs.get(level)
    if wqs == None:
        wqs = wqs_log_dev
    r = rpc.req( content , wqs, 0)
    rpc.noreply_rpc([r ])


if __name__ == '__main__':
    send_log({'kkk':'vvv'},'info')
