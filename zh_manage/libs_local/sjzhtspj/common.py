# -*- coding: utf-8 -*-
# Action: 公共函数
# Author: gaorj
# AddTime: 2014-12-25
# Standard: 注释仅能以“#”开头，sql可以是“--”；注释不能同代码在同一行

import os, sys, io, re, uuid, datetime, hashlib, traceback, py_compile, pickle, pickle,binascii
from . import ModSql, settings, logger, xmltodict, get_sess_hydm, STATIC_DIR, crontab, render_to_string
from .crondescriptor import CronDescriptor
from .const import ZDLX_DIC
from sjzhtspj import TMPDIR,get_sess
from sjzhtspj.esb import get_lsh2con


def get_uuid():
    """
    # 获取新的uuid
    """
    return uuid.uuid4().hex

def get_strftime():
    """
    # 获取当前时间(yyyy-MM-dd HH:mm:ss格式)
    """
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def get_strftime2():
    """
    # 获取当前时间(yyyyMMddHHmmss格式)
    """
    return datetime.datetime.now().strftime('%Y%m%d%H%M%S')

def get_strfdate():
    """
    # 获取当前日期(2015-04-14格式)
    """
    return datetime.datetime.now().strftime('%Y-%m-%d')

def get_strfdate2():
    """
    # 获取当前日期(20150414格式)
    """
    return datetime.datetime.now().strftime('%Y%m%d')

def cal_md5(obj):
    """
    # 计算传入对象的md5值
    # 先将传入对象做str()处理，再计算
    """
    return hashlib.md5(str(obj).encode('utf-8')).hexdigest()

def update_wym(db, lx, id):
    """
    # 更新唯一码
    # db: 数据库连接
    # lx: 类型('jy':交易, 'zlc':子流程, 'jd':节点, 'gghs':公共函数(业务), 'sjk':数据库, 'txgl':通讯管理, 'cdtxgl':C端通讯管理, 'cs':参数, 'dy':打印配置)
    # id: 对应的ID（如lx是'jy'，则此处是交易ID）
    """
    sql_data = {'id': id}
    # 交易唯一码：ID+所属业务ID+交易码+交易名称+交易描述+交易超时时间+交易状态+自动发起配置+流程布局表+流程走向表
    if lx == 'jy':
        # 查询交易定义
        rs_jydy = ModSql.common.execute_sql_dict(db, "get_jydy", sql_data)
        # 查询流程布局表
        rs_lcbj = ModSql.common.execute_sql_dict(db, "get_lcbj_jy", sql_data)
        # 查询流程走向表
        rs_lczx = ModSql.common.execute_sql_dict(db, "get_lczx", sql_data)
        # 计算md5值
        md5 = cal_md5((rs_jydy, rs_lcbj, rs_lczx))
        # 更新唯一码字段值
        sql_data = {'tablename': ['gl_jydy'], 'id': id, 'wym': md5}
        ModSql.common.execute_sql_dict(db, "update_wym_by_tb", sql_data)
    # 子流程唯一码：ID+类别+编码+名称+描述+所属业务ID+流程布局表+流程走向表
    elif lx == 'zlc':
        # 查询子流程定义
        rs_zlcdy = ModSql.common.execute_sql_dict(db, "get_zlcdy", sql_data)
        # 查询流程布局表
        rs_lcbj = ModSql.common.execute_sql_dict(db, "get_lcbj_zlc", sql_data)
        # 查询流程走向表
        rs_lczx = ModSql.common.execute_sql_dict(db, "get_lczx", sql_data)
        # 计算md5值
        md5 = cal_md5((rs_zlcdy, rs_lcbj, rs_lczx))
        # 更新唯一码字段值
        sql_data = {'tablename': ['gl_zlcdy'], 'id': id, 'wym': md5}
        ModSql.common.execute_sql_dict(db, "update_wym_by_tb", sql_data)
    # 节点唯一码
    elif lx == 'jd':
        # 获取节点定义表信息
        rs_jddy = ModSql.common.execute_sql_dict(db, "get_jddy", {'ids': [sql_data['id']]})
        # 获取节点要素表信息
        rs_jdys = ModSql.common.execute_sql_dict(db, "get_jdys", sql_data)
        for row in rs_jdys:
            # 归属类别不参与唯一码计算
            row['gslb'] = None
        # 获取代码内容
        rs_blob = ModSql.common.execute_sql_dict(db, "get_nr_jd", sql_data)
        nr = pickle.loads(rs_blob[0]['nr'].read()) if rs_blob else ''
        # 计算md5值
        md5 = cal_md5((rs_jddy, rs_jdys, nr))
        # 更新唯一码字段值
        sql_data = {'tablename': ['gl_jddy'], 'id': id, 'wym': md5}
        ModSql.common.execute_sql_dict(db, "update_wym_by_tb", sql_data)
    # 公共函数
    elif lx == 'gghs':
        # 获取公共函数信息
        rs_gghs = ModSql.common.execute_sql_dict(db, "get_gghs", sql_data)
        # 计算md5值
        gghs_dic = {}
        if rs_gghs:
            gghs_dic = rs_gghs[0]
            gghs_dic['nr'] = pickle.loads(rs_gghs[0]['nr'].read()) if rs_gghs[0]['nr'] else ''
        md5_nr = cal_md5(gghs_dic)
        # 更新公共函数唯一码字段值
        sql_data = {'tablename': ['gl_yw_gghs'], 'id': id, 'wym': md5_nr}
        ModSql.common.execute_sql_dict(db, "update_wym_by_tb", sql_data)
    # 数据库：所属业务ID+数据表名称+数据表名称描述+数据表字段及字段属性+数据表索引及索引属性+数据库约束及属性
    elif lx == 'sjk':
        # 查询数据库明细定义
        rs_sjkmxdy = ModSql.common.execute_sql_dict(db, "get_sjkmxdy", sql_data)
        # 查询数据表字段及字段属性
        rs_sjkzdb = ModSql.common.execute_sql_dict(db, "get_sjkzdb", sql_data)
        # 查询数据表索引及索引属性
        rs_sjksy = ModSql.common.execute_sql_dict(db, "get_sjksy", sql_data)
        # 查询数据库约束及属性
        rs_sjkys = ModSql.common.execute_sql_dict(db, "get_sjkys", sql_data)
        # 计算md5值
        md5 = cal_md5((rs_sjkmxdy, rs_sjkzdb, rs_sjksy, rs_sjkys))
        # 更新唯一码字段值
        sql_data = {'tablename': ['gl_sjkmxdy'], 'id': id, 'wym': md5}
        ModSql.common.execute_sql_dict(db, "update_wym_by_tb", sql_data)
    # 通讯管理：编码+名称+解出交易码函数ID+服务方向+超时时间+通讯类型+通讯文件名称+解出交易码函数内容
    elif lx == 'txgl':
        # 查询通讯管理信息
        rs_txgl = ModSql.common.execute_sql_dict(db, "get_txgl", sql_data)
        # 计算md5值
        txgl_dic = {}
        if rs_txgl:
            txgl_dic = rs_txgl[0]
            txgl_dic['nr'] = pickle.loads(rs_txgl[0]['nr'].read()) if rs_txgl[0]['nr'] else ''
        md5_nr = cal_md5(txgl_dic)
        # 更新唯一码字段值
        sql_data = {'tablename': ['gl_txgl'], 'id': id, 'wym': md5_nr}
        ModSql.common.execute_sql_dict(db, "update_wym_by_tb", sql_data)
    # C端通讯管理：编码+子流程定义ID+通讯管理ID+对方交易码+对方交易名称+打包节点ID+解包节点ID+超时时间+挡板类型+挡板所属ID+所属业务ID
    elif lx == 'cdtxgl':
        # 查询C端通讯管理
        rs_txgl = ModSql.common.execute_sql_dict(db, "get_cdtx_for_wym", sql_data)
        # 计算md5值
        md5 = cal_md5(rs_txgl)
        # 更新唯一码字段值
        sql_data = {'tablename': ['gl_cdtx'], 'id': id, 'wym': md5}
        ModSql.common.execute_sql_dict(db, "update_wym_by_tb", sql_data)
    # 参数：ID+参数代码+参数描述+参数值+类型+所属ID+状态+支持地区
    elif lx == 'cs':
        # 查询参数定义
        rs_csdy = ModSql.common.execute_sql_dict(db, "get_csdy_bm", sql_data)
        # 计算md5值
        md5 = cal_md5(rs_csdy)
        # 更新唯一码字段值
        sql_data = {'tablename': ['gl_csdy'], 'id': id, 'wym': md5}
        ModSql.common.execute_sql_dict(db, "update_wym_by_tb", sql_data)
    # 打印配置：ID+模板名称+模板描述+模板类型+所属业务ID+模板内容（内容_id所指向的内容）
    elif lx == 'dy':
        # 获取打印配置信息
        rs_dy = ModSql.common.execute_sql_dict(db, "get_dymbdy", sql_data)
        # 计算md5值
        dy_dic = {}
        if rs_dy:
            dy_dic = rs_dy[0]
            dy_dic['nr'] = pickle.loads(rs_dy[0]['nr'].read()) if rs_dy[0]['nr'] else ''
        md5 = cal_md5(dy_dic)
        # 更新唯一码字段值
        sql_data = {'tablename': ['gl_dymbdy'], 'id': id, 'wym': md5}
        ModSql.common.execute_sql_dict(db, "update_wym_by_tb", sql_data)

def update_wym_yw(db, lx, id):
    """
    # 更新唯一码( 运维 )
    # db: 数据库连接
    # lx: 类型('dxdy':对象定义, 'fxgzgl':分析管理, 'xydzgl':响应动作, 'sjcjpzgl':数据采集配置管理,
          'jkpzgl':监控配置管理, 'yzjycspz':阈值校验参数配置, 'yzjypz':阈值校验配置, 'jcxxpz':进程信息配置 )
    # id: 对应的ID（如lx为“dxdy”, id为对象id）
    """
    sql_data = {'id': id}
    # 对象定义（ 监控类别，对象编码，对象名称，描述，状态 ） id为对象id 更新表：对象定义表
    if lx == 'dxdy':
        # 获取对象定义表信息
        rs_dxxx = ModSql.common.execute_sql_dict(db, "wym_select_dxdy", {'dxid': sql_data['id']})
        # 计算md5值
        md5 = cal_md5((rs_dxxx))
        # 更新唯一码字段值
        sql_data = {'tablename': ['gl_dxdy'], 'id': id, 'wym': md5}
        ModSql.common.execute_sql_dict(db, "update_wym_by_tb", sql_data)
    
    # 分析规则管理
    elif lx == 'fxgzgl':
        # 获取分析规则基本信息和规则代码
        rs_fxgzjbxx = ModSql.common.execute_sql_dict(db, "wym_select_fxgz", {'fxgzid': sql_data['id']})
        # 获取分析规则传入参数信息
        rs_csxx = ModSql.common.execute_sql_dict(db, "wym_select_fxgz_crcs", {'fxgzid': sql_data['id']})
        # 处理规则代码
        fxgz_dic = {}
        if rs_fxgzjbxx:
            fxgz_dic = rs_fxgzjbxx[0]
            fxgz_dic['nr'] = pickle.loads(fxgz_dic['nr'].read()) if fxgz_dic['nr'] else ''
        # 计算md5值
        md5 = cal_md5((fxgz_dic, rs_csxx))
        # 更新唯一码字段值
        sql_data = {'tablename': ['gl_hsxxb'], 'id': id, 'wym': md5}
        ModSql.common.execute_sql_dict(db, "update_wym_by_tb", sql_data)
    
    # 响应动作管理
    elif lx == 'xydzgl':
        # 获取响应动作基本信息和动作代码
        rs_xydzjbxx = ModSql.common.execute_sql_dict(db, "wym_select_xydz", {'xydzid': sql_data['id']})
        # 获取响应动作传入参数信息
        rs_csxx = ModSql.common.execute_sql_dict(db, "wym_select_xydz_crcs", {'xydzid': sql_data['id']})
        # 处理动作代码
        xydz_dic = {}
        if rs_xydzjbxx:
            xydz_dic = rs_xydzjbxx[0]
            xydz_dic['nr'] = pickle.loads(xydz_dic['nr'].read()) if xydz_dic['nr'] else ''
        # 计算md5值
        md5 = cal_md5((xydz_dic, rs_csxx))
        # 更新唯一码字段值
        sql_data = {'tablename': ['gl_hsxxb'], 'id': id, 'wym': md5}
        ModSql.common.execute_sql_dict(db, "update_wym_by_tb", sql_data)
    
    #数据采集配置管理
    elif lx == 'sjcjpzgl':
        # 获取数据采集配置基本信息
        rs_cjpzjbxx = ModSql.common.execute_sql_dict(db, "wym_select_cjpz", {'czpzid': sql_data['id']})
        # 获取数据采集配置适应对象
        rs_cjpzsydx = ModSql.common.execute_sql_dict(db, "wym_select_cjpz_sydx", {'czpzid': sql_data['id']})
        # 获取数据采集配置适应对象对应传入参数
        rs_cjpzsydxcrcs = ModSql.common.execute_sql_dict(db, "wym_select_cjpz_crcs", {'czpzid': sql_data['id']})
        # 计算md5值
        md5 = cal_md5((rs_cjpzjbxx, rs_cjpzsydx, rs_cjpzsydxcrcs))
        # 更新唯一码字段值
        sql_data = {'tablename': ['gl_cjpzb'], 'id': id, 'wym': md5}
        ModSql.common.execute_sql_dict(db, "update_wym_by_tb", sql_data)
    # 监控配置管理
    elif lx == 'jkpzgl':
        # 获取监控分析配置表基本信息
        rs_jkfxpzjbxx = ModSql.common.execute_sql_dict(db, "wym_select_jkpzgl", {'jkfxpzid': sql_data['id']})
        # 获取监控分析配置对应规则参数信息
        rs_jkfxpzgzcs = ModSql.common.execute_sql_dict(db, "wym_select_jkpzgl_gzcs", {'jkfxpzid': sql_data['id']})
        # 获取监控分析配置对应的响应动作
        rs_jkfxpzxydz = ModSql.common.execute_sql_dict(db, "wym_select_jkpzgl_xydz", {'jkfxpzid': sql_data['id']})
        # 响应动作对相应的监控主机
        rs_xydzjkzj = ModSql.common.execute_sql_dict(db, "wym_select_jkpzgl_xydz_jkzj", {'jkfxpzid': sql_data['id']})
        # 响应动作对应的参数
        rs_xydzdycs = ModSql.common.execute_sql_dict(db, "wym_select_jkpzgl_xydz_dycs", {'jkfxpzid': sql_data['id']})
        # 计算md5值
        md5 = cal_md5((rs_jkfxpzjbxx, rs_jkfxpzgzcs, rs_jkfxpzxydz, rs_xydzjkzj, rs_xydzdycs))
        # 更新唯一码字段值
        sql_data = {'tablename': ['gl_jkfxpz'], 'id': id, 'wym': md5}
        ModSql.common.execute_sql_dict(db, "update_wym_by_tb", sql_data)
    # 阈值校验参数配置
    elif lx == 'yzjycspz':
        # 获取阈值校验参数配置信息
        rs_yzjycspz = ModSql.common.execute_sql_dict(db, "wym_select_yzjycspz", {'yzjycspzid': sql_data['id']})
        # 计算md5值
        md5 = cal_md5((rs_yzjycspz))
        # 更新唯一码字段值
        sql_data = {'tablename': ['gl_yzjycspz'], 'id': id, 'wym': md5}
        ModSql.common.execute_sql_dict(db, "update_wym_by_tb", sql_data)
    # 阈值校验配置
    elif lx == 'yzjypz':
        # 阈值校验配置
        rs_yzjypz = ModSql.common.execute_sql_dict(db, "wym_select_yzjypz", {'yzjypzid': sql_data['id']})
        # 获取阈值校验配置-扣款明细 信息 扣款明细金额sql
        rs_kkmx_mxjesql = ModSql.common.execute_sql_dict(db, "wym_select_yzjypz_kkmxsql", {'yzjypzid': sql_data['id']})
        # 获取阈值校验配置-扣款明细 信息 扣款明细查询sql
        rs_kkmx_mxcxsql = ModSql.common.execute_sql_dict(db, "wym_select_yzjypz_kkmxcxsql", {'yzjypzid': sql_data['id']})
        # 获取阈值校验配置-扩展模块 信息
        rs_kzmk = ModSql.common.execute_sql_dict(db, "wym_select_yzjypz_kzmk", {'yzjypzid': sql_data['id']})
        # 获取阈值校验配置-流水导入 信息
        rs_lsdr = ModSql.common.execute_sql_dict(db, "wym_select_yzjypz_drls", {'yzjypzid': sql_data['id']})
        # 获取阈值校验配置-异常更新 信息 全部撤销
        rs_ycgx_qbcx = ModSql.common.execute_sql_dict(db, "wym_select_yzjypz_ycgx_qbcx", {'yzjypzid': sql_data['id']})
        # 获取阈值校验配置-异常更新 信息 单笔状态更新
        rs_ycgx_dbztgx = ModSql.common.execute_sql_dict(db, "wym_select_yzjypz_ycgx_dbztgx", {'yzjypzid': sql_data['id']})
        # 获取阈值校验配置-异常更新 信息 全部通过
        rs_ycgx_qbtg = ModSql.common.execute_sql_dict(db, "wym_select_yzjypz_ycgx_qbtg", {'yzjypzid': sql_data['id']})
        # 处理内容信息
        # 明细金额sql
        mxjesql = ''
        if rs_kkmx_mxjesql:
            mxjesql_dic = rs_kkmx_mxjesql[0]
            mxjesql = pickle.loads(mxjesql_dic['kkmxsql'].read()) if mxjesql_dic['kkmxsql'] else ''
        # 查询sql
        mxcxsql = ''
        if rs_kkmx_mxcxsql:
            mxcxsql_dic = rs_kkmx_mxcxsql[0]
            mxcxsql = pickle.loads(mxcxsql_dic['kkmxcxsql'].read()) if mxcxsql_dic['kkmxcxsql'] else ''
        # 扩展模块
        kzmk_dic = {}
        if rs_kzmk:
            kzmk_dic = rs_kzmk[0]
            kzmk_dic['kkjynr'] = pickle.loads(kzmk_dic['kkjynr'].read()) if kzmk_dic['kkjynr'] else ''
        # 流水导入
        lsdr_dic = {}
        if rs_lsdr:
            lsdr_dic = rs_lsdr[0]
            lsdr_dic['lsdrnr'] = pickle.loads(lsdr_dic['lsdrnr'].read()) if lsdr_dic['lsdrnr'] else ''
        # 异常更新 全部撤销
        qbcxsql = ''
        if rs_ycgx_qbcx:
            qbcxsql_dic = rs_ycgx_qbcx[0]
            qbcxsql = pickle.loads(qbcxsql_dic['qbcxsql'].read()) if qbcxsql_dic['qbcxsql'] else ''
        # 异常更新 信息 单笔状态更新
        dbztgxsql = ''
        if rs_ycgx_dbztgx:
            dbztgxsql_dic = rs_ycgx_dbztgx[0]
            dbztgxsql = pickle.loads(dbztgxsql_dic['dbztgxsql'].read()) if dbztgxsql_dic['dbztgxsql'] else ''
        # 异常更新 信息 全部通过
        qbtgsql = ''
        if rs_ycgx_qbtg:
            qbtgsql_dic = rs_ycgx_qbtg[0]
            qbtgsql = pickle.loads(qbtgsql_dic['qbtgsql'].read()) if qbtgsql_dic['qbtgsql'] else ''
        # 计算md5值
        md5 = cal_md5((rs_yzjypz,[mxjesql,mxcxsql],kzmk_dic,lsdr_dic,[qbcxsql,dbztgxsql,qbtgsql]))
        # 更新唯一码字段值
        sql_data = {'tablename': ['gl_yzjypz'], 'id': id, 'wym': md5}
        ModSql.common.execute_sql_dict(db, "update_wym_by_tb", sql_data)
    
    # 进程信息配置
    elif lx == 'jcxxpz':
        # 获取进程信息配置信息
        rs_jcxxpz = ModSql.common.execute_sql_dict(db, "wym_select_jcxxpz", {'jcxxpzid': sql_data['id']})
        # 计算md5值
        md5 = cal_md5((rs_jcxxpz))
        # 更新唯一码字段值
        sql_data = {'tablename': ['gl_jcxxpz'], 'id': id, 'wym': md5}
        ModSql.common.execute_sql_dict(db, "update_wym_by_tb", sql_data)
    # 参数对应表
    elif lx == 'csdyb':
        # 获取参数对应表信息
        rs_csdyb = ModSql.common.execute_sql_dict(db, "wym_select_csdyb", {'csdybid': sql_data['id']})
        # 计算md5值
        md5 = cal_md5((rs_csdyb))
        # 更新唯一码字段值
        sql_data = {'tablename': ['gl_csdyb'], 'id': id, 'wym': md5}
        ModSql.common.execute_sql_dict(db, "update_wym_by_tb", sql_data)

