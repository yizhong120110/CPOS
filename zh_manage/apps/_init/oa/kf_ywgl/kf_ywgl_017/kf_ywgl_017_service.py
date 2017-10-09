# -*- coding: utf-8 -*-
# Action: 公共函数service
# Author: zhangzf
# AddTime: 2015-1-6
# Standard: 注释仅能以“#”开头，sql可以是“--”；注释不能同代码在同一行

import traceback, pickle
from sjzhtspj import logger, get_sess_hydm, ModSql
from sjzhtspj.common import update_wym,get_strftime,get_uuid,py_check,ins_czrz
from sjzhtspj.esb import memcache_data_del

def data_service(map):
    """
    # 查询公共函数
    """
    data = {'total':0, 'rows':[]}
    
    # 查询公共函数总条数
    with sjapi.connection() as db:
        data['total'] = ModSql.kf_ywgl_017.execute_sql(db, "get_gghs_count", map)[0].count
        # 查询公共函数
        gghs = ModSql.kf_ywgl_017.execute_sql_dict(db, "get_gghs", map)
        for gh in gghs:
            if gh['nr'] == None:
                gh['nr'] = ''
            else:
                gh['nr'] = pickle.loads(gh['nr'].read())
        data['rows'] = gghs
    return data

def add_service(map):
    """
    # 添加公共函数
    """
    
    # BLOB管理表id
    gl_blob_id = get_uuid()
    # 公共函数id
    gghs_id = get_uuid()
    
    try:
        # 校验函数名校验
        exec("def " + map['mc'] + ":pass")
    except:
        logger.info(traceback.format_exc())
        return {'state':False, 'msg' : "函数名称["+map['mc']+"]不正确：" + traceback.format_exc()}
    
    # 校验函数内容的合法性
    check_hsnr = "def " + map['mc'] + ":\n" + map['hsnr']
    check_hsnr = check_hsnr.replace( '\n', '\n    ' )
    str_check = py_check( check_hsnr )
    if str_check != '':
        return {'state':False, 'msg' : "函数内容有语法错误：\n" + str_check}
    
    # 校验该业务下是否有函数( 
    # 函数名称在业务公共函数表中在同一业务下为唯一索引, 
    # 在插入之前需要先校验该业务下业务公共函数表是否存在（此处的函数名称不包含参数） )
    with sjapi.connection() as db:
        check_mc = map['mc'][:map['mc'].find('(')]
        # 首先获取此业务下公共函数名称
        rs_yw = ModSql.kf_ywgl_017.execute_sql(db, "gghs_have", {'ywid':map['ywid']})
        ret = False
        for obj in rs_yw:
            mc = obj.mc
            if mc[:mc.find('(')] == check_mc:
                ret = True
                continue
        # 如果函数名存在进行提示
        if(ret):
            return {'state':False, 'msg' : '函数名称['+ check_mc +']已经存在，请重新输入'}
        hsnr = pickle.dumps(map['hsnr'])
        # 登记函数内容
        sql_data = {'blobid':gl_blob_id, 'lx':'gl_yw_gghs', 'czr': get_sess_hydm(), 'czsj':get_strftime(), 'nr': hsnr}
        ModSql.common.execute_sql(db, "add_blob", sql_data)
        # 增加公共函数
        sql_data = {'id':gghs_id, 'mc':map['mc'], 'hsms':map['hsms'], 'ywid':map['ywid'], 'czr':get_sess_hydm(), 'czsj':get_strftime(), 'gl_blob_id':gl_blob_id}
        ModSql.kf_ywgl_017.execute_sql(db, "gghs_add", sql_data)
        # 操作日志流水
        ins_czrz( db, '公共函数新增：公共函数名称[%s]，公共函数描述[%s]' % (sql_data['mc'], sql_data['hsms'] ), gnmc = '公共函数管理_新增' )
        # 更新公共函数定义唯一码
        update_wym(db,'gghs',gghs_id)
        # 清除memcache
        del_memcache_data( db, ywid = map['ywid'] )
    
    return {'state':True, 'msg':'新增成功'}

