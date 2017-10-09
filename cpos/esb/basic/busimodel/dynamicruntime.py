# -*- coding: utf-8 -*-
from cpos.foundation._callable.core import DynamicRuntime
from cpos.esb.basic.substrate.types import StrAttrDict as AttrDict ,AttrDictDefault
from cpos.esb.basic.resource.dycall import dcallpy ,scall
from cpos.esb.basic.resource.logger import logger
from cpos.esb.basic.busimodel.transutils import is_trans_timeout
from cpos.esb.basic.config import settings
ENV_INIT_FILE = settings.TRANS_ENV_INIT
import json
import os



def get_opstrans_dr(filename):
    # 使用提供的文件来初始化运行环境
    dr = scall("")
    logger.ods( "使用【%s】初始化运行时环境"%filename ,lv = 'dev',cat = 'app.tp')
    if os.path.isfile(filename):
        try:
            dr = dcallpy(os.path.split(filename)[-1] ,root=os.path.dirname(filename))
            logger.ods( "初始化运行时环境 成功" ,lv = 'dev',cat = 'app.tp')
        except:
            logger.oes( "初始化运行时环境 失败" ,lv = 'warning',cat = 'app.tp')
    else:
        logger.ods( "初始化运行时环境，【%s】文件不存在"%filename ,lv = 'warning',cat = 'app.tp')
    return dr

class CommonRuntime(DynamicRuntime):
    """
        # 单独调用公共函数时使用
    """
    def __init__ (self):
        dr = get_opstrans_dr(ENV_INIT_FILE)
        DynamicRuntime.__init__(self,np=dr.np)


class TransactionIdentificationRuntime(CommonRuntime):
    """
        # 在交易识别中直接使用
    """
    def __init__ (self,TransDict):
        self.TransDict = TransDict
        CommonRuntime.__init__(self)

    def prepare_environment (self):
        DynamicRuntime.prepare_environment(self)
        self.np['jyzd'] = AttrDict(self.TransDict)


class NodeRun(object):
    """
        # 子流程的执行过程和正常的是一致的，提取一下做插件类
    """
    def node_run(self):
        logger.ods( "flow_node 中获取信息 "+str(self.next_name) ,lv = 'dev',cat = 'app.tp')
        self.np['tlog'].log_info("============================:%s" % str(self.next_name))
        node = self.bank_service_context.get_flow_node(self.next_name)
        logger.ods( "node_run start "+str(node.jdbm) ,lv = 'dev',cat = 'app.tp')
        
        # 记录要执行的节点名
        if self.next_name == 'start':
            self.np['jyzd'].SYS_JYJDGZ += '%s,'%(node.ssjydm)
        
        # 这是为了能够在日志中获得相关信息
        self.np['jyzd'].SYS_JYLOGLEVEL = json.dumps( json.loads(self.np['jyzd'].SYS_JYLOGLEVEL)+[node.jdbm] )
        self.np['tlog'].log_info("开始处理节点【%s】【%s】", node.jdbm, self.np['jyzd'].SYS_JYLOGLEVEL)
        # 节点执行列表
        jyloglevel = eval( self.np['jyzd'].SYS_JYLOGLEVEL )
        # 冲正处理
        if is_trans_timeout(self.np['jyzd'].SYS_CSSJ ,self.np['jyzd'].SYS_CTIME):
            self.np['tlog'].log_info("============================异常处理冲正start")
            ret,msg = insert_jycz( self.np['jyzd'].SYS_JYM, node.ssjydm, node.jdbm, jyloglevel, self.np['jyzd'], self.np['tlog'] )
            if not ret:
                raise RuntimeError( msg )
            self.np['tlog'].log_info("============================异常处理冲正end")
            raise RuntimeError("交易处理超时")
        
        ret_value = self.call(node)
        ret_value = str(ret_value)
        self.next_name = node.route_table[ret_value]
        
        # 记录节点执行的返回结果
        self.np['jyzd'].SYS_JYJDGZ += '%s[%s]:'%(node.jdbm,ret_value)
        self.np['jyzd'].SYS_DZXJDDM = self.next_name
        self.np['tlog'].log_info("节点代码执行处理完成【%s】【%s】",node.ssjydm,node.jdbm ,jyzd=self.np['jyzd'])
        # 放到这里是为了保证在tlog中能够输出刚执行完成的jdid
        self.np['jyzd'].SYS_JYLOGLEVEL = json.dumps( json.loads(self.np['jyzd'].SYS_JYLOGLEVEL)[:-1] )
        logger.ods( "node_run end "+str(node.jdbm) ,lv = 'dev',cat = 'app.tp')
        
        # 书写冲正信息
        self.np['tlog'].log_info("============================正常处理冲正start")
        ret,msg = insert_jycz( self.np['jyzd'].SYS_JYM, node.ssjydm, node.jdbm, jyloglevel, self.np['jyzd'], self.np['tlog'] )
        if not ret:
            raise RuntimeError( msg )
        self.np['tlog'].log_info("============================正常处理冲正end")
        
        return ret_value


