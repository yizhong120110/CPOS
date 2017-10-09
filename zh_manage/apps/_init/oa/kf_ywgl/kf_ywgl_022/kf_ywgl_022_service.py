# -*- coding: utf-8 -*-
# Action: 导入历史 service
# Author: zhangchl
# AddTime: 2015-01-12
# Standard: 注释仅能以“#”开头，sql可以是“--”；注释不能同代码在同一行

from sjzhtspj import ModSql, STATIC_DIR, settings, get_sess_hydm, logger
from sjzhtspj.common import (update_wym, get_strftime, get_strftime2, get_uuid, ins_czrz, get_hy_byjsdm, check_fhr,
    insert_tab_sql, insert_sy_sql, insert_ys_sql,update_jhrw,ins_waitexec_task
)
from sjzhtspj.const import FHR_JSDM
import pickle
import os
import subprocess
from sjzhtspj.esb import send_jr


def data_service( data_dic ):
    """
    # 导入历史：获取显示数据
    """
    # 反馈信息
    data = {'total':0, 'rows':[]}
    # 数据库操作
    nrlx = data_dic['nrlx']
    with sjapi.connection() as db:
        # 初始化查询数据信息，如果是业务限定所属id列表
        sql_dic = { 'czlx': 'dr', 'nrlx': nrlx }
        if nrlx in [ 'yw' ]:
            sql_dic['ss_idlb'] = data_dic['ss_idlb']
        # 交易限定所属业务id
        elif nrlx in [ 'jy' ]:
            sql_dic['ssywid'] = data_dic['ss_idlb']
        total = ModSql.kf_ywgl_022.execute_sql( db, 'data_count', sql_dic )[0].count
        # 获取当前页面显示信息
        sql_dic.update( { 'rn_start': data_dic['rn_start'], 'rn_end': data_dic['rn_end'] } )
        data_row = ModSql.kf_ywgl_022.execute_sql_dict( db, 'data_rs', sql_dic )
        
        # 如果是交易、通讯管理，需要获取对应名称
        if nrlx in ['tx','jy']:
            ss_idlb_lst = []
            for dr_obj in data_row:
                # 首先获取所属id列表
                if dr_obj['ss_idlb']:
                    idlb =  [ idlbxx for idlbxx in dr_obj['ss_idlb'].split(',') if idlbxx]
                    ss_idlb_lst.extend( idlb )
                    dr_obj['ss_idlb_lst'] = idlb
                else:
                    dr_obj['ss_idlb_lst'] = []
            # 如果存在则获取对应名称
            if ss_idlb_lst != []:
                if nrlx == 'tx':
                    get_dr_tx( db, ss_idlb_lst, data_row )
                elif nrlx == 'jy':
                    get_dr_jy( db, ss_idlb_lst, data_row )
        
        # 判断行信息是否有回退按钮
        max_id = get_dr_maxid( db )
        if max_id:
            for dr_obj in data_row:
                if dr_obj['id'] == max_id:
                    dr_obj['sfht'] = 'TRUE'
        # 组织反馈值
        data['total'] = total
        data['rows'] = data_row
    
    return data

def get_dr_tx( db, ss_idlb_lst, data_row ):
    """
    # 导入流水涉及到的通讯名称
    # @params: ss_idlb_lst: 所属id列表
    # @params: data_row:查询导入历史结果集
    """
    # 本次涉及到的所属id名称
    data_dic = { 'ids': ss_idlb_lst }
    rs_txxx = ModSql.common.execute_sql_dict( db, 'get_txgl_mc', data_dic )
    txxx_dic = dict( ( obj['id'], obj['mc'] ) for obj in rs_txxx )
    
    for dr_obj in data_row:
        ss_idlb_mc = [ txxx_dic.get( idlb, '' ) for idlb in dr_obj['ss_idlb_lst'] ]
        dr_obj['txmc'] = ','.join( idlb_mc for idlb_mc in ss_idlb_mc if idlb_mc )

def get_dr_jy( db, ss_idlb_lst, data_row ):
    """
    # 导入流水涉及到的交易名称
    # @params: ss_idlb_lst: 所属id列表
    # @params: data_row:查询导入历史结果集
    """
    # 本次涉及到的所属id名称
    data_dic = { 'ids': ss_idlb_lst }
    rs_txxx = ModSql.common.execute_sql_dict( db, 'get_jydy_mc', data_dic )
    txxx_dic = dict( ( obj['id'], obj['jymc'] ) for obj in rs_txxx )
    
    for dr_obj in data_row:
        ss_idlb_mc = [ txxx_dic.get( idlb, '' ) for idlb in dr_obj['ss_idlb_lst'] ]
        dr_obj['jymc'] = ','.join( idlb_mc for idlb_mc in ss_idlb_mc if idlb_mc )

def get_dr_maxid( db ):
    """
    # 获取导入流水最大值id
    """
    max_id = ''
    max_rs = ModSql.kf_ywgl_022.execute_sql_dict( db, 'get_dr_maxid' )
    if max_rs:
        max_id = max_rs[0]['id']
    
    return max_id

def data_edit_sel_service( data_dic ):
    """
    # 导入历史：信息编辑 页面初始化 service
    """
    result = {'state': False, 'msg':'', 'drid':'', 'czms': '', 'bz': ''}
    with sjapi.connection() as db:
        drxx = ModSql.kf_ywgl_022.execute_sql_dict( db, 'get_drxx', data_dic )
        if drxx:
            result['state'] = True
            result['drlsid'] = drxx[0]['id']
            result['czms'] = drxx[0]['czms']
            result['bz'] = drxx[0]['bz']
        else:
            result['msg'] = '获取编辑信息失败，编辑信息不存在'
    
    return result
    