def del_service(map):
    """
    # 删除公共函数
    """
    ids_lst = map['ids'].split(',')
    nrids_lst = map['nrids'].split(',')
    result = {'state':False, 'msg':''}
    # 函数名称
    strmc = ""
    
    # 查询要删除的公共函数的名字
    with sjapi.connection() as db:
        mclist = ModSql.kf_ywgl_017.execute_sql_dict(db, "get_gghs_name", {'ids_lst': ids_lst})
        strmc = ','.join([row['mc'] for row in mclist])
        # 删除函数内容
        ModSql.common.execute_sql(db, "del_blob", {'lx':'gghs', 'ssid_lst': ids_lst})
        # 删除blob内容
        ModSql.common.execute_sql(db, "del_blob_id", {'id_lst': nrids_lst})
        # 删除公共函数
        ModSql.kf_ywgl_017.execute_sql(db, "del_gghs", {'ids_lst': ids_lst})
        # 删除版本信息
        ModSql.common.execute_sql(db, "del_bbkz", {'lx':'gghs', 'ssid_lst': ids_lst})
        # 记录操作日志
        ins_czrz(db,"删除公共函数【"+ strmc +"】", gnmc = '公共函数管理_删除')
        # 清除memcache
        del_memcache_data( db, ywid = map['ywid'], uuid_lst = ids_lst )
    
    return {'state':True, 'msg':'删除成功'}

def update_service(map):
    """
    # 更新公共函数
    """
    # BLOB管理表id
    gl_blob_id = get_uuid()
    
    # 校验函数内容的合法性
    check_hsnr = "def " + map['mc'] + ":\n" + map['nr']
    check_hsnr = check_hsnr.replace( '\n', '\n    ' )
    str_check = py_check(check_hsnr)
    if str_check != '':
        return {'state': False, 'msg':'[函数内容]有语法错误:' + str_check}
    
    nr = pickle.dumps(map['nr'])
    # 更新BLOB管理表
    with sjapi.connection() as db:
        sql_data = {'nr': nr, 'czr': get_sess_hydm(), 'czsj':get_strftime(), 'pkid':map['nr_id']}
        ModSql.common.execute_sql(db, "edit_blob2", sql_data)
        # 查询修改前的信息
        data = ModSql.kf_ywgl_017.execute_sql(db, "select_gghs", map)[0]
        # 更新公共函数
        sql_data = {'hsms':map['hsms'], 'mc':map['mc'], 'czr':get_sess_hydm(), 'czsj':get_strftime(), 'id':map['id']}
        ModSql.kf_ywgl_017.execute_sql(db, "update_gghs", sql_data)
        # 登记操作日志
        nr_bjq = '编辑前：公共函数名称[%s]，公共函数描述[%s]' % (data['mc'], data['hsms'])
        nr_bjh = '编辑后：公共函数名称[%s]，公共函数描述[%s]' % (map['mc'], map['hsms'])
        ins_czrz( db, '公共函数编辑：%s;%s' % (nr_bjq, nr_bjh), gnmc = '公共函数管理_编辑' )
        # 更新公共函数定义唯一码
        update_wym(db,'gghs',map['id'])
        # 清除memcache
        del_memcache_data( db, ywid = map['ywid'], uuid_lst = [map['id']] )
        
    return {'state':True, 'msg':'编辑成功'}
    
def del_memcache_data( db, ywid = None, ywbm = None, uuid_lst = [] ):
    """
    # 清理memchache_data
    # 交易节点（JYJD）:交易节点UUID
    # 交易（JY）:交易代码
    # 业务（YW):业务代码
    # 函数（HS）:函数UUID ( 业务公共函数、业务打印配置函数、分析函数、响应动作函数 )
    # 子流程（ZLC）:子流程UUID
    # 通讯节点（TXJD）:通讯节点代码
    """
    # 根据业务id获取业务编码进行清理
    if ywid:
        rs = ModSql.common.execute_sql(db, "get_ywdy", {'ywid': ywid})
        if rs:
            memcache_data_del( [rs[0]['ywbm']] )
    # 业务编码存在，则直接调用函数
    if ywbm:
        memcache_data_del( [ywbm] )
    # 如果uuid存在，则根据uuid清理
    if uuid_lst:
        for uuid in uuid_lst:
            memcache_data_del( [uuid] )