def py_check(code):
    """
    # python代码语法检查
    # 可以成功编译成.pyc文件即是检查通过
    # 无错误返回空字符串，有错误返回错误信息
    """
    exc_msg = ''
    try:
        compile(code, '', 'exec')
    except:
        log_err = traceback.format_exc()
        logger.info( log_err )
        # 获取错误信息，并对格式进行整理
        exc_msg = re.sub(r'.+ in py_check', '', log_err)
        exc_msg = exc_msg.replace('\n\n  File "<string>"', '\n  File "<string>"')
    
    return exc_msg

def lc_data_service(id, lx='lc'):
    """
    # 交易/子流程查看获取数据
    # id: 流程ID
    # lx: 'lc'交易，'zlc'子流程
    """
    # 需要关联的字段
    zd = 'sszlcid' if lx == 'zlc' else 'ssjyid'
    
    with sjapi.connection() as db:
        # 查询节点/子流程名称、x坐标、y坐标、节点类型、filename和functionname
        sql_data = {'id': id, 'zd': [zd]}
        rs_lcbj = ModSql.common.execute_sql_dict(db, "get_lcbj_for_xml", sql_data)
        
        # 流程走向
        sql_data = {'ssid': id}
        connector = ModSql.common.execute_sql_dict(db, "get_lczx_for_xml", sql_data)
        for k in connector:
            k.update({'label': k['value']})
        
        # 查询打解包
        sql_data = {'id': id}
        rs_jy = ModSql.common.execute_sql(db, "get_jydy", sql_data) if lx == 'lc' else []
        jbjdid = rs_jy[0].jbjdid if rs_jy else ''
        dbjdid = rs_jy[0].dbjdid if rs_jy else ''
        # 查询唯一码（流程编辑中判断是否需要版本提交）
        sql_data = {'ids': [row['nodeid'] for row in rs_lcbj] + [jbjdid, dbjdid]}
        jd_wym_dic = {}
        zlc_wym_dic = {}
        # 存在流程布局
        if sql_data['ids'] != []:
            # 节点
            rs_jd_wym = ModSql.common.execute_sql_dict(db, "get_jd_wym", sql_data)
            jd_wym_dic = {row['id']:row for row in rs_jd_wym}
            # 子流程
            rs_zlc_wym = ModSql.common.execute_sql_dict(db, "get_zlc_wym", sql_data)
            zlc_wym_dic = {row['id']:row for row in rs_zlc_wym}
        
        # 所有的节点/子流程
        locations = {}
        jdlx_dic = {'1': '', '2': 'zlc', '3': 'start_zlc', '4': 'end_zlc', '5': 'start_jy', '6': 'end_jy', '7': ''}
        
        for lcbj in rs_lcbj:
            # 当前节点
            nodeid = lcbj['nodeid']
            if lcbj['jdlx_bj'] == '5':
                nodeid = jbjdid
            elif lcbj['jdlx_bj'] == '6':
                nodeid = dbjdid
            node_lx = '2' if lcbj['iszlc'] == '1' else '1'
            fhz_lst = [ys['bm'] for ys in get_node_ys(db, nodeid, node_lx, '3')] if nodeid else []
            locations[lcbj['id']] = {
                'left': lcbj['x'],
                'top': lcbj['y'],
                'label': lcbj['mc'],
                'type': jdlx_dic.get(lcbj['jdlx_bj'], ''),
                'nodeid': nodeid or '',
                'wym': jd_wym_dic.get(nodeid, {}).get('wym1') or zlc_wym_dic.get(nodeid, {}).get('wym1'),
                'wym_bbk': jd_wym_dic.get(nodeid, {}).get('wym2') or zlc_wym_dic.get(nodeid, {}).get('wym2'),
                'fhz': fhz_lst,
                'czpzid': lcbj['czpzid'] if lcbj['czpzid'] else ''
            }
    
    return [locations, connector]

def jd_del_service(jdids, lcid=None):
    """
    # 节点删除
    # jdids: 节点ID，逗号分隔
    # lcid: 交易ID/子流程ID。（流程编辑时删除节点会传入此参数）
    """
    result = {'state':False, 'msg':''}
    with sjapi.connection() as db:
        sql_data = {'ids': jdids.split(',')}
        # 判断节点是否被交易引用
        rs_jdyy_jy = ModSql.common.execute_sql(db, "get_jdyy_jy", sql_data)
        jyids = {row.jyid for row in rs_jdyy_jy}
        # 判断节点是否被子流程引用
        rs_jdyy_zlc = ModSql.common.execute_sql(db, "get_jdyy_zlc", sql_data)
        zlcids = {row.zlcid for row in rs_jdyy_zlc}
        if (jyids - {lcid}) or (zlcids - {lcid}):
            result['msg'] = '删除失败，节点已被交易或子流程引用'
            return result
        # 查询要删除的节点
        rs_jd = ModSql.common.execute_sql(db, "get_jddy", sql_data)
        # 删除节点和相关信息需要执行的SQL
        sqlid_lst = ['del_zdhcslsb', 'del_jdcsalys', 'del_jdcsalzxbz', 'update_jdcsalzxbz', 'del_csaldy', 'del_lczx', 'del_lcbj', 'del_jdys', 'del_blob_jdnr', 'del_jddy']
        for sqlid in sqlid_lst:
            ModSql.common.execute_sql(db, sqlid, sql_data)
        ModSql.common.execute_sql(db, 'del_blob', {'ssid_lst': sql_data['ids']})
        ModSql.common.execute_sql(db, 'del_bbkz', {'ssid_lst': sql_data['ids']})
        
        # 登记操作日志
        ins_czrz(db, '节点[%s]已被删除' % ', '.join([k.jdmc for k in rs_jd]))
        
        result = {'state':True, 'msg':'删除成功'}
    
    return result

def ins_czrz( db, nr, pt = 'kf', gnmc = None, gndm = None, hydm = None, czsj = None ):
    """
    # 开发平台登记操作日志
    # db: 数据库连接
    # nr: 日志内容
    # hydm: 操作人行员代码（可空，默认是当前登录人）
    # czsj: 操作时间（可空，默认是当前时间）
    """
    hydm = hydm or get_sess_hydm()
    czsj = czsj or get_strftime()
    result = False
    try:
        sql_data = {'id':get_uuid(), 'czpt': pt, 'gndm':gndm, 'gnmc':gnmc, 'czhydm':hydm, 'czsj':czsj, 'szcz':nr[:4000], 'czjg':' '}
        ModSql.common.execute_sql_dict(db, "insert_hyrcywls", sql_data)
        result = True
    except:
        logger.info(traceback.format_exc())
    return result

def str_len(str):
    """
    # 获取字符串数据库中的长度（字节数）
    """
    try:
        return len(str.encode('utf-8'))
    except:
        pass
    return 0

def change_log_msg( log_lst_dic ):
    """
    # 整理查询出的日志列表
        [
            { "lsh" : "853", "sj" : "2015-10-12 16:17:15.411693", "msgxh" : 18, "msg" : "交易打包结束，SYS_YFSDBW", "jdid" : "end", "jyrq" : "20151012", "level" : "info", "kind" : "Transaction" },
            ……
        ]
    """
    log_all = []
    for log_dic in log_lst_dic:
        log_msg = '%s  %s  %s' % ( log_dic.get( 'sj', '' ), log_dic.get( 'level', 'info' ).upper(), log_dic.get('msg',''))
        # 处理交易字典
        log_jyzd = log_dic.get('jyzd', {})
        log_jyzd_lst = []
        if log_jyzd != {}:
            log_msg += ',数据字典内容为：'
            log_msg = log_msg.replace('\n', '')
            log_jyzd_lst.append( "========================================" )
            log_jyzd_lst.append( "<交易 jym=%s , fqsj=%s%s , lsh=%s , jdmc=%s, sbbh=%s >" % (
                                    log_jyzd.get( 'SYS_JYM', '' ), log_jyzd.get( 'SYS_JYRQ', '' ), log_jyzd.get( 'SYS_JYSJ', '' ),
                                    log_jyzd.get( 'SYS_XTLSH', '' ), log_jyzd.get('SYS_JYMC', '未设定'),
                                    log_jyzd.get('CZGY', 'auto'), 
                                ) )
            log_jyzd_lst.append("{")
            for k in sorted( log_jyzd.keys() ):
                jyzd_msg = "%s:%s" % ( k, log_jyzd.get(k,'') )
                jyzd_msg = jyzd_msg.replace( 'SYS_JSDDBW:0000', 'SYS_JSDDBW:\n0000' )
                log_jyzd_lst.append( jyzd_msg )
            log_jyzd_lst.append("}")
            log_jyzd_lst.append( "========================================" )
        log_all.append( log_msg )
        log_all.extend( log_jyzd_lst )
    
    return log_all

def format_log(log_lst):
    """
    # 日志格式化，添加行号
    # log_lst: 日志列表
    # return: 日志字符串
    """
    log_format = []
    num_width = len(str(len(log_lst)))
    for i, log in enumerate(log_lst):
        # 去掉最后一个换行（只去一个）
        if log[-1] == '\n':
            log = log[:len(log)-1]
        for j, line in enumerate(log.split('\n')):
            if j == 0:
                line = str(i + 1).rjust(num_width, ' ') + ' ' + line
            else:
                line = ' ' * (num_width + 1) + line
            log_format.append(line)
    return '\n'.join(log_format)

