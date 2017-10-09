# -*- coding: utf-8 -*-
# Action: 导入
# Author: jind
# AddTime: 2015-01-31
# Standard: 注释仅能以“#”开头，sql可以是“--”；注释不能同代码在同一行
import os,pickle,traceback,json
from sjzhtspj import ModSql,get_sess_hydm,TMPDIR,logger
from sjzhtspj.common import ( get_uuid,get_strftime,date_imp_exp_check,get_imp_exp_data,get_imp_exp_wtj_data,get_sjbj,get_file_path,
get_strftime2,xml_out,check_fhr,get_bcxx,get_parent_css,ftp_put,update_wym,update_jhrw,ins_czrz,set_zdfqpzsm )
from sjzhtspj.const import SYLX_DIC,JDYS_LB_DIC,JDYS_LY_DIC,JDLX_MC_DIC,FHR_JSDM
from  _init.oa.kf_txgl.kf_txgl_001.kf_txgl_001_common import add_cdtx_lc
from  _init.oa.kf_ywgl.kf_ywgl_022.kf_ywgl_022_service import ht_zdbyz,hy_sybyz,hy_ysbyz,hy_write_file
from sjzhtspj.esb import send_jr, sftp_put, memcache_data_del

def index_service( ):
    """
    # 获取系统类型
    """
    with sjapi.connection() as db:
        # 查询系统类型
        xtlx = ModSql.common.execute_sql(db, "get_xtlx")[0].value
        return xtlx
        
def data_import_jy_service( ywid,drlx,txid ):
    """
    # 导入校验
    """
    return date_imp_exp_check( ywid,drlx,txid )

def data_service( ywid,drlx,txid ):
    """
    # 获取导入数据
    # @param ywid:业务ID
    # @param drlx:导入类型
    """
    if drlx =='yw' and ywid =='-1':
        return {'rows':[],'state':True}
    if drlx =='tx' and txid =='-1':
        return {'rows':[],'state':True}
    return get_imp_exp_data( ywid,drlx,txid )
        
def data_wtjsj_service( ywid,drlx,txid ):
    """
    # 获取未提交数据
    """    
    return get_imp_exp_wtj_data( ywid,drlx,txid )
    
def data_drwj_add_service(filename,wjnr,ywid,drlx,xtlx,txid):
    """
    # 将导入文件中的内容导入值数据库，并重新查询两侧的数据
    """
    with sjapi.connection() as db:
        # 将文件写入到本地目录
        fpath = os.path.join( TMPDIR,filename )
        fobj = open( fpath,'wb')
        fobj.write( wjnr )
        fobj.close()
        # 获取数据库服务器的IP 
        db_ip = ModSql.common.execute_sql_dict(db,"get_csdyv_bycsdm",{'lx':'1','csdm':'db_ip'})[0]['value']
        db_ftp_ip = ModSql.common.execute_sql_dict(db,"get_csdyv_bycsdm",{'lx':'1','csdm':'db_ftp_ip'})[0]['value']
        # 获取数据库服务器FTP端口
        db_ftp_port = ModSql.common.execute_sql_dict(db,"get_csdyv_bycsdm",{'lx':'1','csdm':'db_ftp_port'})[0]['value']
        # 获取数据库服务器FTP用户名
        db_ftp_user = ModSql.common.execute_sql_dict(db,"get_csdyv_bycsdm",{'lx':'1','csdm':'db_ftp_user'})[0]['value']
        # 获取数据库服务器的IP
        db_ftp_pwd = ModSql.common.execute_sql_dict(db,"get_csdyv_bycsdm",{'lx':'1','csdm':'db_ftp_pwd'})[0]['value']
        # 获取导出文件的生成目录
        uploadPath = ModSql.common.execute_sql_dict(db,"get_csdyv_bycsdm",{'lx':'1','csdm':'db_ftp_uploadPath'})[0]['value']
        fpt_file = os.path.join( uploadPath,filename )
        # 到导入的文件上传至数据库服务器
        #flag = ftp_put( db_ftp_ip , int(db_ftp_port) , db_ftp_user , db_ftp_pwd , fpt_file)
        
        # sftp_put:参数1为sftpIP，参数2为sftp端口，参数3为sftp用户名，参数4为sftp用户密码，
        # 参数5为sftp远程路径，参数6为文件名，参数7为本地的文件目录位置，获取的是True/False
        flag = sftp_put(db_ftp_ip ,int(db_ftp_port), db_ftp_user, db_ftp_pwd, uploadPath, filename, TMPDIR)
        # 上传文件失败
        if not flag:
            return {'state':False,'msg':'SFTP失败，请检查问题原因'}
        # 登记导入流水
        drlsid = get_uuid()
        sql_data = {'id':drlsid,'czlx':'dr','nrlx':drlx,'czr':get_sess_hydm(),'czsj':get_strftime(),'czms':'','bfwjm':'','bz':'','zt':'0','wjm':filename,'fhr':'','ss_idlb':'','ssywid':''}
        ModSql.common.execute_sql( db,"insert_drls",sql_data)
        # 获取临时表
        rs = ModSql.common.execute_sql_dict(db,"get_ls_tname")
        # 删除临时表
        for dic in rs:
            ModSql.common.execute_sql(db,"drop_table",{'tname_lst':[dic['table_name']]})
        table_name = []
        if drlx == 'yw':
            table_name = ['GL_YW_GGHS', 'GL_SJKMXDY', 'GL_SJKSY', 'GL_SJKZDB', 'GL_SJKYS', 'GL_BLOB', 'GL_DYMBDY', 'GL_CSDY', 'GL_BBKZ', 'GL_JYDY', 'GL_LCBJ', 'GL_ZLCDY', 'GL_LCZX', 'GL_JDDY', 'GL_YWDY', 'GL_JDYS', 'GL_BMWH']
            if xtlx == 'kf':
                table_name.extend( ['GL_CSALDY', 'GL_JDCSALZXBZ', 'GL_JDCSALYS', 'GL_DEMO_JBXX', 'GL_DEMO_SJ'] )
        if drlx == 'jy':
            table_name = ['GL_YWDY','GL_BLOB', 'GL_CSDY', 'GL_BBKZ', 'GL_JYDY', 'GL_LCBJ', 'GL_ZLCDY', 'GL_LCZX', 'GL_JDDY', 'GL_JDYS', 'GL_BMWH']
            if xtlx == 'kf':
                table_name.extend( ['GL_CSALDY', 'GL_JDCSALZXBZ', 'GL_JDCSALYS', 'GL_DEMO_JBXX', 'GL_DEMO_SJ'] )
        if drlx == 'tx':
            table_name = ['GL_BLOB','GL_CSDY','GL_BMWH','GL_BBKZ','GL_TXGL','GL_CDTX','GL_ZLCDY','GL_LCBJ','GL_LCZX','GL_JDDY','GL_JDYS']
            if xtlx == 'kf':
                table_name.extend( ['GL_DBDY','GL_DBYS','GL_CSALDY', 'GL_JDCSALZXBZ', 'GL_JDCSALYS'] )
        # 创建临时表
        create_table( db,table_name)        
        # 从环境变量中获取数据库的用户名及密码、SID
        # oracle sid
        ORACLE_SID = os.environ['ORACLE_SID']
        # 密码
        ORACLE_DBPW = os.environ['ORACLE_DBPW']
        # 用户名
        ORACLE_DBU = os.environ['ORACLE_RDBU']
        # 获取备份目录
        backPath = ModSql.common.execute_sql_dict(db,"get_csdyv_bycsdm",{'lx':'1','csdm':'db_ftp_backPath'})[0]['value']
        # 导入之前先进行备份
        bfwjm = 'TSPT_EXPORT_%s.dmp'%( get_strftime2() )
        bfwjPath = os.path.join( backPath,bfwjm )
        table_name = ",".join( [ tname+"_LS" for tname in table_name] )
        cmd = "exp %s/%s@%s TABLES = %s COMPRESS=y file=%s statistics=none"%( ORACLE_DBU,ORACLE_DBPW,ORACLE_SID,table_name,bfwjPath )
        # 执行备份命令
        logger.info('备份命令param：%s' % cmd)
        logger.info('备份服务器db_ip：%s' % str(db_ip))
        result = send_jr({'param':[cmd]},db_ip)
        logger.info('反馈值：%s' % str(result))
        #if "Export terminated successfully without warnings" not in result and "成功终止导出, 没有出现警告" not in result:
        if result and result == "ok":
            pass
        else:
            return {'state':False,'msg':'备份命令执行失败，请检查问题原因'}
        import time
        logger.info('备份通知核心后，等待30秒执行下面操作start')
        time.sleep(30)
        logger.info('备份通知核心后，等待30秒执行下面操作end')
        # 更新导入流水
        ModSql.kf_ywgl_019.execute_sql( db,"update_drlswjm",{'id':drlsid,'bfwjm':bfwjm})
        # 获取临时表
        rs = ModSql.common.execute_sql_dict(db,"get_ls_tname")
        # 删除临时表
        for dic in rs:
            ModSql.common.execute_sql(db,"drop_table",{'tname_lst':[dic['table_name']]})
        # 执行导入命令
        fpath = os.path.join( uploadPath,filename )
        cmd = "imp %s/%s@%s file='%s'  full=y ignore=y statistics=none"%( ORACLE_DBU,ORACLE_DBPW,ORACLE_SID,fpath )
        logger.info('导入命令param：%s' % cmd)
        logger.info('导入服务器db_ip：%s' % str(db_ip))
        result = send_jr({'param':[cmd]},db_ip)
        logger.info('导入反馈值：%s' % str(result))
        #if "Import terminated successfully without warnings" not in result and "成功终止导入, 没有出现警告" not in result:
        if result and result == "ok":
            pass
        else:
            return {'state':False,'msg':'导入命令执行失败，请检查问题原因'}
        logger.info('导入通知核心后，等待30秒执行下面操作start')
        time.sleep(30)
        logger.info('导入通知核心后，等待30秒执行下面操作end')
        # 导入成功后，校验文件导入类型是否和预期导入类型一致
        msg = check_drlx( db, drlx, ywid = ywid )
        if msg == 'True':
            #导入文件执行成功后，重新获取左右两侧数据
            rs = get_data(db,ywid,drlx,txid)
            rs['drlsid'] = drlsid
            return rs
        else:
            return {'state':False,'msg': msg}
    
def create_table(db,table_name):
    """
    # 创建临时表
    """
    for tname in table_name:
        sql_data = {'tname':[tname],'lsname':[tname+"_LS"]}
        ModSql.kf_ywgl_019.execute_sql(db,"create_table",sql_data)

def get_data(db,ywid,drlx,txid):
    """
    # 导入文件执行成功后，重新获取左右两侧数据
    """
    if drlx == "yw":
        # 从临时表中获取待导入的业务ID
        id = ModSql.kf_ywgl_019.execute_sql_dict(db,"get_lsyw_id")[0]['id']
        count = ModSql.kf_ywgl_019.execute_sql_dict(db,"get_yw_count",{'ywid':id})[0]['count']
        # 当导入新业务、但待导入的业务在本地库存在或导入已有业务、但待导入的业务在本地不存在或导入已有业务、但左右两侧不是同一业务
        if ( ywid == '-1' and count != 0 ) or ( ywid != '-1' and count == 0 ) or ( ywid != '-1' and count!=0 and id !=ywid):
            return {'state':False,'msg':'待导入库数据与预期导入数据不一致，请检查'}
        return get_yw_data( db,ywid )
    elif drlx == "jy":
        return get_jy_data( db,ywid )
    elif drlx == "tx":
        # 从临时表中获取待导入的通讯ID
        id_rs = ModSql.kf_ywgl_019.execute_sql_dict(db,'get_txlsb_id')
        for dic in id_rs:
            count = ModSql.kf_ywgl_019.execute_sql_dict(db,"get_tx_count",{'txid':dic['id']})[0]['count']
            # 当导入新通讯、但待导入的通讯在本地库存在或导入已有通讯、但待导入的通讯在本地不存在
            if ( txid == '-1' and count != 0 ) or ( txid != '-1' and count == 0 ):
                return {'state':False,'msg':'待导入库数据与预期导入数据不一致，请检查'}
        return get_tx_data( db,txid )

def get_yw_data( db,ywid ):
    """
    # 获取业务导入数据
    """
    data = {'leftRows':'','rightRows':'','state':True}
    leftYwcs_lst,leftJy,leftZlc,leftDymb,leftGghs,leftSjkmx,leftJd = get_yw_left_data( db,ywid )
    if ywid == '-1':
        data['leftRows'] = get_yw_zssj( leftYwcs_lst[0],leftJy,leftZlc,leftSjkmx,leftGghs,leftJd,leftDymb )
        data['rightRows'] = []
    else:
        rightYwcs_lst,rightJy,rightZlc,rightDymb,rightGghs,rightSjkmx,rightJd = get_yw_right_data( db,ywid )
        # 业务参数数据比对
        leftYwcs_lst,rightYwcs_lst = get_sjbj(leftYwcs_lst,rightYwcs_lst)
        # 交易流程数据比对
        leftJy,rightJy = get_sjbj( leftJy,rightJy )   
        # 交易流程数据比对
        leftZlc,rightZlc = get_sjbj( leftZlc,rightZlc )  
        # 打印模版数据比对
        leftDymb,rightDymb = get_sjbj( leftDymb,rightDymb )  
        # 打印模版数据比对
        leftGghs,rightGghs = get_sjbj( leftGghs,rightGghs ) 
        # 数据库模型数据比对
        leftSjkmx,rightSjkmx = get_sjbj( leftSjkmx,rightSjkmx )    
        # 节点数据比对
        leftJd,rightJd = get_jdxx( db,leftJd,rightJd )
        leftJd,rightJd = get_sjbj( leftJd,rightJd ) 
        data['leftRows'] = get_yw_zssj( leftYwcs_lst[0],leftJy,leftZlc,leftSjkmx,leftGghs,leftJd,leftDymb )
        data['rightRows'] = get_yw_zssj( rightYwcs_lst[0],rightJy,rightZlc,rightSjkmx,rightGghs,rightJd,rightDymb)         
    return data 
       
def get_tx_data( db,txid ):
    """
    #获取通讯导入数据
    """  
    data = {'leftRows':'','rightRows':'','state':True}
    leftTxcs,leftTxxx,leftTxjk,leftJdxx = get_tx_left_data( db,txid )
    if txid == '-1':
        data['leftRows'] = get_tx_zssj( leftTxcs,leftTxxx,leftTxjk,leftJdxx )
        data['rightRows'] = []
    else:
        rightTxcs,rightTxxx,rightTxjk,rightJdxx = get_tx_right_data( db,txid )
        # 判断选中通讯是否都在导入文件中存在，不全存在不允许操作
        drtxid_lst = [ tx_dic['id'] for tx_dic in leftTxxx ]
        for txxx_dic in rightTxxx:
            if txxx_dic['id'] not in drtxid_lst:
                data['state'] = False
                data['msg'] = '待导入库数据与预期导入数据不一致，请检查'
                return data
        # 通讯参数数据比对
        leftTxcs,rightTxcs = get_sjbj(leftTxcs,rightTxcs)
        # 通讯信息比对
        leftTxxx,rightTxxx = get_sjbj(leftTxxx,rightTxxx)
        # 通讯接口比对
        leftTxjk,rightTxjk = get_sjbj(leftTxjk,rightTxjk)
        # 节点数据比对
        leftJd,rightJd = get_jdxx( db,leftJdxx,rightJdxx )    
        leftJd,rightJd = get_sjbj( leftJd,rightJd )   
        data['leftRows'] = get_tx_zssj( leftTxcs,leftTxxx,leftTxjk,leftJd )
        data['rightRows'] = get_tx_zssj( rightTxcs,rightTxxx,rightTxjk,rightJd)
    return data 
    