def data_edit_service( data_dic ):
    """
    # 导入历史：信息编辑 提交 service
    """
    # 反馈信息
    result = {'state':False, 'msg':''}
    with sjapi.connection() as db:
        drxx = ModSql.kf_ywgl_022.execute_sql_dict( db, 'get_drxx', data_dic )[0]
        ModSql.kf_ywgl_022.execute_sql_dict( db, 'upd_drxx', data_dic )

        # 登记操作日志
        nr_bjq = '编辑前：%s' % drxx
        drxx['czms'] = data_dic['czms']
        drxx['bz'] = data_dic['bz']
        nr_bjh = '编辑后：%s' % drxx
        ins_czrz( db, '导入历史信息_编辑：%s;%s' % (nr_bjq, nr_bjh), gnmc = '导入历史信息_编辑' )

        # 反馈信息
        result['state'] = True
        result['msg'] = '修改成功'
    
    return result

def drht_sel_service():
    """
    # 导入回退 页面初始化 service
    """
    # 获取复核人列表
    hyxx_lst = get_hy_byjsdm( FHR_JSDM )
    
    return hyxx_lst

def drht_service( data_dic ):
    """
    # 导入回退 提交 service
    """
    # 返回值
    result = {'state': False, 'msg':''}
    nr = ''
    with sjapi.connection() as db:
        # (1)首先校验复核人是否正确
        sq_gnmc = '导入回退'
        if data_dic['nrlx'] == 'yw':
            sq_gnmc += '业务_' + sq_gnmc
            nr = '%s：导入流水ID：%s，内容类型：%s，回退描述：%s，备注：%s' % ( sq_gnmc,data_dic['drlsid'],data_dic['nrlx'],data_dic['htms'],data_dic['bz'] )
        if data_dic['nrlx'] == 'jy':
            sq_gnmc += '交易_' + sq_gnmc
            nr = '%s：导入流水ID：%s，内容类型：%s，回退描述：%s，备注：%s' % ( sq_gnmc,data_dic['drlsid'],data_dic['nrlx'],data_dic['htms'],data_dic['bz'] )
        if data_dic['nrlx'] == 'tx':
            sq_gnmc += '通讯_' + sq_gnmc
            nr = '%s：导入流水ID：%s，内容类型：%s，回退描述：%s，备注：%s' % ( sq_gnmc,data_dic['drlsid'],data_dic['nrlx'],data_dic['htms'],data_dic['bz'] )
        hyxx_dic = { 'hydm': data_dic['fhr'], 'mm': data_dic['fhrmm'], 'jsdm': FHR_JSDM,
                    'sq_gnmc': sq_gnmc, 'czpt': 'kf', 'sqgndm': '', 'szcz': sq_gnmc + '复核人授权' }
        ret,msg = check_fhr( db, hyxx_dic )
        if ret == False:
            result['msg'] = msg
            return result
        
        # (2)获取导入信息,将备份文件导入到数据库(新增一些临时表)，根据临时表更新正式表数据
        drxx = ModSql.common.execute_sql_dict( db, 'get_tab_xx', { 'zd_lst': ['bfwjm', 'ss_idlb', 'ssywid'],
        'tname_lst': ['gl_drls'],
        'sel_lst': ['id'],
        'id': data_dic['drlsid'] })
        if not drxx:
            result['msg'] = "获取导入流水信息失败，回退的导入流水不存在，请查证后再回退。"
            return result
        # 校验备份文件是否存在
        if not drxx[0]['bfwjm']:
            result['msg'] = "此导入流水中备份文件名称不存在，不可继续回退，请查证后再回退。"
            return result
        # 获取dmp文件路径
        fpath = check_backup_dmp( db, drxx[0]['bfwjm'] )
        # 后台查询数据库中的临时表并将其删除
        del_dr_tmptab( db )
        # 将文件导入到数据库 
        ret, msg = upload_dmp( db, fpath )
        if ret == False:
            result['msg'] = msg
            return result
        # 更新正式表数据
        upd_tab( db, data_dic['nrlx'] )
        
        # (3)如果是业务管理回退，则书写数据库模型回退sql到txt文件
        ht_fname = ''
        if data_dic['nrlx'] == 'yw':
            ht_fname = sjkmx_ht( db )
        # 查询此次导入流水的类型
        ls_lx = ModSql.kf_ywgl_022.execute_sql_dict( db, 'get_drls_lx', {'id':data_dic.get('drlsid')})
        if ls_lx and (ls_lx[0]['nrlx'] == 'jy' or ls_lx[0]['nrlx'] == 'yw'):
            # 回退后，遍历所有的交易，将交易对应的计划任务和当日执行计划任务进行重新删除和添加。
            # 查询所有的交易
            all_jy = ModSql.kf_ywgl_022.execute_sql_dict( db, 'get_all_jy')
            # 删除所有的当日执行计划（交易）
            ModSql.kf_ywgl_022.execute_sql( db, 'del_all_drjhrw')
            for jy in all_jy:
                # 查询该交易的计划任务id
                old_jhrwid = ModSql.kf_ywgl_022.execute_sql( db, 'get_jhrw_id', {'jyid':jy.get('id')})
                if old_jhrwid:
                    old_jhrwid = old_jhrwid[0].get('id')
                else:
                    old_jhrwid = get_uuid()
                # 删除交易的计划任务(交易)
                ModSql.kf_ywgl_022.execute_sql( db, 'del_all_jhrw', {'jyid':jy.get('id')})
                # 更新计划任务的状态和当日执行计划'ip','sfkbf','yjjb'
                upd_dic = {'id':old_jhrwid, 'zdfqpz': jy['zdfqpz'],'zdfqpzsm': jy['zdfqpzsm'] if jy['zdfqpzsm'] else '', 'rwlx': 'jy','ssid': jy['id'],'zt': jy['zt'], 'ip':'', 'sfkbf':'', 'yjjb':'' }
                # 插入计划任务
                ModSql.common.execute_sql_dict(db, "ins_jhrwb", upd_dic)
                if jy['zt'] == '1':
                    # 获取计划任务信息
                    jhrwxx = ModSql.common.execute_sql_dict( db, 'get_jhrw', { 'jhrwid': upd_dic.get('id') } )
                    # 当contab配置有值时才插入当日执行计划任务
                    if jhrwxx and jhrwxx[0].get('zdfqpz'):
                        # 插入当日执行计划任务
                        ins_waitexec_task( upd_dic.get('id'), db )
                # 如果导入的交易的自动发起配置为空，则将计划任务表的内容删除掉
                if not upd_dic['zdfqpz']:
                    ModSql.common.execute_sql_dict(db,'del_jhrw_byssid',{'ssid':jy['id']})
                
        # (4)回退成功后，作废原有流水，新增一条回退流水
        # 导入成功后，更新此流水状态
        ModSql.kf_ywgl_022.execute_sql_dict( db, 'upd_drxx_zt', {'drlsid': data_dic['drlsid'],'zt': '0'} )
        # 更新成功后，登记回退流水
        czr = get_sess_hydm()
        czsj = get_strftime()
        sql_data = {
        'id': get_uuid(), 'ss_idlb': drxx[0]['ss_idlb'], 'czlx': 'ht', 'nrlx': data_dic['nrlx'], 'czr': czr,
        'czsj': czsj, 'czms': data_dic['htms'], 'wjm': drxx[0]['bfwjm'], 'bz': data_dic['bz'], 'zt': '1',
        'fhr': data_dic['fhr'], 'bfwjm': '', 'ssywid': drxx[0]['ssywid'] if drxx[0]['ssywid'] else ''
        }
        ModSql.common.execute_sql_dict( db, 'insert_drls', sql_data )
        
        # (5)反馈信息
        result['state'] = True
        result['msg'] = '回退成功'
        # 登记操作日志
        ins_czrz( db, nr , gnmc = '导入历史信息_回退' )
        if data_dic['nrlx'] == 'yw' and ht_fname:
            result['msg'] = "数据库回退操作请参照“%s”手工回退" % ht_fname
        
    return result
    
