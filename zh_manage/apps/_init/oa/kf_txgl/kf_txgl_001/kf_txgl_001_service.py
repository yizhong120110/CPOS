# -*- coding: utf-8 -*-
# Action: 通讯管理-通讯管理 主页面 service
# Author: zhangchl
# AddTime: 2015-01-07
# Standard: 注释仅能以“#”开头，sql可以是“--”；注释不能同代码在同一行

from sjzhtspj import ModSql, get_sess_hydm, logger
from sjzhtspj.common import get_strftime, get_uuid, ins_czrz, update_wym, py_check, get_bmwh_bm
import pickle, json
from sjzhtspj.const import TIMEOUT
from .kf_txgl_001_common import ( get_txwjmc, get_zlc, del_zcl, del_zcl_csal,
    del_cdtx_dbxx, add_cdtx_lc, check_zlc_sy, get_jydy_mc, get_zlcdy_mc )
from sjzhtspj.esb import transaction_test,memcache_data_del


def data_service( data_dic ):
    """
    # 通讯管理-通讯管理展示 列表初始化 service
    """
    # 反馈信息
    data = {'total':0, 'rows':[]}
    # 数据库操作
    with sjapi.connection() as db:
        
        # 查询通讯管理总条数
        total = ModSql.kf_txgl_001.execute_sql( db, 'data_count',data_dic )[0].count
        # 查询通讯管理列表信息
        # sql_dic = { 'rn_start': data_dic['rn_start'], 'rn_end': data_dic['rn_end'] }
        txglxx = ModSql.kf_txgl_001.execute_sql_dict( db, 'data_rs', data_dic )
        
        #组织反馈信息
        data['total'] = total
        data['rows'] = txglxx
    
    return data

def data_add_sel_service( data_dic ):
    """
    # 通讯管理-通讯管理 新增 页面初始化参数查询
    """
    # 反馈信息初始化
    result = {'state':False,'cssj':'', 'txlx_lst': [{'value': '', 'ms': '', 'text': '请选择'}]}
    # 超时时间
    result['cssj'] = TIMEOUT
    # 查询通讯类型
    # 1：地区 2：文件类型 3：打印模板类型 4：通讯类型
    result['txlx_lst'].extend( get_bmwh_bm( '4' ) )
    # 组织信息成功
    result['state'] = True
    
    return result

def data_add_bytxlx_txwj_service( data_dic ):
    """
    # 新增或编辑通讯时，根据通讯类型获取通讯文件列表
    """
    # 反馈信息初始化
    result = {'state':False,'txwjmc_lst':[]}
    # 通讯文件名称下拉列表数据
    if data_dic['txlxbm']:
        result['txwjmc_lst'] = get_txwjmc( data_dic['txlxbm'], data_dic['fwfx'] )
    # 组织信息成功
    result['state'] = True
    return result

def data_add_service( data_dic ):
    """
    # 通讯管理-通讯管理 新增 提交 service
    """
    result = {'state':False, 'msg':''}
    # 操作人
    czr = get_sess_hydm()
    # 操作时间
    czsj = get_strftime()
    # id
    txglid = get_uuid()
    
    with sjapi.connection() as db:
        # 通讯编码在通讯管理表是唯一索引，需要先校验通讯管理表是否存在
        count = ModSql.kf_txgl_001.execute_sql( db, 'add_check_txgl_bm', { 'txbm': data_dic['txbm'] } )[0].count
        if count != 0:
            result['msg'] = '通讯编码[%s]已经存在，请重新输入！' % data_dic['txbm']
            return result
        
        # 新增通讯信息
        sql_data = { 'id': txglid, 'bm': data_dic['txbm'], 'mc': data_dic['txmc'],
            'txlx': data_dic['txlx'],'fwfx': data_dic['fwfx'], 'txwjmc': data_dic['txwjmc'], 
            'cssj': data_dic['cssj'],'czr': czr, 'czsj': czsj,
            'jcbfs': data_dic['jcbfs'] if data_dic['jcbfs'] else 0 }
        ModSql.kf_txgl_001.execute_sql( db, 'add_insert', sql_data )
        
        # 更新模板定义表中的唯一码
        update_wym(db, 'txgl', txglid)
        
        # 登记操作流水
        rznr = '通讯编码[%s],通讯名称[%s],通讯类型[%s],服务方向[%s],通讯文件名称[%s],超时时间[%s]' % (data_dic['txbm'], data_dic['txmc'], data_dic['txlx'], data_dic['fwfx'], data_dic['txwjmc'], data_dic['cssj'] )
        ins_czrz( db, '通讯新增：%s' % rznr, gnmc = '通讯管理_新增' )

        result['state'] = True
        result['msg'] = '保存成功!'
    
    return result

def data_del_service( data_dic ):
    """
    # 通讯管理-通讯管理 删除 提交 service
    """
    # 反馈信息
    result = {'state':False, 'msg':''}
    txid = data_dic['txid']
    with sjapi.connection() as db:
        # 如果是客户端
        if data_dic['fwfx'] == '1':
            # 获取子流程定义信息( 子流程被使用则说明此C端通讯被使用，则不可删除 )
            cdtx_id_lst, zlc_id_lst, msg = get_zlc( db, txid, data_dic['txbm'] )
            if msg:
                result['msg'] = msg
                return result
            # 组织删除sql
            # 子流程存在删除子流程的相关数据
            if zlc_id_lst:
                # 删除子流程定义
                del_zcl( db, zlc_id_lst )
                # 删除子流程对应的测试案例
                del_zcl_csal( db, zlc_id_lst = zlc_id_lst )
            # C端通讯信息挡板信息
            if cdtx_id_lst:
                # 组织删除C端挡板信息
                del_cdtx_dbxx( db, cdtx_id_lst )
                # C端通讯删除
                ModSql.kf_txgl_001.execute_sql( db, 'del_cdtx_byid', { 'id_lst': cdtx_id_lst } )
        
        # 删除参数信息
        # 类型
        #   1:系统参数
        #   2:业务参数
        #   3:交易参数
        #   4:通讯参数
        ModSql.common.execute_sql( db, 'del_csdy_byssid', { 'lx': '4', 'ssid': txid } )
        # 交易码解出函数内容删除
        ModSql.kf_txgl_001.execute_sql( db, 'del_blob_bytxid', {'txid': txid } )
        # 通讯删除
        ModSql.kf_txgl_001.execute_sql( db, 'del_txgl_byid', { 'id_lst': [txid] } )
        # 调用公共函数，登记操作流水
        ins_czrz( db,'删除通讯【%s(%s)】' % ( data_dic['txbm'],  data_dic['txmc'] ), gnmc = '通讯管理_删除' )
        
        # 反馈前台
        result['state'] = True
        result['msg'] = '删除成功!'
    
    return result

def txxq_jbxx_service( data_dic ):
    """
    # 通讯管理-通讯详细信息-基本信息 service
    """
    # 初始化反馈信息
    tx_dic = {'txid': '', 'bm': '', 'mc': '', 'txlx': '', 'fwfx': '', 
    'txwjmc': '', 'cssj': '', 'jcjymjyid': '', 'jcjymjymc': ''}
    data = { 'tx_dic':tx_dic, 'txlx_lst': [{'value': '', 'ms': '', 'text': '请选择'}], 'txwjmc_lst':[],
        'state': False, 'msg': '' }
    # 通讯id
    txid = data_dic['txid']
    
    with sjapi.connection() as db:
        # 查询通讯基本信息
        txrs_lst = ModSql.common.execute_sql_dict( db, 'get_txgl', { 'id': txid } )
        if txrs_lst:
            data['tx_dic'] = txrs_lst[0]
            data['tx_dic']['jcjymjymc'] = ''
            # 默认超时时间
            cssj = TIMEOUT
            if not data['tx_dic']['cssj']:
                data['tx_dic']['cssj'] = cssj
            # 查询通讯类型
            # 1：地区 2：文件类型 3：打印模板类型 4：通讯类型
            data['txlx_lst'].extend( get_bmwh_bm( '4', db = db ) )
            for txlx_xx in data['txlx_lst']:
                if txlx_xx['value'] == data['tx_dic']['txlx']:
                    txlx_xx['selected'] = 'true'
                if not txlx_xx['ms']:
                    txlx_xx['ms'] = ''
            # 通讯文件名称下拉列表数据
            data['txwjmc_lst'] = get_txwjmc( data['tx_dic']['txlx'], data['tx_dic']['fwfx'] )
            for txlx_xx in data['txwjmc_lst']:
                if txlx_xx['value'] == data['tx_dic']['txwjmc']:
                    txlx_xx['selected'] = 'true'
            # 返回值
            data['True'] = True
        else:
            data['msg'] = '查询通讯系统中不存在，请查证'
    
    return data