def get_jy_data( db,ywid ):
    """
    #获取交易导入数据
    """
    data = {'leftRows':'','rightRows':'','state':True}
    ywmc = ModSql.kf_ywgl_019.execute_sql_dict(db,"get_ywmc",{'id':ywid})[0]['ywmc']
    # 获取左侧交易流程
    leftJy = ModSql.kf_ywgl_019.execute_sql_dict(db,"get_left_jy",{'ywid':ywid}) 
    leftJycs_lst = []
    jyid_lst = []
    for index,dic in enumerate(leftJy):
        if not dic['cswym']:
            dic['cswym'] = ''
        if dic['id'] not in jyid_lst:
            leftJycs_lst.append(dic)
            jyid_lst.append(dic['id'])
        else:
            leftJycs_lst[jyid_lst.index(dic['id'])]['cswym'] += dic['cswym']
    # 获取左侧子流程
    leftZlc = ModSql.kf_ywgl_019.execute_sql_dict(db,"get_left_zlc",{'ywid':ywid}) 
    # 获取左侧交易节点
    sql_data = {'ywid':ywid,'tname':['gl_jydy_ls'],'fieldname':['b.ssjyid']}
    jyLeftJd = ModSql.kf_ywgl_019.execute_sql_dict(db,"get_left_jd",sql_data) 
    # 获取左侧子流程节点
    sql_data = {'ywid':ywid,'tname':['gl_zlcdy_ls'],'fieldname':['b.sszlcid']}
    zlcLeftJd = ModSql.kf_ywgl_019.execute_sql_dict(db,"get_left_jd",sql_data) 
    sql_data = {'ywid':ywid,'fieldname':['a.dbjdid']}
    jyLeftdbjd = ModSql.kf_ywgl_019.execute_sql_dict(db,"get_left_jyjd",sql_data) 
    sql_data = {'ywid':ywid,'fieldname':['a.jbjdid']}
    jyLeftjbjd = ModSql.kf_ywgl_019.execute_sql_dict(db,"get_left_jyjd",sql_data) 
    # 合并左侧交易节点、子流程节点、交易打解包节点，去重并重新排序
    jyLeftJd.extend(zlcLeftJd)
    jyLeftJd.extend(jyLeftdbjd)
    jyLeftJd.extend(jyLeftjbjd)
    # 记录节点的ID，循环交易节点、子流程节点、交易打解包节点的合并列表，将ID放入该列表，后续判断重复时使用
    cfid_lst = []
    leftJd = []
    for index,dic in enumerate(jyLeftJd):
        if dic['id'] not in cfid_lst:
            cfid_lst.append(dic['id'])
            leftJd.append(dic)
    sorted(leftJd,key=lambda dic:dic['bm'])  
    
    # 获取右侧交易流程 
    rightJy = ModSql.kf_ywgl_019.execute_sql_dict(db,"get_right_jy",{'ywid':ywid})   
    rightJycs_lst = []
    jyid_lst = []
    for index,dic in enumerate(rightJy):
        if not dic['cswym']:
            dic['cswym'] = ''
        if dic['id'] not in jyid_lst:
            rightJycs_lst.append(dic)
            jyid_lst.append(dic['id'])
        else:
            rightJycs_lst[jyid_lst.index(dic['id'])]['cswym'] += dic['cswym']
    # 获取右侧子流程 
    rightZlc = ModSql.kf_ywgl_019.execute_sql_dict(db,"get_right_zlc",{'ywid':ywid}) 
    # 获取左侧交易节点
    sql_data = {'ywid':ywid,'tname':['gl_jydy_ls'],'fieldname':['b.ssjyid']}
    jyRightJd = ModSql.kf_ywgl_019.execute_sql_dict(db,"get_right_jd",sql_data) 
    # 获取左侧子流程节点
    sql_data = {'ywid':ywid,'tname':['gl_zlcdy_ls'],'fieldname':['b.sszlcid']}
    zlcRightJd = ModSql.kf_ywgl_019.execute_sql_dict(db,"get_right_jd",sql_data) 
    # 获取右侧交易打包节点
    sql_data = {'ywid':ywid,'fieldname':['a.dbjdid']}
    jyRightdbjd = ModSql.kf_ywgl_019.execute_sql_dict(db,"get_right_jyjd",sql_data) 
    # 获取右侧交易解包节点
    sql_data = {'ywid':ywid,'fieldname':['a.jbjdid']}
    jyRightjbjd = ModSql.kf_ywgl_019.execute_sql_dict(db,"get_right_jyjd",sql_data) 
    # 合并右侧交易节点、子流程节点、交易打解包节点，去重并重新排序
    jyRightJd.extend(zlcRightJd)
    jyRightJd.extend(jyRightdbjd)
    jyRightJd.extend(jyRightjbjd)
    # 记录节点的ID，循环交易节点、子流程节点、交易打解包节点的合并列表，将ID放入该列表，后续判断重复时使用
    cfid_lst = []
    rightJd = []
    for index,dic in enumerate(jyRightJd):
        if dic['id'] not in cfid_lst:
            cfid_lst.append(dic['id'])
            rightJd.append(dic)
    sorted(rightJd,key=lambda dic:dic['bm'])  
    # 交易流程数据比对
    leftJy,rightJy = get_sjbj( leftJycs_lst,rightJycs_lst )    
    # 交易流程数据比对
    leftZlc,rightZlc = get_sjbj( leftZlc,rightZlc )  
    # 节点数据比对
    leftJd,rightJd = get_jdxx( db,leftJd,rightJd )    
    leftJd,rightJd = get_sjbj( leftJd,rightJd )    
    data['leftRows'] = get_jy_zssj( ywid,ywmc,leftJy,leftZlc,leftJd )
    data['rightRows'] = get_jy_zssj( ywid,ywmc,rightJy,rightZlc,rightJd)     
    return data

def get_tx_left_data( db,txid ):
    """
    # 将导入文件导入至数据库后，获取左侧的数据
    """
    # 获取左侧通讯参数
    sql_data = {}
    if txid != '-1':
        sql_data['txid_lst'] = txid.split(',')
    leftTxcs = ModSql.kf_ywgl_019.execute_sql_dict(db,"get_left_txcs",sql_data)
    leftTxcs_lst = []
    txid_lst = []
    for dic in leftTxcs:
        if not dic['wym']:
            dic['wym'] = ''
        if dic['id'] in txid_lst:
            leftTxcs_lst[txid_lst.index(dic['id'])]['wym'] += dic['wym']
        else:
            leftTxcs_lst.append( {'id':dic['id'],'wym':dic['wym'],'diff':''})
            txid_lst.append(dic['id'])
    # 获取左侧通讯基本信息
    leftTxxx = ModSql.kf_ywgl_019.execute_sql_dict(db,"get_left_txxx",sql_data)
    # 获取左侧通讯接口信息
    leftTxjk = ModSql.kf_ywgl_019.execute_sql_dict(db,"get_left_cdtx",sql_data)
    # 获取左侧打包节点
    data = {'field':['a.dbjdid']}
    data.update( sql_data )
    leftDbjd = ModSql.kf_ywgl_019.execute_sql_dict(db,"get_left_txjd",data)
    # 获取左侧解包节点     
    data = {'field':['a.jbjdid']}
    data.update( sql_data )
    leftJbjd = ModSql.kf_ywgl_019.execute_sql_dict(db,"get_left_txjd",data)
    leftDbjd.extend( leftJbjd)
    return leftTxcs_lst,leftTxxx,leftTxjk,leftDbjd
    
def get_tx_right_data( db,txid ):
    """
    # 将导入文件导入至数据库后，获取右侧的数据
    """
    # 获取右侧通讯参数
    sql_data = {'txid_lst':txid.split(',')} 
    rightTxcs = ModSql.kf_ywgl_019.execute_sql_dict(db,"get_right_txcs",sql_data)
    rightTxcs_lst = []
    txid_lst = []
    for dic in rightTxcs:
        if not dic['wym']:
            dic['wym'] = ''
        if dic['id'] in txid_lst:
            rightTxcs_lst[txid_lst.index(dic['id'])]['wym'] += dic['wym']
        else:
            rightTxcs_lst.append( {'id':dic['id'],'wym':dic['wym'],'diff':''})
            txid_lst.append(dic['id'])
    # 获取右通讯基本信息
    rightTxxx = ModSql.kf_ywgl_019.execute_sql_dict(db,"get_right_txxx",sql_data)
    # 获取右侧通讯接口信息
    rightTxjk = ModSql.kf_ywgl_019.execute_sql_dict(db,"get_right_cdtx",sql_data)
    # 获取右侧打包节点
    data = {'field':['a.dbjdid']}
    data.update( sql_data )
    rightDbjd = ModSql.kf_ywgl_019.execute_sql_dict(db,"get_right_txjd",data)
    # 获取右侧解包节点     
    data = {'field':['a.jbjdid']}
    data.update( sql_data )
    rightJbjd = ModSql.kf_ywgl_019.execute_sql_dict(db,"get_right_txjd",data)
    rightDbjd.extend( rightJbjd)
    return rightTxcs_lst,rightTxxx,rightTxjk,rightDbjd
   
    
def get_yw_left_data( db,ywid ):
    """
    # 将导入文件导入至数据库后，获取左侧的数据
    """    
    # 获取左侧业务参数
    sql_data = {}
    if ywid != '-1':
        sql_data['ywid'] = ywid
    leftYwcs = ModSql.kf_ywgl_019.execute_sql_dict(db,"get_left_ywcs",sql_data) 
    leftYwcs_lst = []
    for index,dic in enumerate(leftYwcs):
        if not dic['wym']:
            dic['wym'] = ''
        if index ==0:
            leftYwcs_lst.append(dic)
        else:
            leftYwcs_lst[0]['wym'] += dic['wym']
    # 获取左侧交易流程
    leftJy = ModSql.kf_ywgl_019.execute_sql_dict(db,"get_left_jy",sql_data) 
    leftJycs_lst = []
    jyid_lst = []
    for index,dic in enumerate(leftJy):
        if not dic['cswym']:
            dic['cswym'] = ''
        if dic['id'] not in jyid_lst:
            leftJycs_lst.append(dic)
            jyid_lst.append(dic['id'])
        else:
            leftJycs_lst[jyid_lst.index(dic['id'])]['cswym'] += dic['cswym']
     # 获取左侧子流程
    leftZlc = ModSql.kf_ywgl_019.execute_sql_dict(db,"get_left_zlc",sql_data) 
    # 获取左侧打印模版
    leftDymb = ModSql.kf_ywgl_019.execute_sql_dict(db,"get_left_dymb",sql_data) 
    # 获取左侧公共函数
    leftGghs = ModSql.kf_ywgl_019.execute_sql_dict(db,"get_left_gghs",sql_data) 
    # 获取左侧数据库模型
    leftSjkmx = ModSql.kf_ywgl_019.execute_sql_dict(db,"get_left_sjkmx",sql_data) 
    # 获取左侧交易节点
    if ywid != '-1':
        sql_data = {'ywid':ywid,'tname':['gl_jydy_ls'],'fieldname':['b.ssjyid']}
    else:
        sql_data = {'tname':['gl_jydy_ls'],'fieldname':['b.ssjyid']}
    jyLeftJd = ModSql.kf_ywgl_019.execute_sql_dict(db,"get_left_jd",sql_data) 
    # 获取左侧子流程节点
    if ywid != '-1':
        sql_data = {'ywid':ywid,'tname':['gl_zlcdy_ls'],'fieldname':['b.sszlcid']}
    else:
        sql_data = {'tname':['gl_zlcdy_ls'],'fieldname':['b.sszlcid']}
    zlcLeftJd = ModSql.kf_ywgl_019.execute_sql_dict(db,"get_left_jd",sql_data) 
    # 获取左侧交易打包节点
    if ywid != '-1':
        sql_data = {'ywid':ywid,'fieldname':['a.dbjdid']}
    else:
        sql_data = {'fieldname':['a.dbjdid']}
    jyLeftdbjd = ModSql.kf_ywgl_019.execute_sql_dict(db,"get_left_jyjd",sql_data) 
    # 获取左侧交易解包节点
    if ywid != '-1':
        sql_data = {'ywid':ywid,'fieldname':['a.jbjdid']}
    else:
        sql_data = {'fieldname':['a.jbjdid']}
    jyLeftjbjd = ModSql.kf_ywgl_019.execute_sql_dict(db,"get_left_jyjd",sql_data) 
    # 合并左侧交易节点、子流程节点，去重并重新排序
    jyLeftJd.extend(zlcLeftJd)
    jyLeftJd.extend(jyLeftdbjd)
    jyLeftJd.extend(jyLeftjbjd)
    # 记录节点的ID，循环交易节点、子流程节点、交易打解包节点的合并列表，将ID放入该列表，后续判断重复时使用
    cfid_lst = []
    jd_rs = []
    for index,dic in enumerate(jyLeftJd):
        if dic['id'] not in cfid_lst:
            cfid_lst.append(dic['id'])
            jd_rs.append(dic)
    sorted(jd_rs,key=lambda dic:dic['bm'])  
    return leftYwcs_lst,leftJycs_lst,leftZlc,leftDymb,leftGghs,leftSjkmx,jd_rs
    
def get_yw_right_data( db,ywid):
    """
    # 将导入文件导入至数据库后，获取右侧的数据
    """    
    # 获取右侧业务参数
    rightYwcs = ModSql.kf_ywgl_019.execute_sql_dict(db,"get_right_ywcs",{'ywid':ywid})      
    rightYwcs_lst = []
    for index,dic in enumerate(rightYwcs):
        if not dic['wym']:
            dic['wym'] = ''
        if index ==0:
            rightYwcs_lst.append(dic)
        else:
            rightYwcs_lst[0]['wym'] += dic['wym']
    # 获取右侧交易流程 
    rightJy = ModSql.kf_ywgl_019.execute_sql_dict(db,"get_right_jy",{'ywid':ywid}) 
    rightJycs_lst = []
    jyid_lst = []
    for index,dic in enumerate(rightJy):
        if not dic['cswym']:
            dic['cswym'] = ''
        if dic['id'] not in jyid_lst:
            rightJycs_lst.append(dic)
            jyid_lst.append(dic['id'])
        else:
            rightJycs_lst[jyid_lst.index(dic['id'])]['cswym'] += dic['cswym']
    # 获取右侧子流程 
    rightZlc = ModSql.kf_ywgl_019.execute_sql_dict(db,"get_right_zlc",{'ywid':ywid})         
    # 获取右侧打印模版
    rightDymb = ModSql.kf_ywgl_019.execute_sql_dict(db,"get_right_dymb",{'ywid':ywid})         
    # 获取右侧公共函数
    rightGghs = ModSql.kf_ywgl_019.execute_sql_dict(db,"get_right_gghs",{'ywid':ywid})         
    # 获取右侧数据库模型
    rightSjkmx = ModSql.kf_ywgl_019.execute_sql_dict(db,"get_right_sjkmx",{'ywid':ywid})         
    # 获取右侧交易节点
    jyRightJd = ModSql.kf_ywgl_019.execute_sql_dict(db,"get_right_jd",{'ywid':ywid,'tname':['gl_jydy'],'fieldname':['b.ssjyid']})  
    # 获取右侧子流程节点
    zlcRightJd = ModSql.kf_ywgl_019.execute_sql_dict(db,"get_right_jd",{'ywid':ywid,'tname':['gl_zlcdy'],'fieldname':['b.sszlcid']})         
    # 获取右侧交易打包节点
    sql_data = {'ywid':ywid,'fieldname':['a.dbjdid']}
    jyRightdbjd = ModSql.kf_ywgl_019.execute_sql_dict(db,"get_right_jyjd",sql_data) 
    # 获取右侧交易解包节点
    sql_data = {'ywid':ywid,'fieldname':['a.jbjdid']}
    jyRightjbjd = ModSql.kf_ywgl_019.execute_sql_dict(db,"get_right_jyjd",sql_data) 
    # 合并右侧交易节点、子流程节点，去重并重新排序
    jyRightJd.extend(zlcRightJd)
    jyRightJd.extend(jyRightdbjd)
    jyRightJd.extend(jyRightjbjd)
    # 记录节点的ID，循环交易节点、子流程节点、交易打解包节点的合并列表，将ID放入该列表，后续判断重复时使用
    cfid_lst = []
    jd_rs = []
    for index,dic in enumerate(jyRightJd):
        if dic['id'] not in cfid_lst:
            cfid_lst.append(dic['id'])
            jd_rs.append(dic)
    sorted(jd_rs,key=lambda dic:dic['bm'])  
    return rightYwcs_lst,rightJycs_lst,rightZlc,rightDymb,rightGghs,rightSjkmx,jd_rs
    
