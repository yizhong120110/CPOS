# -*- coding: utf-8 -*-
# Action: 导出
# Author: jind
# AddTime: 2015-01-31
# Standard: 注释仅能以“#”开头，sql可以是“--”；注释不能同代码在同一行

from sjzhtspj import ModSql,get_sess_hydm,TMPDIR,logger
from sjzhtspj.common import get_uuid,update_wym,ins_czrz,get_strftime,date_imp_exp_check,get_imp_exp_data,get_imp_exp_wtj_data,get_strftime2,set_zdfqpzsm
import os,pickle,subprocess
from sjzhtspj.esb import send_jr

def index_service( ):
    """
    # 获取系统类型
    """
    with sjapi.connection() as db:
        # 查询系统类型
        xtlx = ModSql.common.execute_sql(db, "get_xtlx")[0].value
        return xtlx

def data_service( ywid,dclx,txid ):
    """
    # 获取导出数据
    # @param ywid:业务ID
    # @param dclx:导出类型
    """
    return get_imp_exp_data( ywid,dclx,txid )
        
def data_wtjsj_service( ywid,dclx,txid ):
    """
    # 获取未提交数据
    """    
    return get_imp_exp_wtj_data( ywid,dclx,txid )
        
def data_export_jy_service( ywid,dclx,txid ):
    """
    # 导出校验
    """
    return date_imp_exp_check( ywid,dclx,txid )
        
def data_export_submit_service( ywid,xtlx,jy_lst,zlc_lst,sjkmx_lst,gghs_lst,jd_lst,dclx,dcms,bzxx,tx_id_lst):
    """
    # 导出提交
    # @param ywid:业务id
    # @param xtlx:系统类型
    # @param jy_lst:交易列表
    # @param zlc_lst:子流程列表
    # @param sjkmx_lst:数据库模型列表
    # @param gghs_lst:公共函数列表
    # @param jd_lst:节点列表
    # @param dclx:导出类型
    # @param dcms:导出描述
    # @param bzxx:备注信息
    # @param tx_id_lst:通讯ID列表
    """
    result = {'state':False,'msg':''}
    nr = ''
    with sjapi.connection() as db:
        # 业务导出
        if dclx == 'yw':
            result['state'],result['msg'] = yw_export( db ,ywid,xtlx,jy_lst,zlc_lst,sjkmx_lst,gghs_lst,jd_lst,dclx )
            # 业务导出日志登记内容
            nr = '业务导出：系统类型：%s，业务ID：%s，导出类型：%s，导出描述：%s，备注信息：%s' % ( xtlx,ywid,dclx,dcms,bzxx )
        # 交易导出
        elif dclx == 'jy':
            result['state'],result['msg'] = jy_export( db ,ywid,xtlx,jy_lst,zlc_lst,sjkmx_lst,gghs_lst,jd_lst,dclx )
            # 交易导出日志登记内容
            nr = '交易导出：系统类型：%s，交易ID列表：%s，导出类型：%s，导出描述：%s，备注信息：%s' % ( xtlx,",".join( [dic['id'] for  dic in jy_lst] ),dclx,dcms,bzxx )
        # 通讯导出
        elif dclx == 'tx':
            result['state'],result['msg'] = tx_export( db,xtlx,tx_id_lst,jd_lst,dclx )
            # 通讯导出日志登记内容
            nr = '通讯导出：系统类型：%s，通讯ID列表：%s，导出类型：%s，导出描述：%s，备注信息：%s' % ( xtlx,",".join( tx_id_lst ),dclx,dcms,bzxx )
        if not result['state']:
            return result
        ssid = ''
        if dclx == 'tx':
            ssid = ",".join( tx_id_lst )
        elif dclx == 'jy':
            ssid = ",".join( [dic['id'] for  dic in jy_lst] )
        else:
            ssid = ywid
        # 将导出类型放在drdc_ls表中
        inset_dclx( db, dclx )
    # 执行导出动作
    with sjapi.connection() as db:
        result['state'],result['msg'] = exe_export( db,ssid,dclx,dcms,bzxx,ywid,nr )
        if not result['msg']:
            result['msg'] = '导出成功'
        return result
        