class FlowDynamicRuntime(DynamicRuntime,NodeRun):
    """
        # 交易中的flow处理过程
    """
    def __init__ (self, global_callable_list, bank_service_context, TransDict):
        self.global_callable_list = global_callable_list
        self.bank_service_context = bank_service_context
        self.next_name = 'start'
        self.TransDict = TransDict
        dr = get_opstrans_dr(ENV_INIT_FILE)
        DynamicRuntime.__init__(self,np=dr.np)

    def prepare_environment (self):
        """
            # 初始化np环境
            # 将一些公共函数绑定到YW上
        """
        DynamicRuntime.prepare_environment(self)
        self.np['YW'] = AttrDictDefault()
        self.np['jyzd'] = AttrDict(self.TransDict)
        # 增加jyzd.SYS_JYJDGZ，用于记录节点执行过程
        self.np['jyzd'].SYS_JYJDGZ = ''
        self.np['jyzd'].SYS_JYLOGLEVEL = json.dumps([])
        
        for global_callable in self.global_callable_list:
            self.call(global_callable)
        return True
        
    def next (self):
        if self.next_name == 'end':
            # 记录要执行的节点名，主要是补充end节点
            self.np['jyzd'].SYS_JYJDGZ += 'end[0]'
            # 这里是为了能够在交易监控中展示交易主流程end节点的日志
            self.np['jyzd'].SYS_JYLOGLEVEL = json.dumps(['end'])
            self.np['tlog'].log_info("节点代码执行处理完成 end ",jyzd=self.np['jyzd'])
            return False
        ret_value = self.node_run()
        return True


class ChildNodesFlowRuntime(DynamicRuntime,NodeRun):
    """
        # 子流程ZLC，这里的run是为了能够被上层正常调用
    """
    def __init__ (self, bank_service_context):
        DynamicRuntime.__init__(self)
        self.np = {}
        self.bank_service_context = bank_service_context
        self.next_name = 'start'

    def run(self,np):
        # 使用传入的np
        self.np = np
        
        while self.next_name != 'end':
            ret_value = self.node_run()
        
        # 记录要执行的节点名，主要是补充end节点
        self.np['jyzd'].SYS_JYJDGZ += 'end[%s]:'%(ret_value)
        # 因为是子流程，所以提供end之前的那个节点的返回值
        return ret_value