def txxq_jbxx_edit_service( data_dic ):
    """
    # 通讯管理-通讯基本信息 编辑 提交 service
    """
    # 初始化返回值
    result = { 'state': 'False', 'msg': '' }
    # 交易码解出交易
    data_dic['jcbfs'] = data_dic['jcbfs'] if data_dic['jcbfs'] else 0
    data_dic['czr'] = get_sess_hydm()
    data_dic['czsj'] = get_strftime()
    
    with sjapi.connection() as db:
        # 查询修改前的信息
        data_rs = ModSql.kf_txgl_001.execute_sql_dict( db, 'select_txgl', data_dic )[0]
        # 修改C端通讯管理
        ModSql.kf_txgl_001.execute_sql_dict( db, 'upd_cdtx', data_dic )
        # 更新模板定义表中的唯一码
        update_wym(db, 'txgl', data_dic['txid'])
        
        # 操作日志流水登记
        upd_befor = '编辑前：通讯编码[%s],通讯名称[%s],通讯类型[%s],服务方向[%s],通讯文件名称[%s],超时时间[%s]' % (data_rs['bm'],data_rs['mc'],data_rs['txlx'],str(data_rs['fwfx']),data_rs['txwjmc'],str(data_rs['cssj']))
        upd_after = '编辑后：通讯编码[%s],通讯名称[%s],通讯类型[%s],服务方向[%s],通讯文件名称[%s],超时时间[%s]' % (data_rs['bm'],data_dic['mc'],data_dic['txlx'],str(data_dic['fwfx']),data_dic['txwjmc'],str(data_dic['cssj']))
        ins_czrz( db, '通讯编辑：%s，%s' % ( upd_befor, upd_after ), gnmc = '通讯管理_编辑' )
        # 组织反馈值
        result['state'] = True
        result['msg'] = '编辑成功!'
    
    return result
    
def txxq_csgl_data_service( data_dic ):
    """
    # 通讯参数数据表格列表数据获取 service
    """
    # 默认返回值
    data = {'total':0, 'rows':[]}
    with sjapi.connection() as db:
        # 查询总条数
        total = ModSql.common.execute_sql_dict( db, 'get_csdy_count', data_dic )[0]['count']
        # 查询信息
        ywcs = ModSql.common.execute_sql_dict( db, 'get_csdy', data_dic )
        # 返回值
        data['total'] = total
        data['rows'] = ywcs
    
    return data

def txxq_csgl_add2edit_sel_service( data_dic ):
    """
    # 参数新增2编辑页面初始化 service
    """
    # 初始化反馈信息
    result = {'state':False, 'msg':'','csxx_dic': {}}
    # 获取通讯参数信息
    if data_dic['id']:
        with sjapi.connection() as db:
            obj_lst = ModSql.common.execute_sql_dict( db, 'get_csdy_bm', data_dic )
            if obj_lst:
                result['csxx_dic'] = obj_lst[0]
    result['state'] = True
    result['msg'] = ''
    
    return result
    
def txxq_csgl_add_service( data_dic ):
    """
    # 通讯参数 新增 提交 service
    """
    # 反馈信息
    result = {'state':False, 'msg':''}
    
    with sjapi.connection() as db:
        # check 参数代码是否在同一通讯下重复
        check_count = ModSql.common.execute_sql_dict( db, 'check_csdm', data_dic )[0]['count']
        if check_count > 0:
            result['msg'] = '通讯参数[%s]已经存在，请重新录入' % data_dic['csdm']
            return result
        
        # 参数定义表 lx(类型 1:系统参数 2:业务参数 3:交易参数 4:通讯参数)
        # 操作人
        data_dic['czr'] = get_sess_hydm()
        # 操作时间
        data_dic['czsj'] = get_strftime()
        # id
        data_dic['id'] = get_uuid()
        # 保存
        ModSql.common.execute_sql( db, 'insert_csdy', data_dic )
        
        # 维护唯一码
        update_wym(db, 'cs', data_dic['id'])
        
        # 操作流水登记
        rznr = '参数代码[%s]，参数值[%s]，参数类型[%s]，参数描述[%s]，参数状态[%s]' % (data_dic['csdm'],data_dic['value'],data_dic['lx'],data_dic['csms'],data_dic['zt'])
        ins_czrz( db, '通讯参数新增：%s' % rznr, gnmc = '通讯参数管理_新增' )

        # 返回值
        result['state'] = True
        result['msg'] = '新增成功'
    
    return result
    
def txxq_csgl_edit_service( data_dic ):
    """
    # 通讯参数 编辑 提交 service
    """
    # 反馈信息
    result = {'state':False, 'msg':''}
    
    with sjapi.connection() as db:
        # 查询修改前的数据
        data_rs = ModSql.kf_txgl_001.execute_sql_dict( db, 'select_csdy', data_dic )[0]
        # 参数定义表 lx(类型 1:系统参数 2:业务参数 3:交易参数 4:通讯参数)
        # 操作人
        data_dic['czr'] = get_sess_hydm()
        # 操作时间
        data_dic['czsj'] = get_strftime()
        # 保存
        ModSql.common.execute_sql( db, 'update_csdy', data_dic )
        
        # 维护唯一码
        update_wym(db, 'cs', data_dic['id'])

        upd_befor = '编辑前：参数代码[%s]，参数值[%s]，参数类型[%s]，参数描述[%s]，参数状态[%s]' % (data_rs['csdm'],data_rs['value'] ,data_rs['lx'],data_rs['csms'] ,data_rs['zt'] )
        upd_after = '编辑后：参数代码[%s]，参数值[%s]，参数类型[%s]，参数描述[%s]，参数状态[%s]' % (data_rs['csdm'],data_dic['value'],data_rs['lx'],data_dic['csms'],data_dic['zt'])
        ins_czrz( db, '通讯参数编辑：%s，%s' % ( upd_befor, upd_after ), gnmc = '通讯参数管理_编辑' )
        
        result['state'] = True
        result['msg'] = '编辑成功'
    
    return result
    
def txxq_csgl_del_service( data_dic ):
    """
    # 通讯参数 删除 提交 service
    """
    # 反馈信息
    result = {'state':False, 'msg':''}
    
    with sjapi.connection() as db:
        # 获取被删除的参数编码
        rs = ModSql.common.execute_sql( db, "get_csdm", data_dic )
        # 删除系统参数
        ModSql.common.execute_sql( db, "delete_csdy", data_dic )
        # 登记操作日志
        ins_czrz( db,'%s(%s)_通讯详情-删除通讯参数[%s]' % ( data_dic['txmc'], data_dic['txbm'], ",".join( [ obj.csdm for obj in rs ] ) ), gnmc = '通讯参数管理_删除' )
        # 返回值
        result['state'] = True
        result['msg'] = '删除成功'
    
    return result