def get_sjktbxx( ywid ):
    """
    # 获取数据库模型表、数据库字段表、数据表索引表、数据库约束表中的数据信息，与oracle系统中的信息进行表对，将比对结果返回
    # sjbtblx 1 删除 2 修改
    # tblx 1:新增 2：删除 3：修改
    # tbnrlx 1 字段 2 索引 3约束 4数据表
    """
    with sjapi.connection() as db:
        # 查询数据库模型总记录
        count = ModSql.kf_ywgl_011.execute_sql(db, "get_sjkmx_count",{'ywid':ywid})[0].count
        # 若该业务下没有数据库模型，则不进行同步操作
        if count == 0:
            return {'sfxytb':False}
        rs = ModSql.common.execute_sql(db, "get_sjbxx",{'ywid':ywid})
        #  数据表ID、名称字典
        sjb_id_mc_dic = {}
        # 数据表名称、描述字典
        sjb_mc_ms_dic = {}
        for obj in rs:
            sjb_id_mc_dic[obj.id] = obj.sjbmc
            sjb_mc_ms_dic[obj.sjbmc] = obj.sjbmcms
        # 拼接查询时,数据表ID的字符串
        sjb_id_lst = list( sjb_id_mc_dic.keys() )
        # 查询数据库字段表,获取数据表的字段信息
        rs_sjbzd = ModSql.common.execute_sql_dict(db, "get_sjbzdxx",{'sjb_id_lst':sjb_id_lst})
        # 查询数据库索引表,获取数据表的索引信息
        rs_sjbsy = ModSql.common.execute_sql_dict(db, "get_sjbsyxx",{'sjb_id_lst':sjb_id_lst})
        # 查询数据库约束表,获取数据表的约束信息
        rs_sjbys = ModSql.common.execute_sql_dict(db, "get_sjbysxx",{'sjb_id_lst':sjb_id_lst})
        # 拼接查询时,数据表名称的字符串
        sjb_mc_lst = list( sjb_id_mc_dic.values() )
        # 通过oracle系统表查询字段信息
        # 查询数据库字段表,获取数据表的字段信息
        rs_xt_sjbzd = ModSql.common.execute_sql_dict(db, "get_ora_sjbzdxx",{'sjb_mc_lst':sjb_mc_lst})
        # 通过oracle系统表查询索引信息
        rs_xt_sjbsy = ModSql.common.execute_sql_dict(db, "get_ora_sjbsyxx",{'sjb_mc_lst':sjb_mc_lst})
        # 通过oracle系统表查询约束信息
        rs_xt_sjbys = ModSql.common.execute_sql_dict(db, "get_ora_sjbysxx",{'sjb_mc_lst':sjb_mc_lst})
        # 通过oracle系统表查询数据表描述
        rs_xt_sjb = ModSql.common.execute_sql_dict(db, "get_ora_sjbmcms",{'sjb_mc_lst':sjb_mc_lst})
    # 数据表字段信息组织
    sjb_zd_dic = {}
    for dic in rs_sjbzd:
        # 因为是以数据表ID为单位进行数据组织,所有需先判断数据表ID在不在字典中,若不在需添加,若已存在,直接使用
        if dic['sjb_id'] not in sjb_zd_dic.keys():
            sjb_zd_dic[dic['sjb_id']] = {}
        sjb_zd_dic[dic['sjb_id']][dic['zdmc']] = {'id':dic['id'],'zdms':dic['zdms'] or '','zdlx':dic['zdlx'] or '','zdcd':dic['zdcd'] or '','xscd':dic['xscd'] or '','sfkk':dic['sfkk'] or '','iskey':dic['iskey'] or '','mrz':dic['mrz'] or ''}
    # 数据表索引信息组织
    sjb_sy_dic = {}
    for dic in rs_sjbsy:
        # 因为是以数据表ID为单位进行数据组织,所有需先判断数据表ID在不在字典中,若不在需添加,若已存在,直接使用
        if dic['sssjb_id'] not in sjb_sy_dic.keys():
            sjb_sy_dic[dic['sssjb_id']] = {}
        sjb_sy_dic[dic['sssjb_id']][dic['symc']] = { 'id':dic['id'],'syzd':dic['syzd'],'sylx':dic['sylx'],'sfwysy':dic['sfwysy'] }
    # 数据表约束信息组织
    sjb_ys_dic = {}
    for dic in rs_sjbys:
        # 因为是以数据表ID为单位进行数据组织,所有需先判断数据表ID在不在字典中,若不在需添加,若已存在,直接使用
        if dic['sssjb_id'] not in sjb_ys_dic.keys():
            sjb_ys_dic[dic['sssjb_id']] = {}
        sjb_ys_dic[dic['sssjb_id']][dic['ysmc']] = { 'id':dic['id'],'yszd':dic['yszd'] }
    
    # 系统数据表字段信息组织
    xt_sjb_zd_dic = {}
    for dic in rs_xt_sjbzd:
        # 因为是以数据表ID为单位进行数据组织,所有需先判断数据表ID在不在字典中,若不在需添加,若已存在,直接使用
        if dic['sjbmc'] not in xt_sjb_zd_dic.keys():
            xt_sjb_zd_dic[dic['sjbmc']] = {}
        sfkk = '1' if dic['sfkk'] == 'Y' else '0'
        xt_sjb_zd_dic[dic['sjbmc']][dic['zdmc']] = {'zdms':dic['zdms'] or '','zdlx':dic['zdlx'] or '','zdcd':dic['zdcd'] or '','xscd':dic['xscd'] or '','sfkk':sfkk,'iskey':dic['iskey'] or '','mrz':  dic['mrz'].replace("\n",'').replace("'",'').strip() if dic['mrz'] else '' }
    
    # 系统数据表索引信息组织:
    xt_sjb_sy_dic = {}
    for dic in rs_xt_sjbsy:
        # 因为是以数据表ID为单位进行数据组织,所有需先判断数据表ID在不在字典中,若不在需添加,若已存在,直接使用
        if dic['sjbmc'] not in xt_sjb_sy_dic.keys():
            xt_sjb_sy_dic[dic['sjbmc']] = {}
        # 因为在oracle系统中,索引字段是分开的,为与数据库索引表中的索引字段一致,对应oracle系统表中同一索引名称,其索引字段使用"|"进行拼接
        if xt_sjb_sy_dic[dic['sjbmc']].get( dic['symc'],''):
            xt_sjb_sy_dic[dic['sjbmc']][dic['symc']]['syzd'] = xt_sjb_sy_dic[dic['sjbmc']][dic['symc']]['syzd'] + "|" + dic['syzd']
        else:
            xt_sjb_sy_dic[dic['sjbmc']][dic['symc']] = { 'syzd':dic['syzd'] ,'sylx':dic['sylx'],'sfwysy':dic['sfwysy'] }
    
    # 系统数据表约束信息组织:
    xt_sjb_ys_dic = {}
    for dic in rs_xt_sjbys:
        # 因为是以数据表ID为单位进行数据组织,所有需先判断数据表ID在不在字典中,若不在需添加,若已存在,直接使用
        if dic['sjbmc'] not in xt_sjb_ys_dic.keys():
            xt_sjb_ys_dic[dic['sjbmc']] = {}
        # 因为在oracle系统中,索引字段是分开的,为与数据库索引表中的索引字段一致,对应oracle系统表中同一索引名称,其索引字段使用"|"进行拼接
        if xt_sjb_ys_dic[dic['sjbmc']].get( dic['ysmc'],'' ):
            xt_sjb_ys_dic[dic['sjbmc']][dic['ysmc']]['yszd'] = xt_sjb_ys_dic[dic['sjbmc']][dic['ysmc']]['yszd'] + "|" + dic['yszd']
        else:
            xt_sjb_ys_dic[dic['sjbmc']][dic['ysmc']] = { 'yszd':dic['yszd'] }
    # 系统数据表数据表名称描述信息组织;
    xt_sjb_mc_ms = {}
    for dic in rs_xt_sjb:
        xt_sjb_mc_ms[dic['sjbmc']] = dic['sjbmcms']
    # 同步信息{数据表ID:[{sjbtblx:数据表同步类型,sjbmc:数据表名称},{tblx:同步类型,tbnrlx:同步内容类型,tbnrmc:同步内容名称,tbnrsx:同步内容属性,tbqsxz:同步前属性值,tbhsxz:同步后属性值},...,{ tblx:同步类型,tbnrlx:同步内容类型,tbnrmc:同步内容名称,tbnrsx:同步内容属性,tbqsxz:同步前属性值,tbhsxz:同步后属性值}]}
    tbxx_dic = {}
    # 本次同步的表ID[表ID,表ID]
    update_table_id = []
    # 需从数据库模型定义中删除的表信息[表ID,表ID,]
    drop_table = []
    # 需从数据库字段表中删除的表字段 [字段ID,字段ID,...,字段ID]
    drop_table_column = []
    # 需从数据库字段表中更新的字段信息{字段ID:{zdms:字段描述,...,sfzj:是否主键},...}
    update_table_column = {}
    # 需从数据库字段表中增加的表字段{表ID:[{zdmc:字段名称,...,sfzj:是否主键},...],...}
    ins_table_column = {}
    # 需从数据库模型定义中更新表描述的字典{表ID:描述,表ID:描述}
    update_table_ms = {}
    # 需从数据库索引表中删除的索引 [索引ID,索引ID,...,索引ID]
    drop_table_index = []
    # 需插入到数据库索引表中的索引信息 {表ID:[{symc:索引名称,sylx:索引类型,sfwysy:是否唯一索引,syzd:索引字段},...],...}
    ins_table_index = {}
    # 需更新的索引信息 {索引ID:{sylx:索引类型,sfwysy:是否唯一索引,syzd:索引字段},...}
    update_table_index = {}
    # 需从数据库约束表中删除的约束 [约束ID,约束ID,...,约束ID]
    drop_table_unique = []
    # 需插入到数据库约束表中的约束信息 {表ID:[{ysmc:约束名称,...}],...}
    ins_table_unique = {}
    # 需更新的约束信息 {约束ID:{yszd:约束字段},...,约束ID:{yszd:约束字段}}
    update_table_unique = {}
    # 无法识别的字段类型{数据表名称:[字段名称，字段名称]}
    nonsupport_type = {} 
    #数据同步处理逻辑
    for bid,bmc in sjb_id_mc_dic.items():# 循环数据库模型定义
        if bmc not in xt_sjb_zd_dic.keys(): # 若数据库模型中的表在系统中不存在,记录到需删除表列表中
            tbxx_dic[bid] = []
            tbxx_dic[bid].append( { 'sjbtblx':'1','sjbmc':bmc })
            # 获取数据库字段表中该表的字段信息
            pt_zd_dic = sjb_zd_dic.get( bid,{} )
            for zdmc,zdxx in pt_zd_dic.items():
                for key,values in zdxx.items():
                    tbxx_dic[bid].append( {'tblx':'2','tbnrlx':'1','tbnrmc':zdmc,'tbnrsx':key,'tbqsxz':values,'tbhsxz':''} )
            # 获取系统中表的描述
            pt_bms = sjb_mc_ms_dic.get( bmc,{} )
            tbxx_dic[bid].append( {'tblx':'2','tbnrlx':'4','tbnrmc':'sjbms','tbnrsx':'sjbmcms','tbqsxz':pt_bms,'tbhsxz':''} )
            # 获取数据库索引表中该表的索引信息
            pt_sy_dic = sjb_sy_dic.get( bid,{} )
            for symc,syxx in pt_sy_dic.items():
                for key,values in syxx.items():
                    tbxx_dic[bid].append( {'tblx':'2','tbnrlx':'2','tbnrmc':symc,'tbnrsx':key,'tbqsxz':values,'tbhsxz':''} )
            # 获取数据库约束表中该表的约束信息
            pt_ys_dic = sjb_ys_dic.get( bid,{} )
            for ysmc,ysxx in pt_ys_dic.items():
                for key,values in ysxx.items():
                    tbxx_dic[bid].append( {'tblx':'2','tbnrlx':'3','tbnrmc':ysmc,'tbnrsx':key,'tbqsxz':values,'tbhsxz':''} )
            drop_table.append( bid )
            continue
        
        #1.字段信息同步
        # 获取系统中该表的字段信息
        xt_zd_dic = xt_sjb_zd_dic.get( bmc,{} )
        # 获取数据库字段表中该表的字段信息
        pt_zd_dic = sjb_zd_dic.get( bid,{} )
        # 循环系统的字段信息,若字段名称在数据库字段表中不存在,需从数据库字段表中新增
        for zdmc,zdxx in xt_zd_dic.items():
            if zdmc not in pt_zd_dic.keys():
                if zdxx['zdlx'] not in ZDLX_DIC.keys():
                    if bmc not in nonsupport_type.keys():
                        nonsupport_type[bmc] = [zdmc+","+zdxx['zdlx']]
                    else:
                        nonsupport_type[bmc].append(zdmc+","+zdxx['zdlx'])
                    continue
                zdxx['zdmc'] = zdmc
                if bid not in ins_table_column.keys():
                    ins_table_column[bid] = []
                ins_table_column[bid].append( zdxx )
                if bid not in update_table_id:
                    update_table_id.append( bid )
                if bid not in tbxx_dic.keys():
                    tbxx_dic[bid] = [{'sjbtblx':'2','sjbmc':bmc }]
                for key,values in zdxx.items():
                    tbxx_dic[bid].append( {'tblx':'1','tbnrlx':'1','tbnrmc':zdmc,'tbnrsx':key,'tbqsxz':'','tbhsxz':values} )
            else:
                # 获取数据库字段表中该字段的信息
                pt_zdxx_dic = pt_zd_dic.get( zdmc,{} )
                # 用来判断字段有没有变更,若有一个属性变更了,就需要登记至数据库同步信息表
                ischange = False
                # 循环系统中该字段的信息,与数据库表字段中的信息进行比较,若不一致,登记至需从数据库字段表中更新的字段信息字典中
                for zdxxkey,zdxxvalue in zdxx.items():
                    # id不需要比较
                    if zdxxkey == 'id':
                        continue
                    if zdxxvalue != pt_zdxx_dic.get( zdxxkey ):
                        if zdxx['zdlx'] not in ZDLX_DIC.keys():
                            if bmc not in nonsupport_type.keys():
                                nonsupport_type[bmc] = [zdmc+","+zdxx['zdlx']]
                            else:
                                nonsupport_type[bmc].append(zdmc+","+zdxx['zdlx'])
                            continue
                        ischange = True
                        if pt_zdxx_dic.get('id') not in update_table_column.keys():
                            update_table_column[pt_zdxx_dic.get('id')] = {}
                        update_table_column[pt_zdxx_dic.get('id')][zdxxkey] = zdxxvalue
                        if bid not in update_table_id:
                            update_table_id.append( bid )
                if ischange:
                    if bid not in tbxx_dic.keys():
                        tbxx_dic[bid] = [{'sjbtblx':'2','sjbmc':bmc }]
                    for key,values in zdxx.items():
                        zdxxvalue = pt_zdxx_dic.get( key )
                        tbxx_dic[bid].append( {'tblx':'3','tbnrlx':'1','tbnrmc':zdmc,'tbnrsx':key,'tbqsxz':zdxxvalue,'tbhsxz':values} )
        # 循环数据库字段表中的字段信息,若字段名称在系统字段信息中不存在,需从数据库字段表中删除:
        for zdmc,zdxx in pt_zd_dic.items():
            if zdmc not in xt_zd_dic.keys():
                drop_table_column.append( zdxx.get('id') )
                if bid not in update_table_id:
                    update_table_id.append( bid )
                if bid not in tbxx_dic.keys():
                    tbxx_dic[bid] = [{'sjbtblx':'2','sjbmc':bmc }]
                for key,values in zdxx.items():
                    tbxx_dic[bid].append( {'tblx':'2','tbnrlx':'1','tbnrmc':zdmc,'tbnrsx':key,'tbqsxz':values,'tbhsxz':''} )
        
        #2.表名称描述同步
        # 获取数据库模型定义中的表描述
        pt_bms = sjb_mc_ms_dic.get( bmc,{} )
        # 获取系统中表的描述
        xt_bms = xt_sjb_mc_ms.get( bmc,{} )
        # 若数据库模型定义中的描述与系统中的描述不一致,需更新
        if pt_bms != xt_bms:
            update_table_ms[bid] = xt_bms
            if bid not in update_table_id:
                update_table_id.append( bid )
            if bid not in tbxx_dic.keys():
                tbxx_dic[bid] = [{'sjbtblx':'2','sjbmc':bmc }]
            tbxx_dic[bid].append( {'tblx':'3','tbnrlx':'4','tbnrmc':bmc,'tbnrsx':'sjbms','tbqsxz':pt_bms,'tbhsxz':xt_bms} )
        #3.索引同步
        # 获取系统中该表的索引信息
        xt_sy_dic = xt_sjb_sy_dic.get( bmc,{} )
        # 获取数据库索引表中该表的索引信息
        pt_sy_dic = sjb_sy_dic.get( bid,{} )
        for symc,syxx in xt_sy_dic.items():
            # 循环系统的索引信息,若索引名称在数据库索引表中不存在,需从数据库索引表中新增
            if symc not in pt_sy_dic.keys():
                syxx['symc'] = symc
                if bid not in ins_table_index.keys():
                    ins_table_index[bid] = []
                ins_table_index[bid].append( syxx )
                if bid not in update_table_id:
                    update_table_id.append( bid )
                if bid not in tbxx_dic.keys():
                    tbxx_dic[bid] = [{'sjbtblx':'2','sjbmc':bmc }]
                for key,values in syxx.items():
                    tbxx_dic[bid].append( {'tblx':'1','tbnrlx':'2','tbnrmc':symc,'tbnrsx':key,'tbqsxz':'','tbhsxz':values} )
            else:
                # 获取数据库索引表中该索引的信息
                pt_syxx_dic = pt_sy_dic.get( symc,{} )
                # 用来判断索引有没有变更,若有一个属性变更了,就需要登记至数据库同步信息表
                ischange = False
                # 循环系统中该索引的信息,与数据库表索引表中的信息进行比较,若不一致,登记至需从数据库索引表中更新的索引信息字典中
                for syxxkey,syxxvalue in syxx.items():
                    # id不需要比较
                    if syxxkey == 'id':
                        continue
                    if syxxvalue != pt_syxx_dic.get( syxxkey ):
                        ischange = True
                        if pt_syxx_dic.get('id') not in update_table_index.keys():
                            update_table_index[pt_syxx_dic.get('id')] = {}
                        update_table_index[pt_syxx_dic.get('id')][syxxkey] =  syxxvalue
                        if bid not in update_table_id:
                            update_table_id.append( bid )
                if ischange:
                    if bid not in tbxx_dic.keys():
                        tbxx_dic[bid] = [{'sjbtblx':'2','sjbmc':bmc }]
                    for key,values in syxx.items():
                        # 获取数据库模型表中该属性的值
                        syxxvalue = pt_syxx_dic.get( key )
                        tbxx_dic[bid].append( {'tblx':'3','tbnrlx':'2','tbnrmc':symc,'tbnrsx':key,'tbqsxz':syxxvalue,'tbhsxz':values} )
        # 循环数据库索引表中的索引信息,若索引名称在系统索引信息中不存在,需从数据库索引表中删除:
        for symc,syxx in pt_sy_dic.items():
            if symc not in xt_sy_dic.keys():
                drop_table_index.append( syxx.get('id') )
                if bid not in update_table_id:
                    update_table_id.append( bid )
                if bid not in tbxx_dic.keys():
                    tbxx_dic[bid] = [{'sjbtblx':'2','sjbmc':bmc }]
                for key,values in syxx.items():
                    tbxx_dic[bid].append( {'tblx':'2','tbnrlx':'2','tbnrmc':symc,'tbnrsx':key,'tbqsxz':values,'tbhsxz':''} )
        #4.约束同步
        # 获取系统中该表的约束信息
        xt_ys_dic = xt_sjb_ys_dic.get( bmc,{} )
        # 获取数据库约束表中该表的约束信息
        pt_ys_dic = sjb_ys_dic.get( bid,{} )
        for ysmc,ysxx in xt_ys_dic.items():
            # 循环系统的约束信息,若约束名称在数据库约束表中不存在,需从数据库约束表中新增
            if ysmc not in pt_ys_dic.keys():
                ysxx['ysmc'] = ysmc
                if bid not in ins_table_unique.keys():
                    ins_table_unique[bid] = []
                ins_table_unique[bid].append( ysxx )
                if bid not in update_table_id:
                    update_table_id.append( bid )
                if bid not in tbxx_dic.keys():
                    tbxx_dic[bid] = [{'sjbtblx':'2','sjbmc':bmc }]
                for key,values in ysxx.items():
                    tbxx_dic[bid].append( {'tblx':'1','tbnrlx':'3','tbnrmc':ysmc,'tbnrsx':key,'tbqsxz':'','tbhsxz':values} )
            else:
                # 获取数据库约束表中该约束的信息
                pt_ysxx_dic = pt_ys_dic.get( ysmc,{} )
                # 用来判断约束有没有变更,若有一个属性变更了,就需要登记至数据库同步信息表
                ischange = False
                # 循环系统中该约束的信息,与数据库表约束表中的信息进行比较,若不一致,登记至需从数据库约束表中更新的约束信息字典中
                for ysxxkey,ysxxvalue in ysxx.items():
                    # id不需要比较
                    if ysxxkey == 'id':
                        continue
                    if ysxxvalue != pt_ysxx_dic.get( ysxxkey ):
                        if pt_ysxx_dic.get('id') not in update_table_unique.keys():
                            update_table_unique[pt_ysxx_dic.get('id')] = {}
                        update_table_unique[pt_ysxx_dic.get('id')][ysxxkey] = ysxxvalue
                        if bid not in update_table_id:
                            update_table_id.append( bid )
                        ischange = True
                    if ischange:
                        if bid not in tbxx_dic.keys():
                            tbxx_dic[bid] = [{'sjbtblx':'2','sjbmc':bmc }]
                        for key,values in ysxx.items():
                            # 获取数据库模型表中该属性的值
                            ysxxvalue = pt_ysxx_dic.get( key )
                            tbxx_dic[bid].append( {'tblx':'3','tbnrlx':'3','tbnrmc':ysmc,'tbnrsx':key,'tbqsxz':ysxxvalue,'tbhsxz':values} )
        # 循环数据库约束表中的约束信息,若约束名称在系统约束信息中不存在,需从数据库约束表中删除:
        for ysmc,ysxx in pt_ys_dic.items():
            if ysmc not in xt_ys_dic.keys():
                drop_table_unique.append( ysxx.get('id') )
                if bid not in update_table_id:
                    update_table_id.append( bid )
                if bid not in tbxx_dic.keys():
                    tbxx_dic[bid] = [{'sjbtblx':'2','sjbmc':bmc }]
                for key,values in ysxx.items():
                    tbxx_dic[bid].append( {'tblx':'2','tbnrlx':'3','tbnrmc':ysmc,'tbnrsx':key,'tbqsxz':values,'tbhsxz':''} )
    sjktbxx_dic = {}
    # 有更新或者删除的表ID,说明需要同步
    if update_table_id or drop_table or nonsupport_type:
        sjktbxx_dic = { 'sfxytb':True }
    else:
        sjktbxx_dic = { 'sfxytb':False }
    sjktbxx_dic['tbxx_dic'] = tbxx_dic
    sjktbxx_dic['update_table_id'] = update_table_id
    sjktbxx_dic['drop_table'] = drop_table
    sjktbxx_dic['drop_table_column'] =  drop_table_column
    sjktbxx_dic['update_table_column'] = update_table_column
    sjktbxx_dic['ins_table_column'] = ins_table_column
    sjktbxx_dic['update_table_ms'] = update_table_ms
    sjktbxx_dic['drop_table_index'] = drop_table_index
    sjktbxx_dic['ins_table_index'] = ins_table_index
    sjktbxx_dic['update_table_index'] = update_table_index
    sjktbxx_dic['drop_table_unique'] = drop_table_unique
    sjktbxx_dic['ins_table_unique'] = ins_table_unique
    sjktbxx_dic['update_table_unique'] = update_table_unique
    sjktbxx_dic['sjb_id_mc_dic'] = sjb_id_mc_dic
    sjktbxx_dic['sjb_mc_ms_dic'] = sjb_mc_ms_dic
    sjktbxx_dic['nonsupport_type'] = nonsupport_type
    return sjktbxx_dic