def jy_export( db ,ywid,xtlx,jy_lst,zlc_lst,sjkmx_lst,gghs_lst,jd_lst,dclx ):
    """
    #交易导出
    """
    # 查询交易所引用的子流程
    rs = ModSql.kf_ywgl_021.execute_sql_dict(db,"get_extend_zlcjy",{'ywid':ywid})
    #如果有结果，说明交易引用了子流程
    if rs:
        # 获取子流程的ID
        zlcid_lst = [ dic['jddyid'] for dic in rs ]
        # 后台判断导出的交易对应的子流程是否存在
        count = ModSql.kf_ywgl_021.execute_sql( db,"check_zlc",{'zlcid_lst':zlcid_lst})[0].count
        # 若查询出的记录数与子流程的个数不一致
        if count != len(zlcid_lst):
            return False,'交易与其调用子流程不能一一对应，请检查'
    # 查询当前系统中的临时表
    rs = ModSql.common.execute_sql_dict(db,"get_ls_tname")
    # 删除临时表
    if rs:
        drop_table_ls( db,rs )
    # 创建交易定义临时表
    ModSql.kf_ywgl_021.execute_sql( db,"create_ls_table",{'lsbname':['GL_JYDY_LS'],'bname':['gl_jydy']})
    # 创建流程布局临时表
    ModSql.kf_ywgl_021.execute_sql( db,"create_ls_table",{'lsbname':['GL_LCBJ_LS'],'bname':['gl_lcbj']})
    # 创建流程走向临时表
    ModSql.kf_ywgl_021.execute_sql( db,"create_ls_table",{'lsbname':['GL_LCZX_LS'],'bname':['gl_lczx']})
    # 创建BLOB管理表临时表
    ModSql.kf_ywgl_021.execute_sql( db,"create_ls_table",{'lsbname':['GL_BLOB_LS'],'bname':['gl_blob']})
    # 批量转单笔的将版本库数据导出到临时表
    for dic in jy_lst:
        # 将内容导入到BLOB管理临时表
        ModSql.kf_ywgl_021.execute_sql( db,"insert_gl_blob_ls",{'ssid':dic['id'],'bbh':dic['version']})
        # 查询版本库中的交易数据
        nr = pickle.loads( ModSql.kf_ywgl_021.execute_sql( db,"get_bb_nr",{'ssid':dic['id'],'bbh':dic['version']})[0].nr.read() )
        # 交易定义信息
        jydy_lst = nr['gl_jydy']
        # 流程走向信息
        lczx_lst = nr['gl_lczx']
        # 流程布局信息
        lcbj_lst = nr['gl_lcbj']
        # 将交易信息导出到交易定义临时表
        for dic in jydy_lst:
            # 由于之前的版本提交没有加自动发起配置说明，所以为了解决线上不出错，只能是手动添加。没有什么实际意义。
            dic['zdfqpzsm'] = set_zdfqpzsm(dic)
            ModSql.kf_ywgl_021.execute_sql( db,"insert_gl_jydy_ls",dic)
        # 将流程布局信息导出到流程布局临时表
        ins_gl_lcbj_ls( db,lcbj_lst )
        # 将流程走向信息导出到流程走向临时表
        ins_gl_lczx_ls( db,lczx_lst )
    
    # 创建参数定义临时表
    ModSql.kf_ywgl_021.execute_sql( db,"create_ls_table",{'lsbname':['GL_CSDY_LS'],'bname':['gl_csdy']})
    # 交易参数导出
    ModSql.kf_ywgl_021.execute_sql( db,"export_jycs" )
    # 创建子流程定义临时表
    ModSql.kf_ywgl_021.execute_sql( db,"create_ls_table",{'lsbname':['GL_ZLCDY_LS'],'bname':['gl_zlcdy']})
    # 批量转单笔的将版本库数据导出到临时表
    for dic in zlc_lst:
        # 将内容导入到BLOB管理临时表
        ModSql.kf_ywgl_021.execute_sql( db,"insert_gl_blob_ls",{'ssid':dic['id'],'bbh':dic['version']})
        # 查询版本控制表中子流程数据
        nr = pickle.loads( ModSql.kf_ywgl_021.execute_sql( db,"get_bb_nr",{'ssid':dic['id'],'bbh':dic['version']})[0].nr.read() )
        # 子流程信息
        zlcdy_lst = nr['gl_zlcdy']
        # 流程走向信息
        lczx_lst = nr['gl_lczx']
        # 流程布局信息
        lcbj_lst = nr['gl_lcbj']
        # 将子流程信息导出到子流程定义临时表
        for dic in zlcdy_lst:
            ModSql.kf_ywgl_021.execute_sql( db,"insert_gl_zlcdy_ls",dic)
        # 将流程布局信息导出到流程布局临时表
        ins_gl_lcbj_ls( db,lcbj_lst )
        # 将流程走向信息导出到流程走向临时表
        ins_gl_lczx_ls( db,lczx_lst )
        
    # 节点导出
    jd_export( db,jd_lst,dclx )    
    # 测试案例导出,若为生产机导出时无需次步骤
    if xtlx == 'kf':
        # 创建测试案例执行步骤临时表
        ModSql.kf_ywgl_021.execute_sql( db,"create_ls_table",{'lsbname':['GL_JDCSALZXBZ_LS'],'bname':['gl_jdcsalzxbz']})
        # 创建测试案例执行步骤要素临时表
        ModSql.kf_ywgl_021.execute_sql( db,"create_ls_table",{'lsbname':['GL_JDCSALYS_LS'],'bname':['gl_jdcsalys']})
        export_csal( db,dclx )
    return True,''
    