def txxq_cdtx_data_service( data_dic ):
    """
    # 通讯管理-通讯详情-C端通讯管理 数据表格初始化 service
    """
    data = {'total':0, 'rows':[]}
    with sjapi.connection() as db:
        # 查询总条数
        total = ModSql.kf_txgl_001.execute_sql_dict( db, "get_cdtx_count", data_dic )[0]['count']
        # 查询C端通讯信息
        cdtx = ModSql.kf_txgl_001.execute_sql_dict( db, "get_cdtx_xx", data_dic )
        # 挡板信息名称化
        # （1）挡板信息
        dbssid_db_lst = [ cdxx['dbssid'] for cdxx in cdtx if cdxx['dbssid'] and cdxx['dblx'] == '1' ]
        dbdy_dic = {}
        if dbssid_db_lst:
            rs_dbdy = ModSql.kf_txgl_001.execute_sql_dict( db, "get_dbdy_xx", { 'id_lst': dbssid_db_lst } )
            dbdy_dic = dict( [ [ obj['id'], obj['mc'] ] for obj in rs_dbdy ] )
        # （2）查询节点测试案例执行步骤信息( 对于选择已有测试案例的情况 )
        dbssid_jd_lst = [ cdxx['dbssid'] for cdxx in cdtx if cdxx['dbssid'] and cdxx['dblx'] != '1' ]
        if dbssid_jd_lst:
            rs_jdcsal = ModSql.kf_txgl_001.execute_sql_dict( db, "get_jdcsalzxbz_xx", { 'id_lst': dbssid_jd_lst } )
            jdcsal_dic = dict( [ [ obj['id'], obj['mc'] ] for obj in rs_jdcsal ] )
        # 查询测试案例信息
        # lx:2:子流程测试案例
        # ssid:2:子流程
        zlcdyid_lst = [ cdxx['zlcdyid'] for cdxx in cdtx if cdxx['zlcdyid'] ]
        dycsal_dic = {}
        if zlcdyid_lst:
            rs_dycsal = ModSql.kf_txgl_001.execute_sql_dict( db, "get_csal_count", { 'ssid_lst': zlcdyid_lst } )
            dycsal_dic = dict( [ [ obj['ssid'], obj['count'] ] for obj in rs_dycsal ] )
        # 整理反馈信息
        for cdxx in cdtx:
            # 挡板类型 1:挡板定义 2:测试案例执行步骤
            if cdxx['dbssid']:
                if cdxx['dblx'] == '1':
                    cdxx['dbmc'] = dbdy_dic.get( cdxx['dbssid'], cdxx['dbssid'] )
                else:
                    cdxx['dbmc'] = jdcsal_dic.get( cdxx['dbssid'], cdxx['dbssid'] )
            else:
                cdxx['dbmc'] = '无'
            # 测试案例数量
            cdxx['csalsl'] = dycsal_dic.get( cdxx['zlcdyid'], 0 )
            
        data['total'] = total
        data['rows'] = cdtx
    
    return data

def txxq_cdtx_add2edit_sel_service( data_dic ):
    """
    # C端管理新增2编辑页面初始化 service
    """
    # 反馈信息
    result = { 'state':False, 'msg':'','cdtxjbxx_dic': {},
                'yw_lst': [] }
    with sjapi.connection() as db:
        # 查询业务信息
        result['yw_lst'] = ModSql.kf_txgl_001.execute_sql_dict( db, "get_ywxx" )
        # 有cdtxid，则获取基本信息
        if data_dic['cdtxid']:
            rs_cdtx = ModSql.kf_txgl_001.execute_sql_dict( db, "get_cdtx_byid", data_dic )
            if rs_cdtx:
                result['cdtxjbxx_dic'] = rs_cdtx[0]
        result['state'] = True
        result['msg'] = ''
    
    return result

def txxq_cdtx_add2edit_dbjb_service( data_dic ):
    """
    # C端管理新增2编辑页面初始化 打包解包配置 service
    """
    # 反馈信息
    result = { 'state':False, 'msg':'','jbjd_lst': [],'yw_lst': [] }
    with sjapi.connection() as db:
        # 查询节点信息，组织打解包配置的下拉框数据
        # jdlx（节点类型） 5:打包节点 6:解包节点
        rs_jdxx = ModSql.kf_txgl_001.execute_sql_dict( db, "get_jddy_byjdlx", { 'jdlx_lst': ['5','6'] } )
        # 组织页面可用数据
        # 打包节点
        result['dbjd_lst'] = [ { 'data': jdxx['id'], 'value': jdxx['jdmc'] } for jdxx in rs_jdxx if jdxx['jdlx'] == '5' ]
        # 解包节点
        result['jbjd_lst'] = [ { 'data': jdxx['id'], 'value': jdxx['jdmc'] } for jdxx in rs_jdxx if jdxx['jdlx'] == '6' ]
        result['state'] = True
        result['msg'] = ''
    
    return result

def txxq_cdtx_add_service( data_dic ):
    """
    # 通讯管理-C端通讯管理 新增
    """
    # 反馈信息
    result = {'state':False, 'msg':''}
    
    with sjapi.connection() as db:
        # 校验C端通讯编码是否已经存在
        check_count = ModSql.kf_txgl_001.execute_sql_dict( db, "check_cdtx_bm", data_dic )[0]['count']
        if check_count <= 0:
            check_count = ModSql.kf_txgl_001.execute_sql_dict( db, "check_zlcdy_bm", data_dic )[0]['count']
        if check_count > 0:
            result['msg'] = 'C端通讯编码[%s]已经存在，请重新录入' % data_dic['bm']
            return result
        
        # 初始化：id，操作时间，行员代码
        data_dic['zlcdyid'] = get_uuid()
        # 子流程 lb: 类别 1:通讯子流程 2:普通子流程
        data_dic['lb'] = '1'
        # 子流程名称
        data_dic['mc'] = data_dic['dfjymc']
        data_dic['cdtxid'] = get_uuid()
        data_dic['czsj'] = get_strftime()
        data_dic['czr'] = get_sess_hydm()
        # 接口是否启用, 默认0：禁用
        data_dic['jkqyzt'] = '0'
        # 新增：子流程
        ModSql.kf_txgl_001.execute_sql( db, "insert_zlcdy", data_dic )
        # 新增：C端通讯管理
        ModSql.kf_txgl_001.execute_sql( db, "insert_cdtx", data_dic )
        # 新增流程流程布局、走向
        add_cdtx_lc( db, data_dic['jbjdid'], data_dic['dbjdid'], data_dic['zlcdyid'] )
        
        # 更新唯一码
        # C端通讯
        update_wym( db, 'cdtxgl', data_dic['cdtxid'] )
        # 子流程
        update_wym( db, 'zlc', data_dic['zlcdyid'] )

        # 操作日志流水登记
        rznr = 'C端通讯编码[%s]，对方交易码[%s]，对方交易名称[%s]，超时时间[%s]，打包配置[%s]，解包配置[%s]，通讯管理ID[%s]，所属业务ID[%s]' % (data_dic['bm'],data_dic['dfjym'],data_dic['dfjymc'],data_dic['cssj'],data_dic['dbjdid'],data_dic['jbjdid'],data_dic['txglid'],data_dic['ssywid'])
        ins_czrz( db, 'C端通讯新增：%s' % rznr, gnmc = 'C端通讯管理_新增' )

        # 组织反馈值
        result['state'] = True
        result['msg'] = '新增成功'
    
    return result
    