def get_yw_zssj( ywcs_dic,jy_lst,zlc_lst,sjkmx_lst,gghs_lst,jd_lst,dymb_lst ):
    """
    # 根据传入的数据，将数据组织成树形展示需要的结构
    """
    jy_diff = get_parent_css(jy_lst)
    zlc_diff = get_parent_css(zlc_lst)
    dymb_diff = get_parent_css(dymb_lst)
    gghs_diff = get_parent_css(gghs_lst)
    sjkmx_diff = get_parent_css(sjkmx_lst)
    jd_diff = get_parent_css(jd_lst)
    # 业务样式
    yw_diff = ''
    if '1' in (jy_diff,zlc_diff,gghs_diff,sjkmx_diff,dymb_diff,ywcs_dic['diff']):
        yw_diff = '1'
    elif '2' in(jy_diff,zlc_diff,gghs_diff,sjkmx_diff,dymb_diff,ywcs_dic['diff']):
        yw_diff = '2'
    dic1 =  { 'id':'业务参数','name':'业务参数','xgr':'','xgsj':'','diff':ywcs_dic['diff'],'lx':'ywcs' }
    dic2 = { 'id':'交易流程','name':'交易流程','children':jy_lst,'diff':jy_diff,'lx':'JY' }
    dic3 = { 'id':'子流程','name':'子流程','children':zlc_lst,'diff':zlc_diff ,'lx':'ZLC'}
    dic4 = { 'id':'打印模版','name':'打印模版','children':dymb_lst,'diff':dymb_diff,'lx':'DYMB' }
    dic5 = { 'id':'公共函数','name':'公共函数','children':gghs_lst,'diff':gghs_diff,'lx':'GGHS' }
    dic6 = { 'id':'数据库模型','name':'数据库模型','children':sjkmx_lst,'diff':sjkmx_diff,'lx':'SJKMX' }
    return [ {'id':ywcs_dic['id'],'name':ywcs_dic['name'],'diff':yw_diff,'children':[dic1,dic2,dic3,dic4,dic5,dic6] },{'id':'节点','name':'节点','xgr':'','diff':jd_diff,'children':jd_lst,'lx':'JD' } ]

def get_jy_zssj( ywid,ywmc,jy_lst,zlc_lst,jd_lst ):
    """
    # 根据传入的数据，将数据组织成树形展示需要的结构
    """
    jy_diff = get_parent_css(jy_lst)
    zlc_diff = get_parent_css(zlc_lst)
    jd_diff = get_parent_css(jd_lst)
    # 业务样式
    yw_diff = ''
    if '1' in (jy_diff,zlc_diff):
        yw_diff = '1'
    elif '2' in(jy_diff,zlc_diff):
        yw_diff = '2'
    dic1 = { 'id':'交易流程','name':'交易流程','children':jy_lst,'diff':jy_diff,'lx':'JY' }
    dic2 = { 'id':'子流程','name':'子流程','children':zlc_lst,'diff':zlc_diff,'lx':'ZLC' }
    return [ {'id':ywid,'name':ywmc,'children':[dic1,dic2],'diff':yw_diff },{'id':'节点','name':'节点','xgr':'','children':jd_lst,'diff':jd_diff,'lx':'JD' } ]

def get_tx_zssj( txcs_lst,txxx_lst,txjk_lst,jd_lst ):
    """
    # 根据传入的数据，将数据组织成树形展示需要的结构
    """
    jd_diff = get_parent_css(jd_lst)
    result = []
    for dic in txxx_lst:
        # 获取该通讯的通讯参数diff属性
        txcs_diff = ''
        for txcsxx in txcs_lst:
            if txcsxx['id'] == dic['id']:
                txcs_diff = txcsxx['diff']
        # 通讯参数节点在页面中是必须展示的，不存在新增，新增的只是参数记录，所有对于通讯参数节点的展示信息为修改          
        if txcs_diff:
            txcs_diff = '1'
        # 获取该通讯下的通讯接口
        tx_jk_lst = []
        for txjkxx in txjk_lst:
            if txjkxx['txglid']==dic['id']:
                tx_jk_lst.append( txjkxx )
        tx_jk_diff = get_parent_css(tx_jk_lst) 
        tx_diff = ''   
        if '1' in (txcs_diff,dic['diff'],tx_diff):
            tx_diff = '1'
        elif '2' in(txcs_diff,dic['diff'],tx_diff):
            tx_diff = '2'
        children = [{'id':'%s-通讯参数'%(dic['id']),'name':'通讯参数','diff':txcs_diff,'lx':'txcs'},{'id':'%s-通讯基本信息'%(dic['id']),'name':'通讯基本信息','diff':dic['diff'],'lx':'txgl'}] 
        for txjk in tx_jk_lst:
            children.append(txjk)
        result.append( {'id':dic['id'],'name': '' if dic['diff'] == '2' else dic['name'],'diff':tx_jk_diff,'children':children} )
    result.append({'id':'节点','name':'节点','xgr':'','diff':jd_diff,'children':jd_lst,'lx':'JD' })
    return result
    