def yw_export( db ,ywid,xtlx,jy_lst,zlc_lst,sjkmx_lst,gghs_lst,jd_lst,dclx ):
    """
    # 业务导出
    """
    # 业务导出比之交易的导出多了业务参数，业务公共函数，数据库，打印模版的导出，其他的可直接调用交易的导出
    result,msg = jy_export( db ,ywid,xtlx,jy_lst,zlc_lst,sjkmx_lst,gghs_lst,jd_lst,dclx )
    if not result:
        return result,msg
    # 创建业务临时表
    ModSql.kf_ywgl_021.execute_sql(db,"create_ywdy_ls",{'cxtj':[('id',ywid)]})
    # 业务参数导出
    ModSql.kf_ywgl_021.execute_sql(db,"export_ywcs")
    # 业务公共函数导出
    ModSql.kf_ywgl_021.execute_sql( db,"create_ls_table",{'lsbname':['GL_YW_GGHS_LS'],'bname':['gl_yw_gghs']})
    # 批量转单笔的将版本库数据导出到临时表
    for dic in gghs_lst:
        # 将内容导入到BLOB管理临时表
        ModSql.kf_ywgl_021.execute_sql( db,"insert_gl_blob_ls",{'ssid':dic['id'],'bbh':dic['version']})
        # 查询版本控制表中公共函数数据
        nr = pickle.loads( ModSql.kf_ywgl_021.execute_sql( db,"get_bb_nr",{'ssid':dic['id'],'bbh':dic['version']})[0].nr.read() )
        # 公共函数信息
        gghsdy_lst = nr['gl_yw_gghs']
        # 将公共函数信息导出至公共函数临时表
        for dic in gghsdy_lst:
            ModSql.kf_ywgl_021.execute_sql( db,"insert_gghs_ls",dic)
            # 获取业务公共函数的内容_id，查询函数逻辑代码导出到BLOB管理临时表
            ModSql.kf_ywgl_021.execute_sql(db,"insert_nr_blob",{'id':dic['nr_id']})
            
    # 打印模版导出,创建打印模版临时表
    ModSql.kf_ywgl_021.execute_sql(db,"create_dymbdy_ls",{'cxtj':[('ssyw_id',ywid)]})
    # 将打印模版内容导出到BLOB临时表
    ModSql.kf_ywgl_021.execute_sql(db,"export_dymbnr")
    # 数据库模型导出
    ModSql.kf_ywgl_021.execute_sql(db,"create_ls_table",{'lsbname':['GL_SJKMXDY_LS'],'bname':['gl_sjkmxdy']})
    # 创建数据库字段临时表
    ModSql.kf_ywgl_021.execute_sql(db,"create_ls_table",{'lsbname':['GL_SJKZDB_LS'],'bname':['gl_sjkzdb']})
    # 创建数据库索引临时表
    ModSql.kf_ywgl_021.execute_sql(db,"create_ls_table",{'lsbname':['GL_SJKSY_LS'],'bname':['gl_sjksy']})
    # 创建数据库约束临时表
    ModSql.kf_ywgl_021.execute_sql(db,"create_ls_table",{'lsbname':['GL_SJKYS_LS'],'bname':['gl_sjkys']})
    # 批量转单笔的将版本库数据导出到临时表
    for dic in sjkmx_lst:
        # 将内容导入到BLOB管理临时表
        ModSql.kf_ywgl_021.execute_sql( db,"insert_gl_blob_ls",{'ssid':dic['id'],'bbh':dic['version']})
        # 查询版本控制表中数据库模型数据
        nr = pickle.loads( ModSql.kf_ywgl_021.execute_sql( db,"get_bb_nr",{'ssid':dic['id'],'bbh':dic['version']})[0].nr.read() )
        # 数据库模型定义信息
        sjkmxdy_lst = nr['gl_sjkmxdy']
        # 数据库模型字段信息
        zd_lst = nr['gl_sjkzdb']
        # 数据库模型约束信息
        ys_lst = nr['gl_sjkys']
        # 数据库模型索引信息
        sy_lst = nr['gl_sjksy']
        # 将数据库模型定义信息导出到数据库模型定义临时表
        for dic in sjkmxdy_lst:
            ModSql.kf_ywgl_021.execute_sql( db,"insert_sjkmxdy_ls",dic)
        # 将数据库字段信息导出到数据库字段临时表
        for dic in zd_lst:
            ModSql.kf_ywgl_021.execute_sql( db,"insert_sjkzdb_ls",dic)
        # 将数据库约束信息导出到数据库约束临时表
        for dic in ys_lst:
            ModSql.kf_ywgl_021.execute_sql( db,"insert_sjkys_ls",dic)
        # 将数据库索引信息导出到数据库索引临时表
        for dic in sy_lst:
            ModSql.kf_ywgl_021.execute_sql( db,"insert_sjksy_ls",dic)
    return True,''
    