def txxq_cdtx_edit_service( data_dic ):
    """
    # 通讯管理-C端通讯管理 编辑 view
    """
    # 反馈信息
    result = {'state':False, 'msg':''}
    # 添加信息
    # 操作时间
    data_dic['czsj'] = get_strftime()
    # 操作人
    data_dic['czr'] = get_sess_hydm()
    # 子流程名称
    data_dic['mc'] = data_dic['dfjymc']
    with sjapi.connection() as db:
        # 查询修改前的数据
        data_rso = ModSql.kf_txgl_001.execute_sql_dict( db, 'select_cdtx', data_dic )[0]
        # 修改子流程
        ModSql.kf_txgl_001.execute_sql( db, "update_zlcdy", data_dic )
        # 修改C端通讯管理
        ModSql.kf_txgl_001.execute_sql( db, "update_cdtx", data_dic )
        # 更新流程布局表( 打包 )
        # 节点类型 = 1 -- 普通节点
        ModSql.kf_txgl_001.execute_sql( db, "update_lcbj_db", data_dic )
        # 更新流程布局表( 解包 )
        # 节点类型 = 1 -- 普通节点
        ModSql.kf_txgl_001.execute_sql( db, "update_lcbj_jb", data_dic )
        # 更新唯一码
        # C端通讯
        update_wym( db, 'cdtxgl', data_dic['cdtxid'] )
        # 子流程
        update_wym( db, 'zlc', data_dic['zlcdyid'] )
        
        # 清空缓存中对应的子流程
        memcache_data_del( [data_dic['zlcdyid']] )
        
        # 操作日志流水登记
        upd_befor = '编辑前：C端通讯编码[%s]，对方交易码[%s]，对方交易名称[%s]，超时时间[%s]，打包配置[%s]，解包配置[%s]，子流程定义ID[%s]，所属业务ID[%s]，通讯管理ID[%s]' % (data_rso['bm'],data_rso['dfjym'],data_rso['dfjymc'],data_rso['cssj'],data_rso['dbjdid'],data_rso['jbjdid'],data_rso['zlcdyid'],data_rso['ssywid'],data_rso['txglid'])
        upd_after = '编辑后：C端通讯编码[%s]，对方交易码[%s]，对方交易名称[%s]，超时时间[%s]，打包配置[%s]，解包配置[%s]，子流程定义ID[%s]，所属业务ID[%s]，通讯管理ID[%s]' % (data_rso['bm'],data_dic['dfjym'],data_dic['dfjymc'],data_dic['cssj'],data_dic['dbjdid'],data_dic['jbjdid'],data_dic['zlcdyid'],data_dic['ssywid'],data_rso['txglid'])
        ins_czrz( db, '通讯参数编辑：%s，%s' % ( upd_befor, upd_after ), gnmc = 'C端通讯管理_编辑' )
        # 提交，组织反馈值
        result['state'] = True
        result['msg'] = '修改成功'
    
    return result
    
def txxq_cdtx_del_service( data_dic ):
    """
    # C端通讯 删除 提交 service
    """
    # 初始化反馈信息
    result = {'state':False, 'msg':''}
    
    # 组织使用数据列表
    zlc_id_lst = [data_dic['zlcdyid']]
    cdtx_id_lst = [data_dic['cdtxid']]
    with sjapi.connection() as db:
        # 验证子流程是否有被其他流程使用
        zlc_sy_dic = check_zlc_sy( db, zlc_id_lst )
        # 只有存在一条子流程被使用则说明此C端通讯被使用，则不可删除
        if True in zlc_sy_dic.values():
            result['msg'] = "C端通讯已被交易使用，无法删除"
            return result
        
        # 删除子流程定义
        del_zcl( db, zlc_id_lst )
        # 删除子流程对应的测试案例
        del_zcl_csal( db, zlc_id_lst = zlc_id_lst )
        # 删除C端通讯对应挡板信息
        del_cdtx_dbxx( db, cdtx_id_lst )
        # C端通讯删除
        ModSql.kf_txgl_001.execute_sql( db, 'del_cdtx_byid', { 'id_lst': cdtx_id_lst } )
        
        # 清空缓存中对应的子流程
        memcache_data_del( [data_dic['zlcdyid']] )
        
        # 登记删除操作流水
        ins_czrz( db, '删除C端通讯[%s]' % ( data_dic['bm'] ), gnmc = 'C端通讯管理_删除' )
        result['state'] = True
        result['msg'] = '删除成功'
    
    return result
    
def txxq_jymjchs_service( data_dic ):
    """
    # 服务方 交易码检查函数 显示信息 service
    """
    # 初始化返回值
    data = { 'txid': data_dic['txid'], 'jcjymhsid': '', 'nr': '' }
    with sjapi.connection() as db:
        # 查询交易码检查函数id
        txglxx = ModSql.kf_txgl_001.execute_sql_dict( db, 'get_txgl_jcjymhsid', { 'txid': data_dic['txid'] } )
        # 存在信息
        if txglxx and txglxx[0]['jcjymhsid']:
            data['jcjymhsid'] = txglxx[0]['jcjymhsid']
            hsnrxx = txglxx = ModSql.common.execute_sql_dict( db, 'sel_blob_byid', { 'id': data['jcjymhsid'] } )
            if hsnrxx and hsnrxx[0]['nr']:
                data['nr'] = pickle.loads(hsnrxx[0]['nr'].read())
    
    return data
    
def txxq_jymjchs_sub_service( data_dic ):
    """
    # 服务方 交易码检查函数 显示信息 提交
    """
    result = {'state':False, 'msg':'', 'jcjymhsid': ''}
    # 校验函数内容的合法性
    check_hsnr = "def " + "test_mc()" + ":\n" + data_dic['nr']
    check_hsnr = check_hsnr.replace( '\n', '\n    ' )
    str_check = py_check( check_hsnr )
    if str_check != '':
        result['msg'] = "函数内容有语法错误：\n" + str_check
        return result
    # 操作人
    czr = get_sess_hydm()
    # 操作时间
    czsj = get_strftime()
    with sjapi.connection() as db:
        # 处理函数内容
        nr = pickle.dumps(data_dic['nr'])
        # 查询交易码检查函数id
        txglxx = ModSql.kf_txgl_001.execute_sql_dict( db, 'get_txgl_jcjymhsid', { 'txid': data_dic['txid'] } )
        if txglxx and txglxx[0]['jcjymhsid']:
            # 编辑
            jcjymhsid = txglxx[0]['jcjymhsid']
            sql_data = {'nr': nr, 'czr': czr, 'czsj':czsj, 'pkid':jcjymhsid}
            ModSql.common.execute_sql(db, "edit_blob2", sql_data)
            # 赋值
            result['jcjymhsid'] = jcjymhsid
        else:
            # 新增
            # 登记函数内容
            gl_blob_id = get_uuid()
            sql_data = {'blobid':gl_blob_id, 'lx':'gl_txgl', 'czr': czr, 'czsj':czsj, 'nr': nr}
            ModSql.common.execute_sql(db, "add_blob", sql_data)
            # 更新通讯管理表：
            sql_data_2 = { 'jcjymhsid': gl_blob_id, 'czr': czr, 'czsj':czsj, 'txid': data_dic['txid'] }
            ModSql.kf_txgl_001.execute_sql(db, "upd_cdtx_jcjymhsid", sql_data_2)
            # 赋值
            result['jcjymhsid'] = gl_blob_id
        # 更新模板定义表中的唯一码
        update_wym(db, 'txgl', data_dic['txid'])
        # 清除memcache
        if txglxx:
            memcache_data_del( [txglxx[0]['bm']] )
        # 组织反馈值
        result['state'] = True
        result['msg'] = '保存成功!'
    
    return result
    
def txxq_jymjchs_testzx_service( data_dic ):
    """
    # 服务方 交易码检查函数 test 提交
    """
    # 初始化返回值
    result = {'state':False, 'msg':''}
    # 获取通讯编码
    with sjapi.connection() as db:
        txxx_rs = ModSql.common.execute_sql(db, "get_txgl_mc", { 'ids': [ data_dic['txid'] ] })
        if txxx_rs:
            # 调用核心执行函数的api，将通讯的编码和录入的报文传入到函数中，核心进行执行
            # lx（类型，必填，jd-节点;zlc-子流程;jysb-交易码解出函数）、
            # 十六进制转化为二进制
            jsddbw = bytes().fromhex( data_dic['bw'].replace(' ','') )
            jyzd = transaction_test( 'jysb', txxx_rs[0]['bm'], jsddbw= jsddbw )
            # 写日志
            logger.info('交易码检查函数执行完反馈的结果：')
            logger.info(jyzd)
            # 核心返回的结果需要进行判断，当SYS_RspCode为“000000”时，提示：测试成功，然后将SYS_JYM的值展示出来，
            # 当SYS_RspCode为“TS9999”时，提示测试失败。
            if jyzd and jyzd['SYS_RspCode'] == '000000':
                result = {'state':True, 'msg': '测试成功，函数解出交易码为：%s。' % jyzd['SYS_JYM']}
            else:
                result['msg'] = '测试失败，请确认交易码解出函数以及发送的报文是否正确。'
        else:
            result['msg'] = '验证函数所在通讯不存在。'
    
    return result