def check_backup_dmp( db, dmp_fname ):
    """
    # 获取备份文件路径
    """
    # 获取备份目录
    backPath = ModSql.common.execute_sql_dict(db,"get_csdyv_bycsdm",{'lx':'1','csdm':'db_ftp_backPath'})[0]['value']
    # 校验dmp路径
    bfwjPath = os.path.join( backPath,dmp_fname )
    
    return bfwjPath

def del_dr_tmptab( db ):
    """
    # 删除导入、导出临时表
    """
    # 获取临时表列表
    tmp_tab = ModSql.common.execute_sql_dict( db, 'get_ls_tname')
    # 删除临时表
    tname_lst = [ obj['table_name'] for obj in tmp_tab if obj['table_name'] ]
    if tname_lst:
        for tname in tname_lst:
            ModSql.common.execute_sql_dict( db, 'drop_table', { 'tname_lst': [tname] } )

def upload_dmp( db, fpath ):
    """
    # 将文件导入数据库
    # @params: fpath: dmp文件路径加名称
    """
    # 获取数据库服务器的IP
    db_ip = ModSql.common.execute_sql_dict(db,"get_csdyv_bycsdm",{'lx':'1','csdm':'db_ip'})[0]['value']
    # 从环境变量中获取数据库的用户名及密码、SID
    # oracle sid
    ORACLE_SID = os.environ['ORACLE_SID']
    # 密码
    ORACLE_DBPW = os.environ['ORACLE_DBPW']
    # 用户名
    ORACLE_DBU = os.environ['ORACLE_RDBU']
    # 定义执行名利
    cmd = "imp %s/%s@%s file='%s'  full=y ignore=y statistics=none"%( ORACLE_DBU,ORACLE_DBPW,ORACLE_SID,fpath )
    # 执行
    logger.info('回退命令param：%s' % cmd)
    logger.info('回退服务器db_ip：%s' % str(db_ip))
    result = send_jr({'param':[cmd]},db_ip)
    logger.info('导入反馈值：%s' % str(result))
    #if "Import terminated successfully without warnings" not in result and "成功终止导入, 没有出现警告" not in result:
    if result and result == "ok":
        pass
    else:
        return False,'回退导入备份文件失败，请检查问题原因'
    logger.info('命令通知核心后，等待90秒执行下面操作start')
    import time
    time.sleep(90)
    logger.info('命令通知核心后，等待90秒执行下面操作end')
    # 成功
    return True, ''

def upd_tab( db, nrlx ):
    """
    # 更新表数据
    # @params: nrlx: 内容类型
    """
    # 获取正式表列表
    sqlid = ''
    if nrlx == 'tx':
        sqlid = 'get_zs_tname_tx'
    elif nrlx == 'jy':
        sqlid = 'get_zs_tname_jy'
    elif nrlx == 'yw':
        sqlid = 'get_zs_tname_yw_ht'
    # 内容类型正确，开始更新表信息
    if sqlid:
        zs_tab = ModSql.common.execute_sql_dict( db, sqlid )
        # 创建正式表
        tname_lst = [ obj['table_name'] for obj in zs_tab if obj['table_name'] ]
        if tname_lst:
            for tname in tname_lst:
                # 先删除表数据
                ModSql.common.execute_sql_dict( db, 'delete_bytab', { 'tname': [tname] } )
                # 后创建
                ModSql.common.execute_sql_dict( db, 'inset_bytab', { 'tname_lst_zs': [tname], 
                    'tname_lst_ls': ['%s_LS' % tname] } )