def bbdb_data_service(id,lx,ywid,drlx,txid,jdlx):
    """
    # 获取对比数据
    """
    with sjapi.connection() as db:
        if drlx == 'yw' and lx == 'ywcs':
            # 获取左侧业务数据
            leftYwxx = ModSql.kf_ywgl_019.execute_sql_dict(db,"get_bd_left_ywxx",{'ywid':ywid})
            # 获取右侧业务数据
            rightYwxx = ModSql.kf_ywgl_019.execute_sql_dict(db,"get_bd_right_ywxx",{'ywid':ywid})
            lYwxx,rYwxx = get_xxbd(leftYwxx,rightYwxx)
            mc_dic = {'ywbm':'业务编码', 'ywmc':'业务名称', 'ywms':'业务描述'}
            sort_lst = ['ywbm','ywmc','ywms']
            pop_zd = ['id','diff']
            leftYwxx = get_sjzz( lYwxx[0],mc_dic,pop_zd,sort_lst)
            rightYwxx = get_sjzz( rYwxx[0],mc_dic,pop_zd,sort_lst)
            sorted(leftYwxx,key=lambda dic:dic['sxmc'])
            sorted(rightYwxx,key=lambda dic:dic['sxmc'])
            leftYwxxRs = {'leftYwxx':leftYwxx,'diff':lYwxx[0]['diff'],'ywmc':lYwxx[0]['ywmc']}
            rightYwxxRs = {'rightYwxx':rightYwxx,'diff':rYwxx[0]['diff'],'ywmc':rYwxx[0]['ywmc']}
            # 获取左侧业务参数
            leftYwcs = ModSql.kf_ywgl_019.execute_sql_dict(db,"get_bd_left_cs",{'id':ywid})
            # 获取右侧业务参数
            rightYwcs = ModSql.kf_ywgl_019.execute_sql_dict(db,"get_bd_right_cs",{'id':ywid})
            leftYwcs,rightYwcs = get_xxbd(leftYwcs,rightYwcs)
            return {'url':'kf_ywgl/kf_ywgl_019/kf_ywgl_019_bbdb_ywcs.html','leftYwxxRs':leftYwxxRs,'rightYwxxRs':rightYwxxRs,'leftYwcs':leftYwcs,'rightYwcs':rightYwcs,'jdlx':jdlx}
        if  lx =='jy':
            # 获取左侧交易信息
            leftJyxx = ModSql.kf_ywgl_019.execute_sql_dict(db,"get_bd_left_jyxx",{'id':id})    
            # 获取右侧交易信息
            rightJyxx = ModSql.kf_ywgl_019.execute_sql_dict(db,"get_bd_right_jyxx",{'id':id})   
            if leftJyxx:
                # 获取左侧交易XML
                leftXml = xml_out(db,'lc',id,lsb = True)
            else:
                leftXml = ''
            if rightJyxx:
                # 获取右侧交易XML
                rightXml = xml_out(db,'lc',id,lsb = False)
            else:
                rightXml = ''
            lJyxx,rJyxx = get_xxbd(leftJyxx,rightJyxx)
            mc_dic = {'jym':'交易码', 'jymc':'交易名称', 'jyms':'交易描述','timeout':'交易超时时间','zt':'交易状态','zdfqpz':'自动发起配置','zdfqpzsm':'自动发起配置说明','dbjdmc':'打包节点名称','jbjdmc':'解包节点名称'}
            sort_lst = ['jym', 'jymc', 'jyms', 'zt', 'zdfqpz', 'zdfqpzsm','timeout','dbjdmc','jbjdmc']
            pop_zd = ['id','diff']
            leftJyxx = get_sjzz( lJyxx[0],mc_dic,pop_zd,sort_lst)
            rightJyxx = get_sjzz( rJyxx[0],mc_dic,pop_zd,sort_lst)
            # 获取左侧交易参数
            leftJycs = ModSql.kf_ywgl_019.execute_sql_dict(db,"get_bd_left_cs",{'id':id})
            # 获取右侧交易参数
            rightJycs = ModSql.kf_ywgl_019.execute_sql_dict(db,"get_bd_right_cs",{'id':id})
            leftJycs,rightJycs = get_xxbd(leftJycs,rightJycs)
            sorted(leftJyxx,key=lambda dic:dic['sxmc'])
            sorted(rightJyxx,key=lambda dic:dic['sxmc'])
            leftRs = {'leftJyxx':leftJyxx,'diff':lJyxx[0]['diff'],'leftJycs':leftJycs}
            rightRs = {'rightJyxx':rightJyxx,'diff':rJyxx[0]['diff'],'rightJycs':rightJycs}
            return {'url':'kf_ywgl/kf_ywgl_019/kf_ywgl_019_bbdb_jy.html','leftRs':leftRs,'rightRs':rightRs,'leftXml':json.dumps(leftXml),'rightXml':json.dumps(rightXml),'jdlx':jdlx}
        if lx == 'zlc':
            # 获取左侧子流程信息
            leftZlcxx = ModSql.kf_ywgl_019.execute_sql_dict(db,"get_bd_left_zlcxx",{'id':id})    
            # 获取右侧子流程信息
            rightZlcxx = ModSql.kf_ywgl_019.execute_sql_dict(db,"get_bd_right_zlcxx",{'id':id})    
            if leftZlcxx:
                # 获取左侧子流程XML
                leftXml = xml_out(db,'zlc',id,lsb = True)
            else:
                leftXml = ''
            if rightZlcxx:
                # 获取右侧子流程XML
                rightXml = xml_out(db,'zlc',id,lsb = False)
            else:
                rightXml = ''
            lZlcxx,rZlcxx = get_xxbd(leftZlcxx,rightZlcxx)
            mc_dic = {'bm':'子流程编码', 'mc':'子流程名称', 'ms':'子流程描述'}
            sort_lst = ['bm','mc','ms']
            pop_zd = ['id','diff']
            leftZlcxx = get_sjzz( lZlcxx[0],mc_dic,pop_zd,sort_lst)
            rightZlcxx = get_sjzz( rZlcxx[0],mc_dic,pop_zd,sort_lst)
            leftZlcxx = sorted(leftZlcxx, key = lambda x:x['id'])
            rightZlcxx = sorted(rightZlcxx, key = lambda x:x['id'])
            leftRs = {'leftZlcxx':leftZlcxx,'diff':lZlcxx[0]['diff']}
            rightRs = {'rightZlcxx':rightZlcxx,'diff':rZlcxx[0]['diff']}
            return {'url':'kf_ywgl/kf_ywgl_019/kf_ywgl_019_bbdb_zlc.html','leftRs':leftRs,'rightRs':rightRs,'leftXml':json.dumps(leftXml),'rightXml':json.dumps(rightXml),'jdlx':jdlx}
        if drlx == 'yw' and lx == 'dymb':
            # 获取左侧打印模版信息
            leftDymb = ModSql.kf_ywgl_019.execute_sql_dict(db,"get_bd_left_dymb",{'id':id})    
            # 获取右侧打印模版信息
            rightDymb = ModSql.kf_ywgl_019.execute_sql_dict(db,"get_bd_right_dymb",{'id':id})   
            if leftDymb:
                # 获取左侧打印模版内容
                leftNr = pickle.loads( ModSql.kf_ywgl_019.execute_sql_dict(db,"get_bd_left_dymbnr",{'id':id})[0]['nr'].read() )  
            else:
                 leftNr = ''
            if rightDymb:
                # 获取右侧打印模版内容L
                rightNr = pickle.loads( ModSql.kf_ywgl_019.execute_sql_dict(db,"get_bd_right_dymbnr",{'id':id})[0]['nr'].read() )   
            else:
                rightNr = ''
            lDymb,rDymb = get_xxbd(leftDymb,rightDymb)
            mc_dic = {'mblx':'模版类型', 'mbmc':'模版名称', 'mbms':'模版描述'}
            sort_lst = ['mblx','mbmc','mbms']
            pop_zd = ['id','diff']
            leftDymb = get_sjzz( lDymb[0],mc_dic,pop_zd,sort_lst)
            rightDymb = get_sjzz( rDymb[0],mc_dic,pop_zd,sort_lst)
            sorted(leftDymb,key=lambda dic:dic['sxmc'])
            sorted(rightDymb,key=lambda dic:dic['sxmc'])
            leftRs = {'leftDymb':leftDymb,'diff':lDymb[0]['diff']}
            rightRs = {'rightDymb':rightDymb,'diff':rDymb[0]['diff']}
            return {'url':'kf_ywgl/kf_ywgl_019/kf_ywgl_019_bbdb_dymb.html','leftRs':leftRs,'rightRs':rightRs,'leftNr':json.dumps(leftNr),'rightNr':json.dumps(rightNr),'jdlx':jdlx}
        if drlx == 'yw' and lx == 'gghs':
            # 获取左侧公共函数信息
            leftGghs = ModSql.kf_ywgl_019.execute_sql_dict(db,"get_bd_left_gghs",{'id':id})    
            # 获取右侧公共函数信息
            rightGghs = ModSql.kf_ywgl_019.execute_sql_dict(db,"get_bd_right_gghs",{'id':id})  
            if leftGghs:
                # 获取左侧函数内容
                leftNr = pickle.loads( ModSql.kf_ywgl_019.execute_sql_dict(db,"get_bd_left_gghsnr",{'id':id})[0]['nr'].read() )  
            else:
                 leftNr = ''
            if rightGghs:
                # 获取右侧函数内容L
                rightNr = pickle.loads( ModSql.kf_ywgl_019.execute_sql_dict(db,"get_bd_right_gghsnr",{'id':id})[0]['nr'].read() )   
            else:
                rightNr = ''
            lGghs,rGghs = get_xxbd(leftGghs,rightGghs)
            mc_dic = {'mc':'函数名称', 'hsms':'函数描述'}
            sort_lst = ['mc','hsms']
            pop_zd = ['id','diff']
            leftGghs = get_sjzz( lGghs[0],mc_dic,pop_zd,sort_lst)
            rightGghs = get_sjzz( rGghs[0],mc_dic,pop_zd,sort_lst)
            sorted(leftGghs,key=lambda dic:dic['sxmc'])
            sorted(rightGghs,key=lambda dic:dic['sxmc'])
            leftRs = {'leftGghs':leftGghs,'diff':lGghs[0]['diff']}
            rightRs = {'rightGghs':rightGghs,'diff':rGghs[0]['diff']}
            return {'url':'kf_ywgl/kf_ywgl_019/kf_ywgl_019_bbdb_gghs.html','leftRs':leftRs,'rightRs':rightRs,'leftNr':json.dumps(leftNr),'rightNr':json.dumps(rightNr),'jdlx':jdlx}
        if drlx == 'yw' and lx == 'sjk':
            # 获取左侧数据库基本信息
            leftSjbxx = ModSql.kf_ywgl_019.execute_sql_dict(db,"get_bd_left_sjbxx",{'id':id})
            # 获取右侧数据库基本信息
            rightSjbxx = ModSql.kf_ywgl_019.execute_sql_dict(db,"get_bd_right_sjbxx",{'id':id})
            lSjbxx,rSjbxx = get_xxbd(leftSjbxx,rightSjbxx)
            mc_dic = {'sjbmc':'数据表名称', 'sjbmcms':'数据表名称描述'}
            sort_lst = ['sjbmc','sjbmcms']
            pop_zd = ['id','diff']
            leftSjbxx = get_sjzz( lSjbxx[0],mc_dic,pop_zd,sort_lst)
            rightSjbxx = get_sjzz( rSjbxx[0],mc_dic,pop_zd,sort_lst)
            # 获取左侧数据表字段
            leftSjbzd = ModSql.kf_ywgl_019.execute_sql_dict(db,"get_bd_left_sjbzd",{'id':id})
            # 获取右侧数据表字段
            rightSjbzd = ModSql.kf_ywgl_019.execute_sql_dict(db,"get_bd_right_sjbzd",{'id':id})
            leftSjbzd,rightSjbzd = get_xxbd(leftSjbzd,rightSjbzd)
            # 获取左侧数据表索引
            leftSjbsy = ModSql.kf_ywgl_019.execute_sql_dict(db,"get_bd_left_sjbsy",{'id':id})
            # 获取右侧数据表索引
            rightSjbsy = ModSql.kf_ywgl_019.execute_sql_dict(db,"get_bd_right_sjbsy",{'id':id})
            leftSjbsy,rightSjbsy = get_xxbd(leftSjbsy,rightSjbsy)
            # 获取左侧数据表约束
            leftSjbys = ModSql.kf_ywgl_019.execute_sql_dict(db,"get_bd_left_sjbys",{'id':id})
            # 获取右侧数据表约束
            rightSjbys = ModSql.kf_ywgl_019.execute_sql_dict(db,"get_bd_right_sjbys",{'id':id})
            leftSjbys,rightSjbys = get_xxbd(leftSjbys,rightSjbys)
            sorted(leftSjbxx,key=lambda dic:dic['sxmc'])
            sorted(rightSjbxx,key=lambda dic:dic['sxmc'])
            leftRs = {'leftSjbxx':leftSjbxx,'diff':lSjbxx[0]['diff'],'leftSjbzd':leftSjbzd,'leftSjbsy':leftSjbsy,'leftSjbys':leftSjbys}
            rightRs = {'rightSjbxx':rightSjbxx,'diff':rSjbxx[0]['diff'],'rightSjbzd':rightSjbzd,'rightSjbsy':rightSjbsy,'rightSjbys':rightSjbys}
            return {'url':'kf_ywgl/kf_ywgl_019/kf_ywgl_019_bbdb_sjkmx.html','leftRs':leftRs,'rightRs':rightRs,'SYLX_DIC':SYLX_DIC,'jdlx':jdlx}
        if lx == 'jd':
            # 获取左侧节点基本信息
            leftJdxx = ModSql.kf_ywgl_019.execute_sql_dict(db,"get_bd_left_jd",{'id':id})
            for jdxx in leftJdxx:
                jdxx['jdlx'] = JDLX_MC_DIC.get(jdxx['jdlx'], jdxx['jdlx'])
            # 获取右侧节点基本信息
            rightJdxx = ModSql.kf_ywgl_019.execute_sql_dict(db,"get_bd_right_jd",{'id':id})
            for jdxx in rightJdxx:
                jdxx['jdlx'] = JDLX_MC_DIC.get(jdxx['jdlx'], jdxx['jdlx'])
            lJdxx,rJdxx = get_xxbd(leftJdxx,rightJdxx)
            mc_dic = {'jdlx':'节点类型', 'bm':'节点编码','jdmc':'节点名称','jdms':'节点描述'}
            sort_lst = ['bm','jdmc','jdlx','jdms']
            pop_zd = ['id','diff']
            leftJdxx = get_sjzz( lJdxx[0],mc_dic,pop_zd,sort_lst)
            rightJdxx = get_sjzz( rJdxx[0],mc_dic,pop_zd,sort_lst)
            # 获取左侧输入要素
            leftSyys = ModSql.kf_ywgl_019.execute_sql_dict(db,"get_bd_left_jdys",{'id':id,'lb':'1'})
            for ysxx in leftSyys:
                ysxx['gslb'] = JDYS_LB_DIC.get(ysxx['gslb'], ysxx['gslb'])
                ysxx['ly'] = JDYS_LY_DIC.get(ysxx['ly'], ysxx['ly'])
            # 获取右侧输入要素
            rightSyys = ModSql.kf_ywgl_019.execute_sql_dict(db,"get_bd_right_jdys",{'id':id,'lb':'1'})
            for ysxx in rightSyys:
                ysxx['gslb'] = JDYS_LB_DIC.get(ysxx['gslb'], ysxx['gslb'])
                ysxx['ly'] = JDYS_LY_DIC.get(ysxx['ly'], ysxx['ly'])
            leftSyys,rightSyys = get_xxbd(leftSyys,rightSyys)
            # 获取左侧输出要素
            leftScys = ModSql.kf_ywgl_019.execute_sql_dict(db,"get_bd_left_jdys",{'id':id,'lb':'2'})
            for ysxx in leftScys:
                ysxx['gslb'] = JDYS_LB_DIC.get(ysxx['gslb'], ysxx['gslb'])
                ysxx['ly'] = JDYS_LY_DIC.get(ysxx['ly'], ysxx['ly'])
            # 获取右侧输出要素
            rightScys = ModSql.kf_ywgl_019.execute_sql_dict(db,"get_bd_right_jdys",{'id':id,'lb':'2'})
            for ysxx in rightScys:
                ysxx['gslb'] = JDYS_LB_DIC.get(ysxx['gslb'], ysxx['gslb'])
                ysxx['ly'] = JDYS_LY_DIC.get(ysxx['ly'], ysxx['ly'])
            leftScys,rightScys = get_xxbd(leftScys,rightScys)
            # 获取左侧返回值
            leftFhz = ModSql.kf_ywgl_019.execute_sql_dict(db,"get_bd_left_jdfhz",{'id':id})
            # 获取右侧返回值
            rightFhz = ModSql.kf_ywgl_019.execute_sql_dict(db,"get_bd_right_jdfhz",{'id':id})
            leftFhz,rightFhz = get_xxbd(leftFhz,rightFhz)
            # 获取左侧逻辑代码
            rs =  ModSql.kf_ywgl_019.execute_sql_dict(db,"get_bd_left_jdljdm",{'id':id})
            leftLjdm = pickle.loads( rs[0]['nr'].read() ) if rs else ''
            # 获取右侧逻辑代码
            rs = ModSql.kf_ywgl_019.execute_sql_dict(db,"get_bd_right_jdljdm",{'id':id})
            rightLjdm = pickle.loads( rs[0]['nr'].read() ) if rs else ''
            sorted(leftJdxx,key=lambda dic:dic['sxmc'])
            sorted(rightJdxx,key=lambda dic:dic['sxmc'])
            leftRs = {'leftJdxx':leftJdxx,'diff':lJdxx[0]['diff'],'leftSyys':leftSyys,'leftScys':leftScys,'leftFhz':leftFhz}
            rightRs = {'rightJdxx':rightJdxx,'diff':rJdxx[0]['diff'],'rightSyys':rightSyys,'rightScys':rightScys,'rightFhz':rightFhz}
            return {'url':'kf_ywgl/kf_ywgl_019/kf_ywgl_019_bbdb_jd.html','leftRs':leftRs,'rightRs':rightRs,'leftLjdm':json.dumps(leftLjdm),'rightLjdm':json.dumps(rightLjdm),'jdlx':jdlx}
        if  drlx == 'tx' and lx =='txcs':
            # 获取通讯名称
            txmc = ModSql.kf_ywgl_019.execute_sql_dict(db,'get_right_txxx',{'txid_lst':[txid]})[0]['name']
            # 获取左侧通讯参数
            leftTxcs = ModSql.kf_ywgl_019.execute_sql_dict(db,"get_bd_left_cs",{'id':txid})
            # 获取右侧通讯参数
            rightTxcs = ModSql.kf_ywgl_019.execute_sql_dict(db,"get_bd_right_cs",{'id':txid})
            leftTxcs,rightTxcs = get_xxbd(leftTxcs,rightTxcs)
            leftRs = {'leftTxcs':leftTxcs,'txmc':txmc}
            rightRs = {'rightTxcs':rightTxcs,'txmc':txmc,'jdlx':jdlx}
            return {'url':'kf_ywgl/kf_ywgl_019/kf_ywgl_019_bbdb_txcs.html','leftRs':leftRs,'rightRs':rightRs}
        if  drlx == 'tx' and lx =='txgl':
            # 获取左侧通讯基本信息
            leftTxxx = ModSql.kf_ywgl_019.execute_sql_dict(db,"get_bd_left_txxx",{'id':txid})
            for dic in leftTxxx:
                dic['fwfx'] = '客户端' if dic['fwfx'] == '1' else '服务端'
                if dic['nr']:
                    dic['nr'] = pickle.loads( dic['nr'].read() )
                else:
                    dic['nr'] = ''
            # 获取右侧通讯基本信息
            rightTxxx = ModSql.kf_ywgl_019.execute_sql_dict(db,"get_bd_right_txxx",{'id':txid})
            for dic in rightTxxx:
                dic['fwfx'] = '客户端' if dic['fwfx'] == '1' else '服务端'
                if dic['nr']:
                    dic['nr'] = pickle.loads( dic['nr'].read() )
                else:
                    dic['nr'] = ''
            lTxxx,rTxxx = get_xxbd(leftTxxx,rightTxxx)
            mc_dic = {'bm':'通讯编码', 'mc':'通讯名称','txlx':'通讯类型','fwfx':'服务方向','txwjmc':'通讯文件名称','cssj':'超时时间','jcbfs':'进程并发数'}
            sort_lst = ['bm', 'mc','txlx','fwfx','txwjmc','cssj','jcbfs']
            pop_zd = ['id','diff','nr']
            leftTxxx = get_sjzz( lTxxx[0],mc_dic,pop_zd,sort_lst)
            rightTxxx = get_sjzz( rTxxx[0],mc_dic,pop_zd,sort_lst)
            sorted(leftTxxx,key=lambda dic:dic['sxmc'])
            sorted(rightTxxx,key=lambda dic:dic['sxmc'])
            leftRs = {'leftTxxx':leftTxxx,'diff':lTxxx[0]['diff']}
            rightRs = {'rightTxxx':rightTxxx,'diff':rTxxx[0]['diff']}
            return {'url':'kf_ywgl/kf_ywgl_019/kf_ywgl_019_bbdb_txgl.html','leftRs':leftRs,'rightRs':rightRs,'leftNr':json.dumps(lTxxx[0]['nr']),'rightNr':json.dumps(rTxxx[0]['nr']),'jdlx':jdlx}
        if lx == 'cdtx':
            # 获取左侧C端通讯信息
            leftCdtx = ModSql.kf_ywgl_019.execute_sql_dict(db,"get_bd_left_cdtx",{'id':id})    
            # 获取右侧C端通讯信息
            rightCdtx = ModSql.kf_ywgl_019.execute_sql_dict(db,"get_bd_right_cdtx",{'id':id})  
            if leftCdtx:
                zlcid = leftCdtx[0]['zlcid']
            elif rightCdtx:
                zlcid = rightCdtx[0]['zlcid']
            lCdtx,rCdtx = get_xxbd(leftCdtx,rightCdtx)
            mc_dic = {'bm':'编码', 'zlcmc':'子流程名称', 'dfjym':'对方交易码','dfjymc':'对方交易名称','dbjdmc':'打包节点名称','jbjdmc':'解包节点名称','cssj':'超时时间'}
            pop_zd = ['id','diff','zlcid']
            sort_lst = ['bm', 'zlcmc', 'dfjym','dfjymc','dbjdmc','jbjdmc','cssj']
            leftCdtx = get_sjzz( lCdtx[0],mc_dic,pop_zd,sort_lst)
            rightCdtx = get_sjzz( rCdtx[0],mc_dic,pop_zd,sort_lst)
            sorted(leftCdtx,key=lambda dic:dic['sxmc'])
            sorted(rightCdtx,key=lambda dic:dic['sxmc'])
            # 获取左侧子流程信息
            leftZlcxx = ModSql.kf_ywgl_019.execute_sql_dict(db,"get_bd_left_zlcxx",{'id':zlcid})    
            # 获取右侧子流程信息
            rightZlcxx = ModSql.kf_ywgl_019.execute_sql_dict(db,"get_bd_right_zlcxx",{'id':zlcid})    
            lZlcxx,rZlcxx = get_xxbd(leftZlcxx,rightZlcxx)
            mc_dic = {'bm':'编码', 'mc':'名称', 'ms':'描述'}
            sort_lst = ['bm','mc','ms']
            pop_zd = ['id','diff']
            leftZlcxx = get_sjzz( lZlcxx[0],mc_dic,pop_zd,sort_lst)
            rightZlcxx = get_sjzz( rZlcxx[0],mc_dic,pop_zd,sort_lst)
            sorted(leftZlcxx,key=lambda dic:dic['sxmc'])
            sorted(rightZlcxx,key=lambda dic:dic['sxmc'])
            leftRs = {'leftCdtx':leftCdtx,'cdtx_diff':lCdtx[0]['diff'],'leftZlcxx':leftZlcxx,'zlc_diff':lZlcxx[0]['diff']}
            rightRs = {'rightCdtx':rightCdtx,'cdtx_diff':rCdtx[0]['diff'],'rightZlcxx':rightZlcxx,'zlc_diff':rZlcxx[0]['diff']}
            return {'url':'kf_ywgl/kf_ywgl_019/kf_ywgl_019_bbdb_cdtx.html','leftRs':leftRs,'rightRs':rightRs,'jdlx':jdlx}
            
            
def get_xxbd( leftLst,rightLst ):
    """
    #左右两侧数据比较
    """
    for index,dic in enumerate(leftLst):
        # 若左侧的再右侧中不存在，说明为新增，左侧的diff属性值设为2
        right_id_lst = [ lst['id'] for lst in rightLst]
        if dic['id'] not in right_id_lst:
            leftLst[index]['diff'] = ",".join( dic.keys() )
            tmp_dic = {}.fromkeys(dic.keys(),'')
            tmp_dic['diff'] = ",".join( dic.keys() )
            tmp_dic['id'] = dic['id']
            rightLst.insert(index,tmp_dic)
        else:
            # 若左侧的数据在右侧有，需先判断该数据在左右两侧的位置是否一致
            rightIndex = right_id_lst.index(dic['id'])
            if index != rightIndex:
                # 若位置不一至，需将右侧中该数据的位置，移到与左侧一致
                rightDic = rightLst[rightIndex]
                rightLst.remove(rightDic)
                rightLst.insert(index,rightDic)
            rightDic = rightLst[index]
            diff_lst = []
            for key,value in dic.items():
                rightValue = rightDic[key]
                if value != rightValue:
                    diff_lst.append( key )
            leftLst[index]['diff'] = ",".join( diff_lst )
            rightLst[index]['diff'] = ",".join( diff_lst )
    for index,dic in enumerate(rightLst):
        # 若右侧的在左侧不存在，说明为删除，右侧的diff属性值为2
        left_id_lst = [ lst['id'] for lst in leftLst]
        if dic['id'] not in left_id_lst:
            rightLst[index]['diff'] = ",".join( dic.keys() )
            tmp_dic = {}.fromkeys(dic.keys(),'')
            tmp_dic['diff'] = ",".join( dic.keys() )
            tmp_dic['id'] = dic['id']
            leftLst.insert(index,tmp_dic)
    return leftLst,rightLst
    
def get_sjzz( data,mc_dic,pop_zd,sort_lst):
    """
    # 页面数据组织
    # @param data:数据源
    # @param mc_dic:页面展示的名称对应字典
    # @param pop_zd:数据源中不需要在页面中展示的字段
    # @sort_dic:页面名称展示顺序
    """
    rs = []
    #for k,v in data.items():
    #    if k not in pop_zd:
    #        rs.append( {'id':k, 'sxnr':v, 'sxmc':mc_dic.get(k)} )
        # 由于之前的版本提交没有加自动发起配置说明，所以为了解决线上不出错，只能是手动添加。
    data['zdfqpzsm'] = set_zdfqpzsm(data)
    for k in sort_lst:
        if k not in pop_zd:
            rs.append( {'id':k, 'sxnr':data.get(k), 'sxmc':mc_dic.get(k)} )
    return rs
    