def txxq_cdtx_yydb_service( data_dic ):
    """
    # 通讯管理-通讯详情-C端通讯管理 应用挡板 主页面 service
    """
    # 默认返回值
    data = {'cdtxid':data_dic['id'], 'dbssid':'', 'dblx':'', 'zlcdyid': ''}
    with sjapi.connection() as db:
        # 查询通讯信息
        rs_txxx = ModSql.common.execute_sql_dict( db, 'get_cdtx', data_dic )
        if rs_txxx:
            # 返回值
            data['dbssid'] = rs_txxx[0]['dbssid']
            data['dblx'] = rs_txxx[0]['dblx']
            data['zlcdyid'] = rs_txxx[0]['zlcdyid']
    
    return data

def txxq_cdtx_yydb_data_service( data_dic ):
    """
    # 通讯管理-通讯详情-C端通讯管理 应用挡板 data 数据 service
    """
    # 默认返回值
    data = {'total':0, 'rows':[]}
    with sjapi.connection() as db:
        # 查询总条数
        total = ModSql.kf_txgl_001.execute_sql_dict( db, 'dbgl_get_dbdy_count', data_dic )[0]['count']
        # 查询信息
        dbxx = ModSql.kf_txgl_001.execute_sql_dict( db, 'dbgl_get_dbdy', data_dic )
        # 返回值
        data['total'] = total
        data['rows'] = dbxx
    
    return data
    
def txxq_cdtx_yydb_add2edit_sel_service( data_dic ):
    """
    # 应用挡板 新增或编辑获取初始化页面数据
    """
    # 反馈信息
    result = { 'state':False, 'msg':'','yydb_dic': {},
                'scys_lst': {} }
    with sjapi.connection() as db:
        # 获取解包节点ID
        rs_cdtx = ModSql.common.execute_sql_dict( db, 'get_cdtx', { 'id': data_dic['cdtxid'] } )
        if rs_cdtx:
            # 获取解包节点要素( 输出要素 )
            rs_jdys = ModSql.common.execute_sql_dict( db, 'get_jdys', { 'id': rs_cdtx[0]['jbjdid'], 'lb': "2" } )
            if rs_jdys:
                result['scys_lst'] = dict( [ ( ysxx['bm'],{ 'id': '', 'ysmc': ysxx['bm'], 'ysz': ysxx['mrz'] if ysxx['mrz'] else '' } ) for ysxx in rs_jdys ] )
        # 有dbid，则获取基本信息
        if data_dic['dbid']:
            # 挡板信息
            rs_dbxx = ModSql.kf_txgl_001.execute_sql_dict( db, "dbgl_get_dbdy_byid", data_dic )
            if rs_dbxx:
                result['yydb_dic'] = rs_dbxx[0]
            # 挡板要素
            rs_dbys = ModSql.kf_txgl_001.execute_sql_dict( db, "dbgl_get_dbys_byid", data_dic )
            if rs_dbys:
                for ysxx in rs_dbys:
                    ys_dic = result['scys_lst'].get( ysxx['ysmc'] )
                    if ys_dic:
                        result['scys_lst'][ysxx['ysmc']]['id'] = ysxx['id']
                        result['scys_lst'][ysxx['ysmc']]['ysz'] = ysxx['ysz']
        # 组织反馈值
        result['scys_lst'] = sorted(result['scys_lst'].values(),key=lambda x:x['ysmc'])
        result['state'] = True
        result['msg'] = ''
    
    return result
    
def txxq_cdtx_yydb_add_service( data_dic ):
    """
    # 应用挡板 新增 提交 service
    """
    # 反馈信息
    result = {'state':False, 'msg':''}
    
    with sjapi.connection() as db:
        # check 简称是否在挡板表下重复
        check_count = ModSql.kf_txgl_001.execute_sql_dict( db, 'dbgl_check_jc', data_dic )[0]['count']
        if check_count > 0:
            result['msg'] = '简称[%s]已经存在，请重新录入' % data_dic['jc']
            return result
        
        # 挡板定义表
        # 操作人
        data_dic['czr'] = get_sess_hydm()
        # 操作时间
        data_dic['czsj'] = get_strftime()
        # id
        data_dic['id'] = get_uuid()
        # 保存
        ModSql.kf_txgl_001.execute_sql( db, 'dbgl_dbdy_insert', data_dic )
        # 新增挡板要素( id|ysmc|ysz,id|ysmc|ysz,…… )
        rz_ys_str = ''
        for id2ysmc, ysz in data_dic['ysxx_str'].items():
            if id2ysmc:
                ysxx_lst = id2ysmc.split('|')
                data_dic_ys = { 'id': get_uuid(), 'dbdyid': data_dic['id'], 
                                'ysmc': ysxx_lst[1], 'ysz': ysz if ysz else '' }
                ModSql.kf_txgl_001.execute_sql( db, 'dbys_insert', data_dic_ys )
                rz_ys_str = '%s,%s:%s' % ( rz_ys_str,ysxx_lst[1],ysz if ysz else '' )
        rznr = '应用挡板简称:[%s],应用挡板名称:[%s],应用挡板描述:[%s],应用挡板返回值:[%s],C端通讯ID:[%s],输出要素[%s]' % (data_dic['jc'],data_dic['mc'],data_dic['ms'],data_dic['fhz'],data_dic['cdtxid'],rz_ys_str[1:])
        ins_czrz( db, '应用挡板新增：%s' % rznr, gnmc = 'C端通讯管理_应用挡板新增' )
        # 返回值
        result['state'] = True
        result['msg'] = '新增成功'
    
    return result
    
def txxq_cdtx_yydb_edit_service( data_dic ):
    """
    # 应用挡板 编辑 提交 service
    """
    # 反馈信息
    result = {'state':False, 'msg':''}
    
    with sjapi.connection() as db:
        # 查询编辑前挡板信息
        data_con = ModSql.kf_txgl_001.execute_sql( db, 'select_dbgl_dbdy', data_dic )[0]
        # 挡板定义表
        # 操作人
        data_dic['czr'] = get_sess_hydm()
        # 操作时间
        data_dic['czsj'] = get_strftime()
        # 保存
        ModSql.kf_txgl_001.execute_sql( db, 'dbgl_dbdy_upd', data_dic )
        # 新增挡板要素( id|ysmc|ysz,id|ysmc|ysz,…… )
        rz_srq_str = ''
        rz_srh_str = ''
        for id2ysmc, ysz in data_dic['ysxx_str'].items():
            if id2ysmc:
                ysxx_lst = id2ysmc.split('|')
                # id存在，则编辑
                if ysxx_lst[0]:
                    data_dic_ys = { 'ysid': ysxx_lst[0], 'ysz': ysz if ysz else '' }
                    data_com = ModSql.kf_txgl_001.execute_sql( db, 'select_dbys', data_dic_ys )[0]
                    ModSql.kf_txgl_001.execute_sql( db, 'dbys_upd', data_dic_ys )
                    rz_srq_str = '%s,%s:%s' % ( rz_srq_str,data_com['ysmc'],data_com['ysz'] )
                # id不存在，则新增
                else:
                    data_dic_ys = { 'id': get_uuid(), 'dbdyid': data_dic['dbid'], 
                                    'ysmc': ysxx_lst[1], 'ysz': ysz if ysz else '' }
                    ModSql.kf_txgl_001.execute_sql( db, 'dbys_insert', data_dic_ys )
                rz_srh_str = '%s,%s:%s' % ( rz_srh_str,ysxx_lst[1],ysz if ysz else '' )
        upd_befor = '编辑前：应用挡板简称:[%s],应用挡板名称:[%s],应用挡板描述:[%s],应用挡板返回值:[%s],C端通讯ID:[%s],输出要素[%s]' % (data_con['jc'],data_con['mc'],data_con['ms'],data_con['fhz'],data_con['cdtxid'],rz_srq_str[1:])
        upd_after = '编辑后：应用挡板简称:[%s],应用挡板名称:[%s],应用挡板描述:[%s],应用挡板返回值:[%s],C端通讯ID:[%s],输出要素[%s]' % (data_con['jc'],data_dic['mc'],data_dic['ms'],data_dic['fhz'],data_con['cdtxid'],rz_srh_str[1:])
        ins_czrz( db, '应用挡板编辑：%s，%s' % ( upd_befor, upd_after ), gnmc = 'C端通讯管理_应用挡板编辑' )
        # 返回值
        result['state'] = True
        result['msg'] = '编辑成功'
    
    return result
    
