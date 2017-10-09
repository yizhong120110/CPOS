# -*- coding: utf-8 -*-
# Action: 通讯管理 公共函数
# Author: zhangchl
# AddTime: 2015-01-16
# Standard: 注释仅能以“#”开头，sql可以是“--”；注释不能同代码在同一行
import os
from sjzhtspj import settings, OCMDIR, ICPDIR, ModSql, logger
from sjzhtspj.common import get_file, update_wym, get_uuid


def get_txwjmc( txlxbm, fwfx ):
    """
    # 通讯文件名称下拉列表数据
    # 参数：
        txlxbm： 通讯类型编码
        fwfx: 服务方向： 1（客户端） 2（服务端）
    """
    logger.info( '服务方向：%s' % fwfx )
    #     判断路径存在
    #if fwfx and fwfx=='1':
    #    if ICPDIR is None or ICPDIR =='':
    #        txwjmc_lst=[]
    #        return txwjmc_lst
    #if fwfx and fwfx=='2':
    #    if OCMDIR is None or OCMDIR =='':
    #        txwjmc_lst=[]
    #        return txwjmc_lst
    # 文件路径( 定义目录 + 通讯类型编码 )
    fpath = os.path.join( OCMDIR if fwfx == '1' else ICPDIR, txlxbm )
    logger.info( '获取路径：%s' % fpath )
    if os.path.exists(fpath) == False:
        os.makedirs( fpath )
    # 获取文件集合
    ret_file_lst = get_file(fpath)
    txwjmc_lst = [ { 'value': fname, 'text': fname } for fname in ret_file_lst ]
    return txwjmc_lst

def get_zlc( db, txid, txbm ):
    """
    # 根据通讯id查询子流程信息
    """
    # 反馈错误信息
    msg = ''
    # 获取该通讯下所有的C端通讯ID及子流程ID
    cdtx_rs = ModSql.kf_txgl_001.execute_sql( db, 'del_get_zlc', { 'txid': txid } )
    # C端通讯id列表
    cdtx_id_lst = [ cdtx_obj.id for cdtx_obj in cdtx_rs ]
    # 子流程id列表
    zlc_id_lst = [ cdtx_obj.zlcdyid for cdtx_obj in cdtx_rs if cdtx_obj.zlcdyid ]
    
    # 查询流程布局，校验该通讯下所有的C端通讯对应的子流程是否已被交易使用
    if zlc_id_lst:
        zlc_sy_dic = check_zlc_sy( db, zlc_id_lst )
        # 只有存在一条子流程被使用则说明此C端通讯被使用，则不可删除
        if True in zlc_sy_dic.values():
            msg = "通讯[%s]下的C端通讯已被交易使用，无法删除" % ( txbm )
    
    return cdtx_id_lst, zlc_id_lst, msg

def check_zlc_sy( db, zlc_id_lst ):
    """
    # 验证子流程是否被其他流程使用
    # 返回值：
        zlc_sy_dic = { 子流程id：使用（True），未使用（Fasle） }
    """
    rs = ModSql.kf_txgl_001.execute_sql_dict( db, 'del_check_dy', { 'jddyid_lst': zlc_id_lst } )
    zlc_sy_dic = dict( [ [ obj['jddyid'], True if obj['count'] > 0 else False ] for obj in rs ] )
    
    return zlc_sy_dic

def del_zcl( db, zlc_id_lst ):
    """
    # 根据子流程id列表组织删除相关定义数据
    # @param: del_sql_lst: 删除sql列表
    # @param: del_sql_data： 删除sql使用数据库列表
    """
    # 删除流程布局
    ModSql.kf_txgl_001.execute_sql( db, 'del_zlc_lcbj', { 'sszlcid_lst': zlc_id_lst } )
    # 删除流程走向
    # 所属类别
    #   1:交易
    #   2:子流程
    ModSql.kf_txgl_001.execute_sql( db, 'del_zlc_lczx', { 'sslb': '2', 'ssid_lst': zlc_id_lst } )
    # 子流程删除
    ModSql.kf_txgl_001.execute_sql( db, 'del_zlc', { 'id_lst': zlc_id_lst } )

