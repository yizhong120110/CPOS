# -*- coding: utf-8 -*-
"""  
    将写到文件中的日志转到mongodb中
"""
from cpos.esb.basic.resource.functools import get_uuid ,get_hostname
from cpos.esb.basic.resource.nosql import get_mlobj
from cpos.esb.basic.resource.logger import logger
from cpos.esb.basic.config import settings
from cpos.esb.basic.application.app_rpclog import env_get
from cpos.esb.basic.application.app_interval import interval
import time
import os
import psutil
import json
import copy
import re


def ispidliving(pid):
    """ 判读pid对应的进程是否存在 """
    return True if pid in list(map(str,psutil.pids())) else False


def get_logfiles(rootpath):
    """ 获取要处理的文件的列表 """
    logfilelst = []
    try:
        for root, dirs, files in os.walk(rootpath):
            for file_t in files:
                fn_old = os.path.join(root,file_t)
                # 暂时不加延迟
#                file_mtime = time.strftime("%Y%m%d%H%M%S", time.localtime(os.stat(fn_old).st_mtime))
#                # 文件存储到mongodb中后，需要重命名，转移10秒之前分钟数的日志
#                if not (time.strftime("%Y%m%d%H%M%S",time.localtime(time.time()-10)) > file_mtime):
#                    continue
                if file_t.endswith('.log'):
                    # 这种的可以直接转移
                    logfilelst.append(fn_old)
                elif file_t.endswith('.tmp'):
                    # 这种的先判断目录的最后一层pid号是否还存活，如果不存活，直接重命名，如果存活，则不处理
                    pid = root.split(os.path.sep)[-1]
                    if ispidliving(pid):
                        # 还活着，不处理
                        pass
                    else:
                        if not pid.isdigit():
                            # pid为数值，说明是TP类的，这样的是为了处理进程死亡时导致的tmp
                            # 非数值类，是二次开发者开发的，一般是占位用的日志
                            continue
                        try:
                            # 先重命名，然后读文件
                            fn_new = '.'.join(fn_old.split('.')[:-1]+['log'])
                            os.renames(fn_old ,fn_new)
                            logfilelst.append(fn_new)
                        except:
                            logger.ods( "日志文件【%s】不予处理"%(fn_old),lv = 'warning',cat = 'app.filelp')
                            continue
                else:
                    pass
    except:
        logger.oes( "获得待转移日志文件列表异常",lv = 'warning',cat = 'app.filelp')
    return logfilelst


def trans_valfunc(content_input):
    content = copy.deepcopy(content_input)
    content['lppid'] = os.getpid()
    content['hostname'] = get_hostname()
    content['writetype'] = "log_file"
    return content


def translog2db(ml):
    """
        将交易执行产生的log从文件转到mongodb中，转移以log结尾的，以及tmp结尾但进程号不存在的
        先将这些文件的内容存到mongodb中，然后将文件重命名到"%s_%s"%(settings.DYLOGPATH,"bak")
    """
    logfilelst = get_logfiles(settings.DYLOGPATH)
    if logfilelst:
        logger.ods( "translog2db 待转移日志文件为：%s"%(logfilelst),lv = 'info',cat = 'app.filelp')

    for filename in logfilelst:
        try:
            newfile_name = filename.replace(settings.DYLOGPATH,"%s_%s"%(settings.DYLOGPATH,"bak"))\
                                .replace(".log",".%s.%s.log"%(os.getpid(),time.strftime("%H%M%S")))
            if ml.writefile2db_file(filename ,valfunc=trans_valfunc ,newfile=newfile_name) and os.path.getsize(filename) == 0:
                # 缓存文件存在，且内容为空，将其删除
                os.remove(filename)
        except FileNotFoundError:
            # 有可能在处理日志时，正好卡在时间点上，文件尚未关闭，然后open报错
            logger.ods( "translog2db 日志文件处理异常：%s"%(filename) ,lv = 'warning',cat = 'app.filelp')
        except:
            # 有可能在处理日志时，正好卡在时间点上，文件尚未关闭，然后open报错
            logger.oes( "translog2db 待转移日志异常：" ,lv = 'warning',cat = 'app.filelp')