def txxq_cdtx_yydb_del_service( data_dic ):
    """
    # 应用挡板 删除 提交 service
    """
    # 反馈信息
    result = {'state':False, 'msg':''}
    
    with sjapi.connection() as db:
        # 查询挡板是否已被使用
        check_count = ModSql.kf_txgl_001.execute_sql_dict( db, 'dbgl_check_dbsy', data_dic )[0]['count']
        if check_count > 0:
            result['msg'] = '挡板已被使用，不可删除'
            return result
        
        # 删除挡板信息：
        ModSql.kf_txgl_001.execute_sql( db, "dbgl_dbdy_del", data_dic )
        # 删除挡板要素
        ModSql.kf_txgl_001.execute_sql( db, "dbys_del", data_dic )
        # 登记操作日志
        ins_czrz( db,'C端通讯挡板，挡板[%s(%s)]已被删除' % ( data_dic['jc'], data_dic['mc']  ), gnmc = 'C端通讯管理_应用挡板删除' )
        # 返回值
        result['state'] = True
        result['msg'] = '删除成功'
    
    return result
    
def txxq_cdtx_yydb_sel_service( data_dic ):
    """
    # 应用挡板 挡板选择 提交 service
    """
    # 反馈信息
    result = {'state':False, 'msg':''}
    
    with sjapi.connection() as db:
        #选择挡板：
        ModSql.kf_txgl_001.execute_sql( db, "dbgl_dbdy_sel", data_dic )
        # 更新唯一码
        # C端通讯
        update_wym( db, 'cdtxgl', data_dic['cdtxid'] )
        # 返回值
        result['state'] = True
        result['msg'] = '选择成功'
    
    return result

def txxq_cdtx_yydb_del_sel_service( data_dic ):
    """
    # 应用挡板 删除选择的挡板 提交 service
    """
    # 反馈信息
    result = {'state':False, 'msg':''}
    
    with sjapi.connection() as db:
        #选择挡板：
        ModSql.kf_txgl_001.execute_sql( db, "dbgl_dbdy_del_sel", data_dic )
        # 更新唯一码
        # C端通讯
        update_wym( db, 'cdtxgl', data_dic['cdtxid'] )
        # 返回值
        result['state'] = True
        result['msg'] = '删除成功'
    
    return result
    
def txxq_cdtx_testdb_data_service( data_dic ):
    """
    # 通讯管理-通讯详情-C端通讯管理 测试案例挡板 data 数据
    """
    # 默认返回值
    data = {'total':0, 'rows':[]}
    with sjapi.connection() as db:
        # 查询总条数
        total = ModSql.kf_txgl_001.execute_sql_dict( db, 'dbgl_get_testdb_count', data_dic )[0]['count']
        # 查询信息
        dbxx_lst = ModSql.kf_txgl_001.execute_sql_dict( db, 'dbgl_get_testdb_xx', data_dic )
        # 查询交易名称
        # 交易
        jydyid_lst = [ dbxx['ssid'] for dbxx in dbxx_lst if dbxx['sslb'] == '1' ]
        jyidmc_dic = get_jydy_mc( db, jydyid_lst )
        # 子流程
        zlcdyid_lst = [ dbxx['ssid'] for dbxx in dbxx_lst if dbxx['sslb'] == '2' ]
        zlcidmc_dic = get_zlcdy_mc( db, zlcdyid_lst )
        for dbxx in dbxx_lst:
            if dbxx['sslb'] == '1':
                dbxx['jymc'] = jyidmc_dic.get( dbxx['ssid'], '' )
            elif dbxx['sslb'] == '2':
                dbxx['jymc'] = zlcidmc_dic.get( dbxx['ssid'], '' )
        
        # 返回值
        data['total'] = total
        data['rows'] = dbxx_lst
    
    return data

def txxq_cdtx_testdb_query_service( data_dic ):
    """
    # 应用挡板 新增或编辑获取初始化页面数据
    """
    # 反馈信息
    result = { 'state':False, 'msg':'','fhz': '',
                'scys_lst': [] }
    with sjapi.connection() as db:
        # 获取输出要素信息
        rs_ys = ModSql.common.execute_sql_dict( db, 'get_jdcsalys', data_dic )
        # 组织反馈值
        result['scys_lst'] = rs_ys
        result['state'] = True
        result['msg'] = ''
    
    return result

def txxq_cdtx_csal_service( data_dic ):
    """
    # 通讯管理-通讯详情-C端通讯管理 测试案例 主页面 service
    """
    # 默认返回值
    data = {'cdtxid':data_dic['id'], 'dfjymc': '', 'zlcdyid': '', 'ssywid': ''}
    with sjapi.connection() as db:
        # 查询通讯信息
        rs_txxx = ModSql.common.execute_sql_dict( db, 'get_cdtx', data_dic )
        if rs_txxx:
            # 返回值
            data['dfjymc'] = rs_txxx[0]['dfjymc']
            data['zlcdyid'] = rs_txxx[0]['zlcdyid']
            data['ssywid'] = rs_txxx[0]['ssywid']
    
    return data
    
def txxq_cdtx_csal_data_service( data_dic ):
    """
    # 通讯管理-通讯详情-C端通讯管理 测试案例 data 数据
    """
    # 默认返回值
    data = {'total':0, 'rows':[]}
    with sjapi.connection() as db:
        # 查询总条数
        total = ModSql.kf_txgl_001.execute_sql_dict( db, 'get_csal_xx_count', data_dic )[0]['count']
        # 查询信息
        csalxx = ModSql.kf_txgl_001.execute_sql_dict( db, 'get_csal_xx', data_dic )
        
        # 返回值
        data['total'] = total
        data['rows'] = csalxx
    
    return data
    
def txxq_cdtx_csal_add2edit_sel_service( data_dic ):
    """
    # 测试案例 新增或编辑获取初始化页面数据
    """
    # 反馈信息
    result = { 'state':False, 'msg':'','cdal_dic': {},
                'srys_lst': {}, 'scys_lst': {}, 'ywmc': '' }
    
    with sjapi.connection() as db:
        # 查询业务名称
        rs_yw = ModSql.common.execute_sql_dict( db, 'get_ywdy', data_dic )
        if rs_yw:
            result['ywmc'] = rs_yw[0]['ywmc']
        if not data_dic['csaldyid']:
            # 查询打包节点的输入要素
            rs_sr_jdys = ModSql.kf_txgl_001.execute_sql_dict( db, 'get_ys_bycdtxid', { 'cdtxid': data_dic['cdtxid'], 'zd_lst': ['dbjdid'], 'lb': "1" } )
            if rs_sr_jdys:
                result['srys_lst'] = dict( [ ( ysxx['bm'],{ 'id': '', 'ysdm': ysxx['bm'], 'ysz': ysxx['mrz'] if ysxx['mrz'] else '' } ) for ysxx in rs_sr_jdys ] )
            # 查询解包节点的输出要素
            rs_sc_jdys = ModSql.kf_txgl_001.execute_sql_dict( db, 'get_ys_bycdtxid', { 'cdtxid': data_dic['cdtxid'], 'zd_lst': ['jbjdid'], 'lb': "2" } )
            if rs_sc_jdys:
                result['scys_lst'] = dict( [ ( ysxx['bm'],{ 'id': '', 'ysdm': ysxx['bm'], 'ysz': ysxx['mrz'] if ysxx['mrz'] else '' } ) for ysxx in rs_sc_jdys ] )
        # 有csalid，则获取基本信息
        else:
            # 测试案例信息
            rs_csalxx = ModSql.common.execute_sql_dict( db, "get_csalxx_byid", data_dic )
            if rs_csalxx:
                result['cdal_dic'] = rs_csalxx[0]
            #打包节点测试案例执行步骤ID  = 节点测试案例执行步骤列表.split(“，”)[0]
            dbjdbzid = result['cdal_dic']['jdcsalzxbzlb'].split(',')[0]
            #解包节点测试案例执行步骤ID = 节点测试案例执行步骤列表.split(“，”)[2]
            jbjdbzid = result['cdal_dic']['jdcsalzxbzlb'].split(',')[2]
            # 要素(输入)
            rs_sr_jdys = ModSql.common.execute_sql_dict( db, "get_jdcsalys", { 'jdcsalzxbz': dbjdbzid, 'lb': '1' } )
            if rs_sr_jdys:
                result['srys_lst'] = dict( [ ( ysxx['ysdm'],{ 'id': ysxx['id'], 'ysdm': ysxx['ysdm'], 'ysz': ysxx['ysz'] if ysxx['ysz'] else '', 'yysz': ysxx['ysz'] if ysxx['ysz'] else '' } ) for ysxx in rs_sr_jdys ] )
            # 要素(输出)
            rs_sc_jdys = ModSql.common.execute_sql_dict( db, "get_jdcsalys", { 'jdcsalzxbz': jbjdbzid, 'lb': '2' } )
            if rs_sc_jdys:
                result['scys_lst'] = dict( [ ( ysxx['ysdm'],{ 'id': ysxx['id'], 'ysdm': ysxx['ysdm'], 'ysz': '' } ) for ysxx in rs_sc_jdys ] )
        
        # 组织反馈值
        result['scys_lst'] = sorted(result['scys_lst'].values(),key=lambda x:x['ysdm'])
        result['srys_lst'] = sorted(result['srys_lst'].values(),key=lambda x:x['ysdm'])
        result['state'] = True
        result['msg'] = ''
    
    return result
    