def del_zcl_csal( db, zlc_id_lst = [], csal_id_lst = [] ):
    """
    # 删除子流程对应的测试案例（ 输入参数是或者的关系 ）
    # zlc_id_lst: 子流程id列表
    # csal_id_lst： 测试案例id列表
    """
    # 根据子流程获取子流程测试案例信息
    csal_rs = []
    if zlc_id_lst:
        csal_rs = ModSql.kf_txgl_001.execute_sql( db, 'del_zlc_getcsal', { 'ssid_lst': zlc_id_lst } )
    # 根据测试案例id获取测试案例信息
    elif csal_id_lst:
        csal_rs = ModSql.kf_txgl_001.execute_sql( db, 'get_csaldy_byid', { 'id_lst': csal_id_lst } )
    
    # 节点测试案例执行步骤ID列表
    zxbz_id_lst = []
    for csal_obj in csal_rs:
        # 节点测试案例执行步骤列表 存在
        if csal_obj.jdcsalzxbzlb:
            zxbzlb_lst = [ bzid for bzid in csal_obj.jdcsalzxbzlb.split(',') if bzid ]
            zxbz_id_lst.extend( zxbzlb_lst )
        # 把节点id添加到测试案例id列表中
        if zlc_id_lst:
            csal_id_lst.append( csal_obj.id )
    
    # 根据查询结果进行删除
    if zxbz_id_lst:
        # 删除节点测试案例要素
        ModSql.kf_txgl_001.execute_sql( db, 'del_zlc_jdcsalyz', { 'jdcsalzxbz_lst': zxbz_id_lst } )
        # 删除节点测试案例执行步骤
        ModSql.kf_txgl_001.execute_sql( db, 'del_zlc_jdcsalzxbz', { 'id_lst': zxbz_id_lst } )
    if csal_id_lst:
        # 子流程测试案例删除
        ModSql.kf_txgl_001.execute_sql( db, 'del_csaldy', { 'id_lst': csal_id_lst } )

def del_cdtx_dbxx( db, cdtx_id_lst ):
    """
    # 删除C端通讯对应的挡板信息
    # @params: cdtx_id_lst: C端通讯id列表
    """
    # 获取挡板id列表
    dbdy_rs = ModSql.kf_txgl_001.execute_sql_dict( db, 'get_dbdy', { 'cdtxid_lst': cdtx_id_lst } )
    dbid_lst = [ dbdy_obj['id'] for dbdy_obj in dbdy_rs ]
    # 挡板存在进行删除
    if dbid_lst:
        # 挡板要素删除
        ModSql.kf_txgl_001.execute_sql_dict( db, 'del_dbys_bydbdyid', { 'dbdyid_lst': dbid_lst } )
        # 挡板删除
        ModSql.kf_txgl_001.execute_sql_dict( db, 'del_dbdy_byid', { 'id_lst': dbid_lst } )

def get_cdtx_csjdxx( db, jdlx_lst ):
    """
    # 获取各个类型对应节点信息
    """
    jdxx_dic = { 'ksjdid': '', 'jsjdid': '', 'txjdid': '', 'ycljdid': '' }
    if jdlx_lst:
        rs_csid = ModSql.kf_txgl_001.execute_sql_dict( db, "get_jddy_byjdlx", { 'jdlx_lst': jdlx_lst } )
        # 节点id
        for obj in rs_csid:
            if obj['jdlx'] == '3':
                jdxx_dic['ksjdid'] = obj['id']
            if obj['jdlx'] == '4':
                jdxx_dic['jsjdid'] = obj['id']
            if obj['jdlx'] == '7':
                jdxx_dic['txjdid'] = obj['id']
            if obj['jdlx'] == '2':
                jdxx_dic['ycljdid'] = obj['id']
    
    return jdxx_dic

def add_cdtx_lc( db, jbjdid, dbjdid, zlcdyid ):
    """
    # 新增C端通讯时，新增流程
    # jbjdid: 解包节点id
    # dbjdid: 打包节点id
    # zlcdyid: 子流程id
    """
    # 获取开始节点、结束节点、通讯节点ID
    # 节点类型：3（开始节点），4（结束节点），7（通讯节点）,
    # 2（系统节点）(预处理节点)[此处从10改为2，是zcl，jindong，zoulj,
    #       确定后的结果为2系统节点，节点定义表中此类型的节点只能有一个且为预设]
    jdxx_dic = get_cdtx_csjdxx( db, ['3','4','7','2'] )
    # 将解包节点和打包节点放在节点信息字典中
    jdxx_dic['jbjdid'] = jbjdid
    jdxx_dic['dbjdid'] = dbjdid
    
    # 保存流程布局
    lcbj_dic = add_cdtx_lcbj( db, zlcdyid, jdxx_dic )
    # 保存流程走向
    add_cdtx_lczx( db, zlcdyid, jdxx_dic, lcbj_dic )