def sjkmx_ht( db ):
    """
    # 回退：数据库操作
    """
    # 回退文件名称
    fname = ''
    # 写文件内容列表
    file_lst = []
    # 从临时表中查询数据表信息
    sjkmx_id_rs = ModSql.kf_ywgl_022.execute_sql_dict( db, 'ht_sjkmx_id')
    # 批量转单笔的进行处理
    for obj in sjkmx_id_rs:
        # 从临时表中查询数据表信息
        tab_wym_ls = ModSql.kf_ywgl_022.execute_sql_dict( db, 'get_wym', { 'tname_lst': ['gl_sjkmxdy_ls'], 'id': obj['id'] })
        # 从正式表中查询数据表信息
        tab_wym_zs = ModSql.kf_ywgl_022.execute_sql_dict( db, 'get_wym', { 'tname_lst': ['gl_sjkmxdy'], 'id': obj['id'] })
        # 对比唯一码
        wym_ls = tab_wym_ls[0]['wym'] if tab_wym_ls else ''
        wym_zs = tab_wym_zs[0]['wym'] if tab_wym_zs else ''
        
        # 临时的唯一码与正式的唯一码相同，则无需导入处理
        if wym_ls == wym_zs:
            continue
        # 临时的唯一码为空，说明此数据表为删除，生成此数据表的操作说明
        elif not wym_ls:
            file_lst.append("""%s数据表操作：删除
建议SQL：
    drop table %s
""" % ( tab_wym_zs[0]['sjbmcms'], tab_wym_zs[0]['sjbmc'] ))
        # 正式的唯一码为空，说明此数据表为新增
        elif not wym_zs:
            # 创建，索引，约束，注释
            create_tab_sql = get_sjkmx( db, obj['id'], '_ls' )
            file_lst.append("""%s数据表操作：新增
建议SQL：
    %s
    %s
    %s
    %s
""" % ( tab_wym_ls[0]['sjbmc'],
            create_tab_sql[0],
            '\n    '.join( create_tab_sql[3] ),
            '\n    '.join( create_tab_sql[1] ),
            '\n    '.join( create_tab_sql[2] ) )
            )
        # 若临时的唯一码与临时的唯一码不同
        elif wym_ls != wym_zs:
            # 处理表字段
            ht_zdbyz( db, obj['id'], tab_wym_zs[0]['sjbmc'], file_lst )
            # 数据表索引处理
            hy_sybyz( db, obj['id'], tab_wym_zs[0]['sjbmc'], file_lst )
            # 数据表约束处理
            hy_ysbyz( db, obj['id'], tab_wym_zs[0]['sjbmc'], file_lst )
    
    # 根据临时表更新正式表数据
    hy_upd_data( db )
    # 写执行sql文件
    if file_lst != []:
        fname = hy_write_file( file_lst )
    
    return fname

def get_sjkmx( db, sjkmxid, lx ):
    """
    # 根据数据库模型表id获取建表语句
    # @params: sjkmxid: 数据库模型表id
    # @lx: ''：正式表，ls：临时表
    """
    # 查询数据表名称
    sjkmx_rs = ModSql.common.execute_sql_dict( db, 'get_tab_xx', { 'zd_lst': ['sjbmc','sjbmcms'],
    'tname_lst': ['gl_sjkmxdy%s' % lx],
    'sel_lst': ['id'],
    'id': sjkmxid })
    sjbmc = sjkmx_rs[0]['sjbmc'] if sjkmx_rs else ''
    sjbmcms = sjkmx_rs[0]['sjbmcms'] if sjkmx_rs else ''
    # 数据表字段查询zdmc,zdms,zdlx,zdcd,xscd,sfkk,iskey,mrz
    zd_lst = ModSql.common.execute_sql_dict( db, 'get_tab_xx', { 'zd_lst': ['zdmc', 'zdms', 'zdlx', 'zdcd', 'xscd', 'sfkk', 'iskey', 'mrz'],
    'tname_lst': ['gl_sjkzdb%s' % lx],
    'sel_lst': ['sjb_id'],
    'id': sjkmxid })
    # 获取新增表sql
    create_sql, zs_sql_lst = insert_tab_sql( sjbmc, sjbmcms, zd_lst )
    
    # 数据表索引查询
    sy_lst = ModSql.common.execute_sql_dict( db, 'get_tab_xx', { 'zd_lst': ['symc', 'syzd', 'sylx', 'sfwysy'],
    'tname_lst': ['gl_sjksy%s' % lx],
    'sel_lst': ['sssjb_id'],
    'id': sjkmxid })
    sy_sql_dic = insert_sy_sql(sjbmc, sy_lst )
    sy_sql_lst = sy_sql_dic.values()
    
    # 数据表约束查询
    ys_lst = ModSql.common.execute_sql_dict( db, 'get_tab_xx', { 'zd_lst': ['ysmc', 'yszd'],
    'tname_lst': ['gl_sjkys%s' % lx],
    'sel_lst': ['sssjb_id'],
    'id': sjkmxid })
    ys_sql_lst = insert_ys_sql( sjbmc, ys_lst )
    
    return [create_sql, sy_sql_lst, ys_sql_lst, zs_sql_lst]