def xml_out(db, lx, id, lsb=False):
    """
    # 生成流程XML
    # db: 数据库连接
    # lx: 类型('lc'交易, 'zlc'子流程)
    # id: 交易ID/子流程ID
    # lsb: 临时表（标明是否查询'_ls'结尾的临时表，在导入对比时会用到）
    # 
    # return: 生成的流程XML字符串，生成失败时返回'Error'
    """
    # 需要关联的字段
    zd = 'sszlcid' if lx=='zlc' else 'ssjyid'
    sqlid_sub = '_lsb' if lsb else ''
    xml = "Error"
    try:
        sql_data = {'id': id}
        # 查询交易/子流程名称
        if lx == 'zlc':
            rs_zlc = ModSql.common.execute_sql(db, "get_zlcdy" + sqlid_sub, sql_data)
            lcmc = rs_zlc[0].mc if rs_zlc else ''
        else:
            rs_jy = ModSql.common.execute_sql(db, "get_jydy" + sqlid_sub, sql_data)
            lcmc = rs_jy[0].jymc if rs_jy else ''
        
        # 查询节点/子流程名称、x坐标、y坐标、节点类型、filename和functionname
        sql_data = {'id': id, 'zd': [zd]}
        rs_lcbj = ModSql.common.execute_sql_dict(db, "get_lcbj_for_xml" + sqlid_sub, sql_data)
        # 流程走向
        sql_data = {'ssid': id}
        connector = ModSql.common.execute_sql_dict(db, "get_lczx_for_xml" + sqlid_sub, sql_data)
        # 查询流程中节点/子流程的要素
        rs_jdys = []
        for row in rs_lcbj:
            node_lx = '2' if row['iszlc'] == '1' else '1'
            # 获取输入、输出、返回值
            for ys_lx in ('1', '2', '3'):
                ys_lst = get_node_ys(db, row['nodeid'], node_lx, ys_lx)
                for ys in ys_lst:
                    ys['jddyid'] = row['nodeid']
                rs_jdys.extend(ys_lst)
        
        if lx == 'lc' and rs_jy:
            # 处理交易解包节点、打包节点
            # 找到流程开始和流程结束的布局ID
            start_bjid = ''
            end_bjid = ''
            for row in rs_lcbj:
                if row['jdlx_jd'] in ('3', '10'):
                    start_bjid = row['id']
                elif row['jdlx_jd'] in ('4', '11'):
                    end_bjid = row['id']
            # 把交易解包节点、打包节点分别放到流程走向的“开始”之后和“结束”之前
            connector_for = connector[:]
            for row in connector_for:
                if rs_jy[0].jbjdid and row['source'] == start_bjid:
                    target = row['target']
                    row['target'] = 'bjid_jbjd'
                    connector.append({'source': 'bjid_jbjd', 'target': target, 'value': ''})
                if rs_jy[0].dbjdid and row['target'] == end_bjid:
                    row['target'] = 'bjid_dbjd'
            connector.append({'source': 'bjid_dbjd', 'target': end_bjid, 'value': ''})
            # 查询打解包节点信息
            sql_data = {'ids': [rs_jy[0].jbjdid, rs_jy[0].dbjdid]}
            rs_djb_jbxx = ModSql.common.execute_sql_dict(db, "get_jddy" + sqlid_sub, sql_data)
            rs_djb_jbxx_dic = {k['id']:k for k in rs_djb_jbxx}
            
            # 将打解包节点信息添加到布局中
            if rs_jy[0].jbjdid:
                rs_lcbj.insert(2, {
                    'id': 'bjid_jbjd',
                    'x': '0',
                    'y': '0',
                    'nodeid': rs_jy[0].jbjdid,
                    'bm': rs_djb_jbxx_dic.get(rs_jy[0].jbjdid, {}).get('bm', ''),
                    'mc': rs_djb_jbxx_dic.get(rs_jy[0].jbjdid, {}).get('jdmc', ''),
                    'jdlx_bj': '',
                    'jdlx_jd': '9',
                    'filename': '',
                    'functionname': '',
                    'type': '',
                    'iszlc': '0'
                })
                rs_jbjdys = ModSql.common.execute_sql_dict(db, "get_jdys" + sqlid_sub, {'id': rs_jy[0].jbjdid})
                if rs_jbjdys:
                    rs_jdys.extend(rs_jbjdys)
            if rs_jy[0].dbjdid:
                rs_lcbj.insert(3, {
                    'id': 'bjid_dbjd',
                    'x': '0',
                    'y': '0',
                    'nodeid': rs_jy[0].dbjdid,
                    'bm': rs_djb_jbxx_dic.get(rs_jy[0].dbjdid, {}).get('bm', ''),
                    'mc': rs_djb_jbxx_dic.get(rs_jy[0].dbjdid, {}).get('jdmc', ''),
                    'jdlx_bj': '',
                    'jdlx_jd': '8',
                    'filename': '',
                    'functionname': '',
                    'type': '',
                    'iszlc': '0'
                })
                rs_dbjdys = ModSql.common.execute_sql_dict(db, "get_jdys" + sqlid_sub, {'id': rs_jy[0].dbjdid})
                if rs_dbjdys:
                    rs_jdys.extend(rs_dbjdys)
        lcbj_dic = {k['id']:k for k in rs_lcbj}
        
        # 所有的节点/子流程
        nodes = []
        for lcbj in rs_lcbj:
            # 当前节点的返回值
            next = []
            for conn in filter(lambda x:x['source']==lcbj['id'], connector):
                next.append({
                    '@value': conn['value'] or '', 
                    '@identifier': lcbj_dic[conn['target']]['bm'] or '',
                    '@g': '-11,-17' if lcbj['jdlx_bj'] in ('3', '5') else '6,-16'
                })
            
            # 当前节点
            node = {
                # 加@符号的作为属性
                '@desc': lcbj['mc'] or '',
                '@nodeid': lcbj['bm'] or '',
                '@identifier': lcbj['bm'] or '',
                '@g': '(%s,%s,48,48)' % (lcbj['x'], lcbj['y']),
                '@czpzbm': lcbj.get('czpzbm') if lcbj.get('czpzbm') else '',
                'return': {'next': next} if next else {}
            }
            
            # 输入要素
            input = [{'@name': '', '@origin': "allparam", '@value': ''}]
            for jdys in rs_jdys:
                if jdys['lb']=='1' and jdys['jddyid']==lcbj['nodeid'] and jdys['bm'] not in [k['@name'] for k in input]:
                    input.append({'@name': jdys['bm'], '@origin': "literal", '@value': jdys['mrz'] or ''})
            
            # 输出要素
            output = [{'@name': '', '@origin': "allparam", '@value': ''}]
            for jdys in rs_jdys:
                if jdys['lb']=='2' and jdys['jddyid']==lcbj['nodeid'] and jdys['bm'] not in [k['@name'] for k in output]:
                    output.append({'@name': jdys['bm'], '@origin': "literal", '@value': jdys['mrz'] or ''})
            
            # 如果不是开始、结束节点，添加'function'
            if lcbj['jdlx_bj'] not in ('3', '4', '5', '6'):
                node.update({
                    'function': {
                        '@filename': lcbj['filename'] or '',
                        '@functionname': lcbj['functionname'] or '',
                        '@type': 'flow' if lcbj['iszlc']=='1' else (lcbj['type'] or ''),
                        'input': {'arg': input},
                        'output': {'arg': output},
                    }
                })
            nodes.append(node)
        
        # 组织成dict结构
        xml_dic = {
            'flow': {
                "@description": lcmc,
                "node": nodes
            }
        }
        # dict结构转换为xml结构
        xml = xmltodict.unparse(xml_dic, encoding='utf-8', short_empty_elements=True, pretty=True, indent='    ')
    except:
        logger.info(traceback.format_exc())
    
    return xml

def get_node_ys(db, nodeid, node_lx, ys_lx):
    """
    # 获取节点或子流程的输入要素、输出要素、返回值
    # 【节点】
    # 输入要素：节点的输入要素。
    # 输出要素：节点的输出要素。
    # 返回值：节点的输出要素。
    # 【通讯子流程】
    # 输入要素：子流程中打包节点的输入要素。
    # 输出要素：子流程中所有节点的输出要素。
    # 返回值：子流程中后置为结束的连线的值。
    # 【普通子流程】
    # 输入要素：子流程第一个节点（前置为开始节点的节点）的输入要素。
    # 输出要素：子流程中所有节点的输出要素。
    # 返回值：子流程中后置为结束的连线的值。
    # 【注意】：如果是子流程，其下的节点可能会有相同的要素，返回时未做去重（因为备注可能不同，无法去重）
    # db: 数据库连接
    # node_lx: 节点/子流程（'1'节点，'2'子流程）
    # ys_lx: 要获取的类型（'1'输入要素，'2'输出要素，'3'返回值）
    """
    if node_lx == '2':
        if ys_lx in ('1', '2'):
            if ys_lx == '1':
                # 查询子流程类别（1通讯子流程 2普通子流程）
                rs = ModSql.common.execute_sql(db, 'get_zlcdy', {'id': nodeid})
                lb = rs[0].lb if rs else None
                if lb == '1':
                    # 如果是通讯子流程，取通讯子流程中的打包节点
                    sql_id = 'get_dbjd_in_zlc'
                elif lb == '2':
                    # 如果是普通子流程，取子流程第一个节点（前置为开始节点的节点）
                    sql_id = 'get_first_jd'
                else:
                    return []
            else:
                sql_id = 'get_all_jd'
            jdids = set()
            zlcids = set()
            zlcids_t = set([nodeid])
            while True:
                # 查询子流程中的节点/子流程
                rs = ModSql.common.execute_sql(db, sql_id, {'zlcids': zlcids_t-zlcids})
                # 目前所有的节点
                jdids = jdids | {row.jddyid for row in rs if row.jdlx=='1'}
                # 目前所有的子流程
                zlcids = zlcids | zlcids_t
                # 当前查询出的子流程
                zlcids_t = {row.jddyid for row in rs if row.jdlx=='2'}
                # 如果没有新查出的子流程，则跳出
                if not zlcids_t - zlcids:
                    break
            jdids = list(jdids)
        else:
            rs = ModSql.common.execute_sql(db, 'get_last_fhz', {'zlcids': [nodeid]})
            return [{'bm': row.fhz, 'lb': '3'} for row in rs]
    else:
        jdids = [nodeid]
    # 查询要素
    sql_data = {'ids': jdids, 'lb': ys_lx}
    rs = ModSql.common.execute_sql_dict(db, "get_jdys_new", sql_data) if jdids else []
    return sorted(rs, key=lambda x:x['bm'])

def get_dbname( lx ):
    """
    # 根据交易的类型代码返回对应的表名
    # lx: 提交内容的类型：交易jy，子流程zlc，节点jd，公共函数gghs，数据库模型sjk
    # 
    # return 类型对应的表名
    """
    dbkey = {'jy': 'gl_jydy', 'zlc': 'gl_zlcdy', 'jd': 'gl_jddy', 'gghs': 'gl_yw_gghs', 'sjk': 'gl_sjkmxdy'}
    return dbkey[lx]

def check_bbwym( db, lx, id ):
    """
    # 查询当前类型对应的表的唯一码进行比较，来判断是否有需要提交的内容
    # lx: 提交内容的类型：交易jy，子流程zlc，节点jd，公共函数gghs，数据库模型sjk
    # id: 提交内容的id
    # 
    # return 返回值的结构体为：{'state':False, 'bbh':0} state:True（唯一码相同）或者False（唯一码不同）
    """
    # 返回对象
    resultobj = {'state':False, 'bbh':0}
    # 获取表名
    dbname = get_dbname(lx)
    sql = """
        select wym from %(dbname)s where id = '%(id)s'
    """ % {'dbname':dbname, 'id':id}
    # 获取当前类型的数据库表中的唯一码
    dbwymset = ModSql.kf_ywgl_023.execute_sql( db,"get_wym",{"tname":[dbname],'id':id})[0]
    # 获取版本库的唯一码
    bbkwymset = ModSql.kf_ywgl_023.execute_sql( db,"get_bbk_wym",{"lx":lx,'id':id})
    if bbkwymset:
        bbkwymset = bbkwymset[0]
        # 当前提交版本表的唯一码和版本库唯一码进行比对，如果一样返回True
        if bbkwymset.wym == dbwymset.wym:
            resultobj['state'] = True
            resultobj['bbh'] = bbkwymset.bbh
        else:
            # 否则新版本号为原版本号+1
            resultobj['bbh'] = bbkwymset.bbh + 1
            resultobj['wym'] = dbwymset.wym
    else:
        # 若版本控制表查询结果为空，则新版本号为1
        resultobj['bbh'] = 1
        resultobj['wym'] = dbwymset.wym
    return resultobj

def get_bcxx( db, lx, id ):
    """
    # 获取版本提交的 版本号，版本内容，唯一码以及该方法执行的状态（True , False）
    # lx: 提交内容的类型：交易jy，子流程zlc，节点jd，公共函数gghs，数据库模型sjk
    # id: 提交内容的id
    # 
    # return 返回值的结构体：（“成功或失败”，新版本号，版本内容，唯一码）
    """
    # 返回对象
    resultobj = {'state':False, 'bbh':0, 'bbnr':'', 'wym':''}
    # 查询当前类型对应的表的唯一码进行比较，来判断是否有需要提交的内容
    checkre = check_bbwym(db, lx, id)
    # 如果唯一码不相同，说明有内容需要提交
    if checkre['state'] == False:
        resultobj['wym'] = checkre['wym']
    resultobj['state'] = checkre['state']
    resultobj['bbh'] = checkre['bbh']
    # 返回内容
    content = {}
    #将版本信息插入到版本信息表和BLOB管理表
    if lx == 'jy':
        # 查询交易信息
        jydy_result = ModSql.kf_ywgl_023.execute_sql_dict(db,"get_jyxx",{'id':id})
        # 查询此交易的流程布局
        lcbj_result = ModSql.kf_ywgl_023.execute_sql_dict(db,"get_lcbj",{'cxtj':[('ssjyid',id)]})
        # 查询此交易的流程走向
        lczx_result = ModSql.kf_ywgl_023.execute_sql_dict(db,"get_lczx",{'sslb':'1','ssid':id})
        # 组织保存内容
        content = {
            'DATA':xml_out(db, 'lc', id),
            'gl_lcbj':lcbj_result,
            'gl_lczx':lczx_result,
            'gl_jydy':jydy_result
        }
    elif lx == 'zlc':
        # 查询子流程定义表
        zlcdy_result = ModSql.kf_ywgl_023.execute_sql_dict(db,"get_zlcxx",{'id':id})
        # 查询此子流程的流程布局
        lcbj_result = ModSql.kf_ywgl_023.execute_sql_dict(db,"get_lcbj",{'cxtj':[('sszlcid',id)]})
        # 查询此子流程的流程走向
        lczx_result = ModSql.kf_ywgl_023.execute_sql_dict(db,"get_lczx",{'sslb':'2','ssid':id})
        # 组织保存内容
        content = {
            'DATA':xml_out(db, lx, id),
            'gl_lcbj':lcbj_result,
            'gl_lczx':lczx_result,
            'gl_zlcdy':zlcdy_result
        }
    elif lx == 'jd':
        # 查询BLOB表信息
        blob_result = ModSql.kf_ywgl_023.execute_sql(db,"get_jdnr",{'id':id})[0]
        # 查询节点要素信息
        jdys_result = ModSql.kf_ywgl_023.execute_sql_dict(db,"get_jdys",{'id':id})
        # 查询节点定义表信息
        jddy_result = ModSql.kf_ywgl_023.execute_sql_dict(db,"get_jdxx",{'id':id})
        if blob_result.nr == None:
            nr = ''
        else:
            nr = pickle.loads(blob_result.nr.read())
        # 组织保存内容
        content = {
            'DATA':nr,
            'gl_jdys':jdys_result,
            'gl_jddy':jddy_result
        }
    elif lx == 'gghs':
        # 查询业务公共函数表
        gghs_result = ModSql.kf_ywgl_023.execute_sql_dict(db,"get_gghs",{'id':id})
        # 查询BLOB表信息
        blob_result = ModSql.kf_ywgl_023.execute_sql(db,"get_gghs_nr",{'id':id})[0]
        if blob_result.nr == None:
            nr = ''
        else:
            nr = pickle.loads(blob_result.nr.read())
        # 组织保存内容
        content = {
            'DATA':nr,
            'gl_yw_gghs':gghs_result
        }
    elif lx == 'sjk':    
        # 查询数据库模型定义表
        sjkmx_result = ModSql.common.execute_sql_dict(db,"get_sjkmxdy",{'id':id})
        # 查询数据库字段表
        sjkzdb_result = ModSql.common.execute_sql_dict(db,"get_sjkzdb",{'id':id})
        # 查询数据库索引表
        sjksy_result = ModSql.common.execute_sql_dict(db,"get_sjksy",{'id':id})
        # 查询数据库约束
        sjkys_result = ModSql.common.execute_sql_dict(db,"get_sjkys",{'id':id})
        # 组织保存内容
        content = {
            'gl_sjkmxdy':sjkmx_result,
            'gl_sjkzdb':sjkzdb_result,
            'gl_sjksy':sjksy_result,
            'gl_sjkys':sjkys_result
        }
    resultobj['bbnr'] = content
    return resultobj