def tx_export( db,xtlx,tx_id_lst,jd_lst,dclx ):
    """
    # 通讯导出
    """
    # 查询当前系统中的临时表
    rs = ModSql.common.execute_sql_dict(db,"get_ls_tname")
    # 删除临时表
    if rs:
        drop_table_ls( db,rs )
    # 通讯参数导出
    ModSql.kf_ywgl_021.execute_sql(db,"export_txcs",{'txidlst':tx_id_lst})
    # 通讯基本信息导出
    ModSql.kf_ywgl_021.execute_sql(db,"export_txgl",{'txidlst':tx_id_lst})
    # 交易码解出函数导出
    ModSql.kf_ywgl_021.execute_sql(db,"export_jymjchs")
    # 编码维护信息导出（通讯类型)
    ModSql.kf_ywgl_021.execute_sql(db,"export_txlx")
    # C端通讯导出
    ModSql.kf_ywgl_021.execute_sql(db,"export_cdtx",{'txidlst':tx_id_lst})
    # 子流程导出
    ModSql.kf_ywgl_021.execute_sql(db,"export_zlc")
    # 通讯节点导出
    jd_export( db,jd_lst,dclx )           
    # 若为开发系统
    if xtlx == 'kf':
        # 通讯挡板导出
        ModSql.kf_ywgl_021.execute_sql(db,"export_dbdy")
        # 通讯挡板要素导出
        ModSql.kf_ywgl_021.execute_sql(db,"export_dbdyys")
        # 将C端通讯的测试案例执行步骤导出到临时表
        ModSql.kf_ywgl_021.execute_sql(db,"export_csalzxbz")
        # 将C端通讯的测试案例执行步骤要素信息导出到临时表
        ModSql.kf_ywgl_021.execute_sql(db,"export_csalzxbz_ys")
        # 测试案例导出
        export_csal( db,dclx )
    return True,''
     