def ht_zdbyz( db, sjkmxid, sjbmc, file_lst, type = '022' ):
    """
    # 回退处理字段不一致情况( 字段不一致 )
    """
    
    # 数据表字段信息
    # 查询临时表中数据表字段信息
    # 字段名称,字段类型,字段长度,小数长度,是否可空,是否主键,默认值
    zd_lst = [ 'zdmc', 'zdlx', 'zdcd', 'xscd', 'sfkk', 'iskey', 'mrz' ]
    sjkzdb_ls = ModSql.common.execute_sql( db, 'get_tab_xx', { 'zd_lst': zd_lst,
    'tname_lst': ['gl_sjkzdb_ls'],
    'sel_lst': ['sjb_id'],
    'id': sjkmxid })
    # [ {字段名称:[字段类型,字段长度,小数长度,是否可空,是否主键,默认值]},…… ]
    zd_lst_ls = [ { obj.zdmc: [ obj.zdlx, obj.zdcd, obj.xscd, obj.sfkk, obj.iskey, obj.mrz ] } for obj in sjkzdb_ls ]
    # 查询正式表中数据表字段信息
    sjkzdb_zc = ModSql.common.execute_sql( db, 'get_tab_xx', { 'zd_lst': zd_lst,
    'tname_lst': ['gl_sjkzdb'],
    'sel_lst': ['sjb_id'],
    'id': sjkmxid })
    zd_lst_zc = [ { obj.zdmc: [ obj.zdlx, obj.zdcd, obj.xscd, obj.sfkk, obj.iskey, obj.mrz ] } for obj in sjkzdb_zc ]
    
    # 数据表有改变需要修改数据表
    if zd_lst_ls != zd_lst_zc:
        # 以临时表为主列表
        for zd_dic_ls in zd_lst_ls:
            flag = False
            # 字段名称
            zdmc = list( zd_dic_ls.keys() )[0]
            # 字段属性
            zdxx = list( zd_dic_ls.values() )[0]
            # 验证与正式表的关系
            for zd_dic_zc in zd_lst_zc:
                if zd_dic_ls == zd_dic_zc:
                    flag = True
                    continue
                # 字段名称一致，字段属性不同，说明此字段为修改
                elif zdmc == list( zd_dic_zc.keys() )[0] and zdxx != list( zd_dic_zc.values() )[0]:
                    flag = True
                    #字段类型,字段长度,小数长度,是否可空,是否主键,默认值
                    zdxx_zc = list( zd_dic_zc.values() )[0]
                    # 原字段信息
                    yzd_dic = { 'sjbmc':sjbmc, 'zdmc': zdmc,
                    'zdlx':zdxx_zc[0], 'zdcd':zdxx_zc[1], 'xscd':zdxx_zc[2], 
                    'sfkk':zdxx_zc[3], 'iskey':zdxx_zc[4], 'mrz':zdxx_zc[5] }
                    zd_dic = { 'sjbmc':sjbmc, 'zdmc': zdmc,
                    'zdlx':zdxx[0], 'zdcd':zdxx[1], 'xscd':zdxx[2], 
                    'sfkk':zdxx[3], 'iskey':zdxx[4], 'mrz':zdxx[5] }
                    tmp = update_sql_zd( yzd_dic, zd_dic )
                    
                    # 追加执行sql
                    if type == '022':
                        file_lst.append( """%s.%s字段操作：修改
    建议SQL：
        %s
    导入前属性：
        字段类型：%s
        字段长度：%s
        小数长度：%s
        是否可空：%s
        是否主键：%s
        默认值：%s
    导入后属性：
        字段类型：%s
        字段长度：%s
        小数长度：%s
        是否可空：%s
        是否主键：%s
        默认值：%s
    """ % ( sjbmc, zdmc, tmp,
    zdxx[0], zdxx[1], zdxx[2], zdxx[3], zdxx[4], zdxx[5],
    zdxx_zc[0], zdxx_zc[1], zdxx_zc[2], zdxx_zc[3], zdxx_zc[4], zdxx_zc[5] ) )
                    else:
                        file_lst.append( """%s.%s字段操作：修改
    建议SQL：
        %s
    导入前属性：
        字段类型：%s
        字段长度：%s
        小数长度：%s
        是否可空：%s
        是否主键：%s
        默认值：%s
    导入后属性：
        字段类型：%s
        字段长度：%s
        小数长度：%s
        是否可空：%s
        是否主键：%s
        默认值：%s
    """ % ( sjbmc, zdmc, tmp,
    zdxx_zc[0], zdxx_zc[1], zdxx_zc[2], zdxx_zc[3], zdxx_zc[4], zdxx_zc[5],
    zdxx[0], zdxx[1], zdxx[2], zdxx[3], zdxx[4], zdxx[5] ) )
                    # 退出此次循环
                    continue
            
            # 临时表中的数据都没在现有表中发现，则需要新增字段
            if flag == False:
                zd_dic = { 'sjbmc':sjbmc, 'zdmc': zdmc,
                    'zdlx':zdxx[0], 'zdcd':zdxx[1], 'xscd':zdxx[2], 
                    'sfkk':zdxx[3], 'iskey':zdxx[4], 'mrz':zdxx[5] }
                tmp = add_sql_zd( zd_dic )
                
                # 追加执行sql
                file_lst.append( """%s.%s字段操作：新增
建议SQL：
    %s
""" % ( sjbmc, zdmc, tmp ) )
    
        # 以正式表为主列表( 查询正式表在临时表不存在的, 说明是导入时做的新增，需要删除掉 )
        zdmc_lst_ls = [ list(zdxx_ls.keys())[0] for zdxx_ls in zd_lst_ls ]
        for zdxx_zc in zd_lst_zc:
            zdmc = list( zdxx_zc.keys() )[0]
            # 不存在，说明此字段需要删除
            if zdmc not in zdmc_lst_ls:
                # 追加执行sql
                file_lst.append( """%s.%s字段操作：删除
建议SQL：
    alter table %s
    drop column %s
    """ % ( sjbmc, zdmc, sjbmc, zdmc ) )
        
        # 查看表的数据是否变动，有变动则修改主键
        zjzd_lst = sorted( [ obj.zdmc for obj in sjkzdb_ls if obj.iskey == '1' ] )
        yzjzd_lst = sorted( [ obj.zdmc for obj in sjkzdb_zc if obj.iskey == '1' ] )
        if yzjzd_lst != zjzd_lst:
            rs = ModSql.kf_ywgl_011.execute_sql_dict(db, "get_zjxx",{'sjbmc':sjbmc})
            # 主键名称
            zjmc = sjbmc + '_key'
            if rs:
                zjmc = rs[0]['zjmc']
            tmp = "alter table %s add constraint %s primary key ( %s )"%( sjbmc,zjmc,",".join( zjzd_lst ) )
            # 追加执行sql
            file_lst.append( """%s主键操作：修改
建议SQL：
    %s
    """ % ( sjbmc, tmp ) )