def dr_submit_service( ywid,drlx,txid,drxx,drms,bzxx,fhr,fhrmm,xtlx,drlsid ):
    """
    # 导入
    """
    data = {'state':False,'msg':''}
    nr = ''
    # 记录导入时，所有的执行SQL
    sql_lst = []
    # 获取所有的交易ID
    jyid_lst = []
    # 记录数据库模型的变更SQL
    file_lst = []
    # 新增的数据表信息
    add_table_dic = {}
    # 数据库导入txt
    fname = ''
    # 修改的数据库模型ID
    upd_id_lst = []
    for str in drxx:
        if str.split('|')[1] == 'jy':
            jyid_lst.append( str.split('|')[0]  )
    # 导入前交易状态
    jy_zt_dic = {}
    try:
        with sjapi.connection() as db:
            # (1)首先校验复核人是否正确
            sq_gnmc = '导入'
            if drlx == 'yw':
                sq_gnmc += '业务_' + sq_gnmc
                nr = '%s：业务ID：%s，导入类型：%s，导入描述：%s，备注信息：%s，系统类型：%s，导入流水ID：%s' % ( sq_gnmc,ywid,drlx,drms,bzxx,xtlx,drlsid )
            if drlx == 'jy':
                sq_gnmc += '交易_' + sq_gnmc
                nr = '%s：交易ID列表：%s，导入类型：%s，导入描述：%s，备注信息：%s，系统类型：%s，导入流水ID：%s' % ( sq_gnmc,jyid_lst,drlx,drms,bzxx,xtlx,drlsid )
            if drlx == 'tx':
                sq_gnmc += '通讯_' + sq_gnmc
                nr = '%s：通讯ID：%s，导入类型：%s，导入描述：%s，备注信息：%s，系统类型：%s，导入流水ID：%s' % ( sq_gnmc,txid,drlx,drms,bzxx,xtlx,drlsid )
            hyxx_dic = { 'hydm': fhr, 'mm':fhrmm, 'jsdm': FHR_JSDM,'sq_gnmc': sq_gnmc, 'czpt': 'kf','sqgndm':'','szcz': sq_gnmc + '复核人授权' }
            ret,msg = check_fhr( db, hyxx_dic )
            if ret == False:
                msg = msg
                return {'state':False,'msg':msg}
            # (2)校验是否有交易导入，若有，需要先校验交易对应的子流程是否存在
            for str in drxx:
                lst = str.split('|')
                if lst[1] == 'jy':
                    rs = ModSql.kf_ywgl_019.execute_sql_dict(db,'get_extend_zlcjy',{'id':lst[0]})
                    if rs:
                        # 获取交易引用的子流程的ID
                        zlcid_lst = [dic['jddyid'] for dic in rs]
                        # 从正式表中获取交易引用的子流程
                        zlc_result1 = ModSql.kf_ywgl_019.execute_sql_dict(db,'check_zlc_exist',{'tname':['gl_zlcdy'],'zlcid_lst':zlcid_lst}) 
                        # 从临时表中获取交易引用的子流程
                        zlc_result2 = ModSql.kf_ywgl_019.execute_sql_dict(db,'check_zlc_exist',{'tname':['gl_zlcdy_ls'],'zlcid_lst':zlcid_lst}) 
                        zlc_result1.extend(zlc_result2)
                        zlcid = [ dic['id'] for dic in zlc_result1]
                        zlcid = list(set(zlcid))
                        if len(zlcid) != len(zlcid_lst):
                            msg = "交易与其调用的子流程不能一一对应,需要子流程列表[%s],本地子流程和导入子流程检索到的子流程列表[%s]，请检查" % ( ','.join ( sorted(zlcid_lst) ), ','.join ( sorted(zlcid) ) )
                            return {'state':False,'msg':msg}
                    
                    # 判断冲正配置的子流程是否存在
                    rs = ModSql.kf_ywgl_019.execute_sql_dict(db,'get_extend_czpz',{'id':lst[0]})
                    if rs:
                        # 获取交易引用的子流程的ID
                        zlcid_lst = [dic['czpzid'] for dic in rs]
                        # 从正式表中获取交易引用的子流程
                        zlc_result1 = ModSql.kf_ywgl_019.execute_sql_dict(db,'check_zlc_exist',{'tname':['gl_zlcdy'],'zlcid_lst':zlcid_lst}) 
                        # 从临时表中获取交易引用的子流程
                        zlc_result2 = ModSql.kf_ywgl_019.execute_sql_dict(db,'check_zlc_exist',{'tname':['gl_zlcdy_ls'],'zlcid_lst':zlcid_lst}) 
                        zlc_result1.extend(zlc_result2)
                        zlcid = [ dic['id'] for dic in zlc_result1]
                        zlcid = list(set(zlcid))
                        
                        logger.info( '冲正：需要子流程[%s],提供子流程[%s]' % ( ','.join ( sorted(zlcid_lst) ), ','.join ( sorted(zlcid) ) ) )
                        
                        if len(zlcid) != len(zlcid_lst):
                            msg = "交易节点配置的冲正子流程不能一一对应,需要子流程列表[%s],本地子流程和导入子流程检索到的子流程列表[%s]，请检查" % ( ','.join ( sorted(zlcid_lst) ), ','.join ( sorted(zlcid) ) )
                            return {'state':False,'msg':msg}
                
                if lst[1] == 'zlc':
                    # 判断冲正配置的子流程是否存在
                    rs = ModSql.kf_ywgl_019.execute_sql_dict(db,'get_extend_czpz_zlc',{'id':lst[0]})
                    if rs:
                        # 获取交易引用的子流程的ID
                        zlcid_lst = [dic['czpzid'] for dic in rs]
                        # 从正式表中获取交易引用的子流程
                        zlc_result1 = ModSql.kf_ywgl_019.execute_sql_dict(db,'check_zlc_exist',{'tname':['gl_zlcdy'],'zlcid_lst':zlcid_lst}) 
                        # 从临时表中获取交易引用的子流程
                        zlc_result2 = ModSql.kf_ywgl_019.execute_sql_dict(db,'check_zlc_exist',{'tname':['gl_zlcdy_ls'],'zlcid_lst':zlcid_lst}) 
                        zlc_result1.extend(zlc_result2)
                        zlcid = [ dic['id'] for dic in zlc_result1]
                        zlcid = list(set(zlcid))
                        
                        logger.info( '子流程冲正：需要子流程[%s],提供子流程[%s]' % ( ','.join ( sorted(zlcid_lst) ), ','.join ( sorted(zlcid) ) ) )
                        
                        if len(zlcid) != len(zlcid_lst):
                            msg = "子流程节点配置的冲正子流程不能一一对应,需要子流程列表[%s],本地子流程和导入子流程检索到的子流程列表[%s]，请检查" % ( ','.join ( sorted(zlcid_lst) ), ','.join ( sorted(zlcid) ) )
                            return {'state':False,'msg':msg}
            
            # 若本次导入了交易，需将交易暂停
            if jyid_lst:
                rs = ModSql.kf_ywgl_019.execute_sql_dict(db,"get_jy_zt",{'jyid_lst':jyid_lst})
                for dic in rs:
                    jy_zt_dic[dic['id']] = dic['zt']
                ModSql.kf_ywgl_019.execute_sql_dict(db,"update_jy_zt",{'zt':'0','jyid_lst':jyid_lst})
                sql = "update gl_jydy set zt = '0' where %s"%("or".join( ["id='%s'"%(id) for id in jyid_lst]))
                sql_lst.append({'lx':"暂停交易",'zxsq':[sql],'yssj':''})    
        #2.先导入数据库模型，因为在导入数据库模型时会执行一些DDL语句，DDL语句会将DML命令给提交，这样在导入出现问题时，无法自动回滚，所以先执行数据库的导入
        with sjapi.connection() as db:
            for str in drxx:
                lst = str.split('|') 
                # 导入记录的ID
                id = lst[0]
                # 导入记录的类型
                lx = lst[1]
                if lx == 'sjk':
                    imp_sjk(db,lx,id,sql_lst,file_lst,add_table_dic,upd_id_lst)
            if file_lst:
                # 将数据库模型的执行SQL写入到文件中
                fname = hy_write_file( file_lst )

        with sjapi.connection() as db:
            # 将修改的数据表操作放到该事务中，这样在出现异常时，可以回滚
            for id in upd_id_lst:
                # 先将正式表中的数据库模型信息删除
                zxsq = del_sjkmxxx( db,id )
                # 在从临时表中将数据库模型信息导入正式表
                zxsq1 = ins_zsb_from_lsb(db,id)
                zxsq.extend(zxsq1)
                # 记录执行SQL
                sql_lst.append({'lx':'数据库模型','zxsq':zxsq,'yssj':''})
            #2.其他信息的导入
            for str in drxx:
                lst = str.split('|') 
                # 导入记录的ID
                id = lst[0]
                # 导入记录的类型
                lx = lst[1]
                # 如果导入类型为ywcs:业务参数
                if lx == 'ywcs':
                    # 查询原业务信息
                    rs = ModSql.kf_ywgl_019.execute_sql_dict(db,"get_ywxx",{'id':ywid})
                    dic = rs[0] if rs else ''
                    ModSql.kf_ywgl_019.execute_sql_dict(db,"delete_yw",{'id':ywid})
                    sql1 = "delete from gl_ywdy where id = '%s'"%( ywid)
                    #将临时表中的业务信息导入到正式表
                    ModSql.kf_ywgl_019.execute_sql_dict(db,"ins_ywdy_from_lsb",{'id':ywid})
                    sql2 = "insert into gl_ywdy select * from gl_ywdy_ls where id = '%s'"%(ywid)
                    sql_lst.append({'lx':'业务信息','zxsq':[sql1,sql2],'yssj':dic})
                    #业务参数导入
                    imp_csdy(db,ywid,sql_lst)
                    # 清空缓存中对应的业务( 业务（YW）业务代码 )
                    if dic:
                        memcache_data_del( [dic['ywbm']] )
                    
                # 如果导入类型为:jy:交易
                if lx == 'jy':
                    # 交易基本信息导入
                    imp_jy_jbxx(db,id,sql_lst)
                    # 交易参数导入
                    imp_csdy(db,id,sql_lst)
                    # 交易流程导入
                    imp_jylc(db,id,lx,sql_lst)
                    # 更新交易唯一码
                    #update_wym(db,'jy',id)
                    # 交易流程提交版本库
                    imp_lcbbk(db,id,lx,sql_lst)
                    if xtlx == 'kf':
                        # 交易测试案例导入
                        imp_csal(db,id,lx,sql_lst)
                # 通讯子流程只导入基本信息
                if drlx in ('yw','jy') and lx == 'zlc': 
                    # 子流程基本信息导入
                    imp_zlc_jbxx(db,id,sql_lst)
                    # 子流程流程导入
                    imp_jylc(db,id,lx,sql_lst)
                    # 子流程提交版本库
                    imp_lcbbk(db,id,lx,sql_lst)
                    if xtlx == 'kf':
                        # 子流程测试案例导入
                        imp_csal(db,id,lx,sql_lst)
                # 如果导入类型为:dymb:打印模版
                if lx == 'dymb':
                    imp_dymb(db,id,sql_lst)
                # 如果导入类型为:gghs:公共函数
                if lx == "gghs":
                    imp_gghs(db,lx,id,sql_lst)
                # 如果导入类型为:sjk:数据库
                if lx == 'sjk':
                    pass
                # 如果导入类型为：jd:节点
                if lx == 'jd':
                    imp_jd(db,lx,id,sql_lst)
                    if xtlx == 'kf':
                        # 节点测试案例导入
                        imp_csal(db,id,lx,sql_lst)
                # 如果导入类型为txcs通讯参数
                if lx == 'txcs':
                    # 通讯参数导入
                    txid = id.split('-')[0]
                    imp_csdy(db,txid,sql_lst)
                if lx == 'txgl':
                    # 通讯信息导入
                    txid = id.split('-')[0]
                    imp_txjbxx(db,txid,sql_lst)
                if lx == 'cdtx':
                    rs = ModSql.kf_ywgl_019.execute_sql_dict(db,"get_cdtx_from_lsb",{'id':id})[0]
                    # 子流程基本信息导入
                    ret = imp_zlc_jbxx(db,rs['zlcdyid'],sql_lst)
                    # C端通讯导入
                    imp_cdtx(db,id,sql_lst)
                    # 创建C端通讯的子流程( 如果新增，新增流程走向和流程布局 )
                    if ret == 1:
                        add_cdtx_lc( db, rs['jbjdid'], rs['dbjdid'], rs['zlcdyid'] )
                    if xtlx == 'kf':
                        # 导入挡板信息
                        imp_dbxx(db,id,sql_lst)
                        # 子流程测试案例导入
                        imp_csal(db,rs['zlcdyid'],'zlc',sql_lst)
            # 编码维护导入
            imp_bmwh(db,sql_lst)
            # 更新导入流水
            if drlx == 'tx':
                ssid = txid
            elif drlx == 'yw':
                ssid = ywid
            elif drlx == 'jy':
                ssid = ",".join( jyid_lst )
            sql_dic = {'id':drlsid,'ss_idlb': ssid,"ssywid":ywid,'czr':get_sess_hydm(),'czsj':get_strftime(),'bz':bzxx,'czms':drms,'fhr':fhr,'zt':'1'}
            ModSql.kf_ywgl_019.execute_sql( db,"update_drls",sql_dic)
            # 将操作流水登记到BLOB管理表
            for dic in sql_lst:
                sql_dic={'id':get_uuid(),'lx':'gl_drls','czr':get_sess_hydm(),'czsj':get_strftime(),'nr':pickle.dumps(dic),'ssls':drlsid}
                ModSql.kf_ywgl_019.execute_sql_dict(db,"ins_czls_to_blob",sql_dic)
            if fname:
                msg = '数据库模型升级出现危险操作，请参照[%s]手工升级'%(fname)
            else:
                msg = "导入成功"
                # 操作日志登记
                ins_czrz( db, nr , gnmc = '导入' )
            return {'state':True,'msg':msg}
    except:
        logger.info(traceback.format_exc())
        # 若导入出现了异常，需要暂停的交易再启用
        if jyid_lst:
            with sjapi.connection() as db:
                zxsq = []
                for id in jyid_lst:
                    if jy_zt_dic.get(id,''):
                        ModSql.kf_ywgl_019.execute_sql_dict(db,"update_jy_zt",{'zt':jy_zt_dic[id],'jyid_lst':[id]})
                        sql = "update gl_jydy set zt = '%s' where id = '%s'"%(jy_zt_dic[id],id) 
                        zxsq.append(sql)
                sql_lst.append({'lx':"启用交易",'zxsq':zxsq,'yssj':''})   
        # 若本次导入有新的数据表，需将表删除
        if add_table_dic:
            with sjapi.connection() as db:
                for id,sjbmc in add_table_dic.items():
                    ModSql.common.execute_sql_dict(db,"drop_table",{'tname_lst':[sjbmc]})
                    ModSql.kf_ywgl_011.execute_sql_dict(db,"del_sjkmxdy",{'drop_table':[id]})
                    ModSql.kf_ywgl_011.execute_sql_dict(db,"del_sjkzdb_by_tabid",{'drop_table':[id]})
                    ModSql.kf_ywgl_011.execute_sql_dict(db,"del_sjksy_by_tabid",{'drop_table':[id]})
                    ModSql.kf_ywgl_011.execute_sql_dict(db,"del_sjkys_by_tabid",{'drop_table':[id]})
        error_msg = traceback.format_exc()
        data['msg'] = '导入失败！异常错误提示信息[%s]' % error_msg
    return data
        
def imp_csdy(db,ssid,sql_lst):
    """
    # 导入业务、交易、通讯参数
    """
    # 从正式表中获取参数
    csxx_lst = ModSql.kf_ywgl_019.execute_sql_dict(db,'get_csxx',{'id':ssid})
    # 从临时表中获取参数
    tmp_csxx_lst = ModSql.kf_ywgl_019.execute_sql_dict(db,'get_csxx_from_lsb',{'id':ssid})
    for index,dic in enumerate(tmp_csxx_lst):
        zsb_id_lst = [ dic['id'] for dic in csxx_lst]
        # 若临时表中的记录在正式表中不存在，需插入到正式表
        if dic['id'] not in zsb_id_lst:
            ModSql.kf_ywgl_019.execute_sql_dict(db,'ins_csdy_from_lsb',{'id':dic['id']})
            sql="insert into gl_csdy select * from gl_csdy_ls where id = '%s'"%(dic['id'])
            sql_lst.append({'lx':'参数','zxsq':[sql],'yssj':''})
        else:
            # 若临时表及正式版都存在，需校验信息是否一致
            zlb_index = zsb_id_lst.index(dic['id'])
            zsb_dic = csxx_lst[zlb_index]
            for key,value in dic.items():
                zsb_val = zsb_dic.get(key)
                # 只要有一个字段的信息不一致，就直接进行更新，不需要在继续比较
                if value != zsb_val:
                    ModSql.kf_ywgl_019.execute_sql_dict(db,'update_csxx',dic)
                    sql = """ 
                        update gl_csdy set csdm='%(csdm)s',csms='%(csms)s',value='%(value)s',lx='%(lx)s',ssid='%(ssid)s',zt='%(zt)s',
                        czr='%(czr)s',czsj='%(czsj)s',wym='%(wym)s'
                        where id = '%(id)s'
                    """%(dic)
                    sql_lst.append({'lx':'参数','zxsq':[sql],'yssj':zsb_dic})
                    break
    