def get_file(fpath,*endstring):
    """
    # 函数说明：获取指定目录下指定后缀的文件列表
    # endstring: 限定文件后缀集合，如果不存在则反馈目录下所有文件
    """
    # 符合条件的文件列表
    ret_file_lst = []
    # 指定目录下文件集合
    file_lst = os.listdir(fpath)
    # 遍历文件集合取出符合规则的文件
    for fname in file_lst:
        # 是文件进入下面的判断
        if os.path.isfile( os.path.join( fpath, fname ) ):
            if endstring:
                if endWith(fname,endstring):
                    ret_file_lst.append(fname)
            else:
                ret_file_lst.append(fname)
    
    return sorted( ret_file_lst )

def endWith(s, *endstring):
    """
    # 校验文件后缀是否是指定后缀
    """
    array = map(s.endswith, endstring)
    return (True in array)

def get_hy_byjsdm( jsdm ):
    """
    # 根据角色代码获取行员信息
    """
    hyxx_lst = []
    with sjapi.connection() as db:
        hyxx_lst = ModSql.common.execute_sql_dict(db,"get_hy_byjsdm",{'jsdm':jsdm})
    
    return hyxx_lst
    
def get_hy_byjsdm_sq( param ):
    """
    # 获取当前登录部门下的复核人
    """
    hyxx_lst = []
    with sjapi.connection() as db:
        hyxx_lst = ModSql.common.execute_sql_dict(db,"get_hy_byjsdm_sq",param)
    
    return hyxx_lst
    
def check_fhr( db, hyxx_dic ):
    """
    # 验证复核人是否正确
    # @params： hyxx_dic： 行员信息字典 { 'hydm': hydm, 'mm': mm, 'jsdm': jsdm }
    """
    # 返回值，默认不正确
    ret = False
    msg = "授权人密码错误，请重新录入"
    # 验证当前登录人和授权人是否是同一人
    # 获取当前登录人的行员代码
    if get_sess('hydm') == hyxx_dic.get('hydm'):
        return False, "登录人和授权人不可相同"
    hyxx_dic['md5mm'] = cal_md5(hyxx_dic['mm'])
    hyxx_lst = ModSql.common.execute_sql_dict(db,"check_hyxx_bymm2jsdm",hyxx_dic)
    if hyxx_lst:
        ret = True
        # 写授权流水表
        data_dic = { 'id': get_uuid(), 'sq_gnmc': hyxx_dic.get( 'sq_gnmc', '' ),
        'sqr': hyxx_dic['hydm'], 'sqsj': get_strftime(), 'czpt': hyxx_dic.get( 'czpt', 'kf' ),
        'sqgndm': hyxx_dic.get( 'sqgndm', '' ), 'szcz': hyxx_dic.get( 'szcz', '' )}
        ModSql.common.execute_sql(db,"insert_gl_sqls",data_dic)
    
    return ret,msg

def date_imp_exp_check( ywid,lx,txid ):
    """
    # 导入、导出校验
    """
    with sjapi.connection() as db:
        if lx == 'yw':
            result = ywdc_jy( db,ywid )
        elif lx == 'jy':
            result = jydc_jy( db ,ywid )
        elif lx == 'tx':
            result = txdc_jy( db,txid )
        return result
        
def jydc_jy( db,ywid ):
    """
    #交易导出时，校验本地是否存在未提交数据
    #ywid:业务ID
    """
    # 查询修改后未提交的交易流程
    count = ModSql.common.execute_sql( db,"get_edit",{'cxtj':[('a.ssywid',ywid)],'lx':'jy','tname':['gl_jydy']})[0].count
    if count != 0:
        return True
    # 查询新增后未提交的交易流程
    count = ModSql.common.execute_sql( db,"get_add",{'cxtj':[('a.ssywid',ywid)],'lx':'jy','tname':['gl_jydy']})[0].count
    if count != 0:
        return True
    # 查询修改后未提交的子流程
    count = ModSql.common.execute_sql( db,"get_edit",{'cxtj':[('a.ssywid',ywid)],'lx':'zlc','tname':['gl_zlcdy']})[0].count
    if count != 0:
        return True
    # 查询新增后未提交的子流程
    count = ModSql.common.execute_sql( db,"get_add",{'cxtj':[('a.ssywid',ywid)],'lx':'zlc','tname':['gl_zlcdy']})[0].count
    if count != 0:
        return True
    # 查询修改后未提交的交易节点
    count = ModSql.common.execute_sql( db,"get_edit_jd",{'ywid':ywid,'tname':['gl_jydy'],'fieldname':['c.ssjyid']})[0].count
    if count != 0:
        return True
    # 查询新增后未提交的交易节点
    count = ModSql.common.execute_sql( db,"get_add_jd",{'ywid':ywid,'tname':['gl_jydy'],'fieldname':['c.ssjyid']})[0].count
    if count != 0:
        return True
    # 查询修改后未提交的子流程节点
    count = ModSql.common.execute_sql( db,"get_edit_jd",{'ywid':ywid,'tname':['gl_zlcdy'],'fieldname':['c.sszlcid']})[0].count
    if count != 0:
        return True
    # 查询新增后未提交的子流程节点
    count = ModSql.common.execute_sql( db,"get_add_jd",{'ywid':ywid,'tname':['gl_zlcdy'],'fieldname':['c.sszlcid']})[0].count
    if count != 0:
        return True
    # 查询修改后未提交的交易打包节点
    count = ModSql.common.execute_sql( db,"get_edit_jyjd",{'ywid':ywid,'field':['b.dbjdid']})[0].count
    if count != 0:
        return True
    # 查询新增后未提交的交易打包节点
    count = ModSql.common.execute_sql( db,"get_add_jyjd",{'ywid':ywid,'field':['b.dbjdid']})[0].count
    if count != 0:
        return True
    # 查询修改后未提交的交易解包节点
    count = ModSql.common.execute_sql( db,"get_edit_jyjd",{'ywid':ywid,'field':['b.jbjdid']})[0].count
    if count != 0:
        return True
    # 查询新增后未提交的交易解包节点
    count = ModSql.common.execute_sql( db,"get_add_jyjd",{'ywid':ywid,'field':['b.jbjdid']})[0].count
    if count != 0:
        return True
    return False
    
def ywdc_jy( db,ywid ):
    """
    #业务导出时，校验本地是否存在未提交数据
    #ywid:业务ID
    """
    # 业务导出时，在校验未提交数据比之交易多了数据库模块及公共函数的校验，对于子流程、交易、节点的校验可以直接调用交易导出时的校验方式
    result = jydc_jy( db ,ywid )
    if result:
        return True
    # 查询修改后未提交的公共函数
    count = ModSql.common.execute_sql( db,"get_edit",{'cxtj':[('a.ssyw_id',ywid)],'lx':'gghs','tname':['gl_yw_gghs']})[0].count
    if count != 0:
        return True
    # 查询新增后未提交的公共函数
    count = ModSql.common.execute_sql( db,"get_add",{'cxtj':[('a.ssyw_id',ywid)],'lx':'gghs','tname':['gl_yw_gghs']})[0].count
    if count != 0:
        return True
    # 查询修改后未提交的数据库模型
    count = ModSql.common.execute_sql( db,"get_edit",{'cxtj':[('a.ssyw_id',ywid)],'lx':'sjk','tname':['gl_sjkmxdy']})[0].count
    if count != 0:
        return True
    # 查询新增后未提交的数据库模型
    count = ModSql.common.execute_sql( db,"get_add",{'cxtj':[('a.ssyw_id',ywid)],'lx':'sjk','tname':['gl_sjkmxdy']})[0].count
    if count != 0:
        return True
    return False

def txdc_jy( db,txid ):
    """
    # 通讯导出，校验是否有未提交数据
    """ 
    # 查询修改后未提交的打包节点
    sql_data = {'jdlxzd':['b.dbjdid']}
    if txid:
        sql_data["txglid"] = txid.split(",")
    count = ModSql.common.execute_sql(db,"get_tx_jd_edit",sql_data)[0].count
    if count != 0:
        return True
    # 查询修改后未提交的解包节点
    sql_data = {'jdlxzd':['b.jbjdid']}
    if txid:
        sql_data["txglid"] = txid.split(",")
    count = ModSql.common.execute_sql(db,"get_tx_jd_edit",sql_data)[0].count
    if count != 0:
        return True
    # 查询新增后未提交的打包节点
    sql_data = {'jdlxzd':['b.dbjdid']}
    if txid:
        sql_data["txglid"] = txid.split(",")
    count = ModSql.common.execute_sql(db,"get_tx_jd_add",sql_data)[0].count
    if count != 0:
        return True
    # 查询新增后未提交的解包节点
    sql_data = {'jdlxzd':['b.jbjdid']}
    if txid:
        sql_data["txglid"] = txid.split(",")
    count = ModSql.common.execute_sql(db,"get_tx_jd_add",sql_data)[0].count
    if count != 0:
        return True
    return False
    
def get_imp_exp_data( ywid,lx,txid ):
    """
    # 获取导入、导出在没有未提交数据时的展示数据
    """    
    with sjapi.connection() as db:
        if lx == 'yw':
            rows = get_dc_yw_data( db,ywid )
        elif lx == 'jy':
            rows = get_jy_data( db,ywid )['rightRows']
        elif lx == 'tx':
            rows = get_tx_dc_data( db,txid ) 
        return {'rows':rows,'state':True}
         
def get_imp_exp_wtj_data( ywid,lx,txid ):
    """
    # 获取导入、导出有未提交数据时的展示数据
    """
    with sjapi.connection() as db:
        if lx == 'yw':
            rows = get_yw_data( db,ywid )
        elif lx == 'jy':
            rows = get_jy_data( db,ywid )
        elif lx == 'tx':
            rows = get_tx_data( db,txid )
        return {'leftRows':rows['leftRows'],'rightRows':rows['rightRows'],'state':True}   

def get_dc_yw_data( db,ywid ):
    """
    #没有未提交数据时，获取业务导出页面展示数据
    """
    # 获取业务名称
    ywmc = ModSql.common.execute_sql( db,'get_ywdy',{'ywid':ywid})[0].ywmc
    # 获取展示数据
    jy_lst,zlc_lst,dymb_lst,sjkmx_lst,gghs_lst,jd_lst = get_yw_right_tree( db ,ywid )
    # 组织数据
    ywcs_dic =  { 'id':'业务参数','name':'业务参数','xgr':'','xgsj':'' }
    jy_dic = { 'id':'交易流程','name':'交易流程','children':jy_lst }
    zlc_dic = { 'id':'子流程','name':'子流程','children':zlc_lst }
    dymb_dic = { 'id':'打印模版','name':'打印模版','children':dymb_lst }
    sjkmx_dic = { 'id':'数据库模型','name':'数据库模型','children':sjkmx_lst }
    gghs_dic = { 'id':'公共函数','name':'公共函数','children':gghs_lst }
    rows = [ {'id':ywid,'name':ywmc,'children':[ywcs_dic,jy_dic,zlc_dic,dymb_dic,sjkmx_dic,gghs_dic] },{'id':'节点','name':'节点','children':jd_lst }]
    return rows 

def get_yw_data( db,ywid ):
    """
    # 获取在有未提交数据时，左右两侧的展示数据
    """
    data = { 'leftRows':[],'rightRows':[] }
    # 获取业务名称
    ywmc = ModSql.common.execute_sql( db,'get_ywdy',{'ywid':ywid})[0].ywmc
    # 获取右侧数据
    rjy_lst,rzlc_lst,rdymb_lst,rsjkmx_lst,rgghs_lst,rjd_lst = get_yw_right_tree( db ,ywid )
    # 获取左侧数据
    ljy_lst,lzlc_lst,lsjkmx_lst,lgghs_lst,ljd_lst = get_yw_left_tree( db ,ywid )
    # 交易流程对比
    ljy_lst,rjy_lst = get_sjbj( ljy_lst,rjy_lst )
    # 子流程对比
    lzlc_lst,rzlc_lst = get_sjbj( lzlc_lst,rzlc_lst )
    # 节点对比
    ljd_lst,rjd_lst = get_sjbj( ljd_lst,rjd_lst )
    # 公共函数对比
    lgghs_lst,rgghs_lst = get_sjbj( lgghs_lst,rgghs_lst )
    # 数据表对比
    lsjkmx_lst,rsjkmx_lst = get_sjbj( lsjkmx_lst,rsjkmx_lst )
    data['leftRows'] = get_yw_zssj( ywid,ywmc,ljy_lst,lzlc_lst,lsjkmx_lst,lgghs_lst,ljd_lst )
    data['rightRows'] = get_yw_zssj( ywid,ywmc,rjy_lst,rzlc_lst,rsjkmx_lst,rgghs_lst,rjd_lst )         
    return data    
    
def get_jy_data( db,ywid ):
    """
    # 获取在有未提交数据时，左右两侧的展示数据
    """
    data = { 'leftRows':[],'rightRows':[] }
    # 获取业务名称
    ywmc = ModSql.common.execute_sql( db,'get_ywdy',{'ywid':ywid})[0].ywmc
    # 获取右侧数据
    rjy_lst,rzlc_lst,rjd_lst = get_jy_right_tree( db ,ywid )
    # 获取左侧数据
    ljy_lst,lzlc_lst,ljd_lst = get_jy_left_tree( db ,ywid )
    # 交易流程对比
    ljy_lst,rjy_lst = get_sjbj( ljy_lst,rjy_lst )
    # 子流程对比
    lzlc_lst,rzlc_lst = get_sjbj( lzlc_lst,rzlc_lst )
    # 节点对比
    ljd_lst,rjd_lst = get_sjbj( ljd_lst,rjd_lst )
    data['leftRows'] = get_jy_zssj( ywid,ywmc,ljy_lst,lzlc_lst,ljd_lst )
    data['rightRows'] = get_jy_zssj( ywid,ywmc,rjy_lst,rzlc_lst,rjd_lst )         
    return data
    
def get_tx_dc_data( db,txid ):
    """
    #获取通讯没有未提交时的展示数据
    """ 
    # 获取打解包节点信息
    dbjd_lst,jbjd_lst = get_tx_right_tree( db,txid )
    # 打包节点与解包节点同在节点下
    dbjd_lst.extend(jbjd_lst)
    # 通讯接口数据查询
    sql_data = {}
    if txid:
        sql_data['txglid'] = txid.split(",")
    rs = ModSql.common.execute_sql_dict(db,"get_tx_data",sql_data)    # 通讯数据结构组织
    # 存放通讯ID
    txid_lst = []
    # 返回页面的结果集 
    result = []
    for dic in rs:
        if dic['txid'] not in txid_lst:
            result.append( {'id':dic['txid'],'name':dic['txmc'],'children':[{'id':'%s通讯参数'%(dic['txid']),'name':'通讯参数'},{'id':'%s通讯基本信息'%(dic['txid']),'name':'通讯基本信息'}]} )
            txid_lst.append( dic['txid'] )
        if dic['id']:
            result[txid_lst.index(dic['txid'])]['children'].append( { 'id':dic['id'],'name':dic['name'],'xgr':dic['xgr'],'xgsj':dic['xgsj'] } )
    result.append( {'id':'节点','name':'节点','children':dbjd_lst} )
    return result 
    
def get_tx_data( db,txid ):
    """
    #通讯导出时，校验本地是否存在未提交数据 
    """
    data = { 'leftRows':[],'rightRows':[] }
    # 获取左侧数据
    ldbjd_lst,ljbjd_lst = get_tx_left_tree( db,txid )
    # 获取右侧数据
    rdbjd_lst,rjbjd_lst = get_tx_right_tree( db,txid )
    # 打包节点对比
    ldbjd_lst,rdbjd_lst = get_sjbj( ldbjd_lst,rdbjd_lst )
    # 解包节点对比
    ljbjd_lst,rjbjd_lst = get_sjbj( ljbjd_lst,rjbjd_lst )
    data['leftRows'] = get_tx_zssj( ldbjd_lst,ljbjd_lst )
    data['rightRows'] = get_tx_zssj( rdbjd_lst,rjbjd_lst ) 
    return data
    