def update_sql_zd( yzd_dic, zd_dic ):
    """
    # 获取字段更新sql
    # @yzd_dic： 原字段字典(zdlx,sjbmc,zdmc,zdcd,xscd,mrz,sfkk)
    # @zd_dic：  现在字段字典
    # 反馈修改sql
    """
    update_sql = ''
    # 拼接修改字段SQL
    if zd_dic['zdlx'] in ( 'CHAR','VARCHAR2','NCHAR','NVARCHAR2','RAW','FLOAT'):
        update_sql = "alter table %s modify %s %s ( %d ) "%( zd_dic['sjbmc'],
            zd_dic['zdmc'],zd_dic['zdlx'],zd_dic['zdcd'] )
    elif zd_dic['zdlx'] == 'DECIMAL':
        if zd_dic['xscd']:
            update_sql = "alter table %s modify %s %s ( %d,%d )"%( zd_dic['sjbmc'],
            zd_dic['zdmc'],zd_dic['zdlx'],zd_dic['zdcd'],zd_dic['xscd'] )
        else:
            update_sql = "alter table %s modify %s %s ( %d ) "%( zd_dic['sjbmc'],
            zd_dic['zdmc'],zd_dic['zdlx'],zd_dic['zdcd'] )
    elif zd_dic['zdlx'] in ( 'DATE', 'LONG', 'BLOB', 'CLOB', 'NCLOB', 'BFILE', 'INTEGER', 'LONG RAW','REAL'):
        update_sql = "alter table %s modify %s %s"%( zd_dic['sjbmc'],
            zd_dic['zdmc'],zd_dic['zdlx'] )
    elif zd_dic['zdlx'] == 'NUMBER':
        if zd_dic['zdcd']:
            if zd_dic['xscd']:
                update_sql = "alter table %s modify %s %s ( %d,%d )"%( zd_dic['sjbmc'],
            zd_dic['zdmc'],zd_dic['zdlx'],zd_dic['zdcd'],zd_dic['xscd'] )
            else:
                update_sql = "alter table %s modify %s %s ( %d ) "%( zd_dic['sjbmc'],
            zd_dic['zdmc'],zd_dic['zdlx'],zd_dic['zdcd'] )
        else:
            update_sql = "alter table %s modify %s %s"%( zd_dic['sjbmc'],
            zd_dic['zdmc'],zd_dic['zdlx'] )
    # 如果有默认值
    if zd_dic['mrz']:
        update_sql += " default '%s' "%(  zd_dic['mrz']  )
    # 字段是否可空 1:是 0:否
    if yzd_dic['sfkk'] == '1' and zd_dic['sfkk'] == '0': 
        if(zd_dic['zdlx'] == yzd_dic['zdlx'] and zd_dic['zdlx'] in ('BLOB', 'CLOB', 'NCLOB', 'BFILE', 'LONG RAW','REAL','LONG') ):
            update_sql = "alter table %s modify %s not null"%( zd_dic['sjbmc'],
            zd_dic['zdmc'] )
        else:
            update_sql += " not null "
    elif yzd_dic['sfkk'] == '0' and zd_dic['sfkk'] == '1':
        if(zd_dic['zdlx'] == yzd_dic['zdlx'] and zd_dic['zdlx'] in ('BLOB', 'CLOB', 'NCLOB', 'BFILE', 'LONG RAW','REAL','LONG') ):
            update_sql = "alter table %s modify %s null"%( zd_dic['sjbmc'],
            zd_dic['zdmc'] )
        else:
            update_sql += " null "
    
    return update_sql

def add_sql_zd( zd_dic ):
    """
    # 获取字段新增sql
    # @zd_dic：  现在字段字典(zdlx,sjbmc,zdmc,zdcd,xscd,mrz,sfkk)
    # 反馈新增sql
    """
    # 拼接创建字段SQL 
    sql = ''
    if zd_dic['zdlx'] in ( 'CHAR','VARCHAR2','NCHAR','NVARCHAR2','RAW','FLOAT'):
        sql = "alter table %s add %s %s ( %d ) "%( zd_dic['sjbmc'],
            zd_dic['zdmc'],zd_dic['zdlx'],zd_dic['zdcd'] )
    elif zd_dic['zdlx'] == 'DECIMAL':
        if zd_dic['xscd']:
            sql = "alter table %s add %s %s ( %d,%d )"%( zd_dic['sjbmc'],
            zd_dic['zdmc'],zd_dic['zdlx'],zd_dic['zdcd'],zd_dic['xscd'] )
        else:
            sql = "alter table %s add %s %s ( %d ) "%( zd_dic['sjbmc'],
            zd_dic['zdmc'],zd_dic['zdlx'],zd_dic['zdcd'] )
    elif zd_dic['zdlx'] in ( 'DATE', 'LONG', 'BLOB', 'CLOB', 'NCLOB', 'BFILE', 'INTEGER', 'LONG RAW','REAL'):
        sql = "alter table %s add %s %s"%( zd_dic['sjbmc'],
            zd_dic['zdmc'],zd_dic['zdlx'] )
    elif zd_dic['zdlx'] == 'NUMBER':
        if zd_dic['zdcd']:
            if zd_dic['xscd']:
                sql = "alter table %s add %s %s ( %d,%d )"%( zd_dic['sjbmc'],
            zd_dic['zdmc'],zd_dic['zdlx'],zd_dic['zdcd'],zd_dic['xscd'] )
            else:
                sql = "alter table %s add %s %s ( %d ) "%( zd_dic['sjbmc'],
            zd_dic['zdmc'],zd_dic['zdlx'],zd_dic['zdcd'] )
        else:
            sql = "alter table %s add %s %s"%( zd_dic['sjbmc'],
            zd_dic['zdmc'],zd_dic['zdlx'] )
    # 如果有默认值
    if zd_dic['mrz']:
        sql += " default '%s' "%(  zd_dic['mrz']  )
    # 字段是否可空 1:是 0:否
    if zd_dic['sfkk'] == '0': 
        sql += " not null "
    
    return sql