def txxq_cdtx_csal_add_service( data_dic ):
    """
    # 测试案例 新增 提交 service
    """
    # 反馈信息
    result = {'state':False, 'msg':''}
    
    with sjapi.connection() as db:
        # check 名称是否在测试案例表下重复
        check_count = ModSql.common.execute_sql_dict( db, 'check_csaldy_mc', data_dic )[0]['count']
        if check_count > 0:
            result['msg'] = '测试案例名称[%s]已经存在，请重新录入' % data_dic['mc']
            return result
        # 获取通讯节点信息( jdlx: 7：通讯节点 )
        rs_txjd = ModSql.kf_txgl_001.execute_sql_dict( db, "get_jddy_byjdlx", { 'jdlx_lst': ['7'] } )
        if not rs_txjd:
            result['msg'] = '通讯节点未初始化，请先初始化通讯节点，再新增测试案例'
            return result
        # 查询通讯信息
        rs_txxx = ModSql.common.execute_sql_dict( db, 'get_cdtx', { 'id': data_dic['cdtxid'] } )
        if not rs_txxx:
            result['msg'] = 'C端通讯不存在，请联系管理员'
            return result
        # 测试案例定义id
        csaldyid = get_uuid()
        # 节点测试案例执行步骤
        jddyid_dic = { 'dbjd': rs_txxx[0]['dbjdid'], 'txjd': rs_txjd[0]['id'], 'jbjd': rs_txxx[0]['jbjdid'] }
        jdbzid_dic = { 'dbjd': get_uuid(), 'txjd': get_uuid(), 'jbjd': get_uuid() }
        for jd_key in jddyid_dic.keys():
            sql_data = { 'id': jdbzid_dic[jd_key],
                'lx': '1', 'ssdyid': jddyid_dic[jd_key], 
                'csaldyid': csaldyid, 'fhz': '0', 'mc': '', 'ms': '', 'sftg': '0', 'demoid': '', 'rzlsh':'' }
            ModSql.common.execute_sql_dict( db, 'insert_jdcsalzxbz', sql_data )
        # 节点测试案例要素
        rz_sr_str = ''
        # 输入( id^ysdm^ysz~id^ysdm^ysz~…… )
        for ysxx in data_dic['ysxx_sr_str'].split('~'):
            if ysxx:
                sql_data = { 'id': get_uuid(), 'jdcsalzxbz': jdbzid_dic['dbjd'], 'lx': '1', 
                        'ysdm': ysxx.split('^')[1], 
                        'ysz': ysxx.split('^')[2] if ysxx.split('^')[2] else ''  }
                ModSql.common.execute_sql_dict( db, 'insert_jdcsalys', sql_data )
                rz_sr_str = '%s,%s:%s' % ( rz_sr_str,ysxx.split('^')[1],ysxx.split('^')[2] if ysxx.split('^')[2] else '' )
        # 输出( id^ysdm^ysz~id^ysdm^ysz,…… )
        rz_sc_str = ''
        for ysxx in data_dic['ysxx_sc_str'].split('~'):
            if ysxx:
                sql_data = { 'id': get_uuid(), 'jdcsalzxbz': jdbzid_dic['jbjd'], 'lx': '2', 
                        'ysdm': ysxx.split('^')[1], 'ysz': ''  }
                ModSql.common.execute_sql_dict( db, 'insert_jdcsalys', sql_data )
                rz_sc_str = '%s,%s:%s' % ( rz_sc_str,ysxx.split('^')[1],'' )
        # 新增测试案例
        sql_data = { 'id': csaldyid, 'lb': '4', 'mc': data_dic['mc'], 'ms': data_dic['ms'],
            'jdcsalzxbzlb': ','.join( [jdbzid_dic['dbjd'], jdbzid_dic['txjd'], jdbzid_dic['jbjd']] ),
            'ssywid': data_dic['ssywid'], 'sslb': '2', 'ssid': data_dic['zlcdyid'],
            'demoid': '', 'rzlsh': '', 'zjzxsj': '', 'zjzxr': '', 'ssjy_id': '' }
        ModSql.common.execute_sql_dict( db, 'insert_csaldy', sql_data )

        # 操作日志流水登记
        rznr = '测试案例名称:[%s],测试案例描述:[%s],C端通讯ID:[%s],所属业务ID:[%s],输入要素[%s],输出要素[%s]' % (data_dic['mc'],data_dic['ms'],data_dic['cdtxid'],data_dic['ssywid'],rz_sr_str[1:],rz_sc_str[1:])
        ins_czrz( db, '测试案例新增：%s' % rznr, gnmc = 'C端通讯管理_测试案例新增' )
        
        # 返回值
        result['state'] = True
        result['msg'] = '新增成功'
    
    return result
    
def txxq_cdtx_csal_edit_service( data_dic ):
    """
    # 测试案例 编辑 提交 service
    """
    # 反馈信息
    result = {'state':False, 'msg':''}
    
    with sjapi.connection() as db:
        # 更新测试案例信息
        data_con = ModSql.kf_txgl_001.execute_sql_dict( db, 'select_csaldy', data_dic )[0]
        # 更新测试案例信息
        ModSql.common.execute_sql_dict( db, 'update_csaldy', data_dic )
        # 输入( id^ysdm^ysz~id^ysdm^ysz~…… )
        rz_srq_str = ''
        rz_srh_str = ''
        for ysxx in data_dic['ysxx_sr_str'].split('~'):
            if ysxx:
                sql_data = { 'ysid': ysxx.split('^')[0], 'ysz': ysxx.split('^')[2] if ysxx.split('^')[2] else '' }
                data_com = ModSql.kf_txgl_001.execute_sql_dict( db, 'select_jdcsalys', sql_data )[0]
                ModSql.common.execute_sql_dict( db, 'update_jdcsalys', sql_data )
                rz_srq_str = '%s,%s:%s' % ( rz_srq_str,data_com['ysdm'],data_com['ysz'] )
                rz_srh_str = '%s,%s:%s' % ( rz_srh_str,data_com['ysdm'],ysxx.split('^')[2] if ysxx.split('^')[2] else '' )
        # 查询修改前的信息
        upd_befor = '编辑前：测试案例名称:[%s],测试案例描述:[%s],C端通讯ID:[%s],所属业务ID:[%s],输入要素[%s]' % (data_con['mc'],data_con['ms'],data_con['ssid'],data_con['ssywid'],rz_srq_str[1:])
        upd_after = '编辑后：测试案例名称:[%s],测试案例描述:[%s],C端通讯ID:[%s],所属业务ID:[%s],输入要素[%s]' % (data_con['mc'],data_dic['ms'],data_con['ssid'],data_con['ssywid'],rz_srh_str[1:])
        ins_czrz( db, '测试案例编辑：%s，%s' % ( upd_befor, upd_after ), gnmc = 'C端通讯管理_测试案例编辑' )
        # 返回值
        result['state'] = True
        result['msg'] = '编辑成功'
    
    return result
    