def get_sjbj( leftLst,rightLst ):
    """
    #左右两侧数据比较
    """
    for index,dic in enumerate(leftLst):
        # 若左侧的再右侧中不存在，说明为新增，左侧的diff属性值设为2
        right_id_lst = [ dic['id'] for dic in rightLst]
        if dic['id'] not in right_id_lst:
            leftLst[index]['diff'] = '2'
            if dic.get("txglid",''):
                rightLst.insert(index,{'id':dic['id'],'diff':'2','txglid':dic.get('txglid')})
            else:
                rightLst.insert(index,{'id':dic['id'],'diff':'2'})
        else:
            # 若左侧的数据在右侧有，需先判断该数据在左右两侧的位置是否一致
            rightIndex = right_id_lst.index(dic['id'])
            if index != rightIndex:
                # 若位置不一至，需将右侧中该数据的位置，移到与左侧一致
                rightDic = rightLst[rightIndex]
                rightLst.remove(rightDic)
                rightLst.insert(index,rightDic)
            lwym = dic['wym']
            rwym = rightLst[index]['wym']
            lzt = dic.get('jyzt','')
            rzt = rightLst[index].get('jyzt','')
            # 若有参数唯一码时，说明是交易的对比，此时需要将交易的参数唯一码也进行对比
            lcswym = dic.get('cswym','')
            rcswym = rightLst[index].get('cswym','')
            # 若两侧的唯一码不一致，说明为修改，左右两侧diff属性的值设为1
            if lwym != rwym or lzt != rzt:
                leftLst[index]['diff'] = '1'
                rightLst[index]['diff'] = '1'
            # 如果唯一码不是32位的的MD5，说明这个唯一码是异常的（异常包括None，null），这时候我们将唯一码变为空字符串
            if len(str(lcswym)) < 32:
                lcswym = ""
            if len(str(rcswym)) < 32:
                rcswym = ""
            if lcswym != rcswym:
                leftLst[index]['diff'] = '1'
                rightLst[index]['diff'] = '1'
    for index,dic in enumerate(rightLst):
        # 若右侧的在左侧不存在，说明为删除，右侧的diff属性值为2
        left_id_lst = [ dic['id'] for dic in leftLst]
        if dic['id'] not in left_id_lst:
            rightLst[index]['diff'] = '2'
            if dic.get("txglid",''):
                leftLst.insert(index,{'id':dic['id'],'diff':'2','txglid':dic.get('txglid')})
            else:
                leftLst.insert(index,{'id':dic['id'],'diff':'2'})
    return leftLst,rightLst

def get_jy_zssj( ywid,ywmc,jy_lst,zlc_lst,jd_lst ):
    """
    # 根据传入的数据，将数据组织成树形展示需要的结构
    """
    # 按照ID排序，保证左右两侧的数据顺序是一致的
    # 交易文件夹的样式
    jy_diff = get_parent_css( jy_lst)
    # 子流程文件夹的样式
    zlc_diff = get_parent_css( zlc_lst)
    # 节点的样式
    jd_diff = get_parent_css( jd_lst)
    # 业务样式
    yw_diff = ''
    # 如果业务下的子流程、交易有修改的，业务样式为修改，不考虑新增 1：修改 2：新增
    if '1' in (jy_diff,zlc_diff):
        yw_diff = '1'
    elif '2' in(jy_diff,zlc_diff):
        yw_diff = '2'
    dic1 = { 'id':'交易流程','name':'交易流程','diff':jy_diff,'children':jy_lst,'lx':'ZLC' }
    dic2 = { 'id':'子流程','name':'子流程','diff':zlc_diff,'children':zlc_lst,'lx':'JY' }
    return [ {'id':ywid,'name':ywmc,'diff':yw_diff,'children':[dic1,dic2] },{'id':'节点','name':'节点','diff':jd_diff,'children':jd_lst,'lx':'JD' } ]
    
def get_yw_zssj( ywid,ywmc,jy_lst,zlc_lst,sjkmx_lst,gghs_lst,jd_lst ):
    """
    # 根据传入的数据，将数据组织成树形展示需要的结构
    """
    # 交易文件夹的样式
    jy_diff = get_parent_css( jy_lst)
    # 子流程文件夹的样式
    zlc_diff = get_parent_css( zlc_lst)
    # 公共函数文件夹的样式
    gghs_diff = get_parent_css( gghs_lst)
    # 数据库模型文件夹的样式
    sjkmx_diff = get_parent_css( sjkmx_lst)
    # 节点的样式
    jd_diff = get_parent_css( jd_lst)
    # 业务样式
    yw_diff = ''
    if '1' in (jy_diff,zlc_diff,gghs_diff,sjkmx_diff):
        yw_diff = '1'
    elif '2' in(jy_diff,zlc_diff,gghs_diff,sjkmx_diff):
        yw_diff = '2'
    #dic1 =  { 'id':'业务参数','name':'业务参数','lx':'YWCS'}
    dic2 = { 'id':'交易流程','name':'交易流程','children':jy_lst,'diff':jy_diff,'lx':'JY' }
    dic3 = { 'id':'子流程','name':'子流程','children':zlc_lst,'diff':zlc_diff,'lx':'ZLC'  }
    dic4 = { 'id':'公共函数','name':'公共函数','children':gghs_lst,'diff':gghs_diff,'lx':'GGHS'  }
    dic5 = { 'id':'数据库模型','name':'数据库模型','children':sjkmx_lst,'diff':sjkmx_diff,'lx':'SJKMX'  }
    return [ {'id':ywid,'name':ywmc,'children':[dic2,dic3,dic4,dic5],'diff':yw_diff },{'id':'节点','name':'节点','children':jd_lst,'diff':jd_diff,'lx':'JD'  } ]

def get_tx_zssj( dbjd_lst,jbjd_lst ):
    """
    #组织左右侧的数据展示
    """    
    dbjd_lst.extend( jbjd_lst )
    # 节点的样式
    jd_diff = get_parent_css( dbjd_lst)
    return [ {'id':'通讯节点','name':'通讯节点','children':dbjd_lst,'diff':jd_diff,'lx':'JD' } ]
       
def get_jy_left_tree( db,ywid ):
    """
    # 获取交易导出时，左侧的展示数据
    """
    # 左侧交易流程查询
    jy_lst = ModSql.common.execute_sql_dict( db,"get_left_jylc",{'ywid':ywid} )
    # 左侧子流程查询
    zlc_lst = ModSql.common.execute_sql_dict( db,"get_left_zlc",{'ywid':ywid} )
    # 左侧交易节点查询
    jyjd_lst = ModSql.common.execute_sql_dict( db,"get_left_jd",{'ywid':ywid,'tname':['gl_jydy'],'fieldname':['b.ssjyid']} )
    # 左侧子流程查询
    zlcjd_lst = ModSql.common.execute_sql_dict( db,"get_left_jd",{'ywid':ywid,'tname':['gl_zlcdy'],'fieldname':['b.sszlcid']} )
    # 左侧交易打包查询
    dbjd_lst = ModSql.common.execute_sql_dict( db,"get_left_jyjd",{'ywid':ywid,'field':['a.dbjdid']} )
    # 左侧交易解包查询
    jbjd_lst = ModSql.common.execute_sql_dict( db,"get_left_jyjd",{'ywid':ywid,'field':['a.jbjdid']} )
    jyjd_lst.extend(zlcjd_lst)
    jyjd_lst.extend(dbjd_lst)
    jyjd_lst.extend(jbjd_lst)
    # 记录节点的ID，循环交易节点、子流程节点、交易打解包节点的合并列表，将ID放入该列表，后续判断重复时使用
    cfid_lst = []
    jd_rs = []
    for index,dic in enumerate(jyjd_lst):
        if dic['id'] not in cfid_lst:
            cfid_lst.append(dic['id'])
            jd_rs.append(dic)
    sorted(jd_rs,key=lambda dic:dic['bm'])        
    return jy_lst,zlc_lst,jd_rs
    
def get_jy_right_tree( db,ywid ):
    """
    #导出时获取右侧区域所展示的数据
    """   
    # 右侧交易流程查询
    jy_lst = ModSql.common.execute_sql_dict( db,"get_right_jylc",{'ywid':ywid} )
    # 右侧子流程查询
    zlc_lst = ModSql.common.execute_sql_dict( db,"get_right_zlc",{'ywid':ywid} )
    # 右侧交易节点查询
    jyjd_lst = ModSql.common.execute_sql_dict( db,"get_right_jd",{'ywid':ywid,'tname':['gl_jydy'],'fieldname':['b.ssjyid']} )
    # 右侧子流程节点查询
    zlcjd_lst = ModSql.common.execute_sql_dict( db,"get_right_jd",{'ywid':ywid,'tname':['gl_zlcdy'],'fieldname':['b.sszlcid']} )
    # 右侧交易打包查询
    dbjd_lst = ModSql.common.execute_sql_dict( db,"get_right_jyjd",{'ywid':ywid,'field':['c.dbjdid']} )
    # 右侧交易解包查询
    jbjd_lst = ModSql.common.execute_sql_dict( db,"get_right_jyjd",{'ywid':ywid,'field':['c.jbjdid']} )
    jyjd_lst.extend(zlcjd_lst)
    jyjd_lst.extend(dbjd_lst)
    jyjd_lst.extend(jbjd_lst)
    # 记录节点的ID，循环交易节点、子流程节点、交易打解包节点的合并列表，将ID放入该列表，后续判断重复时使用
    cfid_lst = []
    jd_rs = []
    for index,dic in enumerate(jyjd_lst):
        if dic['id'] not in cfid_lst:
            cfid_lst.append(dic['id'])
            jd_rs.append( dic)
    sorted(jd_rs,key=lambda dic:dic['bm'])        
    return jy_lst,zlc_lst,jd_rs

def get_yw_left_tree( db ,ywid ):
    """
    # 获取左侧区域数据
    """ 
    # 业务比之交易多了公共函数既数据库模型的查询，其他的可以直接调用交易的查询
    jy_lst,zlc_lst,jd_lst = get_jy_left_tree( db,ywid )
    # 左侧公共函数查询
    gghs_lst = ModSql.common.execute_sql_dict( db,"get_left_gghs",{'ywid':ywid} )
    # 左侧数据库模型查询
    sjkmx_lst = ModSql.common.execute_sql_dict( db,"get_left_sjkmx",{'ywid':ywid} )
    return jy_lst,zlc_lst,sjkmx_lst,gghs_lst,jd_lst
    
def get_yw_right_tree( db,ywid ):
    """
    # 导出时获取右侧区域所展示的数据
    """
    # 获取交易、子流程、节点信息
    jy_lst,zlc_lst,jd_lst = get_jy_right_tree( db,ywid )    
    # 业务打印模版查询
    dymb_lst = ModSql.common.execute_sql_dict( db,"get_right_dymb",{'ywid':ywid} )
    # 业务数据库模型查询
    sjkmx_lst = ModSql.common.execute_sql_dict( db,"get_right_sjkmx",{'ywid':ywid} )
    # 业务公共函数查询
    gghs_lst = ModSql.common.execute_sql_dict( db,"get_right_gghs",{'ywid':ywid} )
    return jy_lst,zlc_lst,dymb_lst,sjkmx_lst,gghs_lst,jd_lst
   
def get_tx_left_tree( db,txid ):
    """
    #获取左侧展示数据
    """    
    # 查询打包节点数据
    sql_data = {'jdlxzd':['a.dbjdid']}
    if txid:
        sql_data["txglid"] = txid.split(",")
    dbjd_lst = ModSql.common.execute_sql_dict(db,"get_tx_left_jd",sql_data)
    # 给打包节点加入打包节点的标志,这样通讯的导出在双击进行版本比对时就可以查看到接口校验等三个列了。
    # 5:通讯打包节点
    for dbjd in dbjd_lst:
        dbjd['jdlx'] = '5'
    # 查询解包节点数据
    sql_data = {'jdlxzd':['a.jbjdid']}
    if txid:
        sql_data["txglid"] = txid.split(",")
    jbjd_lst = ModSql.common.execute_sql_dict(db,"get_tx_left_jd",sql_data)
    return dbjd_lst,jbjd_lst
    
def get_tx_right_tree( db,txid ):
    """
    #获取右侧展示数据
    """    
    # 查询打包节点数据
    sql_data = {'jdlxzd':['a.dbjdid']}
    if txid:
        sql_data["txglid"] = txid.split(",")
    dbjd_lst = ModSql.common.execute_sql_dict(db,"get_tx_right_jd",sql_data)
    # 给打包节点加入打包节点的标志,这样通讯的导出在双击进行版本比对时就可以查看到接口校验等三个列了。
    # 5:通讯打包节点
    for dbjd in dbjd_lst:
        dbjd['jdlx'] = '5'
    # 查询解包节点数据
    sql_data = {'jdlxzd':['a.jbjdid']}
    if txid:
        sql_data["txglid"] = txid.split(",")
    jbjd_lst = ModSql.common.execute_sql_dict(db,"get_tx_right_jd",sql_data)
    return dbjd_lst,jbjd_lst
        

def get_file_path( db, dir_name, csdm ):
    """
    # 获取文件保存路径
    # 文档存储目录：--项目static的目录/指定目录/参数定义目录(可以没有值，那么就是指定目录下)
    # @params: dir_name: 默认书写文件目录
    # @params: csdm: 定义相对目录的参数代码
    """
    # 反馈信息
    msg = True
    fpath = ''
    # 首先获取系统参数管理中定义的相对路径
    xd_path = get_csdyv_bycsdm( db, csdm )
    if xd_path:
        val = xd_path['value'] if xd_path['value'] else ''
        fpath = os.path.join( STATIC_DIR, settings._T.APP_NAME, dir_name, val )
        # 判断路径是否存在( 不存在，则在真实的路径上上传 )
        if os.path.exists(fpath) == False:
            os.makedirs( fpath )
    else:
        msg = '获取文档路径失败，未在系统参数中定义文档相对路径，请通过功能[系统参数管理]定义文档相对路径[参数代码：%s]。' % csdm
    
    return msg, fpath

def get_csdyv_bycsdm( db, csdm, lx = '1', ssid = None ):
    """
    # 获取参数值根据参数代码（默认系统参数的参数值）
    """
    csxx = None
    sql_data = { 'csdm': csdm, 'lx': lx }
    if ssid:
        sql_data['ssid'] = ssid
    csxx_lst = ModSql.common.execute_sql_dict( db,"get_csdyv_bycsdm", sql_data )
    if csxx_lst:
        csxx = csxx_lst[0]
    
    return csxx
    
def get_parent_css(lst):
    """
    # 获取父节点样式
    """
    result = ''
    for dic in lst:
        diff = '' if dic.get('diff','') == None else dic.get('diff','')
        if diff == '1':
            result = '1'
            break
        elif diff == '2':
            result = '2'
    return result
    
def insert_tab_sql( sjbmc, sjbmcms, zd_lst ):
    """
    # 获取新增数据表及注释的sql
    # @param sjbmc: 数据表名称
    # @param sjbmcms: 数据表名称描述
    # @param zd_lst: 字段集合[{zdmc:zdmc,zdms:zdms,zdlx:zdlx,zdcd;zdcd,xscd:xscd,
        sfkk:sfkk,iskey:iskey,mrz:mrz},{},……]
    # 返回值：
    #   @tab_sql: 新增表sql
    #   @zs_subsql_lst：注释sql列表[zs_sql1,zs_sql2,……]
    """
    # 新增表sql
    tab_sql = "create table %s ( \n"%sjbmc
    # 用来存放创建数据表及字段注释SQL
    zs_subsql_lst = []
    # 为表增加注释SQ
    zs_subsql_lst.append( "comment on table %s is '%s'"%( sjbmc,sjbmcms) )
    # 用来存放创建字段的SQL
    subsql_lst = []
    # 主键字段
    iskey_lst = []
    for zdxx_dic in zd_lst:
        # 创建字段SQL
        subsql = ""
        # 字段名称 需转换为大写，方便之后与oracle系统表进行关联
        zdmc = zdxx_dic['zdmc'].upper()
        # 字段描述
        zdms = zdxx_dic['zdms']
        # 字段类型
        zdlx = zdxx_dic['zdlx']
        # 字段长度
        zdcd = int( zdxx_dic['zdcd'] ) if zdxx_dic['zdcd'] else zdxx_dic['zdcd']
        # 小数长度
        xscd = int( zdxx_dic['xscd'] ) if zdxx_dic['xscd'] else zdxx_dic['xscd']
        # 是否可空
        sfkk = zdxx_dic['sfkk']
        # 是否主键
        iskey = zdxx_dic['iskey']
        # 默认值
        mrz = zdxx_dic['mrz']
        if zdlx in ( 'CHAR','VARCHAR2','NCHAR','NVARCHAR2','RAW','FLOAT'):
            subsql = "%s %s ( %d ) "%( zdmc,zdlx,zdcd )
        elif zdlx == 'DECIMAL':
            if xscd:
                subsql = "%s %s ( %d,%d )"%( zdmc,zdlx,zdcd,xscd )
            else:
                subsql = "%s %s ( %d ) "%( zdmc,zdlx,zdcd )
        elif zdlx in ( 'DATE', 'LONG', 'BLOB', 'CLOB', 'NCLOB', 'BFILE', 'INTEGER', 'LONG RAW','REAL'):
            subsql = "%s %s"%( zdmc,zdlx )
        elif zdlx == 'NUMBER':
            if zdcd:
                if xscd:
                    subsql = "%s %s ( %d,%d )"%( zdmc,zdlx,zdcd,xscd )
                else:
                    subsql = "%s %s ( %d ) "%( zdmc,zdlx,zdcd )
            else:
                subsql = "%s %s"%( zdmc,zdlx )
        # 如果有默认值
        if mrz:
            subsql += " default '%s' "%(  mrz  )
        # 字段是否可空 1:是 0:否
        if sfkk == '0': 
            subsql += " not null "
        # 如果该字段为主键 1:是 0：否
        if iskey == '1':
            iskey_lst.append( zdmc )
        # 将创建字段SQL添加到列表中
        subsql_lst.append( subsql )
        # 添加创建注释SQL
        zs_subsql = "comment on column %s.%s is '%s'"%( sjbmc,zdmc,zdms )
        zs_subsql_lst.append( zs_subsql )
    tab_sql = tab_sql + ",\n".join( subsql_lst ) + " ,\n constraint PK_%s primary key ( %s )"%( sjbmc,",".join( iskey_lst ) ) + " )" 
    
    return tab_sql, zs_subsql_lst

