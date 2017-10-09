# -*- coding: utf-8 -*-
import cpos.esb.basic.rpc.rpc_log as rlog
from cpos.foundation.nosql.mongodb_spec import build_mongodb_frame
from cpos.foundation.substrate.utils.logger import FileLogger
from cpos.esb.basic.substrate.types import StrAttrDict as AttrDict
from cpos.esb.basic.substrate.binhex import bytes_to_hex
from cpos.esb.basic.resource.functools import get_uuid
from cpos.esb.basic.resource.logger import logger
from cpos.esb.basic.busimodel.transutils import get_xtlsh
from cpos.esb.basic.config import settings
import copy
import datetime
import json
import pickle
import os


class TransactionLogger(FileLogger):
    """
        交易使用的日志对象
        # 构建log的内容字典，包含msgxh的自增
    """
    def __init__(self):
        self.d = AttrDict({})
        self.kind = "Transaction"
        # 日志的处理类型，默认为文件类
        self.logtype = "file"
        FileLogger.__init__(self)
        self.runtime_level = self.level_map.get(settings.LOG_LEVEL_TRANS.upper() ,0)

    def set_root(self ,root):
        """
            root 写日志文件的根目录，按进程号区分
        """
        self.root = root
        try:
            # 保证文件目录是存在的
            os.makedirs(self.root)
        finally:
            return self.root

    def write(self ,msgobj):
        """
            将写入内容写到文件中，按照mongodb的缓存结构保存
        """
        if self.root is None:
            #raise RuntimeError("需要指定文件的根目录")
            print(str(msgobj))
            return   
        try:
            nr_level = self.level_map.get( msgobj["logcontent"]["level"].upper() ,0)
            if self.runtime_level > nr_level:
                # 控制日志的展示级别
                return
        except:
            logger.oes( "tlog level:" ,lv = 'warning',cat = 'basic.dictlog')
        self.write_bytes(build_mongodb_frame(msgobj ,msgobj["_id"]).marshal() ,root_has_pid=False)

    def set_data(self ,data_t):
        self.d = data_t

    def set_kind(self ,kind):
        self.kind = kind

    def set_rpctype(self ,logtype = "rpc"):
        """
            不使用文件日志的方式，使用rpc方式记录log
        """
        self.logtype = logtype

    def msgxhinc(self):
        """
            # 对self.d中的msgxh做自增处理
        """
        if self.d.msgxh is None:
            self.d.msgxh = '0'
        self.d.msgxh = str(int(self.d.msgxh)+1)
        return True

    def _loginfo( self ,level , *args , **kwargs ):
        logger.ods( "进入_loginfo " ,lv = 'dev',cat = 'basic.tlog')
        self.msgxhinc()
        logger.ods( "_loginfo 处理logcontent" ,lv = 'dev',cat = 'basic.tlog')
        logcontent = {}
        logcontent[ 'kind' ] = self.kind
        logcontent[ 'level' ] = level
        logcontent[ 'sj' ] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        logcontent[ 'jyrq' ] = self.d.SYS_JYRQ or ''
        logcontent[ 'lsh' ] = self.d.SYS_XTLSH or ''
        logcontent[ 'jdid' ] = "|".join(json.loads(self.d.SYS_JYLOGLEVEL or '[]'))
        logcontent[ 'msgxh' ] = int(self.d.msgxh or '0')
        logger.ods( "_loginfo 处理logcontent 结束" ,lv = 'dev',cat = 'basic.tlog')

        if len( args ) > 1:
            msg = args[0] % args[1:]
        elif len( args ) == 1:
            msg = args[0]
        else:
            msg = ''
        
        # 处理block
        logger.ods( "_loginfo 处理block" ,lv = 'dev',cat = 'basic.tlog')
        block = kwargs.get( 'block' , None )
        if isinstance(block, bytes):
            # 是块日志
            bin = kwargs.get( 'bin' , True )
            if bin:
                block = bytes_to_hex( block )

        if block:
            block = '\n'+'='*40+'\n'+block+ ('\n' if block[-1] != '\n' else '' ) +'='*40 + '\n'
        elif msg[-1] == '\n':
            block = ''
        else:
            block = '\n'
        logcontent[ 'msg' ] = msg + block

        # 处理jyzd
        logger.ods( "_loginfo 处理jyzd" ,lv = 'dev',cat = 'basic.tlog')
        jyzd = kwargs.get( 'jyzd' )
        if isinstance(jyzd, dict):
            logcontent[ 'jyzd' ] = jyzd
        elif isinstance(jyzd, AttrDict):
            logcontent[ 'jyzd' ] = jyzd.to_dict()
        
        logcontent_tt = copy.deepcopy(kwargs)
        if logcontent_tt.get('jyzd'):
            logcontent_tt.pop('jyzd')
        if logcontent_tt.get('block'):
            logcontent_tt.pop('block')
        logcontent_tt.update(logcontent)
        
        logger.ods( "_loginfo 构建content" ,lv = 'dev',cat = 'basic.tlog')
        content = {"logcontent":logcontent_tt, "logtype":"translog", "_id":get_uuid(), "tppid":os.getpid()}
        logger.ods( "_loginfo 构建content 结束" ,lv = 'dev',cat = 'basic.tlog')
        logger.ods( "_loginfo.write" ,lv = 'dev',cat = 'basic.tlog')
        if self.logtype == "rpc":
            # 只有单步调试是需要立即看日志的，走rpc，其他的log写文件，然后转储到mongodb
            rlog.send_log(content,level)
        else:
            self.write(content)
        logger.ods( "离开_loginfo " ,lv = 'dev',cat = 'basic.tlog')
        
    def log_debug( self , *args , **kwargs ):
        self._loginfo( 'dev', *args , **kwargs)

    def log_info( self , *args , **kwargs ):
        self._loginfo( 'info', *args , **kwargs)

    def log_warning( self , *args , **kwargs ):
        self._loginfo( 'warning', *args , **kwargs)

    def log_error( self , *args , **kwargs ):
        self._loginfo( 'error', *args , **kwargs)

    def log_critical( self , *args , **kwargs ):
        self._loginfo( 'fatal', *args , **kwargs)

    def log_exception( self , *args , **kwargs ):
        from cpos.foundation.substrate import traceback2
        exc_msg = traceback2.format_exc( show_locals = True )
        args = list( args )
        if args:
            args[0] += '\n%s'
        else:
            args.append( '%s' )
        args.append( exc_msg )
        self._loginfo( 'error', *args , **kwargs)