def hy_sybyz( db, sjkmxid, sjbmc, file_lst, type = '022' ):
    """
    # 回退：处理数据库索引( 索引不一致 )
    """
    # 数据索引信息
    # 查询临时表中索引信息
    # 索引名称,索引字段,索引类型,是否唯一索引
    zd_lst = [ 'symc', 'syzd', 'sylx', 'sfwysy' ]
    sjksy_ls = ModSql.common.execute_sql( db, 'get_tab_xx', { 'zd_lst': zd_lst,
    'tname_lst': ['gl_sjksy_ls'],
    'sel_lst': ['sssjb_id'],
    'id': sjkmxid })
    # [ { 索引名称:[索引字段,索引类型,是否唯一索引] } ]
    sy_lst_ls = [ { obj.symc: [ obj.syzd, obj.sylx, obj.sfwysy ] } for obj in sjksy_ls ]
    # 查询正式表中索引信息
    sjksy_zc = ModSql.common.execute_sql( db, 'get_tab_xx', { 'zd_lst': zd_lst,
    'tname_lst': ['gl_sjksy'],
    'sel_lst': ['sssjb_id'],
    'id': sjkmxid })
    sy_lst_zc = [ { obj.symc: [ obj.syzd, obj.sylx, obj.sfwysy ] } for obj in sjksy_zc ]
    
    # 判断索引列表是否一致
    if sy_lst_ls != sy_lst_zc:
        # 以临时表为主列表
        for sy_dic_ls in sy_lst_ls:
            flag = False
            symc = list( sy_dic_ls.keys() )[0]
            syxx = list( sy_dic_ls.values() )[0]
            # 验证与正式表的关系
            for sy_dic_zc in sy_lst_zc:
                if sy_dic_ls == sy_dic_zc:
                    flag = True
                    continue
                # 索引名称相同，索引属性不同，说明此索引为修改（删除索引重建）
                elif symc == list( sy_dic_zc.keys() )[0] and syxx != list( sy_dic_zc.values() )[0]:
                    flag = True
                    syxx_zc = list( sy_dic_zc.values() )[0]
                    # 索引名称:[索引字段,索引类型,是否唯一索引]
                    # 新增索引{sylx:sylx,sfwysy:sfwysy,symc:symc,syzd:syzd}
                    sy_lst = [{ 'sylx': syxx[1], 'sfwysy': syxx[2], 'symc': symc, 
                    'syzd': ','.join( syxx[0].split('|') ) }]
                    sy_sql_dic = insert_sy_sql(sjbmc, sy_lst )
                    tmp = ''
                    if sy_sql_dic:
                        tmp = list(sy_sql_dic.values())[0]
                    
                    # 追加执行sql
                    if type == '022':
                        file_lst.append( """%s.%s索引操作：修改
    建议SQL：
        drop index %s;
        %s
    导入前属性：
        索引名称：%s
        索引类型：%s
        索引字段：%s
        是否唯一索引：%s
    导入后属性：
        索引名称：%s
        索引类型：%s
        索引字段：%s
        是否唯一索引：%s
    """ % ( sjbmc, symc, symc, tmp,
    symc, syxx[1], syxx[0], syxx[2],
    symc, syxx_zc[1], syxx_zc[0], syxx_zc[2] ) )
                    else:
                        file_lst.append( """%s.%s索引操作：修改
    建议SQL：
        drop index %s;
        %s
    导入前属性：
        索引名称：%s
        索引类型：%s
        索引字段：%s
        是否唯一索引：%s
    导入后属性：
        索引名称：%s
        索引类型：%s
        索引字段：%s
        是否唯一索引：%s
    """ % ( sjbmc, symc, symc, tmp,
    symc, syxx_zc[1], syxx_zc[0], syxx_zc[2],
    symc, syxx[1], syxx[0], syxx[2] ) )
                    # 退出此次循环
                    continue
            
            # 在现有表中不存在，说明此索引为新增
            if flag == False:
                # 索引名称:[索引字段,索引类型,是否唯一索引]
                # 新增索引{sylx:sylx,sfwysy:sfwysy,symc:symc,syzd:syzd}
                sy_lst = [{ 'sylx': syxx[1], 'sfwysy': syxx[2], 'symc': symc, 
                'syzd': ','.join( syxx[0].split('|') ) }]
                sy_sql_dic = insert_sy_sql(sjbmc, sy_lst )
                tmp = ''
                if sy_sql_dic:
                    tmp = list(sy_sql_dic.values())[0]
                
                # 追加执行sql
                file_lst.append( """%s.%s索引操作：新增
建议SQL：
    %s
""" % ( sjbmc, symc, tmp ) )
        
        # 以正式表为主列表( 查询正式表在临时表不存在的 )
        symc_lst_ls = [ list( syxx_dic.keys() )[0] for syxx_dic in sy_lst_ls ]
        for sy_dic_zc in sy_lst_zc:
            symc = list( sy_dic_zc.keys() )[0]
            # 不存在，说明此所以需要删除
            if symc not in symc_lst_ls:
                # 追加执行sql
                file_lst.append( """%s.%s索引操作：删除
    建议SQL：
        drop index %s
    """ % ( sjbmc, symc, symc ) )