def jd_export( db,jd_lst,dclx ):
    """
    # 节点导出，在业务、交易、通讯导出时，都需要导出节点，所以提取出来
    """    
    # 节点导出,创建节点定义临时表
    ModSql.kf_ywgl_021.execute_sql( db,"create_ls_table",{'lsbname':['GL_JDDY_LS'],'bname':['gl_jddy']})
    # 创建节点要素临时表
    ModSql.kf_ywgl_021.execute_sql( db,"create_ls_table",{'lsbname':['GL_JDYS_LS'],'bname':['gl_jdys']})
    # 批量转单笔的将版本库数据导出到临时表
    for dic in jd_lst:
        # 将内容导入到BLOB管理临时表
        ModSql.kf_ywgl_021.execute_sql( db,"insert_gl_blob_ls",{'ssid':dic['id'],'bbh':dic['version']})
        # 查询版本控制表中公共函数数据
        nr = pickle.loads( ModSql.kf_ywgl_021.execute_sql( db,"get_bb_nr",{'ssid':dic['id'],'bbh':dic['version']})[0].nr.read() )
        # 节点信息
        jddy_lst = nr['gl_jddy']
        # 节点要素信息
        jdysdy_lst = nr['gl_jdys']
        # 将节点信息登记至节点定义临时表
        ins_gl_jddy_ls( db,jddy_lst )
        # 将节点要素信息登记至节点要素临时表
        ins_gl_jdys_ls( db,jdysdy_lst )

def exe_export( db,ssid,dclx,dcms,bzxx,ywid,nr ):
    """
    #执行导出命令，并登记导出流水
    """
    # 从环境变量中获取数据库的用户名及密码、SID
    # oracle sid
    ORACLE_SID = os.environ['ORACLE_SID']
    # 密码
    ORACLE_DBPW = os.environ['ORACLE_DBPW']
    # 用户名
    ORACLE_DBU = os.environ['ORACLE_RDBU']
    # 对于用户名及密码需解密,对于用户名及密码尚不确定是否需要解密
    #ORACLE_DBPW,ORACLE_DBU = _DBdecrypt.DBdecrypt(ORACLE_DBPW, ORACLE_DBU)
    create_table = ModSql.common.execute_sql_dict(db,"get_ls_tname")
    table_name = ",".join( [ dic['table_name'] for dic in create_table] )
    fname = 'TSPT_EXPORT_%s_%s.dmp'%( dclx.upper(), get_strftime2() )
    # 获取导出文件的生成目录
    uploadPath = ModSql.common.execute_sql_dict(db,"get_csdyv_bycsdm",{'lx':'1','csdm':'db_ftp_uploadPath'})[0]['value']
    filename = os.path.join( uploadPath,fname )
    cmd = "exp %s/%s@%s file='%s' TABLES = %s "%( ORACLE_DBU,ORACLE_DBPW,ORACLE_SID,filename,table_name )
    # 获取数据库服务器的IP
    db_ip = ModSql.common.execute_sql_dict(db,"get_csdyv_bycsdm",{'lx':'1','csdm':'db_ip'})[0]['value']
    logger.info('导出命令param：%s' % cmd)
    logger.info('导出服务器db_ip：%s' % str(db_ip))
    result = send_jr({'param':[cmd]},db_ip)
    logger.info('反馈值：%s' % str(result))
    #if "Export terminated successfully without warnings" in result or "成功终止导出, 没有出现警告" in result:
    if result and result == "ok":
        sql_data = {'id':get_uuid(),'ss_idlb':ssid,'ssywid':ywid,'czlx':'dc','nrlx':dclx,'czr':get_sess_hydm(),'czsj':get_strftime(),'czms':dcms,'bfwjm':fname,'bz':bzxx,'zt':'1','wjm':'','fhr':''}
        ModSql.common.execute_sql( db,"insert_drls",sql_data)
        # 删除临时表(zcl 20150618 因为是异步请求，所以不能立即删除临时表)
        # drop_table_ls( db,create_table )
        # 操作日志登记
        nr = '%s，导出流水ID：%s' % ( nr,sql_data['id'] )
        ins_czrz( db, nr , gnmc = '导出' )
        return True,'导出请求已发送，请稍后到系统参数[db_ftp_uploadPath]配置目录[%s]下，下载文件：【%s】' % ( uploadPath, fname )
    else:
        return False,'导出失败，请检查问题原因'
    