def add_cdtx_lcbj( db, lcid, jdxx_dic ):
    """
    # 新增流程布局
    # jdxx_dic: 流程布局对应节点信息
    """
    # 新增流程布局信息
    #   节点类型 1:普通节点 2:子流程 3:开始节点 4:结束节点
    lcbj_lst = []
    lcbj_dic = { 'ksjdid': get_uuid(), 'ycljdid': get_uuid(), 'jbjdid': get_uuid(),
    'txjdid': get_uuid(), 'dbjdid': get_uuid(), 'jsjdid': get_uuid() }
    #登记开始节点（ jdlx：3:子流程开始节点 ）
    lcbj_lst.append( {
        'id': lcbj_dic.get('ksjdid', ''), 'bm': ' ', 'jdlx': '3',  'x': 50, 'y': 50, 'jddyid': jdxx_dic.get('ksjdid', ''),
        'sszlcid': lcid
    } )
    #登记预处理节点( jdlx：7：系统预设 )
    lcbj_lst.append( {
        'id': lcbj_dic.get('ycljdid', ''), 'bm': ' ', 'jdlx': '7',  'x': 50, 'y': 150, 'jddyid': jdxx_dic.get('ycljdid', ''),
        'sszlcid': lcid
    } )
    #登记打包节点（ jdlx：1（普通节点） ）
    lcbj_lst.append( {
        'id': lcbj_dic.get('dbjdid', ''), 'bm': ' ', 'jdlx': '1', 'x': 275, 'y': 50, 'jddyid': jdxx_dic.get('dbjdid', ''),
        'sszlcid': lcid
    } )
    #登记通讯节点( jdlx：7：系统预设 )
    lcbj_lst.append( {
        'id': lcbj_dic.get('txjdid', ''), 'bm': ' ', 'jdlx': '7', 'x': 500, 'y': 150, 'jddyid': jdxx_dic.get('txjdid', ''),
        'sszlcid': lcid
    } )
    
    #登记解包节点（ jdlx：1（普通节点） ）
    lcbj_lst.append( {
        'id': lcbj_dic.get('jbjdid', ''), 'bm': ' ', 'jdlx': '1', 'x': 500, 'y': 250, 'jddyid': jdxx_dic.get('jbjdid', ''),
        'sszlcid': lcid
    } )
    #登记结束节点（ jdlx：4:子流程结束节点 ）
    lcbj_lst.append( {
        'id': lcbj_dic.get('jsjdid', ''), 'bm': ' ', 'jdlx': '4', 'x': 150, 'y': 350, 'jddyid': jdxx_dic.get('jsjdid', ''),
        'sszlcid': lcid
    } )
    
    # 保存数据库
    for lcbjxx_dic in lcbj_lst:
        ModSql.kf_txgl_001.execute_sql_dict( db, "insert_lcbj", lcbjxx_dic )
    
    return lcbj_dic
    
def add_cdtx_lczx( db, lcid, jdxx_dic, lcbj_dic ):
    """
    # 新增流程走向
    # lcid: 流程id
    # jdxx_dic: 节点信息字典
    # lcbj_dic: 流程布局各个节点对应id
    """
    # 新增流程走向列表
    lczx_lst = []
    # 登记连接开始节点与预处理节点的流程走向( 2015-04-22 经齐姗、房超、高仁军、张成丽 测试从1改为0 )
    lczx_lst.append( { 'id': get_uuid(), 'fhz': '0',
        'qzjdlcbjid': lcbj_dic.get('ksjdid'),
        'hzjdlcbjid': lcbj_dic.get('ycljdid'),
        'sslb': '2', 'ssid': lcid
    } )