def txxq_cdtx_csal_del_service( data_dic ):
    """
    # 测试案例 删除 提交 service
    """
    # 反馈信息
    result = {'state':False, 'msg':''}
    
    with sjapi.connection() as db:
        # 删除测试案例信息
        del_zcl_csal( db, csal_id_lst = data_dic['id_lst'] )
        # 登记操作日志
        ins_czrz( db,'删除测试案例【%s】' % ( data_dic['ids_mc'] ), gnmc = 'C端通讯管理_测试案例删除' )
        # 返回值
        result['state'] = True
        result['msg'] = '删除成功'
    
    return result
    
def txxq_cdtx_jkjy_qyjy_sel_service( data_dic ):
    """
    # 测试案例 新增或编辑获取初始化页面数据
    """
    # 反馈信息
    result = {'cdtxid':data_dic['cdtxid'], 'ssyw':'', 'ssjk':'', 'zt': ''}
    
    with sjapi.connection() as db:
        # 查询交易信息( 接口校验信息 )
        rs_yw = ModSql.kf_txgl_001.execute_sql_dict( db, 'get_jkjy_xx', data_dic )
        if rs_yw:
            if rs_yw[0]['ywmc']:
                result['ssyw'] = rs_yw[0]['ywmc']
            else:
                result['ssyw'] = ''
            result['ssjk'] = rs_yw[0]['dfjymc']
            result['zt'] = rs_yw[0]['jkqyzt']
        # 组织反馈值
        result['state'] = True
        result['msg'] = ''
    
    return result

def txxq_cdtx_jkjy_qyjy_sel_data_service( data_dic ):
    """
    # C端通讯 接口校验 启用禁用 页面初始化数据准备 data 数据
    """
        # 默认返回值
    data = {'total':0, 'rows':[]}
    with sjapi.connection() as db:
        # 查询C端通讯打包节点输入要输信息
        data_dic['lb'] = '1'
        data_dic['zd_lst'] = ['dbjdid']
        rs_ysxx = ModSql.kf_txgl_001.execute_sql_dict( db, 'get_ys_bycdtxid', data_dic )
        # 返回值
        data['rows'] = rs_ysxx
    
    return data
    
def txxq_cdtx_jkjy_qyjy_service( data_dic ):
    """
    # C端通讯 接口校验 启用禁用 页面提交
    """
    # 反馈信息
    result = {'state':False, 'msg':''}
    # 添加信息
    # 操作时间
    data_dic['czsj'] = get_strftime()
    # 操作人
    data_dic['czr'] = get_sess_hydm()
    with sjapi.connection() as db:
        # 查询修改前的数据
        data_con = ModSql.kf_txgl_001.execute_sql_dict( db, 'select_cdtx', data_dic )[0]
        # 修改C端通讯管理
        ModSql.kf_txgl_001.execute_sql( db, "update_cdtx_jkqyzt", data_dic )
        # 更新唯一码
        # C端通讯
        update_wym( db, 'cdtxgl', data_dic['cdtxid'] )
        # 登记操作流水日志
        upd_befor = '编辑前：C端通讯编码[%s]，接口启用状态[%s]' % (data_con['bm'],data_con['jkqyzt'])
        upd_after = '编辑后：C端通讯编码[%s]，接口启用状态[%s]' % (data_con['bm'],data_dic['jkqyzt'])
        ins_czrz( db, '接口校验启用禁用编辑：%s，%s' % ( upd_befor, upd_after ), gnmc = '接口校验启用禁用_编辑' )
        # 提交，组织反馈值
        result['state'] = True
        result['msg'] = '修改成功'
    
    return result
    
def txxq_cdtx_jkjy_qyjy_jdys_sel_service( data_dic ):
    """
    # C端通讯 接口校验 节点要素编辑 页面初始化
    """
    # 反馈信息
    result = { 'state':False, 'msg':'','zddm': '', 'zdmc': '',
                'sfjkjy': '', 'jygzmc': 'zjcs', 'jygz_lst': [{'value': '请选择', 'ms': '', 'text': ''}] }
    
    with sjapi.connection() as db:
        # 查询节点要素信息
        rs_jdysxx = ModSql.common.execute_sql_dict( db, 'get_jdys_byid', data_dic )
        if rs_jdysxx:
            result['zddm'] = rs_jdysxx[0]['bm']
            result['zdmc'] = rs_jdysxx[0]['ysmc']
            result['sfjkjy'] = rs_jdysxx[0]['jkjy']
            result['jygzmc'] = rs_jdysxx[0]['ssgzmc']
            result['zjcs'] = rs_jdysxx[0]['zjcs']
        # 获取校验规则(10006: 接口有效性校验规则)
        result['jygz_lst'].extend( get_bmwh_bm( '10006', db = db ) )
        # 组织反馈值
        result['state'] = True
        result['msg'] = ''
    
    return result
    
def txxq_cdtx_jkjy_qyjy_jdys_service( data_dic ):
    """
    # C端通讯 接口校验 节点要素编辑 提交
    """
    # 反馈信息
    result = {'state':False, 'msg':''}
    
    with sjapi.connection() as db:
        data_con = ModSql.common.execute_sql_dict( db, 'get_jdys_byid', data_dic )[0]
        # 更新节点要素
        ModSql.kf_txgl_001.execute_sql_dict( db, 'update_jdys', data_dic )
        # 更新唯一码
        # 节点定义id
        rs_jdysxx = ModSql.common.execute_sql_dict( db, 'get_jdys_byid', data_dic )
        if rs_jdysxx:
            update_wym( db, 'jd', rs_jdysxx[0]['jddyid'] )
            # 返回值
            result['state'] = True
            result['msg'] = '编辑成功'
        else:
            result['msg'] = '修改对应节点唯一码失败。'
        # 操作流水日志登记
        upd_befor = '编辑前：字段代码[%s]，字段名称[%s]，是否有效[%s]，校验规则[%s]，追加参数[%s]' % (data_con['bm'],data_con['ysmc'],data_con['jkjy'],data_con['ssgzmc'],data_con['zjcs'] if data_con['zjcs'] else '')
        upd_after = '编辑后：字段代码[%s]，字段名称[%s]，是否有效[%s]，校验规则[%s]，追加参数[%s]' % (data_con['bm'],data_con['ysmc'],data_dic['jkjy'],data_dic['ssgzmc'],data_dic['zjcs'])
        ins_czrz( db, '接口校验节点要素编辑：%s，%s' % ( upd_befor, upd_after ), gnmc = '接口校验节点要素_编辑' )
    
    return result

def dr_data_service( ):
    """
    # 通讯管理-获取导入窗口中下拉框数据
    """
    # 反馈信息
    data = {'total':0, 'rows':[]}
    # 数据库操作
    with sjapi.connection() as db:
        txglxx = ModSql.kf_txgl_001.execute_sql_dict( db, 'dr_data_rs' )
        txglxx.insert(0,{'id':'-1',"mc":'导入新通讯'})
        data['rows'] = txglxx
    return data
    
def txxq_cdtx_czpz_service( data_dic ):
    """
    # 获取所属业务对应的通讯子流程 service
    """
    # 反馈信息
    result = {'state':False, 'msg':'', 'czpz_lst': []}
    # 数据库操作
    with sjapi.connection() as db:
        czpz_lst = ModSql.kf_txgl_001.execute_sql_dict( db, 'select_zcl_byssywid', data_dic )
        result['czpz_lst'] = czpz_lst
        result['state'] = True
        result['msg'] = '查询成功'
    
    return result
    
    
    
    