def insert_jycz( zjym, jym, next_name, jg_lst, jyzd, tlog ):
    """
    # 冲正登记
    # zjym: 主交易编码
    # jym：交易码或子流程编码：执行交易码
    # next_name: 待执行节点或子流程id
    # jg_lst: 执行节点列表
    # jyzd：交易字典
    # tlog: log对象
    """
    # 将主交易放在最前面
    jg_lst.insert(0, zjym)
    tlog.log_info('处理自动冲正：开始[jg_lst:%s]' % str(jg_lst))
    try:
        with connection() as db:
            # 判断是有有配置冲正信息
            sql_jy = """select czpzid from gl_lcbj
                        where jddyid in ( select id from gl_jddy where bm = %(bm)s )
                        and ssjyid in ( select id from gl_jydy where jym = %(jym)s )"""
            sql_jy2 = """select czpzid from gl_lcbj
                        where jddyid in ( select id from gl_zlcdy where bm = %(bm)s )
                        and ssjyid in ( select id from gl_jydy where jym = %(jym)s )"""
            sql_zlc = """select czpzid from gl_lcbj
                        where jddyid in ( select id from gl_jddy where bm = %(bm)s )
                        and sszlcid in ( select id from gl_zlcdy where bm = %(jym)s )"""
            sql_zlc2 = """select czpzid from gl_lcbj
                        where jddyid in ( select id from gl_zlcdy where bm = %(bm)s )
                        and sszlcid in ( select id from gl_zlcdy where bm = %(jym)s )"""
            sql_dic = { 'bm': next_name, 'jym': jg_lst[-2] }
            # 当执行节点所处流程为子流程时，使用子流程
            sql_check = ( sql_jy if sql_dic['jym'] == jym else sql_jy2 ) if len(jg_lst) <= 2 else ( sql_zlc if sql_dic['jym'] == jym else sql_zlc2  )
            tlog.log_info('处理自动冲正：判断是有有配置冲正信息sql[%s]' % sql_check)
            tlog.log_info( '处理自动冲正：判断是有有配置冲正信息sql_dic[%s]' % str( sql_dic ) )
            rs = db.execute_sql( sql_check, sql_dic )
            # 有配置冲正子流程
            if rs and rs[0] and rs[0].czpzid:
                # 冲正执行冲正子流程
                jyzd.HTZLCID = rs[0].czpzid
                tlog.log_info('处理自动冲正：存在冲正配置id：%s' % jyzd.HTZLCID)
                # 判断HTXX是否有值
                if jyzd.HTXX and jyzd.HTXX != '{}':
                    tlog.log_info('处理自动冲正：有登记回退信息[%s]' % jyzd.HTXX)
                    # 新增回退日志表（JY_HTRZ）
                    import pickle
                    htxx = pickle.dumps( jyzd.HTXX )
                    SJ_XH = jyzd.SJ_XH if jyzd.SJ_XH else 0
                    jyzd.SJ_XH = int(SJ_XH) + 1
                    sql_ins_htrz = """ insert into JY_HTRZ( lsh, jyrq, xh, rq, jym, jdmc, htxx, htzlcid ) 
                                    values( %(lsh)s, %(jyrq)s, %(xh)s, %(rq)s, %(jym)s, %(jdmc)s, %(htxx)s, %(htzlcid)s )
                                    """
                    sql_ins_dic = { 'lsh': jyzd.SYS_XTLSH, 'jyrq': jyzd.SYS_JYRQ, 'xh': jyzd.SJ_XH, 'rq': jyzd.SYS_XTRQ,
                                    'jym': jyzd.SYS_JYM, 'jdmc': next_name, 'htxx': htxx, 'htzlcid': jyzd.HTZLCID }
                    
                    tlog.log_info('处理自动冲正：登记回退日志XX[%s]' % str( sql_ins_dic ))
                    db.execute_sql( sql_ins_htrz, sql_ins_dic )
                    # 将是否记录回退操作记录标识置为yes
                    jyzd.ISSAF = 'yes'
                    # 清空回退信息
                    jyzd.HTXX = {}
                    return True, ''
                else:
                    tlog.log_info('处理自动冲正：回退信息未定义')
                    return False, '处理自动冲正：回退信息未定义'
            else:
                tlog.log_info('处理自动冲正：未查询到冲正配置信息，无需登记冲正日志')
                return True, ''
    except:
        # 创建连接失败
        tlog.log_exception( '处理冲正操作失败：' )
        return False, '处理冲正操作失败'