def imp_jy_jbxx(db,id,sql_lst):
    """
    # 交易基本信息导入
    """
    # 从正式表中获取交易信息
    jyxx_lst = ModSql.kf_ywgl_019.execute_sql_dict(db,'get_jyxx',{'id':id})
    # 从临时表中获取交易信息
    tmp_jyxx_lst = ModSql.kf_ywgl_019.execute_sql_dict(db,'get_jyxx_from_lsb',{'id':id})
    for index,dic in enumerate(tmp_jyxx_lst):
        zsb_id_lst = [ dic['id'] for dic in jyxx_lst]
        # 由于之前的版本提交没有加自动发起配置说明，所以为了解决线上不出错，只能是手动添加。没有什么实际意义。
        dic['zdfqpzsm'] = set_zdfqpzsm(dic)
        # 若临时表中的记录在正式表中不存在，需插入到正式表
        if dic['id'] not in zsb_id_lst:
            ModSql.kf_ywgl_019.execute_sql_dict(db,'ins_jydy_from_lsb',{'id':dic['id']})
            sql1 = "insert into gl_jydy select * from gl_jydy_ls where id = '%s'"%(dic['id'])
            # 登记计划任务
            if dic['zdfqpz']:
                # 新增计划任务
                #sql_data = {'id':get_uuid(),'zdfqpz':dic['zdfqpz'] if dic['zdfqpz'] else '','zdfqpzsm':dic['zdfqpzsm'],'ssid':dic['id'],'rwlx':'jy','zt':dic['zt']}
                #ModSql.common.execute_sql_dict(db,'ins_jhrwb',sql_data )
                upd_dic = { 'id':get_uuid(), 'zdfqpz': dic['zdfqpz'] if dic['zdfqpz'] else '','zdfqpzsm': dic['zdfqpzsm'], 'rwlx': 'jy','ssid': dic['id'],'zt': dic['zt'] }
                #update_jhrw( db, dic['zt'], dic['zdfqpz'], upd_dic = upd_dic )
                # 调用公共函数 第二个参数是原状态，第三个是原自动发起配置。此时正式表中不存在计划任务，所以元状态为1（启用），自动发起配置应当都是空。
                update_jhrw( db, '0', '', upd_dic = upd_dic, sfxz = True )
                sql2="""
                    insert into gl_jhrwb (id,zdfqpz,zdfqpzsm,rwlx,ssid,zt)
                    values( '%(id)s','%(zdfqpz)s','%(zdfqpzsm)s','%(rwlx)s','%(ssid)s','%(zt)s') 
                """%(upd_dic)
                sql_lst.append({'lx':'交易','zxsql':[sql1,sql2],'yssj':''})
        else:
            # 若临时表及正式版都存在，需校验信息是否一致
            zlb_index = zsb_id_lst.index(dic['id'])
            zsb_dic = jyxx_lst[zlb_index]
            for key,value in dic.items():
                zsb_val = zsb_dic.get(key)
                # 只要有一个字段的信息不一致，就直接进行更新，不需要在继续比较
                if value != zsb_val:
                    ModSql.kf_ywgl_019.execute_sql_dict(db,'update_jyxx',dic)
                    sql1="""
                        update gl_jydy set ssywid='%(ssywid)s',jym='%(jym)s',jymc='%(jymc)s',jyms='%(jyms)s',timeout='%(timeout)s',zdfqpz='%(zdfqpz)s',zdfqpzsm='%(zdfqpzsm)s',dbjdid='%(dbjdid)s',jbjdid='%(jbjdid)s',
                        czr='%(czr)s',czsj='%(czsj)s',wym='%(wym)s'
                        where id = '%(id)s'
                    """%( dic )
                    # 更新计划任务
#                    if dic['zdfqpz']:
#                        # 存在则更新
#                        sql_data = {'zdfqpz':dic['zdfqpz'],'zdfqpzsm': dic['zdfqpz'] if dic['zdfqpz'] else '','ssid':dic['id'],'rwlx':'jy','zt':dic['zt']}
#                        #ModSql.common.execute_sql_dict(db,'upd_jhrwb_by_ssid',sql_data )
#                        sql2="""
#                            update gl_jhrwb set zdfqpz = '%(zdfqpz)s',zdfqpzsm = '%(zdfqpzsm)s',rwlx = '%(rwlx)s',zt = '%(zt)s'
#                            where ssid = '%(ssid)s'
#                        """%(sql_data)
#                        sql_lst.append({'lx':'交易','zxsq':[sql1,sql2],'yssj':zsb_dic})
#                    else:
#                        # 不存在则删除
#                        sql_data = {'ssid':dic['id']}
#                        #ModSql.common.execute_sql_dict(db,'del_jhrw_byssid',sql_data )
#                        sql2="""
#                            delete from gl_jhrwb
#                            where ssid = %(ssid)s
#                        """%(sql_data)
#                        sql_lst.append({'lx':'交易','zxsq':[sql1,sql2],'yssj':zsb_dic})
            
            # 处理交易的计划任务信息
            # upd_dic = { 'zdfqpz': zdfqpz,'zdfqpzsm': zdfqpzsm,'rwlx': rwlx,'ssid':ssid,'zt':zt }
            upd_dic = { 'zdfqpz': dic['zdfqpz'],'zdfqpzsm': dic['zdfqpzsm'] if dic['zdfqpzsm'] else '', 'rwlx': 'jy','ssid': dic['id'],'zt': '0' }
            # 交易发起配置由没值变为有值，则往计划任务表中插入记录
            if not zsb_dic['zdfqpz'] and upd_dic['zdfqpz']:
                # 获取id
                upd_dic['id'] = get_uuid()
                # 补充字段
                upd_dic['ip'] = ''
                upd_dic['sfkbf'] = ''
                upd_dic['yjjb'] = ''
                ModSql.common.execute_sql_dict(db, "ins_jhrwb", upd_dic)
            
            # 调用公共函数 第二个参数为正式表，也就是交易表的状态
            update_jhrw( db, '1', zsb_dic['zdfqpz'], upd_dic = upd_dic, sfxz = False )
            # 如果导入的交易的自动发起配置为空，则将计划任务表的内容删除掉
            if not dic['zdfqpz']:
                ModSql.common.execute_sql_dict(db,'del_jhrw_byssid',{'ssid':dic['id']})
            
            # 清空缓存中（memcache）对应的交易
            memcache_data_del( [zsb_dic['jym']] )
            
def imp_jylc(db,id,lx,sql_lst):
    """
    # 交易流程及子流程导入
    """       
    xml = xml_out(db,lx,id)
    # 获取流程布局ID列表
    rs = ModSql.kf_ywgl_019.execute_sql_dict(db,'get_lcbj_id',{'field': ['ssjyid' if lx =='jy' else 'sszlcid'],'id':id }) 
    if rs:
        lcbjid_lst = [ dic['id'] for dic in rs]
        # 删除正式表中流程走向的信息
        ModSql.kf_ywgl_019.execute_sql_dict(db,"delete_lczx",{'ssid':id})
        sql1= "delete from gl_lczx where ssid = '%s' "%( id )
        # 删除正式表中流程布局信息
        ModSql.kf_ywgl_019.execute_sql_dict(db,"delete_lcbj",{'field': ['ssjyid' if lx =='jy' else 'sszlcid'],'id':id })
        sql2= "delete from gl_lcbj where %s = '%s'"%( 'ssjyid' if lx =='jy' else 'sszlcid',id )
        # 将流程布局信息从临时表导入正式表
        ModSql.kf_ywgl_019.execute_sql_dict(db,"ins_lbcj_from_lsb",{'field': ['ssjyid' if lx =='jy' else 'sszlcid'],'id':id }) 
        sql3 = "insert into gl_lcbj select * from gl_lcbj_ls where %s = '%s'"%( 'ssjyid' if lx =='jy' else 'sszlcid',id)   
        # 将流程走向信息从临时表导入到正式表
        ModSql.kf_ywgl_019.execute_sql_dict(db,"ins_lczx_from_lsb",{'ssid':id })
        sql4 = "insert into gl_lczx select * from gl_lczx_ls where ssid = '%s'"%( id )
        sql_lst.append({'lx':'流程','zxsq':[sql1,sql2,sql3,sql4],'yssj':xml})
        
def imp_lcbbk(db,id,lx,sql_lst):
    """
    # 导入时提交版本库
    """
    # 获取版本信息
    rs = get_bcxx(db,lx,id)
    # 说明不需要进行版本提交
    if rs['state'] == True:
        return
    # 插入BLOB管理表
    blob_id = get_uuid()
    sql_dic = {'id':blob_id,'lx':'gl_bbkz','czr':get_sess_hydm(),'czsj':get_strftime(),'nr':pickle.dumps(rs['bbnr'])}
    ModSql.kf_ywgl_019.execute_sql_dict(db,"ins_blob_for_bbtj",sql_dic )
    sql1 = "insert into gl_blob(id,lx,czr,czsj,nr) values('%(id)s','%(lx)s','%(czr)s','%(czsj)s','%(nr)s)'"%(sql_dic)
    # 插入版本控制表
    sql_dic = {'id':get_uuid(),'lx':lx,'ssid':id,'bbh':rs['bbh'],'tjr':get_sess_hydm(),'tjsj':get_strftime(),'tjms':'业务交易导入提交','nr_id':blob_id,'wym':rs['wym']}
    ModSql.kf_ywgl_019.execute_sql_dict(db,"ins_bbkz_for_bbtj",sql_dic)   
    sql2 = """
        insert into gl_bbkz(id,lx,ssid,bbh,tjr,tjsj,tjms,nr_id,wym)
        values('%(id)s','%(lx)s','%(ssid)s','%(bbh)s','%(tjr)s','%(tjsj)s','%(tjms)s','%(nr_id)s','%(wym)s')
    """%(sql_dic)
    sql_lst.append({'lx':"版本控制",'zxsq':[sql1,sql2],'yssj':''})
    
def imp_zlc_jbxx(db,id,sql_lst):
    """
    # 子流程基本信息导入
    """
    # 返回值，默认是新增1,0：修改
    ret = 1
    # 从正式表中获取交易信息
    zlcxx_lst = ModSql.kf_ywgl_019.execute_sql_dict(db,'get_zlcxx',{'id':id})
    # 从临时表中获取交易信息
    tmp_zlcxx_lst = ModSql.kf_ywgl_019.execute_sql_dict(db,'get_zlcxx_from_lsb',{'id':id})
    for index,dic in enumerate(tmp_zlcxx_lst):
        zsb_id_lst = [ dic['id'] for dic in zlcxx_lst]
        # 若临时表中的记录在正式表中不存在，需插入到正式表
        if dic['id'] not in zsb_id_lst:
            ModSql.kf_ywgl_019.execute_sql_dict(db,'ins_zlcdy_from_lsb',{'id':dic['id']})
            sql = "insert into gl_zlcdy select * from gl_zlcdy_ls where id = '%s'"%(dic['id'])
            sql_lst.append({'lx':'子流程','zxsq':[sql],'yssj':''})
        else:
            # 若临时表及正式版都存在，需校验信息是否一致
            zlb_index = zsb_id_lst.index(dic['id'])
            zsb_dic = zlcxx_lst[zlb_index]
            for key,value in dic.items():
                zsb_val = zsb_dic.get(key)
                # 只要有一个字段的信息不一致，就直接进行更新，不需要在继续比较
                if value != zsb_val:
                    ModSql.kf_ywgl_019.execute_sql_dict(db,'update_zlcxx',dic)
                    sql = """
                        update gl_zlcdy set lb='%(lb)s',bm='%(bm)s',ms='%(ms)s',ssywid='%(ssywid)s',czr='%(czr)s',czsj='%(czsj)s',
                        wym='%(wym)s',mc='%(mc)s'
                        where id = '%(id)s'
                    """%( dic )
                    sql_lst.append({'lx':'子流程','zxsq':[sql],'yssj':zsb_dic})
                    break    
            
            # 清空缓存中对应的子流程
            memcache_data_del( [id] )
            # 返回值为编辑 0
            ret = 0
    # 反馈标志新增或编辑标志
    return ret
    
def imp_dymb(db,id,sql_lst):
    """
    # 打印模版导入
    """
    # 执行SQL
    sql1 = ''
    # 原始数据
    yssj = ''
    # 从正式表中获取打印模版信息
    dymb_lst = ModSql.kf_ywgl_019.execute_sql_dict(db,'get_dymbxx',{'id':id})
    for dic in dymb_lst:
        if dic['nr']:
            dic['nr'] = pickle.loads( dic['nr'].read() )
        else:
            dic['nr'] = ''
    # 从临时表中获取打印模版信息
    tmp_dymb_lst = ModSql.kf_ywgl_019.execute_sql_dict(db,'get_dymbxx_from_lsb',{'id':id})
    for dic in tmp_dymb_lst:
        if dic['nr']:
            dic['nr'] = pickle.loads( dic['nr'].read() )
        else:
            dic['nr'] = ''
    for index,dic in enumerate(tmp_dymb_lst):
        zsb_id_lst = [ dic['id'] for dic in dymb_lst]
        # 若临时表中的记录在正式表中不存在，需插入到正式表
        if dic['id'] not in zsb_id_lst:
            ModSql.kf_ywgl_019.execute_sql_dict(db,'ins_dymb_from_lsb',{'id':dic['id']})
            sql1 = "insert into gl_dymbdy select * from gl_dymbdy_ls where id = '%s'"%(dic['id'])
        else:
            # 若临时表及正式版都存在，需校验信息是否一致
            zlb_index = zsb_id_lst.index(dic['id'])
            zsb_dic = dymb_lst[zlb_index]
            for key,value in dic.items():
                zsb_val = zsb_dic.get(key)
                # 只要有一个字段的信息不一致，就直接进行更新，不需要在继续比较
                if value != zsb_val:
                    del dic['nr']
                    ModSql.kf_ywgl_019.execute_sql_dict(db,'update_dymbxx',dic)
                    sql2 = """
                        update gl_dymbdy set mbmc='%(mbmc)s',mbms='%(mbms)s',mblx='%(mblx)s',czr='%(czr)s',czsj='%(czsj)s',nr_id='%(nr_id)s',
                        ssyw_id='%(ssyw_id)s',wym='%(wym)s'
                        where id = '%(id)s'
                    """%(dic)
                    yssj = zsb_dic
                    break    
    # 删除正式表中的打印模版内容
    ModSql.kf_ywgl_019.execute_sql_dict(db,"delete_blob",{'id':dymb_lst[0]['nr_id'] if dymb_lst else ''})
    sql2="delete from gl_blob where id ='%s'"%(dymb_lst[0]['nr_id'] if dymb_lst else '')
    # 将临时表中的数据导入到正式版
    ModSql.kf_ywgl_019.execute_sql_dict(db,"ins_blob_for_lsb",{'id':tmp_dymb_lst[0]['nr_id'] if tmp_dymb_lst else ''})
    sql3="insert into gl_blob select * from gl_blob_ls where id = '%s'"%(tmp_dymb_lst[0]['nr_id'] if tmp_dymb_lst else '')
    sql_lst.append({'lx':'打印模版','zxsq':[sql1,sql2,sql3],'yssj':yssj})   
     