def insert_sy_sql(sjbmc, sy_lst ):
    """
    # 获取新增索引sql
    # @param sjbmc: 数据表名称
    # @param sy_lst: 约束集合[{sfwysy:sfwysy,symc:symc,syzd:syzd},{},……]
    # 返回值：
    #   @tab_sql: 新增表sql
    #   @sy_sql_dic：注释sql列表{symc: sy_sql1,symc: sy_sql2,……}
    """
    sy_sql_dic = {}
    for dic in sy_lst:
        sql = ''
        # 拼接创建索引SQL
        if dic['sylx'] == 'NORMAL':
            sql = "create %s index %s on %s ('%s')"%( 'unique' if dic['sfwysy'] == 'UNIQUE' else '',dic['symc'],sjbmc,"','".join( dic['syzd'].split("|") ) );
        elif dic['sylx'] == 'NORMAL/REV':
            sql = "create %s index %s on %s ('%s') reverse"%( 'unique' if dic['sfwysy'] == 'UNIQUE' else '', dic['symc'],sjbmc,"','".join( dic['syzd'].split("|") ) );
        elif dic['sylx'] == 'BITMAP':
            sql = "create  bitmap index %s on %s ('%s') "%( dic['symc'],sjbmc,"','".join( dic['syzd'].split("|") ) );
        sy_sql_dic[dic['symc']] = sql
    
    return sy_sql_dic

def insert_ys_sql( sjbmc, ys_lst ):
    """
    # 获取新增约束sql
    # @param sjbmc: 数据表名称
    # @param ys_lst: 约束集合[{ysmc:ysmc,yszd:yszd},{},……]
    # 返回值：
    #   @tab_sql: 新增表sql
    #   @ys_sql_lst：注释sql列表[ys_sql1,ys_sql2,ys_sql3,……]
    """
    ys_sql_lst = []
    for dic in ys_lst:
        sql = "alter table %s add constraint %s unique （%s）"%( sjbmc,dic['ysmc'],",".join( dic['yszd'].split("|") ) )
        ys_sql_lst.append(sql)
    
    return ys_sql_lst
    
import ftplib
def ftp_put( host , port , user , passwd , filen , noerror = False , pasv = 1 , debug = 0 , localpath = TMPDIR ):
    """
        把文件上传到服务器上
        参数列表：
            host:主机ip
            port:端口号
            user:用户名
            passwd:密码
            filen:文件名
            noerror:???
    """
    ftp = ftplib.FTP()
    try:
        ftp.set_pasv( pasv )                                #设置ftp put为被动模式
        ftp.set_debuglevel( debug )                         #打开调试级别2，显示详细信息
        ftp.connect( host , port )                    #连接
        ftp.login( user ,passwd )                     #登录
        filen = filen.rsplit('/',1)                   #分析出文件路径和文件名
        filepath = filen[0]
        filename = 'STOR ' + filen[1]                 #操作命令，"stor"为上传命令
        ftp.cwd(filepath)                             #改变文件目录到要上传目录下
        bufsize = 1024                                #设置缓冲块大小
        localfile = os.path.join( localpath , filen[1] )
        try:
            file_handler = open(localfile,"rb")           #以读模式在本地打开文件
            try:
                ftp.storbinary(filename,file_handler,bufsize) #上传文件
                return True
            finally:
                file_handler.close()
        except:
            if noerror:
                return False
            else:
                raise
    finally:
        #退出ftp服务器
        ftp.quit()

def zz_nr( db, data_dic, gnmc, upd_id = None ):
    """
    # 组织行员日常运维流水需要的内容
    # @param data_dic: 当前信息字典
    # @param upd_id：修改id
    """
    # 内容
    nr = ''
    # 编辑修改前信息
    upd_dic = {}
    # 如果修改id存在，则为编辑
    if upd_id:
        rs = ModSql.common.execute_sql(db, "get_csdy_bm",{'id':upd_id})
        if rs:
            upd_dic = rs[0]
    if upd_dic:
        # 组织内容( id, csdm, csms, value, lx, ssid, zt )
        updQ = '参数代码：%s，参数值：%s，参数描述：%s，参数状态：%s' % ( upd_dic['csdm'] ,upd_dic['value'], upd_dic['csms'], upd_dic['zt'] )
        updH = '参数代码：%s，参数值：%s，参数描述：%s，参数状态：%s' % ( upd_dic['csdm'] ,data_dic['value'], data_dic['csms'], data_dic['zt'] )
        nr = "%s：编辑前[%s]，编辑后[%s]" % ( gnmc, updQ, updH )
    else:
        nr = "%s：新增内容[ 参数代码：%s,参数值：%s，参数描述：%s，参数状态：%s ]" % ( gnmc, 
            data_dic['csdm'], data_dic['value'], data_dic['csms'], data_dic['zt'] )
    
    return nr
    
def get_bmwh( lx, db=None ):
    """
    # 获取编码维护列表（id，mc）
    """
    # 查询编码
    bmwh_lst = []
    if db:
        bmwh_lst = ModSql.common.execute_sql_dict( db, 'get_bmwh', { 'lx': lx } )
    else:
        with sjapi.connection() as db:
            bmwh_lst = ModSql.common.execute_sql_dict( db, 'get_bmwh', { 'lx': lx } )
        
    return bmwh_lst
    
def get_bmwh_bm( lx, db=None ):
    """
    # 获取编码维护列表(bm，mc)
    """
    # 查询编码
    bmwh_lst = []
    if db:
        bmwh_lst = ModSql.common.execute_sql_dict( db, 'get_bmwh_bm', { 'lx': lx } )
    else:
        with sjapi.connection() as db:
            bmwh_lst = ModSql.common.execute_sql_dict( db, 'get_bmwh_bm', { 'lx': lx } )
    for obj in bmwh_lst:
        if not obj['ms']:
            obj['ms'] = ''
    
    return bmwh_lst
    
def update_jhrw( db, yzt, yzdfqpz, upd_dic = {}, sfxz = True, ysfkbf = None, yyjjb = None ):
    """
    # 更新交易的计划任务信息
    # @param db: 数据库连接
    # @param yzt：原交易状态
    # @param yzdfqpz：原自动发起配置
    # @param upd_dic: 更新字典( { 'zdfqpz': zdfqpz,'zdfqpzsm': zdfqpzsm,'rwlx': rwlx,'ssid':ssid,'zt':zt } )
    # @param sfxz: 是否可新增，默认没有可新增
    """
    # 初始化返回值
    ret = True
    msg = ""
    # 交易发起配置由没值变为有值，则往计划任务表中插入记录
    # 自动发起配置操作标志
    type = ''
    if not yzdfqpz and upd_dic['zdfqpz'] and sfxz:
        # 获取id
        upd_dic['id'] = upd_dic['id'] if upd_dic.get('id') else get_uuid()
        # 补充字段
        for zd in ['ip','sfkbf','yjjb']:
            if zd not in upd_dic:
                upd_dic[zd] = ''
        ModSql.common.execute_sql_dict(db, "ins_jhrwb", upd_dic)
        # 新增计划任务
        type = 'add'
    # 原来存在，现在存在, 且不一致
    elif yzdfqpz and upd_dic['zdfqpz'] and yzdfqpz != upd_dic['zdfqpz']:
        # 更新计划任务信息
        ModSql.common.execute_sql_dict(db, "upd_jhrwb_by_ssid", upd_dic)
        # 编辑计划任务
        type = 'update'
    elif yzt != upd_dic['zt'] or ( ysfkbf and yyjjb ):
        # 更新计划任务信息( 执行时间未变动 )
        ModSql.common.execute_sql_dict(db, "upd_jhrwb_by_ssid", upd_dic)
    
    # 获取交易的计划任务id
    jhrw_rs = ModSql.common.execute_sql_dict(db, "get_jhrwid_byssid", { 'ssid': upd_dic['ssid'] })
    # 计划任务存在
    if jhrw_rs:
        # 计划任务id
        jhrwid = jhrw_rs[0]['id']
        upd_dic['id'] = jhrwid
        # 分情况处理计划任务
        # (1)若交易状态由禁用变为启用，交易自动发起配置有值：
        #   则需调用公共函数ins_waitexec_task，传入参数计划任务表ID，
        #   向当日计划表中插入当前时间往后的当日未执行任务。
        if yzt == '0' and upd_dic['zt'] == '1' and upd_dic['zdfqpz']:
            ins_waitexec_task( jhrwid, db )
        # (2)若交易状态由启用变为禁用，交易自动发起配置有值:
        # 则需调用公共函数del_waitexec_task，传入参数计划任务表ID，
        # 将当日计划表中当前时间往后的未执行任务删除。
        elif yzt == '1' and upd_dic['zt'] == '0' and yzdfqpz:
            del_waitexec_task( jhrwid, db )
        # (3)若交易状态没变且为启用，交易自动发起配置改变且非空:
        # 则需调用公共函数del_waitexec_task，传入参数计划任务表ID，将当日计划表中当前时间往后的未执行任务删除，
        # 再调用公共函数ins_waitexec_task，传入参数计划任务表ID，向当日计划表中插入当前时间往后的当日未执行任务。
        elif yzt == '1' and upd_dic['zt'] == '1' and type == 'update':
            del_waitexec_task( jhrwid, db )
            ins_waitexec_task( jhrwid, db )
        # (4)若交易自动发起配置为空，但原交易自动发起配置有值：
        elif yzdfqpz and not upd_dic['zdfqpz']:
            # 1.调用公共函数del_waitexec_task，传入参数计划任务表ID，将当日计划表中当前时间往后的未执行任务删除。
            del_waitexec_task( jhrwid, db )
            # 2.删除计划任务表
            ModSql.common.execute_sql_dict(db, "del_jhrw_byid", { 'id': upd_dic['id'] })
        # (5)若交易状态没变且为启用，交易自动发起配置由空变为有值：
        #   则需调用公共函数ins_waitexec_task，传入参数计划任务表ID，
        #   向当日计划表中插入当前时间往后的当日未执行任务。
        elif yzt == '1' and upd_dic['zt'] == '1' and type == 'add':
            ins_waitexec_task( jhrwid, db )
        # (6)是否可并发修改
        if ysfkbf and upd_dic['sfkbf'] != ysfkbf:
            # 更新当日执行计划任务表中未发起的计划任务(zt:0:未发起)
            ModSql.common.execute_sql_dict(db, "update_jhrw_sfkbf", { 'sfkbf': upd_dic['sfkbf'], 'jhrwid': jhrwid, 'zt': '0' })
        # (7)预警级别修改
        if yyjjb and upd_dic['yjjb'] != yyjjb:
            # 更新当日执行计划任务表中未发起的计划任务(zt:0:未发起)
            ModSql.common.execute_sql_dict(db, "update_jhrw_yjjb", { 'yjjb': upd_dic['yjjb'], 'jhrwid': jhrwid, 'zt': '0' })
    else:
        ret = False
        msg = "没有对应的计划任务信息，数据有问题"
    
    return ret, msg

def crontab_cj(ct, rq=None, sj=None):
    """
    # 对crontab拆解
    # 根据传入的日期和时间进行拆分，若传入的时间为空，则默认从指定日期的当前时间拆分到指定日期的24点；
    # 若传入的时间不为空，则从指定日期指定时间拆分到指定日。
    # ct: crontab字符串
    # rq: 开始日期YYYYmmdd，默认为当前日期
    # sj: 开始时间HHMM，默认为当前时间
    """
    limit_end = get_strftime2()[:8] + '235959'
    return [k[8:12] for k in crontab.main(ct, rq, sj) if k <= limit_end]

def crontab_fy(ct):
    """
    # 对crontab信息进行中文翻译，并同时进行校验是否合理。
    # ct: crontab字符串
    # return (True/False, 中文翻译, message)
    """
    state = True
    description = '解析失败'
    try:
        # 对crontab拆解，以校验合法性
        crontab_cj(ct)
        # 获取中文翻译
        description = CronDescriptor().getDescription(ct)
    except:
        state = False
    if not state or '失败' in description:
        return (False, '', description)
    else:
        return (True, description, '')

def analyse_sys_run_trace(a, start_type = 'jystart'):
    """
    # 根据执行日志分析交易执行过程，返回交易执行过程和子流程字典
    """
    # 获取除交易码外的交易走向
    b=a[a.find(start_type):]
    # 子流程列表
    zlc_dic = {}
    # 主流程走向
    lczx = []
    # 计数器，防止无限循环，导致程序卡死
    count = 0
    while 1:
        # 获取子流程的开始
        ind = b.find(',')
        if (ind == -1):
            break
        else:
            # 获取子流程编码
            c=b[:ind]    
            zlcbm = c[c.rfind(':')+1:]
            # 获取子流程
            # 防止流程中节点名称与子流程名称重复
            #zlc = a[a.find(':'+zlcbm+',zlcstart[0]')+1:a.rfind('zlcend[0]:'+zlcbm+'[')+9]
            zlc = a[a.find(':'+zlcbm+',zlcstart[0]')+1:a.rfind(']:'+zlcbm+'[')+1]
            # 对主流程进行处理，将子流程去除
            b = b.replace(zlc+':','')
            zlc_dic[zlcbm] = zlc
        # 计数器加一，判断是否超过一百次，如果是，则不再进行循环
        count += 1
        if count > 100:
            break
    # 对b拆分为列表
    x = b.split(':')
    for i in x:
        lczx.append([i[:i.find('[')],i[i.find('[')+1:i.find(']')]])
    # 将主流程走向和子流程信息返回
    return lczx,zlc_dic
    
def check_jyhs(hsmc,tablename,search,db):
    """
    # 校验函数名称在数据库中是否存在
    # hsmc       函数名称
    # tablename  表名称
    # search     查询条件 字典{key:value}
    # db         数据库对象
    """
    # 将函数名称隔离
    end_length = hsmc.find('(') + 1
    str_tmp = hsmc.split('(')[0] + '('
    sql_data = {'tablename':[tablename],'length':end_length,'strtmp':str_tmp}
    for k,v in search.items():
        sql_data[k] = v
    # 从数据库中查询
    return ModSql.common.execute_sql(db, "check_jyhs", sql_data)[0].count

def get_hscs(hsmc):
    """
    # 获取函数名称中的参数信息并校验参数中是否有单‘*’的可变数量参数
    # hsmc       函数名称
    """
    str_tmp = hsmc[hsmc.find('(')+1:]
    str_lst = str_tmp[:str_tmp.find(')')]
    hs_lst_tmp = str_lst.split(',')
    if not str_lst :
        return [True,[],'']
    hs_lst = []
    message = ''
    # 判断参数表中是否有*arg的形式，目前核心执行函数不支持*arg的形式，只支持**arg形式
    flag = True
    for cs in hs_lst_tmp:
        if cs.count('*') == 1:
            flag = False
            message = '函数传参不允许是列表，请重新输入'
        #判断参数是否有默认值，若有，只取参数代码即可
        sfkk = False  #是否可空，默认为False，不可空
        mrz = ''      #默认值
        if '=' in cs:
            csxx = cs.split('=')
            sfkk = True
            cs,mrz = csxx[0].strip(' '),csxx[1]
            mrz = mrz = mrz.strip()[1:-1] if mrz.strip()[0] in ("'",'"') else mrz
        hs_lst.append((cs,sfkk,mrz))
    hsjg_lst = [flag,hs_lst,message]
    return hsjg_lst
    