tlog = TransactionLogger()


def set_tlog_parms(_tlog ,root ,filename=None ,kind = "Transaction" ,reload_jyzd="no"):
    """
        对tlog的相关参数赋值，提取出来的目的是为了能够解决jr、rdcs中使用logger的问题
    """
    # 全局的日志对象
    _tlog.kind = kind
    # 生产交易日志，root/日期/通讯节点/pid/流水号
    rootpath = os.path.join(settings.DYLOGPATH, datetime.datetime.now().strftime('%Y-%m-%d') ,root)
    _tlog.set_root(rootpath)
    # 流水号做文件名
    if filename is None:
        filename = get_xtlsh()
    _tlog.set_filename(filename)
    
    # 这里赋值的目的是为了能够最后查询到
    if reload_jyzd == "yes":
        jyzd = {"SYS_XTLSH":str(filename) ,"SYS_JYRQ":datetime.datetime.now().strftime('%Y%m%d')}
        _tlog.set_data(AttrDict(jyzd))
    
    # 返回文件名，一般是日志的流水号
    logger.ods( "tlog文件的文件信息为: root【%s】 kind【%s】 filename【%s】"%(root ,kind ,filename) ,lv = 'info',cat = 'basic.tlog')
    return filename


def test_Logger():
    jyzd = AttrDict({'jyrq':'2015-03-11', 'lsh':'201503100001101010', 'jdid':'aaaaa'})
    tlog.set_root(os.path.join(r'E:\TDDOWNLOAD', "translog"))
    tlog.set_filename(jyzd["lsh"])
    tlog.set_data(jyzd)
    tlog.log_debug('1111111111111111111111111')
    tlog.log_info('2222222222222222222222222222')
    tlog.log_warning('3333333333333333333333333333',jyzd=jyzd)
    tlog.log_error('44444444444444444444444444')
    tlog.log_critical('555555555555555555555555555 %s','--------------------------')
    suc_buf = b"397 ZZ02            (dp1\nS'SJGM_SPECIALS'\np2\nS'SYS_RspCode,XYM|SYS_RspInfo,XYNR,CXXYXX'\np3\nsS'HMLX'\np4\nS'G'\nsS'JYJGM'\np5\nS'5500'\np6\nsS'CZGY'\np7\nS'admin'\np8\nsS'JFHM'\np9\nS'13583128471'\np10\nsS'DQDM'\np11\ng6\nsS'SJGM_FIELDS'\np12\nS'XYM,XYNR,CXXYXX,YHMC,HFYE'\np13\nsS'QDLSH'\np14\nS'11111Z000003'\np15\nsS'QDBH'\np16\nS'00'\np17\nsS'JYDM'\np18\nS'ZZ02'\np19\nsS'QDJYRQ'\np20\nS'20150312'\np21\nsS'ZDID'\np22\nS'11111'\np23\ns."
    
    tlog.log_info('666666666666666666666666666666' ,block=suc_buf ,bin=True)
    tlog.log_info('77777777777777777777777777' ,block=suc_buf ,test_=11111111111111111111111)

    try:
        aaaaaaaa
    except:
        tlog.log_exception( '更新流水[%s]失败' , 111111 )
    tlog.close(jyzd["lsh"])

if __name__=="__main__":
    test_Logger()