def hy_ysbyz( db, sjkmxid, sjbmc, file_lst, type = '022' ):
    """
    # 回退：处理数据库约束( 约束不一致 )
    """
    # 数据约束信息
    # 查询临时表中约束信息
    # 约束名称,约束字段
    zd_lst = [ 'ysmc', 'yszd' ]
    sjkys_ls = ModSql.common.execute_sql( db, 'get_tab_xx', { 'zd_lst': zd_lst,
    'tname_lst': ['gl_sjkys_ls'],
    'sel_lst': ['sssjb_id'],
    'id': sjkmxid })
    # [ { 约束名称:[约束字段] } ]
    ys_lst_ls = [ { obj.ysmc: [ obj.yszd ] } for obj in sjkys_ls ]
    # 查询正式表中索引信息
    sjkys_zc = ModSql.common.execute_sql( db, 'get_tab_xx', { 'zd_lst': zd_lst,
    'tname_lst': ['gl_sjkys'],
    'sel_lst': ['sssjb_id'],
    'id': sjkmxid })
    ys_lst_zc = [ { obj.ysmc: [ obj.yszd ] } for obj in sjkys_zc ]
    
    if ys_lst_ls != ys_lst_zc:
        # 以临时表为主列表
        for ys_dic_ls in ys_lst_ls:
            flag = False
            ysmc = list( ys_dic_ls.keys() )[0]
            ysxx = list( ys_dic_ls.values() )[0]
            # 验证与正式表的关系
            for ys_dic_zc in ys_lst_zc:
                if ys_dic_ls == ys_dic_zc:
                    flag = True
                    continue
                #  约束信息不同，说明此约束有修改
                elif ysmc == list( ys_dic_zc.keys() )[0] and ysxx != list( ys_dic_zc.values() )[0]:
                    flag = True
                    ysxx_zc = list( ys_dic_zc.values() )[0]
                    # 约束名称:[约束字段]
                    # 修改约束{ysmc:ysmc,yszd:yszd}
                    ys_lst = [{ 'ysmc': ysmc, 
                    'yszd': ','.join( ysxx[0].split('|') ) }]
                    ys_sql_lst = insert_ys_sql(sjbmc, ys_lst )
                    tmp = ys_sql_lst[0]
                    
                    # 追加执行sql
                    if type == '022':
                        file_lst.append( """%s.%s约束操作：修改
    建议SQL：
        alter table %s drop constraint %s
        %s
    导入前属性：
        约束名称：%s
        约束字段：%s
    导入后属性：
        约束名称：%s
        约束字段：%s
    """ % ( sjbmc, ysmc, sjbmc, ysmc, tmp,
    ysmc, ysxx[0],
    ysmc, ysxx_zc[0] ) )
                    else:
                        file_lst.append( """%s.%s约束操作：修改
    建议SQL：
        alter table %s drop constraint %s
        %s
    导入前属性：
        约束名称：%s
        约束字段：%s
    导入后属性：
        约束名称：%s
        约束字段：%s
    """ % ( sjbmc, ysmc, sjbmc, ysmc, tmp,
    ysmc, ysxx_zc[0],
    ysmc, ysxx[0] ) )
                    # 退出此次循环
                    continue
            
            # 在现有表中不存在，说明此约束为新增
            if flag == False:
                # 约束名称:[约束字段]
                # 修改约束{ysmc:ysmc,yszd:yszd}
                ys_lst = [{ 'ysmc': ysmc, 
                'yszd': ','.join( ysxx[0].split('|') ) }]
                ys_sql_lst = insert_ys_sql(sjbmc, ys_lst )
                tmp = ys_sql_lst[0]
                # 追加执行sql
                file_lst.append( """%s.%s约束操作：新增
建议SQL：
    %s
""" % ( sjbmc, ysmc, tmp ) )
    
    # 以正式表为主列表( 查询正式表在临时表不存在的 )
    ysmc_lst_ls = [ list( ysxx_dic.keys() )[0] for ysxx_dic in ys_lst_ls ]
    for ys_dic_zc in ys_lst_zc:
        ysmc = list( ys_dic_zc.keys() )[0]
        # 不存在，说明此所以需要删除
        if ysmc not in ysmc_lst_ls:
            # 追加执行sql
            file_lst.append( """%s.%s约束操作：删除
建议SQL：
    alter table %s drop constraint %s
""" % ( sjbmc, ysmc, sjbmc, ysmc ) )

def hy_upd_data( db ):
    """
    # 后台批量处理完成后将临时表中的数据导入到正式表( 数据表相关数据 )
    """
    zs_tab_lst = [ 'gl_sjkmxdy', 'gl_sjkzdb', 'gl_sjksy', 'gl_sjkys' ]
    if zs_tab_lst:
        for tname in zs_tab_lst:
            # 先删除表数据
            ModSql.common.execute_sql_dict( db, 'delete_bytab', { 'tname': [tname] } )
            # 后创建
            ModSql.common.execute_sql_dict( db, 'inset_bytab', { 'tname_lst_zs': [tname], 
                'tname_lst_ls': ['%s_LS' % tname] } )

def hy_write_file( file_lst ):
    """
    # 需要执行的sql放在指定文件中
    """
    # txt 书写目录
    app_name = '_init'
    try:
        app_name = settings._T.APP_NAME
    except:
        app_name = '_init'
    path = os.path.join( STATIC_DIR, app_name, 'backup_dmp' )
    # 文件名称( 数据库模型回退步骤 )
    fname = '数据模型回退步骤_%s.TXT' % ( get_strftime2() )
    # 写文件
    fpath = os.path.join( path, fname )
    file = open( fpath, 'w' )
    file.writelines( file_lst )
    file.close()
    
    return fpath