def ins_waitexec_task( jhrwid, db = None ):
    """
    # 向当日计划表中插入当前时间往后的当日未执行任务
    # jhrwid       计划任务表ID
    # db  数据库连接
    """
    result = False
    try:
        if db:
            # 获取计划任务信息
            jhrwxx = ModSql.common.execute_sql_dict( db, 'get_jhrw', { 'jhrwid': jhrwid } )
            # 对crontab进行拆解
            zxsj_lst = crontab_cj( jhrwxx[0]['zdfqpz'] )
            # 将拆解后的信息插入到当日执行计划表中
            jhrwxx[0]['rq'] = get_strftime2()[:8]  # 当前日期
            #流水号应为 日期yyyymmddhhmmss+六位递增数 需与核心登记一致
            for zxsj in zxsj_lst:
                xtlsh = get_lsh2con( 'gl_drzxjhb', min = 1 , max = 1000000, con = db )
                jhrwxx[0]['lsh'] = datetime.datetime.now().strftime('%Y%m%d%H%M%S') + str(xtlsh).rjust(6,'0')
                jhrwxx[0]['uuid'] = get_uuid()
                jhrwxx[0]['jhfqsj'] = zxsj
                ModSql.common.execute_sql_dict( db, 'ins_drzxrw', jhrwxx[0] )
        else:
            with sjapi.connection() as db:
                jhrwxx = ModSql.common.execute_sql_dict( db, 'get_jhrw', { 'jhrwid': jhrwid } )
                # 对crontab进行拆解
                zxsj_lst = crontab_cj( jhrwxx[0]['zdfqpz'] )
                # 将拆解后的信息插入到当日执行计划表中
                jhrwxx[0]['rq'] = get_strftime2()[:8]  # 当前日期
                #流水号应为 日期yyyymmddhhmmss+六位递增数 需与核心登记一致
                for zxsj in zxsj_lst:
                    xtlsh = get_lsh2con( 'gl_drzxjhb', min = 1 , max = 1000000, con = db )
                    jhrwxx[0]['lsh'] = datetime.datetime.now().strftime('%Y%m%d%H%M%S') + str(xtlsh).rjust(6,'0')
                    jhrwxx[0]['uuid'] = get_uuid()
                    jhrwxx[0]['jhfqsj'] = zxsj
                    ModSql.common.execute_sql_dict( db, 'ins_drzxrw', jhrwxx[0] )
        result = True
    except:
        logger.info(traceback.format_exc())
    return result

def del_waitexec_task( jhrwid, db = None ):
    """
    # 将当日计划表中所有未执行任务删除
    # jhrwid       计划任务表ID
    # db  数据库连接
    """
    result = False
    try:
        if db:
            # 删除当日计划表中信息
            ModSql.common.execute_sql_dict( db, 'del_drzxrw', { 'jhrwid': jhrwid } )
        else:
            with sjapi.connection() as db:
                ModSql.common.execute_sql_dict( db, 'del_drzxrw', { 'jhrwid': jhrwid } )
        result = True
    except:
        logger.info(traceback.format_exc())
    return result
    
def get_srysjdid(SYS_RUN_TRACE):
    """
    @param: SYS_RUN_TRACE: 子流程执行走向
    #取子流程输入要素节点编码
    """
    lczx,zlc_dic = analyse_sys_run_trace(SYS_RUN_TRACE, start_type = 'zlcstart')
    if zlc_dic.get(lczx[1][0],'') == '':
        return lczx[1][0]
    return get_srysjdid(zlc_dic.get(lczx[1][0]))

def get_scysjdid(SYS_RUN_TRACE):
    """
    @param: SYS_RUN_TRACE: 子流程执行走向
    #取子流程输出要素节点编码
    """
    lczx,zlc_dic = analyse_sys_run_trace(SYS_RUN_TRACE, start_type = 'zlcstart')
    if zlc_dic.get(lczx[-2][0],'') == '':
        return lczx[-2][0]
    return get_scysjdid(zlc_dic.get(lczx[-2][0]))

def ip_is_called(ip,db):
    """
    @param: ip: 主机ip
    # 查看主机Ip是否被使用。
    """
    # 检查在对象采集配置表中是否被使用
    count = ModSql.common.execute_sql_dict( db, 'check_ip_use_in_cjpz', { 'zdzjip': ip } )[0]['count']
    if count > 0:
        return True
    # 检查动作执行主机表中是否被使用
    count = ModSql.common.execute_sql_dict( db, 'check_ip_use_in_dzzj', { 'zdzjip': ip } )[0]['count']
    if count > 0:
        return True
    # 检查参数表中预置的信息
    value = ModSql.common.execute_sql_dict( db, 'get_xx_csdy', {} )
    if len(value) > 0 and value[0]['value'] == ip:
        return True
    return False

def check_yzjy_single(id):
    """
    @param: id: 文件记录的id
    # 校验要更新sql的文件中是否有单笔异常的数据，如果有，需要业务人员先处理。
    """
    with sjapi.connection() as db:
        # 检查要更新sql的文件中是否有单笔异常的数据
        data_sql = ModSql.common.execute_sql( db, 'get_wjycmx_sql', { 'wjid': id } )[0]
        data_wjm = ModSql.common.execute_sql_dict( db, 'get_wjm', { 'wjid': id } )[0]
        sql = pickle.loads(data_sql.kkmxsjsql.read()) if data_sql.kkmxsjsql else ''
        count_sql = "select count(0) as num  from ( %s ) where zt='55'" % sql
        cur = db.cursor()
        cur.execute( count_sql, [id] )
        count = cur.fetchone()[0]
    if count:
        return '0','该文件[%s]中包含单笔阈值异常的记录,请处理完毕后再执行本操作'%data_wjm['wjm']
    else:
        return '1',''

def get_hsxxb( db, lb = None ):
    """
    # 获取编码维护列表(bm，mc)
    """
    # 查询编码
    sql_data = {}
    if lb:
        sql_data.update( { 'lb': lb } )
    fxgz_lst = ModSql.common.execute_sql_dict( db, 'get_hsxxb', sql_data )
    
    return fxgz_lst
 
def pickle_dumps(d):
    """
    将传入的对象转换为字符串
    """
    return pickle.dumps(d, False).decode('utf-8')

def get_task_lsh():
    """
    生成当日执行计划表中的流水号
    """
    xtlsh = get_lsh2con( 'gl_drzxjhb', min = 1 , max = 1000000 )
    lsh = datetime.datetime.now().strftime('%Y%m%d%H%M%S') + str(xtlsh).rjust(6,'0')
    return lsh
    
def trans_io_dic(list):
    """
    解析io采集结果
    """
    # 要返回的内容 {'dev':[], 'sjv':[]}
    data = {}
    # 确定返回内容的key
    for nr in list:
        nr_detail = nr.split('\n')
        for de in nr_detail:
            # 解析内容
            io = de.split(':')
            if len(io) > 1:
                if (io[0] in data.keys()) == False:
                    data[io[0]] = []
                data[io[0]].append(io[1].replace('%',''))
    # 返回数据
    return data

def get_xtcsdy( db, csdm ):
    """
    # 根据参数代码获取对应的参数信息
    # 有值传参数信息字典
    # 无值传空字典
    """
    csxx_lst = ModSql.common.execute_sql_dict( db, 'get_xtcsdy_bycsdm', { 'csdm': csdm } )
    if csxx_lst:
        return csxx_lst[0]
    else:
        return {}

def trans_mem_dic( nc_lst ):
    """
    # 对获取到的内存使用率进行数据转换
    # nc_lst: [{ip:ip,nr:采集结果内容}，{ip:ip,nr:采集结果内容}]
    # nr格式：
    #物理内存已使用5764612,未使用6487964
    #交换分区已使用0,未使用13328376
    #虚拟内存总大小34359738367
    #虚拟内存已使用308672
    # 返回信息：
    # [ {'46.17.189.101': {'p_un_use': '6487964', 'p_use': '5764612', # 物理内存未使用，已使用
               's_un_use': '13328376',  's_use': '0',                 # 交换分区未使用, 已使用
               'v_total': '34359738367',                              # 虚拟内存总大小
               'v_use': '308672'}},                                   # 虚拟内存已使用
        {'ip': {使用率}}]
    """
    nc_rs = []
    for k in nc_lst:
        nc = re.findall(r"\d+\.?\d*",k['nr'])
        nc_rs.append({k['ip']:{'p_use': nc[0],'p_un_use': nc[1],'s_use':nc[2],'s_un_use': nc[3],'v_total': nc[4],'v_use': nc[5]}})
    return nc_rs
    
def get_time_lst( jyrq, seconds_bj = 60, kssj = '000000' ):
    """
    # 获取从零点到当前时间点，根据间隔得到的时间点信息
    # jyrq: 交易日期(yyymmdd)
    # seconds_bj: 时间间隔(秒)
    # 返回信息格式： [00:00:00,00:30:00,01:00:00]
    """
    time_lst = []
    if jyrq:
        now = datetime.datetime.now().strftime('%H:%M:%S')
        jyrq = jyrq.replace('-','').replace('/','')
        start_date = datetime.datetime(int(jyrq[:4]),int(jyrq[4:6]),int(jyrq[6:]),int(kssj[:2]),int(kssj[2:4]),int(kssj[4:]))
        while True:
            if start_date.strftime('%H:%M:%S') > now:
                time_lst.append( now )
                break
            time_lst.append( start_date.strftime('%H:%M:%S') )
            start_date = start_date + datetime.timedelta(seconds=int(seconds_bj))
    return time_lst
    
def update_xtcsdy_bycsdm( db, csdm, value ):
    """
    # 根据参数代码获取对应的参数信息
    # 有值传参数信息字典
    # 无值传空字典
    """
    ModSql.common.execute_sql_dict( db, 'upd_xtcsdy_bycsdm', { 'csdm': csdm, 'value': value } )

def get_hyxx( db, hydm = None ):
    """
    # 获取行员信息
    @param hydm: 行员代码
    """
    hyxx_dic = {}
    hyxx_lst = ModSql.common.execute_sql_dict( db, 'select_hyxx_byhydm', { 'hydm': hydm } )
    hyxx_dic = dict( [ ( obj.get('hydm'), obj.get('xm') ) for obj in hyxx_lst ] )
    
    return hyxx_dic

def bytes_to_hex( s ):
    """
    # 将二进制转化为十六进制
    # 调用方式：bytes_to_hex(b'abcdefghijklmnopqrstuvwxyz中国'.encode('gbk')) 需要指定编码集
    """
    st = io.StringIO()
    
    def fmt( x ):
        # 这是可见字符(十进制32到126)，不可见字符返回 '.'
        if ord(b' ') <= x <= ord(b'\x7E'):
            return chr(x)
        return '.'
    i = 0
    end = 0
    line = ''
    if not isinstance(s, bytes):
        s = bytes( s )
    for c in s:
        i += 1
        if i % 16 == 1:
            line += '%04X: ' % ( i - 1 )
        line += '%02X ' % c
        if i % 8 == 0 and ( i / 8 ) % 2 == 1 :
            line += '- '
        if i % 16 == 0:
            line += ' ' + ''.join( map( fmt , s[i-16:i] ) )
            st.write( line + '</br>' )
            line = ''
            end = i
    if line :
        line += ' ' * ( 56 - len( line ) )
        st.write( line )
        st.write( ' ' + ''.join( map( fmt , s[end:] ) ) + '</br>' )
    return st.getvalue()
    
def to_binary(data):
    """
    # 将接收到的报文转二进制
    # data 接收到的报文
    """
    if data.get('SYS_JSDDBW') and isinstance( data.get('SYS_JSDDBW'), str ):
        try:
            # 十六进制转化为二进制
            data['SYS_JSDDBW'] = bytes().fromhex(data['SYS_JSDDBW'].replace(' ',''))
        except:
            error_msg = traceback.format_exc()
            logger.info(error_msg)
        return data

def binary_to_hex(trans_dict):
    """
    # 将返回值中二进制的数据转换为16进制
    # data 接收到返回值的报文
    """
    if trans_dict:
        for k in list( trans_dict.keys() ):
            # 二进制转换
            if trans_dict[k] and isinstance( trans_dict[k], bytes ):
                trans_dict[k] = str(binascii.b2a_hex(trans_dict[k]))[2:-1].upper()
            # bytearray类型转换（先转换为二进制，再转16进制）
            elif trans_dict[k] and isinstance( trans_dict[k], bytearray ):
                trans_dict[k] = str(binascii.b2a_hex( bytes( trans_dict[k]) ) )[2:-1].upper()
    return trans_dict

def binary_to_hex_db(trans_dict):
    """
    # 将返回值中二进制的数据转换为16进制
    # data 接收到返回值的报文
    """
    if trans_dict:
        for k in list( trans_dict.keys() ):
            # 二进制转换
            if trans_dict[k] and isinstance( trans_dict[k], bytes ):
                trans_dict[k] = bytes_to_hex( trans_dict[k] )
            # bytearray类型转换（先转换为二进制，再转16进制）
            elif trans_dict[k] and isinstance( trans_dict[k], bytearray ):
                trans_dict[k] = bytes_to_hex( bytes( trans_dict[k] ) )

def db_hex_to_binary(scys):
    """
    # 将数据库中的数据转为二进制
    # data 接收到返回值的报文
    """
    null_bytes = "b''"
    for scys_xx in scys:
        if scys_xx.get( 'ysdm' ) == 'SYS_JSDDBW':
            if scys_xx.get('qwscz') and scys_xx.get('sjscz') != null_bytes:
                try:
                    # 十六到二进制
                    scys_xx['qwscz'] = bytes().fromhex(scys_xx.get('qwscz','').replace(' ',''))
                    # 二进制转为对比十六进制
                    scys_xx['qwscz'] = bytes_to_hex( scys_xx.get('qwscz','') )
                except:
                    error_msg = traceback.format_exc()
                    logger.info(error_msg)
            else:
                scys_xx['qwscz'] = ""
            if scys_xx.get('sjscz') != None and scys_xx.get('sjscz') != 'None' and scys_xx.get('sjscz') != null_bytes:
                try:
                    # 十六到二进制
                    scys_xx['sjscz'] = bytes().fromhex(scys_xx['sjscz'].replace(' ',''))
                    # 二进制转为对比十六进制
                    scys_xx['sjscz'] = bytes_to_hex( scys_xx['sjscz'] )
                except:
                    error_msg = traceback.format_exc()
                    logger.info(error_msg)
            else:
                scys_xx['sjscz'] = ""
        if scys_xx.get( 'ysdm' ) == 'SYS_YFSDBW':
            if scys_xx.get('qwscz') and scys_xx.get('sjscz') != 'None' and scys_xx.get('qwscz') != null_bytes:
                try:
                    # 十六到二进制
                    scys_xx['qwscz'] = bytes().fromhex(scys_xx.get('qwscz','').replace(' ',''))
                    # 二进制转为对比十六进制
                    scys_xx['qwscz'] = bytes_to_hex( scys_xx.get('qwscz','') )
                except:
                    error_msg = traceback.format_exc()
                    logger.info(error_msg)
            if scys_xx.get('sjscz') != None and scys_xx.get('sjscz') != 'None' and scys_xx.get('sjscz') != null_bytes:
                try:
                    # 十六到二进制
                    scys_xx['sjscz'] = bytes().fromhex(scys_xx['sjscz'].replace(' ',''))
                    # 二进制转为对比十六进制
                    scys_xx['sjscz'] = bytes_to_hex( scys_xx['sjscz'] )
                except:
                    error_msg = traceback.format_exc()
                    logger.info(error_msg)
def srscys_hex_to_binary( ys_lst ):
    """
    # 输入输出要素，经十六进制数据转化为对比十六进制
    # ys_lst 要素列表
    """
    for ys_xx in ys_lst:
        if ys_xx.get( 'ysdm' ) == 'SYS_JSDDBW':
            # 十六到二进制
            try:
                ys_xx['ysz'] = bytes().fromhex(ys_xx['ysz'].replace(' ',''))
                # 二进制转为对比十六进制
                ys_xx['ysz'] = bytes_to_hex( ys_xx['ysz'] )
            except:
                error_msg = traceback.format_exc()
                logger.info(error_msg)
        if ys_xx.get( 'ysdm' ) == 'SYS_YFSDBW':
            try:
                # 十六到二进制
                ys_xx['ysz'] = bytes().fromhex(ys_xx['ysz'].replace(' ',''))
                # 二进制转为对比十六进制
                ys_xx['ysz'] = bytes_to_hex( ys_xx['ysz'] )
            except:
                error_msg = traceback.format_exc()
                logger.info(error_msg)

def grid_xml(data, req_lx='', mako="grid_printer/grid_data.xml", **kwd):
    """
    # 格式化显示数据到xml
    """
    if req_lx == 'bb':
        filepath = '%s_%s.xml'%(datetime.datetime.now().strftime('%Y%m%d%H%M%S%f'),uuid.uuid4())
        fpath = os.path.join( TMPDIR,filepath )
        fobj = open( fpath, 'wb' )
        fobj.write( render_to_string( mako, data=data, **kwd ).encode('utf8'))
        fobj.close()
        return {'filepath': filepath}
    else:
        return data

def anqx_service(param):
    """
    #获取登录者拥有的菜单按钮权限
    :param param:
    :return:
    """
     # 登录用户ID
    yhid = get_sess('hyid')
    # 初始化返回值
    data = {'an_lst':[]}
    # 数据库链接
    with sjapi.connection() as db:
        sql_data={'cddm':param['cddm'],'yhid':yhid}
        # 获取菜单对应的按钮列表
        anqx_lst = ModSql.common_anqx.execute_sql_dict(db, "get_anqx",sql_data)

        data['an_lst']=anqx_lst
    return  data
    
def set_zdfqpzsm(dic):
    """
    # 由于之前的版本提交没有加自动发起配置说明，所以为了解决线上不出错，只能是手动添加。
    :param dic:
    :return 自动发起配置说明:
    """
    zdfqpzsm = None
    if not dic.get('zdfqpzsm'):
        try:
            # 返回信息：(True/False, 中文翻译, message)
            ret = crontab_fy(dic.get('zdfqpz'))
            # 翻译成功
            if ret[0]:
                # 翻译成功，将中文翻译放在保存字典中
                zdfqpzsm = ret[1]
        except:
            zdfqpzsm = None
            logger.info('***************************导入交易的自动发起配置不正确**************************--> ' + str(dic.get('zdfqpz')))
        return zdfqpzsm
    else:
        return dic.get('zdfqpzsm')