def imp_gghs(db,lx,id,sql_lst):
    """
    # 公共函数导入
    """
    # 执行SQL
    sql1 = ''
    # 原始数据
    yssj = ''
    # 从正式表中获取公共函数信息
    gghs_lst = ModSql.kf_ywgl_019.execute_sql_dict(db,'get_gghsxx',{'id':id})
    for dic in gghs_lst:
        if dic['nr']:
            dic['nr'] = pickle.loads( dic['nr'].read() )
        else:
            dic['nr'] = ''
    # 从临时表中获取公共函数信息
    tmp_gghs_lst = ModSql.kf_ywgl_019.execute_sql_dict(db,'get_gghsxx_from_lsb',{'id':id})
    for dic in tmp_gghs_lst:
        if dic['nr']:
            dic['nr'] = pickle.loads( dic['nr'].read() )
        else:
            dic['nr'] = ''
    for index,dic in enumerate(tmp_gghs_lst):
        zsb_id_lst = [ dic['id'] for dic in gghs_lst]
        # 若临时表中的记录在正式表中不存在，需插入到正式表
        if dic['id'] not in zsb_id_lst:
            ModSql.kf_ywgl_019.execute_sql_dict(db,'ins_gghs_from_lsb',{'id':dic['id']})
            sql1="insert into gl_yw_gghs select * from gl_yw_gghs_ls where id = '%s'"%(dic['id'])
        else:
            # 若临时表及正式版都存在，需校验信息是否一致
            zlb_index = zsb_id_lst.index(dic['id'])
            zsb_dic = gghs_lst[zlb_index]
            for key,value in dic.items():
                zsb_val = zsb_dic.get(key)
                # 只要有一个字段的信息不一致，就直接进行更新，不需要在继续比较
                if value != zsb_val:
                    del dic['nr']
                    ModSql.kf_ywgl_019.execute_sql_dict(db,'update_gghsxx',dic)
                    sql1 = """
                        update gl_yw_gghs set ssyw_id='%(ssyw_id)s',czr='%(czr)s',czsj='%(czsj)s',nr_id='%(nr_id)s',
                        mc='%(mc)s',hsms='%(hsms)s',wym='%(wym)s'
                        where id = '%(id)s'
                    """%(dic)
                    yssj = zsb_dic
                    break    
            # 清空缓存中对应的公共函数( 函数（HS）函数UUID )
            memcache_data_del( [id] )
            
    # 删除正式表中的公共函数内容
    ModSql.kf_ywgl_019.execute_sql_dict(db,"delete_blob",{'id':gghs_lst[0]['nr_id'] if gghs_lst else ''})
    sql2="delete from gl_blob where id ='%s'"%( gghs_lst[0]['nr_id'] if gghs_lst else '')
    # 将临时表中的数据导入到正式版
    ModSql.kf_ywgl_019.execute_sql_dict(db,"ins_blob_for_lsb",{'id':tmp_gghs_lst[0]['nr_id'] if tmp_gghs_lst else ''})
    sql3="insert into gl_blob select * from gl_blob_ls where id = '%s'"%(tmp_gghs_lst[0]['nr_id'] if tmp_gghs_lst else '')
    sql_lst.append({'lx':'公共函数','zxsq':[sql1,sql2,sql3],'yssj':yssj})   
    # 公共函数版本提交
    imp_lcbbk(db,id,lx,sql_lst)
    
def imp_sjk(db,lx,id,sql_lst,file_lst,add_table_dic,upd_id_lst):
    """
    # 数据库模型导入
    """
    zxsq = []
    # 从临时表中查询数据表信息
    tmp_sjb_wym = ModSql.kf_ywgl_019.execute_sql_dict(db,"get_sjbwym_from_lsb",{'id':id})
    # 从正式表中查询数据表信息
    sjb_wym = ModSql.kf_ywgl_019.execute_sql_dict(db,"get_sjbwym",{'id':id})  
    # 正式表唯一码为空，说明本次导入的数据表为新增
    if not sjb_wym:
        # 将临时表数据导入至正式表
        zxsq = ins_zsb_from_lsb(db,id)
        sjbmc,create_sql,zs_subsql_lst,sy_dic,ys_lst = get_sjkmx(db,id)
        # 建表
        db.execute( create_sql ) 
        add_table_dic[id] = tmp_sjb_wym[0]['sjbmc']
        zxsq.append( create_sql )
        # 创建注释
        for sql in zs_subsql_lst:
            db.execute( sql ) 
            zxsq.append(sql)
        # 创建约束
        for sql in ys_lst:
            db.execute( sql ) 
            zxsq.append(sql)
        # 创建约束后，查询该表已有的索引，因在创建约束及表时，会自动创建一些索引，此时在创建索引表中的索引可能会发送冲突，需将自动创建的索引去除
        rs = ModSql.kf_ywgl_011.execute_sql_dict(db,"get_oracle_sy",{'sjbmc':sjbmc})
        symc_lst = [dic['symc'] for dic in rs]
        for symc,sql in sy_dic.items():
            if symc not in symc_lst:
                db.execute( sql ) 
                zxsq.append(sql)
        # 记录执行SQL
        sql_lst.append({'lx':'数据库模型','zxsq':zxsq,'yssj':''})
        # 提交版本库
        imp_lcbbk(db,id,lx,sql_lst)
    elif  sjb_wym[0]['wym'] != tmp_sjb_wym[0]['wym']:
        # 处理表字段
        ht_zdbyz( db, id, tmp_sjb_wym[0]['sjbmc'], file_lst, type = '019' )
        # 数据表索引处理
        hy_sybyz( db, id, tmp_sjb_wym[0]['sjbmc'], file_lst, type = '019' )
        # 数据表约束处理
        hy_ysbyz( db, id, tmp_sjb_wym[0]['sjbmc'], file_lst, type = '019' )
        # 将数据表ID添加到
        upd_id_lst.append(id)
def get_sjkmx(db,id):
    """
    # 获取数据表的建表语句
    """
    # 获取数据表信息
    sjbxx = ModSql.kf_ywgl_019.execute_sql_dict(db,"get_sjkmx",{'id':id})[0]
    # 获取数据表字段
    zd_lst = ModSql.kf_ywgl_019.execute_sql_dict(db,"get_sjkzd",{'id':id})
    # 获取数据表索引
    sy_lst = ModSql.kf_ywgl_019.execute_sql_dict(db,"get_sjksy",{'id':id})
    # 获取数据表约束
    ys_lst = ModSql.kf_ywgl_019.execute_sql_dict(db,"get_sjkys",{'id':id})
    # 数据表名称
    sjbmc = sjbxx['sjbmc']
    # 数据表名称描述
    sjbmcms = sjbxx['sjbmcms']
    sql = " create table %s ( "%sjbmc
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
            subsql = " %s %s ( %d ) "%( zdmc,zdlx,zdcd )
        elif zdlx == 'DECIMAL':
            if xscd:
                subsql = "  %s %s ( %d,%d )"%( zdmc,zdlx,zdcd,xscd )
            else:
                subsql = " %s %s ( %d ) "%( zdmc,zdlx,zdcd )
        elif zdlx in ( 'DATE', 'LONG', 'BLOB', 'CLOB', 'NCLOB', 'BFILE', 'INTEGER', 'LONG RAW','REAL'):
            subsql = " %s %s"%( zdmc,zdlx )
        elif zdlx == 'NUMBER':
            if zdcd:
                if xscd:
                    subsql = "  %s %s ( %d,%d )"%( zdmc,zdlx,zdcd,xscd )
                else:
                    subsql = " %s %s ( %d ) "%( zdmc,zdlx,zdcd )
            else:
                subsql = " %s %s"%( zdmc,zdlx )
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
    create_sql = sql + ",".join( subsql_lst ) + " ,constraint PK_%s primary key ( %s )"%( sjbmc,",".join( iskey_lst ) ) + " )" 
    # 为表及字段增加注释,本来想将所有增加的SQL拼接起来进行执行，但是一直报无效的字符，找不到具体原因，拼接后的SQL拿到数据库中也可以直接执行，通过代码执行就报错
    sy_sql_dic = {}
    for dic in sy_lst:
        sql = ''
        # 拼接创建索引SQL
        if dic['sylx'] == 'NORMAL':
            sql = "create %s index %s on %s (%s)"%( 'unique' if dic['sfwysy'] == 'UNIQUE' else '',dic['symc'],sjbmc,",".join( dic['syzd'].split("|") ) );
        elif dic['sylx'] == 'NORMAL/REV':
            sql = "create %s index %s on %s (%s) reverse"%( 'unique' if dic['sfwysy'] == 'UNIQUE' else '', dic['symc'],sjbmc,",".join( dic['syzd'].split("|") ) );
        elif dic['sylx'] == 'BITMAP':
            sql = "create  bitmap index %s on %s (%s) "%( dic['symc'],sjbmc,",".join( dic['syzd'].split("|") ) );
        sy_sql_dic[dic['symc']] = sql
    ys_sql_lst = []
    for dic in ys_lst:
        sql = "alter table %s add constraint %s unique （%s）"%( sjbmc,dic['ysmc'],",".join( dic['yszd'].split("|") ) )
        ys_sql_lst.append(sql)
    return sjbmc,create_sql,zs_subsql_lst,sy_sql_dic,ys_sql_lst
    
    
def imp_jd(db,lx,id,sql_lst):
    """
    # 导入节点
    """
    # 执行SQL
    sql1 = ''
    # 原始数据
    yssj = ''
    # 从正式表中获取公共函数信息
    jg_lst = ModSql.kf_ywgl_019.execute_sql_dict(db,'get_jdxx',{'id':id})
    for dic in jg_lst:
        if dic['nr']:
            dic['nr'] = pickle.loads( dic['nr'].read() )
        else:
            dic['nr'] = ''
    # 从临时表中获取公共函数信息
    tmp_jd_lst = ModSql.kf_ywgl_019.execute_sql_dict(db,'get_jdxx_from_lsb',{'id':id})
    for dic in tmp_jd_lst:
        if dic['nr']:
            dic['nr'] = pickle.loads( dic['nr'].read() )
        else:
            dic['nr'] = ''
    for index,dic in enumerate(tmp_jd_lst):
        zsb_id_lst = [ dic['id'] for dic in jg_lst]
        # 若临时表中的记录在正式表中不存在，需插入到正式表
        if dic['id'] not in zsb_id_lst:
            ModSql.kf_ywgl_019.execute_sql_dict(db,'ins_jd_from_lsb',{'id':dic['id']})
            sql1="insert into gl_jddy select distinct * from gl_jddy_ls where id = '%s'"%(dic['id'])
        else:
            # 若临时表及正式版都存在，需校验信息是否一致
            zlb_index = zsb_id_lst.index(dic['id'])
            zsb_dic = jg_lst[zlb_index]
            for key,value in dic.items():
                zsb_val = zsb_dic.get(key)
                # 只要有一个字段的信息不一致，就直接进行更新，不需要在继续比较
                if value != zsb_val:
                    ModSql.kf_ywgl_019.execute_sql_dict(db,'update_jdxx',dic)
                    sql1 = """
                        update gl_jdxx set bm='%(bm)s',jdlx='%(jdlx)s',jdmc='%(jdmc)s',jdms='%(jdms)s',dm_id='%(dm_id)s',
                        filename='%(filename)s',functionname='%(functionname)s',type='%(type)s',czr='%(czr)s',czsj='%(czsj)s',wym='%(wym)s'
                        where id = '%(id)s'
                    """%(dic)
                    yssj = zsb_dic
                    break    
            
            # 清理节点缓存（ 交易节点（JYJD）交易节点UUID ）
            memcache_data_del( [id] )
            
    # 删除正式表中的节点代码
    ModSql.kf_ywgl_019.execute_sql_dict(db,"delete_blob",{'id':jg_lst[0]['dm_id'] if jg_lst else ''})
    sql2="delete from gl_blob where id ='%s'"%(jg_lst[0]['dm_id'] if jg_lst else '')
    # 将临时表中的数据导入到正式版
    ModSql.kf_ywgl_019.execute_sql_dict(db,"ins_blob_for_lsb",{'id':tmp_jd_lst[0]['dm_id'] if tmp_jd_lst else ''})
    sql3="insert into gl_blob select * from gl_blob_ls where id = '%s'"%(tmp_jd_lst[0]['dm_id'] if tmp_jd_lst else '')
    sql_lst.append({'lx':'节点信息','zxsq':[sql1,sql2,sql3],'yssj':yssj}) 
    # 获取节点要素的原始数据
    rs = ModSql.kf_ywgl_019.execute_sql_dict(db,"get_jdys",{'id':id})
    # 将正式表中的节点要素删除
    ModSql.kf_ywgl_019.execute_sql_dict(db,"delete_jdys",{'id':id})
    sql1 = "delete from gl_jdys where jddyid='%s'"%(id)
    # 将临时表中的节点要素插入到正式表
    ModSql.kf_ywgl_019.execute_sql_dict(db,"ins_jdys_from_lsb",{'id':id})  
    sql2 = "insert into gl_jdys select * from gl_jdys_ls where jddyid = '%s'"%(id)
    sql_lst.append({'lx':'节点要素','zxsq':[sql1,sql2],'yssj':rs})
    # 节点版本提交
    imp_lcbbk(db,id,lx,sql_lst)

def imp_csal(db,id,lx,sql_lst):
    """
    # 导入测试案例
    """
    lx_dic = {'jy':'1','zlc':'2','jd':'3'}
    # 查询测试案例信息
    rs = ModSql.kf_ywgl_019.execute_sql_dict(db,"get_csal_from_lsb",{'ssid':id,'sslb':lx_dic.get(lx)})
    # 当导出的dmp中没有测试案例信息时，无法删除对应交易的测试案例，这时需要验证正式库有没有测试案例，如果有就删除
    if not rs:
        rs = ModSql.kf_ywgl_019.execute_sql_dict(db,"get_csal_from_zsb",{'ssid':id,'sslb':lx_dic.get(lx)})
    zxsq = []
    if rs:
        jdcsalzxbz_id_lst = []
        demoid_lst = []
        for dic in rs:
            jdcsalzxbzlb_lst = dic['jdcsalzxbzlb'].split(",")
            jdcsalzxbz_id_lst.extend( jdcsalzxbzlb_lst )
            if dic['demoid']:
                demoid_lst.append(dic['demoid'])
        # 删除节点测试案例要素
        ModSql.kf_ywgl_019.execute_sql_dict(db,"delete_jdcsalys",{'jdcsalzxbzid_lst':jdcsalzxbz_id_lst})
        sql1=" delete from gl_jdcsalys where %s"%( "or".join( ["jdcsalzxbz='%s'"%(id) for id in jdcsalzxbz_id_lst]))
        zxsq.append(sql1)
        # 删除节点测试案例执行步骤
        ModSql.kf_ywgl_019.execute_sql_dict(db,"delete_jdcsalzxbz",{'jdcsalzxbzid_lst':jdcsalzxbz_id_lst})
        sql2="delete from gl_jdcsalzxbz where %s"%( "or".join( ["id='%s'"%(id) for id in jdcsalzxbz_id_lst]))
        zxsq.append(sql2)
        # 删除测试案例
        if lx == 'jd':
            # 节点类型（因为节点是可以被多个交易共用的，此节点的测试案例不能全部删除） 
            # 删除测试案例，只删除此次导入交易对应节点的测试案例，不删除其他交易对于此节点的测试案例
            ModSql.kf_ywgl_019.execute_sql_dict(db,"delete_csal2",{'ssid':id,'sslb':lx_dic.get(lx)})
            sql3="delete from gl_csaldy a, gl_jydy_ls b where a.ssjy_id = b.id and ssid = '%s' and sslb = '%s'"%(id,lx_dic.get(lx))
            zxsq.append(sql3)
        else:
            # 其他类型正常操作
            ModSql.kf_ywgl_019.execute_sql_dict(db,"delete_csal",{'ssid':id,'sslb':lx_dic.get(lx)})
            sql3="delete from gl_csaldy where ssid = '%s' and sslb = '%s'"%(id,lx_dic.get(lx))
            zxsq.append(sql3)
        if demoid_lst:
            # 删除demo数据
            ModSql.kf_ywgl_019.execute_sql_dict(db,"delete_demo_sj",{'demoid_lst':demoid_lst})
            sql4="delete from gl_demo_sj where  %s"%( "or".join( ["demojbxxid='%s'"%(id) for id in demoid_lst]))
            zxsq.append(sql4)
            # 删除demo基本信息
            ModSql.kf_ywgl_019.execute_sql_dict(db,"delete_demo_jbxx",{'demoid_lst':demoid_lst})
            sql5="delete from gl_demo_jbxx where %s "%( "or".join( ["id='%s'"%(id) for id in demoid_lst]))
            zxsq.append(sql5)
        # 插入测试案例
        ModSql.kf_ywgl_019.execute_sql_dict(db,"ins_csal_from_lsb",{'ssid':id,'sslb':lx_dic.get(lx)})
        sql6 = "insert into gl_csaldy select distinct * from gl_csaldy_ls where where ssid = '%s' and sslb = '%s'"%(id,lx_dic.get(lx))
        zxsq.append(sql6)
        # 插入节点测试案例执行步骤
        ModSql.kf_ywgl_019.execute_sql_dict(db,"ins_jdcsalzxbz_from_lsb",{'jdcsalzxbzid_lst':jdcsalzxbz_id_lst})
        sql7 = " insert into gl_jdcsalzxbz select distinct * from gl_jdcsalzxbz_ls where %s"%( "or".join( ["id='%s'"%(id) for id in jdcsalzxbz_id_lst]))
        zxsq.append(sql7)
        # 插入节点测试案例要素
        ModSql.kf_ywgl_019.execute_sql_dict(db,"ins_jdcsalys_from_lsb",{'jdcsalzxbzid_lst':jdcsalzxbz_id_lst})
        sql8 = "insert into  gl_jdcsalys select distinct * from gl_jdcsalys_ls where %s"%( "or".join( ["jdcsalzxbz='%s'"%(id) for id in jdcsalzxbz_id_lst]))
        zxsq.append(sql8)
        if demoid_lst:
            # 插入demo基本信息
            ModSql.kf_ywgl_019.execute_sql_dict(db,"ins_demojbxx_from_lsb",{'demoid_lst':demoid_lst})
            sql9 = "insert into  gl_demo_jbxx select * from gl_demo_jbxx_ls where  %s "%( "or".join( ["id='%s'"%(id) for id in demoid_lst]))
            zxsq.append(sql9)
            # 插入demo数据
            ModSql.kf_ywgl_019.execute_sql_dict(db,"ins_demosj_from_lsb",{'demoid_lst':demoid_lst})
            sql10 = "insert into  gl_demo_sj select * from gl_demo_sj_ls where %s"%( "or".join( ["demojbxxid='%s'"%(id) for id in demoid_lst]))
            zxsq.append(sql10)
        sql_lst.append({'lx':'测试案例','zxsq':zxsq,'yssj':''})
    