def drop_table_ls( db,table_name ):
    """
    #删除临时表
    """
    for dic in table_name:
        ModSql.common.execute_sql(db,"drop_table",{'tname_lst':[dic['table_name']]})
        
def ins_gl_lcbj_ls( db,lcbj_lst ):
    """
    #将版本库数据登记至流程布局临时表
    """ 
    for dic in lcbj_lst:
        # 处理版本提交没有保存此字段的现象
        dic['czpzid'] = dic.get('czpzid','')
        ModSql.kf_ywgl_021.execute_sql( db,"insert_gl_lcbj_ls",dic )
        
def ins_gl_lczx_ls( db,lczx_lst ):
    """
    #将版本库数据登记至流程走向临时表
    """ 
    for dic in lczx_lst:
        ModSql.kf_ywgl_021.execute_sql( db,"insert_gl_lczx_ls",dic )
        
def ins_gl_jddy_ls( db,jddy_lst ):
    """
    # 将节点信息登记至节点定义临时表
    """
    for dic in jddy_lst:
        # 登记节点信息
        ModSql.kf_ywgl_021.execute_sql(db,"insert_gl_jddy_ls",dic)
        # 将节点代码登记至BLOB临时表
        ModSql.kf_ywgl_021.execute_sql(db,"insert_nr_blob",{'id':dic['dm_id']})
        
def ins_gl_jdys_ls( db,jdysdy_lst ):
    """
    # 将节点要素信息登记至节点要素临时表
    """
    for dic in jdysdy_lst:
        ModSql.kf_ywgl_021.execute_sql(db,"insert_gl_jdys_ls",dic)
        
def export_csal( db,dclx ):
    """ 
    # 测试案例导出操作
    """
    # 创建测试案例临时表
    ModSql.kf_ywgl_021.execute_sql( db,"create_ls_table",{'lsbname':['GL_CSALDY_LS'],'bname':['gl_csaldy']})
    # 将子流程测试案例导出到临时表
    ModSql.kf_ywgl_021.execute_sql(db,"insert_gl_csaldy_ls",{'lsbname':['gl_zlcdy_ls'], 'jylsbname':[]})
    # 将节点测试案例导出到临时表
    if dclx != 'tx':
        ModSql.kf_ywgl_021.execute_sql(db,"insert_gl_csaldy_ls",{'lsbname':['gl_jddy_ls'], 'jylsbname':['gl_jydy_ls']})
    else:
        ModSql.kf_ywgl_021.execute_sql(db,"insert_gl_csaldy_ls",{'lsbname':['gl_jddy_ls'], 'jylsbname':[]})
    # 将节点测试案例执行步骤导出到临时表
    ModSql.kf_ywgl_021.execute_sql(db,"insert_jdcsalzxbz_ls",{'cloumnname': ['jdcsaldyid']})
    if dclx != 'tx':
        # 将交易测试案例导出到临时表
        ModSql.kf_ywgl_021.execute_sql(db,"insert_gl_csaldy_ls",{'lsbname':['gl_jydy_ls'], 'jylsbname':[]})
        # 将交易测试案例执行步骤导出到临时表
        ModSql.kf_ywgl_021.execute_sql(db,"insert_jdcsalzxbz_ls",{'cloumnname': ['csaldyid']})
        # 将demo基本信息导出到临时表
        ModSql.kf_ywgl_021.execute_sql(db,"create_demo_jbxx_ls")
        # 将demo数据导出到临时表
        ModSql.kf_ywgl_021.execute_sql(db,"create_demo_sj_ls")
    # 将节点测试案例要素导出到临时表
    ModSql.kf_ywgl_021.execute_sql(db,"insert_jdcsalys_ls")
    
def inset_dclx( db, dclx ):
    """
    # 将导出类型放在drdc_ls表中，并将此临时表放在导出文件件中，用于导入判断
    @param db 数据库连接
    @param dclx 导出类型
    """
    # 创建导入导出类型临时表
    ModSql.kf_ywgl_021.execute_sql(db,"create_drdclx_tab_ls")
    # 想临时表中插入本次导出类型
    ModSql.kf_ywgl_021.execute_sql(db,"insert_drdclx", { 'lx': dclx })
    