#    # 登记连接预处理节点与结束节点的流程走向（预处理校验失败或者是挡板信息）
#    lczx_lst.append( { 'id': get_uuid(), 'fhz': '1',
#        'qzjdlcbjid': lcbj_dic.get('ycljdid'),
#        'hzjdlcbjid': lcbj_dic.get('jsjdid'),
#        'sslb': '2', 'ssid': lcid
#    } )
    # 登记连接预处理节点与结束节点的流程走向（预处理节点执行异常）
    lczx_lst.append( { 'id': get_uuid(), 'fhz': '-1',
        'qzjdlcbjid': lcbj_dic.get('ycljdid'),
        'hzjdlcbjid': lcbj_dic.get('jsjdid'),
        'sslb': '2', 'ssid': lcid
    } )
    # 登记连接预处理节点与结束节点的流程走向（预处理节点执行正常）
    lczx_lst.append( { 'id': get_uuid(), 'fhz': '0',
        'qzjdlcbjid': lcbj_dic.get('ycljdid'),
        'hzjdlcbjid': lcbj_dic.get('jsjdid'),
        'sslb': '2', 'ssid': lcid
    } )
    # 登记连接预处理节点与结束节点的流程走向（预处理节点执行超时）
    lczx_lst.append( { 'id': get_uuid(), 'fhz': '99',
        'qzjdlcbjid': lcbj_dic.get('ycljdid'),
        'hzjdlcbjid': lcbj_dic.get('jsjdid'),
        'sslb': '2', 'ssid': lcid
    } )
    # 登记连接预处理节点与打包节点的流程走向（预处理校验成功 邹提需求，由0变为2）
    lczx_lst.append( { 'id': get_uuid(), 'fhz': '2',
        'qzjdlcbjid': lcbj_dic.get('ycljdid'),
        'hzjdlcbjid': lcbj_dic.get('dbjdid'),
        'sslb': '2', 'ssid': lcid
    } )
    # 登记连接打包节点与通讯节点的流程走向
    lczx_lst.append( { 'id': get_uuid(), 'fhz': '0',
        'qzjdlcbjid': lcbj_dic.get('dbjdid'),
        'hzjdlcbjid': lcbj_dic.get('txjdid'),
        'sslb': '2', 'ssid': lcid
    } )
    # 登记连接打包节点与结束节点间的流程走向
    lczx_lst.append( { 'id': get_uuid(), 'fhz': '-1',
        'qzjdlcbjid': lcbj_dic.get('dbjdid'),
        'hzjdlcbjid': lcbj_dic.get('jsjdid'),
        'sslb': '2', 'ssid': lcid
    } )
    # 登记连接通讯节点与解包的流程走向
    lczx_lst.append( { 'id': get_uuid(), 'fhz': '0',
        'qzjdlcbjid': lcbj_dic.get('txjdid'),
        'hzjdlcbjid': lcbj_dic.get('jbjdid'),
        'sslb': '2', 'ssid': lcid
    } )
    # 登记连接通讯节点与结束的流程走向
    lczx_lst.append( { 'id': get_uuid(), 'fhz': '-1',
        'qzjdlcbjid': lcbj_dic.get('txjdid'),
        'hzjdlcbjid': lcbj_dic.get('jsjdid'),
        'sslb': '2', 'ssid': lcid
    } )
    # 登记解包节点与结束节点的流程走向（正常）
    lczx_lst.append( { 'id': get_uuid(), 'fhz': '0',
        'qzjdlcbjid': lcbj_dic.get('jbjdid'),
        'hzjdlcbjid': lcbj_dic.get('jsjdid'),
        'sslb': '2', 'ssid': lcid
    } )
    # 登记解包节点与结束节点的流程走向(异常)
    lczx_lst.append( { 'id': get_uuid(), 'fhz': '-1',
        'qzjdlcbjid': lcbj_dic.get('jbjdid'),
        'hzjdlcbjid': lcbj_dic.get('jsjdid'),
        'sslb': '2', 'ssid': lcid
    } )
    # 登记解包节点与结束节点的流程走向（超时）
    lczx_lst.append( { 'id': get_uuid(), 'fhz': '99',
        'qzjdlcbjid': lcbj_dic.get('jbjdid'),
        'hzjdlcbjid': lcbj_dic.get('jsjdid'),
        'sslb': '2', 'ssid': lcid
    } )
    # 保存流程走向
    for lczxxx_dic in lczx_lst:
        ModSql.kf_txgl_001.execute_sql_dict( db, "insert_lczx", lczxxx_dic )
        
def get_jydy_mc( db, jydyid_lst ):
    """
    # 获取交易定义名称字典
    """
    jyidmc_dic = {}
    if jydyid_lst:
        rs_jy = ModSql.common.execute_sql_dict( db, 'get_jydy_mc', { 'ids': jydyid_lst } )
        jyidmc_dic = dict( [ ( jy['id'], jy['jymc'] ) for jy in rs_jy ] )
    
    return jyidmc_dic

def get_zlcdy_mc( db, zlcdyid_lst ):
    """
    # 获取交易定义名称字典
    """
    zlcidmc_dic = {}
    if zlcdyid_lst:
        rs_jy = ModSql.common.execute_sql_dict( db, 'get_jydy_mc', { 'ids': zlcdyid_lst } )
        jyidmc_dic = dict( [ ( jy['id'], jy['mc'] ) for jy in rs_jy ] )
    
    return zlcidmc_dic