def imp_bmwh(db,sql_lst):
    """
    # 编码维护导入
    """   
    # 查询编码维护临时表是否存在
    count = ModSql.kf_ywgl_019.execute_sql_dict(db,"get_drlsb",{'tname':'GL_BMWH_LS'})[0]['count']
    if count == 0:
        return 
    # 从临时表中获取需要导入的编码维护表信息
    rs = ModSql.kf_ywgl_019.execute_sql_dict(db,"get_bmwh_id")
    if rs:
        # 获取编码维护表的原始数据
        yssj = ModSql.kf_ywgl_019.execute_sql_dict(db,"get_bmwh_xx",{'id_lst':[dic['id'] for dic in rs]}) 
        # 删除编码维护表信息
        ModSql.kf_ywgl_019.execute_sql_dict(db,"delete_bmwh",{'id_lst':[dic['id'] for dic in rs]})
        sql1="delete from gl_bmwh where %s"%("or".join( ["id='%s'"%(dic['id']) for dic in rs]))
        # 将编码维护信息从临时表，导入至正式表
        ModSql.kf_ywgl_019.execute_sql_dict(db,"ins_bmwh_from_lsb",{'id_lst':[dic['id'] for dic in rs]})
        sql2=" insert into gl_bmwh select * from gl_bmwh_ls where %s"%("or".join( ["id='%s'"%(dic['id']) for dic in rs]))
        sql_lst.append({'lx':'编码维护','zxsq':[sql1,sql2],'yssj':yssj})
    
def imp_txjbxx(db,txid,sql_lst):
    """
    # 通讯基本信息导入
    """
    # 从正式表中获取通讯信息
    txglxx_lst = ModSql.kf_ywgl_019.execute_sql_dict(db,'get_txglxx',{'id':txid})
    # 从临时表中获取交易信息
    tmp_txglxx_lst = ModSql.kf_ywgl_019.execute_sql_dict(db,'get_txglxx_from_lsb',{'id':txid})
    for index,dic in enumerate(tmp_txglxx_lst):
        zsb_id_lst = [ dic['id'] for dic in txglxx_lst]
        # 若临时表中的记录在正式表中不存在，需插入到正式表
        if dic['id'] not in zsb_id_lst:
            ModSql.kf_ywgl_019.execute_sql_dict(db,'ins_txgl_from_lsb',{'id':dic['id']})
            sql1 = "insert into gl_txgl select * from gl_txgl_ls where id = '%s'"%(dic['id'])
            # 函数解析信息从临时blob表中导入到正式表中
            ModSql.kf_ywgl_019.execute_sql_dict(db,'ins_txgl_blob_from_lsb',{'id':dic['id']})
            sql2 = "insert into gl_blob select * from gl_blob_ls where id in ( select jcjymhsid from gl_txgl_ls where id = '%s' )"%(dic['id'])
            sql_lst.append({'lx':'通讯基本信息','zxsql':[sql1,sql2],'yssj':''})
        else:
            # 若临时表及正式版都存在，需校验信息是否一致
            zlb_index = zsb_id_lst.index(dic['id'])
            zsb_dic = txglxx_lst[zlb_index]
            for key,value in dic.items():
                zsb_val = zsb_dic.get(key)
                # 只要有一个字段的信息不一致，就直接进行更新，不需要在继续比较
                if value != zsb_val:
                    ModSql.kf_ywgl_019.execute_sql_dict(db,'update_txglxx',dic)
                    sql1="""
                        update gl_txgl set bm='%(bm)s',mc='%(mc)s',fwfx='%(fwfx)s',cssj='%(cssj)s',txwjmc='%(txwjmc)s',wym='%(wym)s',
                        txlx='%(txlx)s',czr='%(czr)s',czsj='%(czsj)s',jcbfs='%(jcbfs)s',jcjymhsid='%(jcjymhsid)s'
                        where id = '%(id)s'
                    """%( dic )
                    # 删除正式表中的交易码解出函数代码
                    ModSql.kf_ywgl_019.execute_sql_dict(db,"delete_blob",{'id':dic['jcjymhsid'] if dic['jcjymhsid'] else ''})
                    sql2="delete from gl_blob where id ='%s'"%(dic['jcjymhsid'] if dic['jcjymhsid'] else '')
                    # 将临时表中的数据导入到正式版
                    ModSql.kf_ywgl_019.execute_sql_dict(db,"ins_blob_for_lsb",{'id':dic['jcjymhsid'] if dic['jcjymhsid'] else ''})
                    sql3="insert into gl_blob select * from gl_blob_ls where id = '%s'"%(dic['jcjymhsid'] if dic['jcjymhsid'] else '')
                    sql_lst.append({'lx':'通讯基本信息','zxsq':[sql1,sql2,sql3],'yssj':zsb_dic})
                    break 
            
            # 清除memcache
            memcache_data_del([zsb_dic['bm']])

def imp_cdtx(db,id,sql_lst):
    """
    # C端通讯导入
    """
    # 从正式表中获取交易信息
    cdtx_lst = ModSql.kf_ywgl_019.execute_sql_dict(db,'get_cdtx',{'id':id})
    # 从临时表中获取交易信息
    tmp_cdtx_lst = ModSql.kf_ywgl_019.execute_sql_dict(db,'get_cdtx_from_lsb',{'id':id})
    for index,dic in enumerate(tmp_cdtx_lst):
        zsb_id_lst = [ dic['id'] for dic in cdtx_lst]
        # 若临时表中的记录在正式表中不存在，需插入到正式表
        if dic['id'] not in zsb_id_lst:
            ModSql.kf_ywgl_019.execute_sql_dict(db,'ins_cdtx_from_lsb',{'id':dic['id']})
            sql = "insert into gl_cdtx select * from gl_cdtx_ls where id = '%s'"%(dic['id'])
            sql_lst.append({'lx':'C端通讯','zxsql':[sql],'yssj':''})
        else:
            # 若临时表及正式版都存在，需校验信息是否一致
            zlb_index = zsb_id_lst.index(dic['id'])
            zsb_dic = cdtx_lst[zlb_index]
            for key,value in dic.items():
                zsb_val = zsb_dic.get(key)
                # 只要有一个字段的信息不一致，就直接进行更新，不需要在继续比较
                if value != zsb_val:
                    ModSql.kf_ywgl_019.execute_sql_dict(db,'update_cdtx',dic)
                    sql="""
                        update gl_cdtx set bm='%(bm)s',zlcdyid='%(zlcdyid)s',txglid='%(txglid)s',dfjym='%(dfjym)s',dfjymc='%(dfjymc)s',cssj='%(cssj)s',
                        dblx='%(dblx)s',dbssid='%(dbssid)s',wym='%(wym)s',ssywid='%(ssywid)s',jbjdid='%(jbjdid)s',dbjdid='%(dbjdid)s',czr='%(czr)s',czsj='%(czsj)s',jkqyzt='%(jkqyzt)s'
                        where id = '%(id)s'
                    """%( dic )
                    sql_lst.append({'lx':'C端通讯','zxsq':[sql],'yssj':zsb_dic})
                    break 
    
def imp_dbxx(db,id,sql_lst):
    """
    # 导入挡板信息
    """
    # 判断通讯挡板信息表是否存在
    count = ModSql.kf_ywgl_019.execute_sql_dict(db,"get_drlsb",{'tname':'GL_DBDY_LS'})[0]['count']
    if count == 0:
        return 
    # 删除该C端通讯下的所有的挡板要素
    ModSql.kf_ywgl_019.execute_sql_dict(db,"del_dbys",{'id':id})
    sql1="delete from gl_dbys where dbdyid in ( select id from gl_dbdy where cdtxid = '%s')"%(id)
    # 删除该C端通讯下的所有的挡板
    ModSql.kf_ywgl_019.execute_sql_dict(db,"del_dbdy",{'id':id})
    sql2="delete from gl_dbdy where cdtxid = '%s'"%(id)
    # 将临时表中的挡板定义信息导入到正式
    ModSql.kf_ywgl_019.execute_sql_dict(db,"ins_dbdy_from_lsb",{'id':id})
    sql3="insert into gl_dbdy select * from gl_dbdy_ls where cdtxid = '%s'"%(id)
    # 将临时表中的挡板要素信息导入到正式版
    ModSql.kf_ywgl_019.execute_sql_dict(db,"ins_dbys_from_lsb",{'id':id})
    sql4="insert into gl_dbys  select * from gl_dbys_ls where dbdyid in ( select id from gl_dbdy_ls where cdtxid = '%s' )"%(id)
    sql_lst.append({'lx':'C端通讯挡板','zxsq':[sql1,sql2,sql3,sql4],'yssj':''})
    
def ins_zsb_from_lsb(db,id):
    """
    # 将临时表中的数据库模型数据导入到正式表
    """    
    ModSql.kf_ywgl_019.execute_sql_dict(db,"ins_sjkmxdy",{'id':id})
    sql1="insert into gl_sjkmxdy select * from gl_sjkmxdy_ls where id = '%s'"%(id)
    ModSql.kf_ywgl_019.execute_sql_dict(db,"ins_sjkzdb",{'id':id})
    sql2="insert into gl_sjkzdb select * from gl_sjkzdb_ls where sjb_id = '%s'"%(id)
    ModSql.kf_ywgl_019.execute_sql_dict(db,"ins_sjkys",{'id':id})
    sql3="insert into gl_sjkys select * from gl_sjkys_ls where sssjb_id = '%s'"%(id)
    ModSql.kf_ywgl_019.execute_sql_dict(db,"ins_sjksy",{'id':id})
    sql4="insert into gl_sjksy select * from gl_sjksy_ls where sssjb_id = '%s'"%(id)
    zxsq=[sql1,sql2,sql3,sql4]
    return zxsq
    
def del_sjkmxxx(db,id):
    """
    # 将正式表中的数据库模型信息删除
    """
    # 先将正式表的数据删除
    ModSql.kf_ywgl_011.execute_sql_dict(db,"del_sjkmxdy",{'drop_table':[id]})
    ModSql.kf_ywgl_011.execute_sql_dict(db,"del_sjkzdb_by_tabid",{'drop_table':[id]})
    ModSql.kf_ywgl_011.execute_sql_dict(db,"del_sjksy_by_tabid",{'drop_table':[id]})
    ModSql.kf_ywgl_011.execute_sql_dict(db,"del_sjkys_by_tabid",{'drop_table':[id]})
    sql1 = "delete from gl_sjkmxdy where id = '%s'"%(id)
    sql2 = "delete from gl_sjkzdb where sjb_id = '%s'"%(id)
    sql3 = "delete from gl_sjksy where sssjb_id = '%s'"%(id)
    sql4 = "delete from gl_sjkys where sssjb_id = '%s'"%(id)
    zxsq = [sql1,sql2,sql3,sql4]
    return zxsq
    
def get_jdxx( db,leftJd,rightJd ):
    """
        # 从节点定义表中获取数据
    """ 
    ljd_rs = []
    rjd_rs = []
    # 获取左侧所有的节点
    ljd_lst = [ dic['id'] for dic in leftJd]
    # 获取右侧所有的节点
    rjd_lst = [ dic['id'] for dic in rightJd]
    # 获取左侧比右侧多的节点
    left_lst = list(set(ljd_lst).difference(set(rjd_lst)))
    # 获取右侧壁左侧多的节点
    right_lst = list(set(rjd_lst).difference(set(ljd_lst)))
    if right_lst:
        lResult = ModSql.kf_ywgl_019.execute_sql_dict(db,"get_jdxx_from_jddy",{'tname':['gl_jddy_ls'],'id_lst':right_lst})
        # 组织左侧结果
        leftJd.extend(lResult)
        # 记录节点的ID，循环交易节点、子流程节点、交易打解包节点的合并列表，将ID放入该列表，后续判断重复时使用
        cfid_lst = []
        for index,dic in enumerate(leftJd):
            if dic['id'] not in cfid_lst:
                cfid_lst.append(dic['id'])
                ljd_rs.append(dic)
        sorted(ljd_rs,key=lambda dic:dic['bm'])  
    else:
        ljd_rs = leftJd
    if left_lst:
        rResult = ModSql.kf_ywgl_019.execute_sql_dict(db,"get_jdxx_from_jddy",{'tname':['gl_jddy'],'id_lst':left_lst})
        # 组织左侧结果
        rightJd.extend(rResult)
        # 记录节点的ID，循环交易节点、子流程节点、交易打解包节点的合并列表，将ID放入该列表，后续判断重复时使用
        cfid_lst = []
        for index,dic in enumerate(rightJd):
            if dic['id'] not in cfid_lst:
                cfid_lst.append(dic['id'])
                rjd_rs.append(dic)
        sorted(rjd_rs,key=lambda dic:dic['bm'])  
    else:
        rjd_rs = rightJd
    return ljd_rs,rjd_rs
    
def check_drlx( db, drlx, ywid = None ):
    """
    # 验证文件导入类型是否和导入类型一致
    @param db 数据库连接
    @param drlx 导出类型
    """
    # 返回信息
    msg = '待导入库数据与预期导入数据不一致，请检查'
    try:
        if drlx != 'tx':
            # 因为新增加czpzid影响到导入，为了支持从没有czpzid版本库导出，可以导入到有czpzid库情况
            count_rs = db.execute_sql( """ select count(1) as count from user_tab_columns c
                                        where c.table_name = 'GL_LCBJ_LS' and column_name= 'CZPZID'""" )
            logger.info('校验流程布局表字段信息：%s', str(count_rs))
            if count_rs[0]['count'] == 0:
                logger.info('临时表中没有czpzid字段，需要添加此字段')
                db.execute_sql( "alter table GL_LCBJ_LS add CZPZID VARCHAR2(32)" )
        
        # 验证文件导入类型是否和导入类型一致
        rs = ModSql.kf_ywgl_019.execute_sql_dict(db,"get_drdclx_ls")
        if rs:
            if rs[0]['lx'] and rs[0]['lx'] == drlx:
                if drlx == 'jy':
                    # 如果是交易判断导入文件对应的业务是否和指定业务一致
                    # 从交易临时表中获取对应业务
                    rs_ywid = ModSql.kf_ywgl_019.execute_sql_dict(db,"get_ywid_ls")
                    if rs_ywid and rs_ywid[0]['ssywid'] == ywid:
                        msg = 'True'
                    else:
                        msg = '导入交易文件中交易列表对应业务与页面操作业务不一致，请检查'
                else:
                    msg = 'True'
            else:
                msg = '待导入库数据[lx:%s]与预期导入数据[lx:%s]不一致，请检查' % ( rs[0]['lx'], drlx )
    except:
        msg = '验证文件导入类型是否和导入类型一致出现异常,请检查问题原因'
        logger.info(traceback.format_exc())
    
    return msg