def syslog2db(ml):
    """
        将核心执行产生的log从文件转到mongodb中
        先将这些文件的内容存到mongodb中，然后将文件重命名到"%s_%s"%(settings.APPLOGPATH,"bak")
    """
    logfilelst = get_logfiles(settings.APPLOGPATH)
    logger.ods( "syslog2db 待转移日志文件数量为：%s"%(len(logfilelst)),lv = 'dev',cat = 'app.filelp')

    for filename in logfilelst:
        try:
            # filter、map得到的不是list类型，是iterable
            # 读取文件的内容不是json，是普通的str
            tmp_filename = list(filter(lambda x:x ,filename.replace(settings.APPLOGPATH,"").split(os.sep)))
            content = {"logtype":"syslog" ,"writetype":"log_file"}
            content['lprq'] = time.strftime("%Y%m%d")
            content['lppid'] = os.getpid()
            content['hostname'] = get_hostname()
            content['filename'] = tmp_filename
            content['logcontent'] = {"msg":""}
            for msgstr in open(filename ,'rb').readlines():
                msgstr = msgstr.decode(encoding="utf-8")
                msg_tlist = re.split(r'(^\d{4}-\d{2}-\d{2}) (\d{2}:\d{2}:\d{2}.\d{6}) \| (\d*) \| (\w*) \|([^|]*) \|' ,msgstr)
                if len(msg_tlist)>1:
                    # 这是一条新的记录，先将之前的写入mongodb中
                    if content['logcontent']["msg"]:
                        # 避免写入空数据
                        ml.writedata(get_uuid(), content)
                    # 开始新的
                    msg_tlist = [x.strip('| ') for x in msg_tlist if x]
                    content['logcontent'] = {"msg":""}
                    content['logcontent']["rq"] = msg_tlist[0]
                    content['logcontent']["sj"] = '%s %s'%(msg_tlist[0] ,msg_tlist[1])
                    content['logcontent']["pid"] = msg_tlist[2]
                    content['logcontent']["level"] = msg_tlist[3]
                    content['logcontent']["cat"] = msg_tlist[4]
                    content['logcontent']["msg"] += msg_tlist[5]
                else:
                    # 这是上面内容的一部分，直接写到前一条中
                    content['logcontent']["msg"] += msgstr

            if content['logcontent']["msg"]:
                # 避免写入空数据
                ml.writedata(get_uuid(), content)

            # 文件存储到mongodb中后，需要重命名
            os.renames(filename ,filename.replace(settings.APPLOGPATH,"%s_%s"%(settings.APPLOGPATH,"bak")))
        except FileNotFoundError:
            logger.ods( "syslog2db 日志文件处理异常：%s"%(str(tmp_filename)) ,lv = 'warning',cat = 'app.filelp')
        except:
            # 有可能在处理日志时，正好卡在时间点上，文件尚未关闭，然后open报错
            logger.oes( "syslog2db 待转移日志异常：" ,lv = 'warning',cat = 'app.filelp')

def main_all():
    """
        这是含 syslog 和 translog 转移的，由于syslog内容过多，一般不需要使用，暂时不用这个
        需要使用时，使用一个单独的脚本来处理syslog的文件内容合并
    """
    ml_trans = None
    ml_sys = None
    # 这是固定间隔，不需要变为配置的
    while interval.run(1,env_get('keep_running',True)):
        if not ml_trans or not ml_trans.coll:
            ml_trans = get_mlobj("translog")
            if ml_trans and ml_trans.coll:
                # 创建索引，如果有了，则不会创建新的
                ml_trans.coll.ensure_index([("logcontent.lsh",-1) ,("logcontent.jyrq",-1)] ,name='translog_index')
            
        # 连接mongodb失败了，就不用做转移了
        if ml_trans and ml_trans.coll:
            logger.ods( "转移translog日志文件" ,lv = 'dev',cat = 'app.filelp')
            translog2db(ml_trans)
        
        if not ml_sys or not ml_sys.coll:
            # 核心运行产生的日志写入到mongodb中时连接名为："%s_%s_%s"%(mlparas["collection"],get_hostname(),time.strftime("%Y%m%d"))
            ml_sys = get_mlobj("syslog")
            if ml_sys and ml_sys.coll:
                # 创建索引，如果有了，则不会创建新的
                ml_sys.coll.ensure_index([("hostname",-1) ,("lprq",-1) ,("lppid",-1)] ,name='syslog_index')
            
        # 连接mongodb失败了，就不用做转移了
        if ml_sys and ml_sys.coll:
            logger.ods( "转移syslog日志文件" ,lv = 'dev',cat = 'app.filelp')
            syslog2db(ml_sys)
        logger.ods( "本次转移日志文件结束" ,lv = 'dev',cat = 'app.filelp')
    if ml_trans:
        ml_trans.close()
    if ml_sys:
        ml_sys.close()


def main():
    """
        这仅仅是 translog 转移的
    """
    ml_trans = None
    # 这是固定间隔，不需要变为配置的
    while interval.run(1,env_get('keep_running',True)):
        if not ml_trans or not ml_trans.coll:
            ml_trans = get_mlobj("translog")
            if ml_trans and ml_trans.coll:
                # 创建索引，如果有了，则不会创建新的
                ml_trans.coll.ensure_index([("logcontent.lsh",-1) ,("logcontent.jyrq",-1)] ,name='translog_index')
            
        # 连接mongodb失败了，就不用做转移了
        if ml_trans and ml_trans.coll:
            logger.ods( "转移translog日志文件" ,lv = 'dev',cat = 'app.filelp')
            translog2db(ml_trans)
        
        logger.ods( "本次转移日志文件结束" ,lv = 'dev',cat = 'app.filelp')
    if ml_trans:
        ml_trans.close()


if __name__=="__main__":
    get_logfiles(settings.DYLOGPATH)
