# -*- coding: utf-8 -*-
# Action: 维护系统导入
# Author: zhangzhf
# AddTime: 2015-10-20
# Standard: 注释仅能以“#”开头，sql可以是“--”；注释不能同代码在同一行

import os,pickle,json,copy,traceback
from sjzhtspj import ModSql,get_sess_hydm,TMPDIR,logger
from sjzhtspj.common import ( get_uuid,get_strftime,get_strftime2,check_fhr,ftp_put,set_zdfqpzsm,get_bmwh_bm,del_waitexec_task,ins_waitexec_task,ins_czrz )
from sjzhtspj.const import FHR_JSDM
from sjzhtspj.esb import send_jr, sftp_put

# 当前库临时表的列表
table_ls = ['GL_DXDY_LS','GL_ZJXX_LS','GL_CJPZB_LS','GL_DXCJPZ_LS','GL_CRCS_LS','GL_CSDYB_LS','GL_HSXXB_LS','GL_JKFXPZ_LS','GL_XYDZPZ_LS','GL_DZZXZJ_LS','GL_JHRWB_LS','GL_JCXXPZ_LS','GL_YZJYPZ_LS','GL_YZJYCSPZ_LS','GL_BLOB_LS']
# 当前库正式表的列表
table_zs = ['GL_DXDY','GL_ZJXX','GL_CJPZB','GL_DXCJPZ','GL_CRCS','GL_CSDYB','GL_HSXXB','GL_JKFXPZ','GL_XYDZPZ','GL_DZZXZJ','GL_JHRWB','GL_JCXXPZ','GL_YZJYPZ','GL_YZJYCSPZ','GL_BLOB']

def local_data_service():
    """
    # 获取右侧本地库数据service
    """
    return_data = dc_data()
    data = {'state':True, 'msg':'','rows':[]}
    # 链接数据库
    with sjapi.connection() as db:
        # 获取监控对象类别
        jkdxlb_lst = ModSql.yw_pzsj_002.execute_sql_dict(db,"get_jklb",{})
        # 循环监控类别列表，依次查询监控类别对应的对象
        for jk in jkdxlb_lst:
            j = {'id': jk['lbmc'], 'czsj': '', 'name':jk['lbmc']+'('+jk['lbbm']+')', 'czr': ''}
            j['children'] = ModSql.yw_pzsj_002.execute_sql_dict(db,"get_jkdx",{'jkdxlb_sql_data':[jk['lbbm']]})
            return_data[0]['children'][0]['children'].append(j)
        # 查询分析规则
        fxgz_lst = ModSql.yw_pzsj_002.execute_sql_dict(db,"get_fxgz",{})
        # 查询响应动作
        xydz_lst = ModSql.yw_pzsj_002.execute_sql_dict(db,"get_xydz",{})
        # 数据采集配置
        sjcjpz_lst = ModSql.yw_pzsj_002.execute_sql_dict(db,"get_sjcjpz",{})
        # 查询监控配置
        jkpz_lst = ModSql.yw_pzsj_002.execute_sql_dict(db,"get_jkfxpz",{})
        
        # 查询业务配置
        ywpz_lst = ModSql.yw_pzsj_002.execute_sql_dict(db,"get_yzjypz",{})
        # 查询进程配置
        jcpz_lst = ModSql.yw_pzsj_002.execute_sql_dict(db,"get_jcxxpz",{})
        
        # 组织数据
        # 分析规则
        return_data[0]['children'][1]['children'].extend(fxgz_lst)
        # 相应动作
        return_data[0]['children'][2]['children'].extend(xydz_lst)
        # 数据采集配置
        return_data[0]['children'][3]['children'].extend(sjcjpz_lst)
        # 监控配置
        return_data[0]['children'][4]['children'].extend(jkpz_lst)
        # 业务配置
        return_data[1]['children'][1]['children'].extend(ywpz_lst)
        
        ywcspz_lst = ModSql.yw_pzsj_002.execute_sql_dict(db,"get_yzjycspz",{})
        # 在得到的参数中，获取所有业务
        ywpz_lst = {yw['ywbm']:yw['ywmc'] for yw in ywcspz_lst}
        # 循环阈值校验参数，使其和业务对应
        for k,v in ywpz_lst.items():
            chi = {'id': k, 'czsj': '', 'name':v+'('+k+')', 'czr': ''}
            cspz_lst = ModSql.yw_pzsj_002.execute_sql_dict(db,"get_yzjycspz",{'ywbm':k})
            if cspz_lst:
                chi['children'] = copy.deepcopy(cspz_lst)
            return_data[1]['children'][0]['children'].append(copy.deepcopy(chi))
        
        # 进程配置
        return_data[2]['children'].extend(jcpz_lst)
    data['rows'] = return_data 
    return data
    
def data_drwj_add_service(filename,wjnr,drlx):
    data = {'state':True,'msg':'','leftRows':[], 'rightRows':[],'id_dic':{},'drlsid':''}
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
        
        if not flag:
            return {'state':False,'msg':'SFTP失败，请检查问题原因'}
        # 登记导入流水
        drlsid = get_uuid()
        sql_data = {'id':drlsid,'czlx':'dr','nrlx':drlx,'czr':get_sess_hydm(),'czsj':get_strftime(),'czms':'','bfwjm':'','bz':'','zt':'0','wjm':filename,'fhr':'','ss_idlb':'','ssywid':''}
        ModSql.common.execute_sql( db,"insert_drls",sql_data)
        # 删除临时表
        drop_table(db)
        # 创建临时表
        create_table( db,table_zs)        
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
        table_name = ",".join( table_zs )
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
        # 删除临时表
        drop_table(db)
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
        logger.info("导入完成，正在获取两侧数据......")
        if check_drlx(db) == False:
            data['state'] = False
            data['msg'] = '您当前导入不是维护系统的内容，请检查!'
            return data
        # 矫正正式表和临时表的id
        refresh_id(db)
        # 获取【数据采集配置】和【适用对象(监控对象)】的对应关系；【监控配置】和【分析规则，响应动作】的对应关系；
        relation,relation_reverse = get_relation(db)
        # 获取两侧侧数据（）
        leftData , rightData = get_all_data(db)
        data['leftRows'] = leftData
        data['rightRows'] = rightData
        data['drlsid'] = drlsid
        data['relation'] = relation
        data['relation_reverse'] = relation_reverse
        return data

def check_drlx(db):
    """
    # 判断当前导入的内容是否是维护系统的内容
    """
    try:
        rs = ModSql.yw_pzsj_001.execute_sql_dict(db,"check_drlx",{})
    except:
        logger.info(traceback.format_exc())
        return False
    return True
    
def get_relation(db):
    """
    # 获取【数据采集配置】和【适用对象(监控对象)】的对应关系；【监控配置】和【分析规则，响应动作】的对应关系；
    """
    # 数据采集配置
    sjcjpz_dic = {}
    # 监控配置
    jkpz_dic = {}
    # 数据采集配置反转关系
    sjcjpz_dic_reverse = {}
    # 监控配置反转关系
    jkpz_dic_reverse = {}
    # 获取数据采集配置对应的监控对象
    sjcjpz_list = ModSql.yw_pzsj_001.execute_sql_dict(db,"get_sjcjpz",{'table_name':["gl_cjpzb_ls"]})
    for pz in sjcjpz_list:
        # 获取采集配置所需要的监控对象
        jkdx_list = ModSql.yw_pzsj_001.execute_sql_dict(db,"get_jkdx_for_sjcjpz",{'cjpzid':pz['id']})
        for jk in jkdx_list:
            # 获取数据采集配置的关系
            if not sjcjpz_dic.get(pz['id']):
                sjcjpz_dic[pz['id']] = [jk['dxid']]
            else:
                sjcjpz_dic[pz['id']].append(jk['dxid'])
            # 获取数据采集配置的反转关系
            if not sjcjpz_dic_reverse.get(jk['dxid']):
                sjcjpz_dic_reverse[jk['dxid']] = [pz['id']]
            else:
                sjcjpz_dic_reverse[jk['dxid']].append(pz['id'])
    # 获取监控配置
    jkfxpz_list = ModSql.yw_pzsj_001.execute_sql_dict(db,"get_jkfxpz",{'table_name':["gl_jkfxpz_ls"]})
    # 获取监控对象所需要的，分析规则
    jkpz_dic = {jk['id']:[jk['gzid']] for jk in jkfxpz_list}
    # 获取监控对象所需的分析规则的反转关系
    jkpz_dic_reverse = {jk['gzid']:[jk['id']] for jk in jkfxpz_list}
    # 获取监控对象所需要的，响应动作
    for jkpz in jkfxpz_list:
        xydx_list = ModSql.yw_pzsj_001.execute_sql_dict(db, "get_jcpz_xydzcs", {'table_name_xydzpz':['gl_xydzpz_ls'],'table_name_hsxxb':['gl_hsxxb_ls'], 'table_name_jkfxpz':['gl_jkfxpz_ls'],'id':jkpz['id']})
        for xy in xydx_list:
            if not jkpz_dic.get(jkpz['id']):
                jkpz_dic[jkpz['id']] = [xy['dzid']]
            else:
                jkpz_dic[jkpz['id']].append(xy['dzid'])
            if not jkpz_dic_reverse.get(xy['dzid']):
                jkpz_dic_reverse[xy['dzid']] = [jkpz['id']]
            else:
                jkpz_dic_reverse[xy['dzid']].append(jkpz['id'])
    return dict(sjcjpz_dic, **jkpz_dic),dict(sjcjpz_dic_reverse, **jkpz_dic_reverse)
def refresh_id(db):
    """
    # 该方法是根据正式表的函数名称更新临时表的函数id，使函数名称相同的函数保持id一致。
    # 为了每个项目上线时函数信息表（分析规则，相应动作）的id都不一致的问题，故加此方法。
    # 1.组织临时表和正式的的id对应关系{'临时表id':'正式表id'}
    # 2.更新参数对应表的【传入参数ID】
    # 3.更新传入参数的id
    # 4.更新监控分析配置中的【分析规则id】和【相应动作id】
    # 5.更新响应动作配置的【动作id】
    # 6.更新临时表的分析规则id
    # 7.更新临时表的响应动作id
    # 8.更新分析规则响应动作的的传入参数的所属id   
    """
    # 查询临时表中所有的分析规则和相应动作
    fxgl_zs_list = ModSql.yw_pzsj_001.execute_sql_dict(db,"get_fxgz_xydz",{'table_name':['gl_hsxxb']})
    fxgl_ls_list = ModSql.yw_pzsj_001.execute_sql_dict(db,"get_fxgz_xydz",{'table_name':['gl_hsxxb_ls']})
    # 组织临时表和正式的的id对应关系{'正式表id':'临时表id'}
    # 正式表id和函数名的对应{'函数名称':'id'}
    id_mc_dic_zs = {hs['hsmc']:hs['id'] for hs in fxgl_zs_list}
    # 临时表id和函数名的对应{'函数名称':'id'}
    id_mc_dic_ls = {hs['hsmc']:hs['id'] for hs in fxgl_ls_list}
    # 正式表内容id和函数名的对应{'函数名称':'nr_id'}
    nr_id_mc_dic_zs = {hs['hsmc']:hs['nr_id'] for hs in fxgl_zs_list}
    # 临时表内容id和函数名的对应{'函数名称':'nr_id'}
    nr_id_mc_dic_ls = {hs['hsmc']:hs['nr_id'] for hs in fxgl_ls_list}
    # 获取对应关系
    id_dic = get_id_dic(id_mc_dic_ls,id_mc_dic_zs)
    # 获取函数名称和函数内容id的对应关系
    nr_id_dic = get_id_dic(nr_id_mc_dic_ls,nr_id_mc_dic_zs)
    # 更新临时表的分析规则，响应动作的内容id
#    for ls_nr_id,zs_nr_id in nr_id_dic.items():
#        # 更新内容id
#        ModSql.yw_pzsj_001.execute_sql(db,"update_nrid",{'table_name':['gl_hsxxb_ls'],'ls_id':ls_nr_id,'zs_id':zs_nr_id})
    # 更新临时表的分析规则，响应动作id
    for ls_id,zs_id in id_dic.items():
        # 获取正式表函数的所有参数 
        hsxxb_crcs_ls_list = ModSql.yw_pzsj_001.execute_sql_dict(db,"get_crcs_id",{'table_name':['gl_crcs_ls'],'hsxxb_id':ls_id})
        # 获取临时表函数的所有参数
        hsxxb_crcs_zs_list = ModSql.yw_pzsj_001.execute_sql_dict(db,"get_crcs_id",{'table_name':['gl_crcs'],'hsxxb_id':zs_id})
        # 正式表参数id和参数名的对应{'参数名称':'id'}
        crcs_id_mc_dic_zs = {hs['csdm']:hs['id'] for hs in hsxxb_crcs_zs_list}
        # 临时表参数id和参数名的对应{'参数名称':'id'}
        crcs_id_mc_dic_ls = {hs['csdm']:hs['id'] for hs in hsxxb_crcs_ls_list}
        # 临时表和正式标的id对应关系{'临时表id':'正式表id'}
        crcs_id_dic = get_id_dic(crcs_id_mc_dic_ls,crcs_id_mc_dic_zs)
        # 更新临时表的传入参数id
        for crcs_ls_id,crcs_zs_id in crcs_id_dic.items():
            # 更新参数对应表的【所属ID】
            ModSql.yw_pzsj_001.execute_sql(db,"update_csdyb_crcsid",{'table_name':['gl_csdyb_ls'],'ls_id':crcs_ls_id,'zs_id':crcs_zs_id})
            ModSql.yw_pzsj_001.execute_sql(db,"update_crcs_id",{'table_name':['gl_crcs_ls'],'ls_id':crcs_ls_id,'zs_id':crcs_zs_id})
        # 更新监控分析配置中的【分析规则id】
        ModSql.yw_pzsj_001.execute_sql(db,"update_jkfxpz_fxgz_id",{'table_name':['gl_jkfxpz_ls'],'ls_id':ls_id,'zs_id':zs_id})
        # 更新响应动作配置的【动作id】
        ModSql.yw_pzsj_001.execute_sql(db,"update_xydz_id",{'table_name':['gl_xydzpz_ls'],'ls_id':ls_id,'zs_id':zs_id})
        # 更新分析规则，响应动作
        ModSql.yw_pzsj_001.execute_sql(db,"update_fxgz_xydz_id",{'table_name':['gl_hsxxb_ls'],'ls_id':ls_id,'zs_id':zs_id})
        # 更新分析规则响应动作的的传入参数的所属id
        ModSql.yw_pzsj_001.execute_sql(db,"update_crcs_ssid",{'table_name':['gl_crcs_ls'],'ls_id':ls_id,'zs_id':zs_id})
            
def get_id_dic(id_mc_dic_ls,id_mc_dic_zs):
    """
    # 生成对应关系{'临时表id':'正式表id'}
    """
    id_dic = {}
    for hsmc,id in id_mc_dic_ls.items():
        # 如果临时表的函数名称在正式表中存在
        if id_mc_dic_zs.get(hsmc):
            # 组成对应关系{'临时表id':'正式表id'}
            id_dic[id] = id_mc_dic_zs.get(hsmc)
    return id_dic
    
def create_table(db,table_name):
    """
    # 创建临时表
    """
    for tname in table_name:
        ModSql.yw_pzsj_002.execute_sql(db,"create_ls_table",{'table_name':[tname],'table_name_ls':[tname+"_LS"]})
        
def get_all_data(db):
    """
    # 获取左右两侧数的数据
    """
    zs_id = []
    ls_id = []
    
    # 左侧数据
    leftData = dc_data()
    # 右侧数据
    rightData = dc_data()
    # 获取监控对象
    # 获取监控类别（监控类别表在导出时没有导出，所以查询的是正式表）
    jkdxlb_lst = ModSql.yw_pzsj_001.execute_sql_dict(db,"get_jklb",{})
    # 循环监控类别列表，依次查询监控类别对应的对象
    for jk in jkdxlb_lst:
        jkdx_t_zs = {'id': jk['lbmc'], 'czsj': '', 'name':jk['lbmc']+'('+jk['lbbm']+')', 'czr': ''}
        jkdx_t_ls = {'id': jk['lbmc'], 'czsj': '', 'name':jk['lbmc']+'('+jk['lbbm']+')', 'czr': ''}
        jkdx_t_zs['children'] = ModSql.yw_pzsj_001.execute_sql_dict(db,"get_jkdx",{'jkdxlb_sql_data':[jk['lbbm']], 'table_name':['gl_dxdy']})
        jkdx_t_ls['children'] = ModSql.yw_pzsj_001.execute_sql_dict(db,"get_jkdx",{'jkdxlb_sql_data':[jk['lbbm']], 'table_name':['gl_dxdy_ls']})
        
        # 比较正式表与临时表监控对象
        compare_data(jkdx_t_zs['children'],jkdx_t_ls['children'])
        rightData[0]['children'][0]['children'].append(jkdx_t_zs)
        leftData[0]['children'][0]['children'].append(jkdx_t_ls)
        # 获取对象id
        zs_id.extend([z['id'] for z in jkdx_t_zs['children']])
        ls_id.extend([z['id'] for z in jkdx_t_ls['children']])
    # 合并对象id
    zs_id.extend(ls_id)
    jkdx_ids = zs_id
    
    # 获取分析规则
    fxgz_lst_zs,fxgz_lst_ls,fxgz_ids = get_lr_data(db,"get_fxgz", "gl_hsxxb")
    # 获取响应动作
    xydz_lst_zs,xydz_lst_ls,xydz_ids = get_lr_data(db,"get_xydz", "gl_hsxxb")
    # 获取数据采集配置
    sjcjpz_lst_zs,sjcjpz_lst_ls,sjcjpz_ids = get_lr_data(db,"get_sjcjpz", "gl_cjpzb")
    # 获取监控配置
    jkpz_lst_zs,jkpz_lst_ls,jkfxpz_ids = get_lr_data(db,"get_jkfxpz", "gl_jkfxpz")
    # 获取阈值校验，参数配置
    cspz_lst_zs,cspz_lst_ls,yzjycspz_ids = get_lr_data(db,"get_yzjycspz", "gl_yzjycspz")
    # 获取阈值校验-业务配置查询
    ywpz_lst_zs,ywpz_lst_ls,yzjypz_ids = get_lr_data(db,"get_yzjypz", "gl_yzjypz")
    
    # 获取进程配置信息
    jcpz_lst_zs,jcpz_lst_ls,jcxxpz_ids = get_lr_data(db,"get_jcxxpz", "gl_jcxxpz")
    
    # 组织数据结构
    rightData[0]['children'][1]['children'].extend(fxgz_lst_zs)
    rightData[0]['children'][2]['children'].extend(xydz_lst_zs)
    rightData[0]['children'][3]['children'].extend(sjcjpz_lst_zs)
    rightData[0]['children'][4]['children'].extend(jkpz_lst_zs)
    rightData[1]['children'][0]['children'].extend(do_yzcs(cspz_lst_zs,cspz_lst_ls))
    rightData[1]['children'][1]['children'].extend(ywpz_lst_zs)
    rightData[2]['children'].extend(jcpz_lst_zs)
    # 组织数据结构
    leftData[0]['children'][1]['children'].extend(fxgz_lst_ls)
    leftData[0]['children'][2]['children'].extend(xydz_lst_ls)
    leftData[0]['children'][3]['children'].extend(sjcjpz_lst_ls)
    leftData[0]['children'][4]['children'].extend(jkpz_lst_ls)
    leftData[1]['children'][0]['children'].extend( do_yzcs(cspz_lst_ls,cspz_lst_zs))
    leftData[1]['children'][1]['children'].extend(ywpz_lst_ls)
    leftData[2]['children'].extend(jcpz_lst_ls)
    return leftData,rightData
    
def do_yzcs(cspz_lst_par_f,cspz_lst_par_s):
    """
    # 将查询的参数配置
    # cspz_lst_par_f  需要组织数据的阈值校验参数
    # cspz_lst_par_s  相对应的阈值校验参数，左侧树或者右侧树的
    """
    cspz_dic = {}
    cspz_lst = []
    # 循环需要组织的阈值校验参数 ， 形成{'业务':[参数1,参数2]}形式
    for cspz in cspz_lst_par_f:
        if cspz.get('ywmc') and cspz.get('ywbm'):
            key = cspz['ywmc']+'('+cspz['ywbm']+')'
            # 如果在字典中不存在，则新增key
            if not cspz_dic.get(key):
                cspz_dic[key] = [cspz]
            else:
                cspz_dic[key].append(cspz)
    # 补充当前阈值校验参数不存在的业务，以保证在显示时，左右对应
    for cs in cspz_lst_par_s:
        if cs.get('ywmc') and cs.get('ywbm') and not cspz_dic.get(cs['ywmc']+'('+cs['ywbm']+')'):
            cspz_dic[cs['ywmc']+'('+cs['ywbm']+')'] = []
    # 组织数据        
    for k,v in cspz_dic.items():
        chi = {'id': k.split('(')[0], 'czsj': '', 'name':k, 'czr': '','children':v}
        cspz_lst.append(chi)
    return cspz_lst
            
def get_lr_data(db,sql_id,table_name):
    # 正式表内容
    zs = ModSql.yw_pzsj_001.execute_sql_dict(db,sql_id,{'table_name':[table_name]})
    # 临时表内容
    ls = ModSql.yw_pzsj_001.execute_sql_dict(db,sql_id,{'table_name':[table_name+"_ls"]})
    
    # 获取对象id
    zs_id = [z['id'] for z in zs]
    ls_id = [z['id'] for z in ls]
    # 合并对象id
    zs_id.extend(ls_id)
    
    # 比较正式表与临时表监控对象
    rightLst,leftLst = compare_data(zs,ls)
    return rightLst,leftLst,zs_id
    
def compare_data(rightLst,leftLst):
    """
    # 比较左右两侧的数据
    """
    for index,dic in enumerate(leftLst):
        # 若左侧的再右侧中不存在，说明为新增，左侧的diff属性值设为2
        right_id_lst = [ dic['id'] for dic in rightLst]
        if dic['id'] not in right_id_lst:
            leftLst[index]['diff'] = '2'
            dc = {'id':dic['id'],'diff':'2','ywbm':dic.get('ywbm'),'ywmc':dic.get('ywmc')}
            if dic.get('lx'):
                dc['lx'] = dic.get('lx')
            rightLst.insert(index,dc)
        else:
            # 若左侧的数据在右侧有，需先判断该数据在左右两侧的位置是否一致
            rightIndex = right_id_lst.index(dic['id'])
            if index != rightIndex:
                # 若位置不一至，需将右侧中该数据的位置，移到与左侧一致
                rightDic = rightLst[rightIndex]
                rightLst.remove(rightDic)
                rightLst.insert(index,rightDic)
            lwym = dic.get('wym')
            rwym = rightLst[index].get('wym')
            # 如果唯一码不是32位的的MD5，说明这个唯一码是异常的（异常包括None，null），这时候我们将唯一码变为空字符串
            if len(str(lwym)) < 32:
                lwym = ""
            if len(str(rwym)) < 32:
                rwym = ""
            # 若两侧的唯一码不一致，说明为修改，左右两侧diff属性的值设为1
            if lwym != rwym:
                leftLst[index]['diff'] = '1'
                rightLst[index]['diff'] = '1'
    for index,dic in enumerate(rightLst):
        # 若右侧的在左侧不存在，说明为删除，右侧的diff属性值为2
        left_id_lst = [ dic['id'] for dic in leftLst]
        if dic['id'] not in left_id_lst:
            rightLst[index]['diff'] = '2'
            dc = {'id':dic['id'],'diff':'2','ywbm':dic.get('ywbm'),'ywmc':dic.get('ywmc')}
            if dic.get('lx'):
                dc['lx'] = dic.get('lx')
            leftLst.insert(index,dc)
    return rightLst,leftLst
    
def dc_data():
    """
    # 返回导出的数据结构
    """
    return_data = [{
        "id": "监控定义",
        "name": "监控定义",
        "czr": "",
        "czsj": "",
        "children": [{
                "id": "监控对象",
                "name": "监控对象",
                "czr": "",
                "czsj": "",
                "children": []
            },
            {
                "id": "分析规则",
                "name": "分析规则",
                "czr": "",
                "czsj": "",
                "children": []
            },
            {
                "id": "响应动作",
                "name": "响应动作",
                "czr": "",
                "czsj": "",
                "children": []
            },
            {
                "id": "数据采集配置",
                "name": "数据采集配置",
                "czr": "",
                "czsj": "",
                "children": []
            },
            {
                "id": "监控配置",
                "name": "监控配置",
                "czr": "",
                "czsj": "",
                "children": []
            }
        ]
    },
    {
        "id": "阈值校验",
        "name": "阈值校验",
        "czr": "",
        "czsj": "",
        "children": [
            {
                "id": "参数配置",
                "name": "参数配置",
                "czr": "",
                "czsj": "",
                "children": []
            },{
                "id": "业务配置",
                "name": "业务配置",
                "czr": "",
                "czsj": "",
                "children": []
            }
        ]
    },
    {
        "id": "进程配置",
        "name": "进程配置",
        "czr": "",
        "czsj": "",
        "children": []
    }]
    
    return return_data
    
def bbdb_data_service(id,lx,mc,zbid,gzid):
    """
    # 数据比对
    """
    with sjapi.connection() as db:
        if lx == 'jkdx':
            # 获取临时表内容
            leftJkdx = ModSql.yw_pzsj_001.execute_sql_dict(db,"get_jkdx_bbdb",{'table_name':['gl_dxdy_ls'], 'id':id})
            # 获取正式表内容
            rightJkdx = ModSql.yw_pzsj_001.execute_sql_dict(db,"get_jkdx_bbdb",{'table_name':['gl_dxdy'], 'id':id})
            
            mc_dic = {'sslbbm':'对象类型', 'dxbm':'对象编码', 'dxmc':'对象名称','dxms':'对象描述','zt':'对象状态'}
            sort_lst = ['sslbbm','dxbm','dxmc','dxms','zt']
            pop_zd = ['id','diff']
            # 排序字段
            sxmc = 'sxmc'
            # 比对数据
            leftJkdxRs,rightJkdxRs = bbdb_detail(leftJkdx,rightJkdx,mc_dic,sort_lst,pop_zd,sxmc)
            
            return {'url':'yw_pzsj/yw_pzsj_001/jkdx_bbdb.html','leftJkdxRs':json.dumps(leftJkdxRs),'rightJkdxRs':json.dumps(rightJkdxRs)}
        elif lx == 'fxgz':
            # 获取临时表内容
            leftFxgzJbxx = ModSql.yw_pzsj_001.execute_sql_dict(db,"get_fxgz_jbxx",{'table_name':['gl_hsxxb_ls'], 'id':id})
            # 获取正式表内容
            rightFxgzJbxx = ModSql.yw_pzsj_001.execute_sql_dict(db,"get_fxgz_jbxx",{'table_name':['gl_hsxxb'], 'id':id})
            mc_dic = {'hsmc':'规则函数名称', 'zwmc':'中文名称', 'ms':'规则描述','zt':'状态'}
            sort_lst = ['hsmc','zwmc','ms','zt']
            pop_zd = ['id','diff']
            # 排序字段
            sxmc = 'sxmc'
            # 比对数据
            leftFxgzRs,rightFxgzRs = bbdb_detail(leftFxgzJbxx,rightFxgzJbxx,mc_dic,sort_lst,pop_zd,sxmc)
            # 获取规则代码
            # 获取临时表内容
            leftGzdmJbxx = ModSql.yw_pzsj_001.execute_sql_dict(db,"get_fxgz_fxgz",{'table_name_blob':['gl_blob_ls'],'table_name_hsxx':['gl_hsxxb_ls'], 'id':id,'lb':'gz'})
            # 获取正式表内容
            rightGzdmJbxx = ModSql.yw_pzsj_001.execute_sql_dict(db,"get_fxgz_fxgz",{'table_name_blob':['gl_blob'], 'table_name_hsxx':['gl_hsxxb'],'id':id,'lb':'gz'})
            
            leftGzdmNr = "''"
            rightGzdmNr= "''"
            if leftGzdmJbxx:
                leftGzdmNr = str(pickle.loads( leftGzdmJbxx[0]['nr'].read() ))
            if rightGzdmJbxx:
                rightGzdmNr = str(pickle.loads( rightGzdmJbxx[0]['nr'].read()) )
            # 传入参数
            # 获取规则代码
            # 获取临时表内容
            leftCrcsJbxx = ModSql.yw_pzsj_001.execute_sql_dict(db,"get_fxgz_crcs",{'table_name':['gl_crcs_ls'], 'id':id,'sslb':'1'})
            # 获取正式表内容
            rightCrcsJbxx = ModSql.yw_pzsj_001.execute_sql_dict(db,"get_fxgz_crcs",{'table_name':['gl_crcs'], 'id':id,'sslb':'1'})
            # 比对数据
            leftCrcsRs,rightCrcsRs = get_xxbd(leftCrcsJbxx,rightCrcsJbxx)
            
            return {'url':'yw_pzsj/yw_pzsj_001/fxgz_bbdb.html','leftFxgzRs':json.dumps(leftFxgzRs),'rightFxgzRs':json.dumps(rightFxgzRs),'leftGzdmNr':json.dumps(leftGzdmNr), 'rightGzdmNr':json.dumps(rightGzdmNr),'leftCrcsRs':json.dumps(leftCrcsRs), 'rightCrcsRs':json.dumps(rightCrcsRs)}
        elif lx == 'xydz':
            # 获取临时表内容
            leftXydzJbxx = ModSql.yw_pzsj_001.execute_sql_dict(db,"get_xydz_jbxx",{'table_name':['gl_hsxxb_ls'], 'id':id})
            # 获取正式表内容
            rightXydzJbxx = ModSql.yw_pzsj_001.execute_sql_dict(db,"get_xydz_jbxx",{'table_name':['gl_hsxxb'], 'id':id})
            mc_dic = {'hsmc':'规则函数名称', 'zwmc':'中文名称', 'ms':'规则描述','zt':'状态'}
            sort_lst = ['hsmc','zwmc','ms','zt']
            pop_zd = ['id','diff']
            # 排序字段
            sxmc = 'sxmc'
            # 比对数据
            leftXydzRs,rightXydzRs = bbdb_detail(leftXydzJbxx,rightXydzJbxx,mc_dic,sort_lst,pop_zd,sxmc)
            # 获取规则代码
            # 获取临时表内容
            leftGzdmJbxx = ModSql.yw_pzsj_001.execute_sql_dict(db,"get_fxgz_fxgz",{'table_name_blob':['gl_blob_ls'],'table_name_hsxx':['gl_hsxxb_ls'], 'id':id,'lb':'dz'})
            # 获取正式表内容
            rightGzdmJbxx = ModSql.yw_pzsj_001.execute_sql_dict(db,"get_fxgz_fxgz",{'table_name_blob':['gl_blob'], 'table_name_hsxx':['gl_hsxxb'],'id':id,'lb':'dz'})
            
            leftGzdmNr = "''"
            rightGzdmNr= "''"
            if leftGzdmJbxx:
                leftGzdmNr = str(pickle.loads( leftGzdmJbxx[0]['nr'].read() ))
            if rightGzdmJbxx:
                rightGzdmNr = str(pickle.loads( rightGzdmJbxx[0]['nr'].read()) )
            # 传入参数
            # 获取规则代码
            # 获取临时表内容
            leftCrcsJbxx = ModSql.yw_pzsj_001.execute_sql_dict(db,"get_fxgz_crcs",{'table_name':['gl_crcs_ls'], 'id':id,'sslb':'2'})
            # 获取正式表内容
            rightCrcsJbxx = ModSql.yw_pzsj_001.execute_sql_dict(db,"get_fxgz_crcs",{'table_name':['gl_crcs'], 'id':id,'sslb':'2'})
            # 比对数据
            leftCrcsRs,rightCrcsRs = get_xxbd(leftCrcsJbxx,rightCrcsJbxx)
            
            return {'url':'yw_pzsj/yw_pzsj_001/xydz_bbdb.html','leftXydzRs':json.dumps(leftXydzRs),'rightXydzRs':json.dumps(rightXydzRs),'leftGzdmNr':json.dumps(leftGzdmNr), 'rightGzdmNr':json.dumps(rightGzdmNr),'leftCrcsRs':json.dumps(leftCrcsRs), 'rightCrcsRs':json.dumps(rightCrcsRs)}
        elif lx == 'sjcjpz':
            # 获取左侧适用对象
            leftSydxRs = get_sydx(zbid,['gl_crcs_ls'],['gl_dxcjpz_ls'],['gl_dxdy_ls'],['gl_zjxx_ls'],id,['gl_csdyb_ls'],db)
            # 获取右侧适用对象
            rightSydxRs = get_sydx(zbid,['gl_crcs'],['gl_dxcjpz'],['gl_dxdy'],['gl_zjxx'],id,['gl_csdyb'],db)
            # 比对数据
            syl,syr = get_xxbd(leftSydxRs['rows'],rightSydxRs['rows'])
            leftSydxRs['rows'] = syl
            rightSydxRs['rows'] = syr
            # 获取临时表适用对象id
            left_sydxid = [s['id'] for s in syl]
            # 获取正式表适用对象id
            right_sydxid = [s['id'] for s in syr]
            
            # 获取对象采集配置基本信息
            # 获取临时表内容
            leftDxcjpzJbxx = ModSql.yw_pzsj_001.execute_sql_dict(db,"get_dxcjpz",{'table_name':['gl_cjpzb_ls'], 'id':id})
            # 获取正式表内容
            rightDxcjpzJbxx = ModSql.yw_pzsj_001.execute_sql_dict(db,"get_dxcjpz",{'table_name':['gl_cjpzb'], 'id':id})
            mc_dic = {'mc':'名称', 'ms':'描述', 'cjlb':'采集类别','cjzb':'采集指标','lx':'类型','zdfqpz':'Crontab配置','zdfqpzsm':'Crontab配置说明','sfkbf':'是否可并发'}
            sort_lst = ['mc','ms','cjlb','lx','zdfqpz','zdfqpzsm','sfkbf']
            pop_zd = ['id']
            # 排序字段
            sxmc = 'sxmc'
            # 比对数据
            leftDxcjpzRs,rightDxcjpzRs = bbdb_detail(leftDxcjpzJbxx,rightDxcjpzJbxx,mc_dic,sort_lst,pop_zd,sxmc)
            lzbid = leftDxcjpzJbxx[0]['zbid'] if leftDxcjpzJbxx else ''
            rzbid = rightDxcjpzJbxx[0]['zbid'] if rightDxcjpzJbxx else ''
            left_crcs = []
            right_crcs = []
            # 获取传入参数
            if left_sydxid:
                lcs = {'table_name_crcs':['GL_CRCS_LS'],'table_name_csdyb':['GL_CSDYB_LS'],'table_name_dxcjpz':['GL_DXCJPZ_LS'],'table_name_dxdy':['GL_DXDY_LS'], 'zbid':lzbid, 'sydxid':left_sydxid}
                left_crcs = ModSql.yw_pzsj_001.execute_sql_dict(db,"get_zb_crcs",lcs)
            if right_sydxid:
                rcs = {'table_name_crcs':['GL_CRCS'],'table_name_csdyb':['GL_CSDYB'],'table_name_dxcjpz':['GL_DXCJPZ'],'table_name_dxdy':['GL_DXDY'], 'zbid':rzbid, 'sydxid':right_sydxid}
                right_crcs = ModSql.yw_pzsj_001.execute_sql_dict(db,"get_zb_crcs",rcs)
            leftCrcsRs,rightCrcsRs = get_xxbd(left_crcs,right_crcs)
            return {'url':'yw_pzsj/yw_pzsj_001/sjcjpz_bbdb.html','leftSydxRs':json.dumps(leftSydxRs),'rightSydxRs':json.dumps(rightSydxRs),'leftDxcjpzRs':json.dumps(leftDxcjpzRs),'rightDxcjpzRs':json.dumps(rightDxcjpzRs),'leftCrcsRs':json.dumps(leftCrcsRs),'rightCrcsRs':json.dumps(rightCrcsRs)}
        elif lx == 'jkfxpz':
            # 获取进程配置基本信息
            # 获取临时表内容
            leftJcpzJbxx = ModSql.yw_pzsj_001.execute_sql_dict(db,"get_jcpz",{'table_name_jkfxpz':['gl_jkfxpz_ls'],'table_name_hsxxb':['gl_hsxxb_ls'], 'id':id})
            # 获取正式表内容
            rightJcpzJbxx = ModSql.yw_pzsj_001.execute_sql_dict(db,"get_jcpz",{'table_name_jkfxpz':['gl_jkfxpz'],'table_name_hsxxb':['gl_hsxxb'], 'id':id})
            mc_dic = {'mc':'名称', 'fxgz':'分析规则', 'yjjb':'预警级别','zdfqpz':'Crontab配置','zdfqpzsm':'Crontab配置说明','sfkbf':'是否可并发','ms':'描述','zt':'状态'}
            sort_lst = ['mc','fxgz','yjjb','zdfqpz','zdfqpzsm','sfkbf','ms','zt']
            pop_zd = ['id','diff']
            # 排序字段
            sxmc = 'sxmc'
            # 比对数据
            leftJcpzRs,rightJcpzRs = bbdb_detail(leftJcpzJbxx,rightJcpzJbxx,mc_dic,sort_lst,pop_zd,sxmc)
            # 获取正式表规则id
            zs_gzid = ModSql.yw_pzsj_001.execute_sql_dict(db,"get_gzid",{'id':id,'table_name_jkfxpz':['gl_jkfxpz']})
            if zs_gzid:
                zs_gzid = zs_gzid[0].get('gzid')
            else:
                zs_gzid = ''
            # 获取临时表规则id
            ls_gzid = ModSql.yw_pzsj_001.execute_sql_dict(db,"get_gzid",{'id':id,'table_name_jkfxpz':['gl_jkfxpz_ls']})
            if ls_gzid:
                ls_gzid = ls_gzid[0].get('gzid')
            else:
                ls_gzid = ''
            # 获取监控配置-分析规则参数
            # 获取临时表内容
            leftFxgzcsJbxx = ModSql.yw_pzsj_001.execute_sql_dict(db,"get_jcpz_fxgzcs",{'table_name_crcs':['gl_crcs_ls'],'table_name_csdyb':['gl_csdyb_ls'], 'gzid':ls_gzid,'id':id})
            # 获取正式表内容
            rightFxgzcsJbxx = ModSql.yw_pzsj_001.execute_sql_dict(db,"get_jcpz_fxgzcs",{'table_name_crcs':['gl_crcs'],'table_name_csdyb':['gl_csdyb'], 'gzid':zs_gzid,'id':id})
            # 比对数据
            leftFxgzcsRs,rightFxgzcsRs = get_xxbd(leftFxgzcsJbxx,rightFxgzcsJbxx)
            
            # 获取相应动作
            # 获取临时表内容
            leftJcpzXydz = get_jkpz_xydz('gl_xydzpz_ls','gl_hsxxb_ls','gl_jkfxpz_ls','gl_dzzxzj_ls','gl_zjxx_ls',id,db)
            # 获取正式表内容
            rightJcpzXydz = get_jkpz_xydz('gl_xydzpz','gl_hsxxb','gl_jkfxpz','gl_dzzxzj','gl_zjxx',id,db)
            # 比对数据
            leftJcpzXydzRs,rightJcpzXydzRs = get_xxbd(leftJcpzXydz,rightJcpzXydz)
            
            # 获取监控配置-响应动作参数
            # 获取正式表内容
            rightJkpzXydzcs = get_jkpz_xydzcs('gl_xydzpz','gl_hsxxb','gl_csdyb','gl_crcs',id,db)
            # 获取临时表内容
            leftJkpzXydzcs = get_jkpz_xydzcs('gl_xydzpz_ls','gl_hsxxb_ls','gl_csdyb_ls','gl_crcs_ls',id,db)
            # 比对数据
            leftJkpzXydzcsRs,rightJkpzXydzcsRs = get_xxbd(leftJkpzXydzcs,rightJkpzXydzcs)
            
            return {'url':'yw_pzsj/yw_pzsj_001/jkpz_bbdb.html','leftJcpzRs':json.dumps(leftJcpzRs),'rightJcpzRs':json.dumps(rightJcpzRs),'leftFxgzcsRs':json.dumps(leftFxgzcsRs),'rightFxgzcsRs':json.dumps(rightFxgzcsRs),
            'leftJcpzXydzRs':json.dumps(leftJcpzXydzRs),'rightJcpzXydzRs':json.dumps(rightJcpzXydzRs),'leftJkpzXydzcsRs':json.dumps(leftJkpzXydzcsRs),'rightJkpzXydzcsRs':json.dumps(rightJkpzXydzcsRs)}
        elif lx == 'yzjycspz':
            # 获取阈值校验参数基本信息
            # 获取临时表内容
            leftYzjycspzJbxx = ModSql.yw_pzsj_001.execute_sql_dict(db,"get_yzjycs",{'table_name_yzjycspz':['gl_yzjycspz_ls'], 'id':id})
            # 获取正式表内容
            rightYzjycspzJbxx = ModSql.yw_pzsj_001.execute_sql_dict(db,"get_yzjycs",{'table_name_yzjycspz':['gl_yzjycspz'], 'id':id})
            # 比对数据
            leftYzjycspzRs,rightYzjycspzRs = get_xxbd(leftYzjycspzJbxx,rightYzjycspzJbxx)
            
            return {'url':'yw_pzsj/yw_pzsj_001/yzjy_cspz_bbdb.html','leftYzjycspzRs':json.dumps(leftYzjycspzRs),'rightYzjycspzRs':json.dumps(rightYzjycspzRs)}
            
        elif lx == 'yzjypz':
            # 获取阈值校验基本信息
            # 获取临时表内容
            leftYzjycspz = ModSql.yw_pzsj_001.execute_sql_dict(db,"get_yzjy_jbxx",{'table_name_yzjypz':['gl_yzjypz_ls'], 'id':id})
            # 获取正式表内容
            rightYzjycspz = ModSql.yw_pzsj_001.execute_sql_dict(db,"get_yzjy_jbxx",{'table_name_yzjypz':['gl_yzjypz'], 'id':id})
            mc_dic = {'ywmc':'业务名称', 'ywbm':'业务编码', 'wjlx':'文件类型'}
            sort_lst = ['ywmc','ywbm','wjlx']
            pop_zd = []
            # 排序字段
            sxmc = 'sxmc'
            # 比对数据
            leftYzjycspzRs,rightYzjycspzRs = bbdb_detail(leftYzjycspz,rightYzjycspz,mc_dic,sort_lst,pop_zd,sxmc)
            
            # 获取阈值校验业务信息
            # 获取临时表内容
            leftYzjyRs = get_yzjy_ywxx('gl_yzjypz_ls',id,'gl_blob_ls',db)
            # 获取正式表内容
            rightYzjyRs = get_yzjy_ywxx('gl_yzjypz',id,'gl_blob',db)
            return {'url':'yw_pzsj/yw_pzsj_001/yzjy_ywpz_bbdb.html','leftYzjycspzRs':json.dumps(leftYzjycspzRs),'rightYzjycspzRs':json.dumps(rightYzjycspzRs),'leftYzjyRs':json.dumps(leftYzjyRs),'rightYzjyRs':json.dumps(rightYzjyRs)}
        elif lx == 'jcxxpz':
            # 获取进程配置信息
            # 获取临时表内容
            leftJcpz = ModSql.yw_pzsj_001.execute_sql_dict(db,"get_jcxxpz_jc",{'table_name_jcxxpz':['gl_jcxxpz_ls'], 'id':id})
            # 获取正式表内容
            rightJcpz = ModSql.yw_pzsj_001.execute_sql_dict(db,"get_jcxxpz_jc",{'table_name_jcxxpz':['gl_jcxxpz'], 'id':id})
            mc_dic = {'jcmc':'进程名称', 'jcsl':'进程数量', 'ckml':'查看命令', 'qdlx':'启动类型', 'zdzj':'指定主机', 'zt':'状态'}
            sort_lst = ['jcmc','jcsl','ckml','qdlx','zdzj','zt']
            pop_zd = []
            # 排序字段
            sxmc = 'sxmc'
            # 比对数据
            leftJcpzRs,rightJcpzRs = bbdb_detail(leftJcpz,rightJcpz,mc_dic,sort_lst,pop_zd,sxmc)
            return {'url':'yw_pzsj/yw_pzsj_001/jcpz_bbdb.html','leftJcpzRs':json.dumps(leftJcpzRs),'rightJcpzRs':json.dumps(rightJcpzRs)}
def dr_submit_service(id_dic, drlx,drms,bzxx,fhr,fhrmm,drlsid):
    """
    # 将临时表数据转到正式表
    """
    data = {'state':True,'msg':'导入成功'}
    #id_dic = {'jkdx_ids':jkdx_ids,'fxgz_ids':fxgz_ids,'xydz_ids':xydz_ids,'sjcjpz_ids':sjcjpz_ids,'jkfxpz_ids':jkfxpz_ids,'yzjycspz_ids':yzjycspz_ids,'yzjypz_ids':yzjypz_ids,'jcxxpz_ids':jcxxpz_ids}
    if type(id_dic) == str:
        id_dic = json.loads(id_dic)
    with sjapi.connection() as db:
        sq_gnmc = '维护系统_导入'
        # 校验复核人
        hyxx_dic = { 'hydm': fhr, 'mm':fhrmm, 'jsdm': FHR_JSDM,'sq_gnmc': sq_gnmc, 'czpt': 'kf','sqgndm':'','szcz': sq_gnmc + '复核人授权' }
        ret,msg = check_fhr( db, hyxx_dic )
        if ret == False:
            msg = msg
            return {'state':False,'msg':msg}
        # 校验阈值校验参数和阈值校验业务,进程信息，数据采集配置，监控配置是否有重复数据
        ret,msg = check_yz( db, id_dic )
        if ret == False:
            msg = msg
            return {'state':False,'msg':msg}
        # 导入监控对象
        dr_jbxx(id_dic,'gl_dxdy','jkdx_ids',db,'')
        # 导入分析规则
        dr_jbxx(id_dic,'gl_hsxxb','fxgz_ids',db,'gz')
        # 导入分析规则--规则代码
        dr_blob({'table_name1':['gl_blob'],'table_name2':['gl_blob_ls'],'table_name3':['gl_hsxxb_ls'],'table_name4':['gl_hsxxb'],'id':id_dic.get('fxgz_ids')},db)
        # 导入分析规则--传入参数
        dr_crcs({'table_name1':['gl_crcs'],'table_name2':['gl_crcs_ls'],'sslb':'1','id':id_dic.get('fxgz_ids')},db)
        # 导入响应动作
        dr_jbxx(id_dic,'gl_hsxxb','xydz_ids',db,'dz')
        # 导入响应动作--规则代码
        dr_blob({'table_name1':['gl_blob'],'table_name2':['gl_blob_ls'],'table_name3':['gl_hsxxb_ls'],'table_name4':['gl_hsxxb'],'id':id_dic.get('xydz_ids')},db)
        # 导入响应动作--传入参数
        dr_crcs({'table_name1':['gl_crcs'],'table_name2':['gl_crcs_ls'],'sslb':'2','id':id_dic.get('xydz_ids')},db)
        # 导入对象采集配置
        ret = dr_jbxx(id_dic,'gl_cjpzb','sjcjpz_ids',db,'','1')
        # 如果若是基本信息跳过不予处理，该环节也不做
        if ret != False:
            par = {'table_name_csdyb':['gl_csdyb'],'table_name_csdyb_ls':['gl_csdyb_ls'],'table_name_dxcjpz':['gl_dxcjpz'],'table_name_dxcjpz_ls':['gl_dxcjpz_ls'],
            'table_name_jhrwb_ls':['gl_jhrwb_ls'],'table_name_jhrwb':['gl_jhrwb'],'sscjpzid':id_dic.get('sjcjpz_ids'),
            'table_name_zjxx':['gl_zjxx'],'table_name_zjxx_ls':['gl_zjxx_ls'],'rwlx':'cj'}
            if id_dic.get('sjcjpz_ids'):
                # 导入适用对象
                dr_sydx(par,db)
        # 导入监控分析配置
        ret = dr_jbxx(id_dic,'gl_jkfxpz','jkfxpz_ids',db,'')
        # 如果若是基本信息跳过不予处理，该环节也不做
        if ret != False:
            # 导入监控配置
            dr_jkpz(id_dic,db)
        # 导入阈值校验参数信息
        ret = dr_jbxx(id_dic,'gl_yzjycspz','yzjycspz_ids',db,'')
        # 导入阈值校验业务配置信息
        ret = dr_jbxx(id_dic,'gl_yzjypz','yzjypz_ids',db,'')
        if ret != False:
            # 阈值校验配置-配置信息导入
            dr_yzjypz(id_dic,db)
        # 进程配置导入
        ret = dr_jbxx(id_dic,'gl_jcxxpz','jcxxpz_ids',db,'','1')
        if ret != False:
            # 导入主机信息
            dr_zjxx(id_dic,db)
        # 更新导入流水
        sql_dic = {'id':drlsid,'czr':get_sess_hydm(),'czsj':get_strftime(),'bz':bzxx,'czms':drms,'fhr':fhr,'zt':'1'}
        ModSql.yw_pzsj_001.execute_sql( db,"update_drls",sql_dic)
        # 操作日志登记
        nr = '导入类型：%s，导入描述：%s，备注信息：%s，导入流水ID：%s' % ( 'wh',drms,bzxx,drlsid )
        ins_czrz( db, nr ,pt = 'wh' , gnmc = '导入' )
        # 删除临时表
        drop_table(db)
    return data

def check_yz( db, id_dic ):
    """
    # 校验阈值校验参数和阈值校验业务是否有重复数据
    # 校验进程信息是否有重复数据
    # 校验数据采集配置，监控配置
    """
    ret = True
    msg = ''
    if id_dic.get('jkdx_ids'):
        # 查询所有的监控对象
        jkdx_list = ModSql.yw_pzsj_001.execute_sql_dict(db,"get_jkdx_all",{'id_list':id_dic.get('jkdx_ids')})
        for jkdx in jkdx_list:
            # 查询正式表中是否有重复数据
            count = ModSql.yw_pzsj_001.execute_sql(db,"check_dxbm",{'dxlx':jkdx.get('sslbbm'),'dxbm':jkdx.get('dxbm'),'id':jkdx.get('id')})[0].count
            if count > 0:
                ret = False
                msg = '目标库监控对象【%s】已经存在,但id不同,将目标库内容删除后重新导入！'%(jkdx.get('name'))
                return ret,msg
    if id_dic.get('sjcjpz_ids'):
        # 查询所有的数据采集配置
        cj_list = ModSql.yw_pzsj_001.execute_sql_dict(db,"get_sjcjpz",{'table_name':["gl_cjpzb_ls"],'id_list':id_dic.get('sjcjpz_ids')})
        for cj in cj_list:
            # 查询正式表中是否有重复数据
            count = ModSql.yw_pzsj_001.execute_sql(db,"check_cjmc",{'mc':cj.get('name'),'id':cj.get('id')})[0].count
            if count > 0:
                ret = False
                msg = '目标库采集名称【%s】已经存在,但id不同,将目标库内容删除后重新导入！'%(cj.get('name'))
                return ret,msg
    if id_dic.get('jkfxpz_ids'):
        # 查询所有的监控分析配置
        jkfx_list = ModSql.yw_pzsj_001.execute_sql_dict(db,"get_jkfxpz",{'table_name':["gl_jkfxpz_ls"],'id_list':id_dic.get('jkfxpz_ids')})
        for jkfx in jkfx_list:
            # 查询正式表中是否有重复数据
            count = ModSql.yw_pzsj_001.execute_sql(db,"check_jkfxpzmc",{'mc':jkfx.get('name'),'id':jkfx.get('id')})[0].count
            if count > 0:
                ret = False
                msg = '目标库监控分析配置名称【%s】已经存在,但id不同,将目标库内容删除后重新导入！'%(jkfx.get('name'))
                return ret,msg
    # 查询临时表中所有的阈值校验参数
    if id_dic.get('yzjycspz_ids'):
        cs_list = ModSql.yw_pzsj_001.execute_sql_dict(db,"get_yzjycspz",{'table_name':["gl_yzjycspz_ls"],'id_list':id_dic.get('yzjycspz_ids')})
        for cs in cs_list:
            # 查询正式表中是否有重复数据
            count = ModSql.yw_pzsj_001.execute_sql(db,"check_yzjycspz",{'csdm':cs.get('name'),'ssywid':cs.get('ssywid'),'id':cs.get('id')})[0].count
            if count > 0:
                ret = False
                msg = '目标库的阈值校验业务【%s】下已存在参数【%s】,但id不同,将目标库参数删除后重新导入！'%(cs.get('ywmc'),cs.get('name'))
                return ret,msg
    if id_dic.get('yzjypz_ids'):
        # 查询临时表中所有的阈值校验业务
        yw_list = ModSql.yw_pzsj_001.execute_sql_dict(db,"get_yzjypz",{'table_name':["gl_yzjypz_ls"],'id_list':id_dic.get('yzjypz_ids')})
        for yw in yw_list:
            # 查询正式表中是否有重复数据
            count = ModSql.yw_pzsj_001.execute_sql(db,"check_yzjypz",{'ssywid':yw.get('ssywid'),'id':yw.get('id')})[0].count
            if count > 0:
                ret = False
                msg = '目标库的阈值校验业务【%s】已存在,但id不同,将目标库内容删除后重新导入！'%(yw.get('name'))
                return ret,msg
    if id_dic.get('jcxxpz_ids'):
        # 查询所有的进程信息
        jc_list = ModSql.yw_pzsj_001.execute_sql_dict(db,"get_jcxxpz",{'table_name':["gl_jcxxpz_ls"],'id_list':id_dic.get('jcxxpz_ids')})
        for jc in jc_list:
            # 查询正式表中是否有重复数据
            count = ModSql.yw_pzsj_001.execute_sql(db,"get_jclxcount",{'ip':jc.get('sszj_ip'),'txwjmc':jc.get('txwjmc'),'id':jc.get('id')})[0].count
            if count > 0:
                ret = False
                msg = '目标库主机【%s】下已存在进程【%s】,但id不同,将目标库内容删除后重新导入！'%(jc.get('sszj_ip'),jc.get('name'))
                return ret,msg
    return ret,msg
def drop_table(db):
    # 查询存在的临时表
    l = ModSql.yw_pzsj_002.execute_sql_dict(db,"get_table_ls",{'table_name':table_ls})
    table_name_ls = [llt['table_name'] for llt in l]
    # 删除临时表
    for dic in table_name_ls:
        ModSql.common.execute_sql(db,"drop_table",{'tname_lst':[dic]})
            
def dr_zjxx(id_dic,db):
    """
    # 导入主机信息
    """
    # 获取进程配置的主机Ip
    ip_lst = ModSql.yw_pzsj_001.execute_sql_dict(db, "get_jcxxpz_zjip",{'table_name_jcxxpz':['gl_jcxxpz'],'jcpzid':id_dic.get('jcxxpz_ids')})
    sszjip = [i['sszjip'] for i in ip_lst]
    # 查询主机ip在正式表中是否存在
    count = ModSql.yw_pzsj_001.execute_sql(db, "get_dr_zjxxcount",{'table_name_zjxx':['gl_zjxx'],'zdzjip':sszjip})[0].count   
    if count == 0:
        ModSql.yw_pzsj_001.execute_sql(db, "insert_dr_zjxx",{'table_name_zjxx':['gl_zjxx'],'table_name_zjxx_ls':['gl_zjxx_ls'],'zdzjip':sszjip})
        
def dr_yzjypz(id_dic,db):
    """
    # 阈值校验配置-配置信息导入
    """
    colum_name = ['kkmxsqlid','lsdrid','kzjyid','kkmxcxsqlid','yc_allpass_sqlid','yc_allcancel_sqlid','yc_single_sqlid']
    param = {'table_name_blob':['gl_blob'], 'table_name_blob_ls':['gl_blob_ls'], 'colum_name':[], 'table_name_yzjypz':['gl_yzjypz'], 'table_name_yzjypz_ls':['gl_yzjypz_ls'],'ywpzid':id_dic.get('yzjypz_ids')}
    for colum in colum_name:
        param['colum_name'] = [colum]
        # 删除表内容
        ModSql.yw_pzsj_001.execute_sql(db, "del_blob_nr",param)
    for colum in colum_name:
        param['colum_name'] = [colum]
        # 添加表内容
        ModSql.yw_pzsj_001.execute_sql(db, "insert_blob_nr",param)

def dr_jkpz(id_dic,db):
    """
    # 导入监控配置
    """
    # 删除计划任务
    ModSql.yw_pzsj_001.execute_sql(db, "del_dr_jcpz_jhrw",{'table_name_jhrwb_ls':['gl_jhrwb'], 'rwlx':'fx', 'jcpzid':id_dic.get('jkfxpz_ids')})
    # 插入到计划任务表
    ModSql.yw_pzsj_001.execute_sql(db, "insert_dr_jcpz_jhrw",{'table_name_jhrwb_ls':['gl_jhrwb_ls'],'table_name_jhrwb':['gl_jhrwb'], 'rwlx':'fx', 'jcpzid':id_dic.get('jkfxpz_ids')})
    jhrw_list = ModSql.yw_pzsj_001.execute_sql_dict(db, "get_dr_jhrw_qy",{'table_name_jhrwb':['gl_jhrwb'],'rwlx':'fx','dxcjpzid':id_dic.get('jkfxpz_ids'),'zt':'1'})
    # 导入当日执行计划任务
    for l in jhrw_list:
        del_waitexec_task(l.get('id'),db)
        ins_waitexec_task(l.get('id'),db)
    # 分析规则参数导入
    # 删除规则参数
    ModSql.yw_pzsj_001.execute_sql(db, "del_dr_jcpz_fxgzcs",{'table_name_csdyb':['gl_csdyb'], 'jcpzid':id_dic.get('jkfxpz_ids')})
    # 查询进程配置分析规则参数
    csid_lst = ModSql.yw_pzsj_001.execute_sql_dict(db, "get_dr_jcpz_fxgzcs",{'table_name_csdyb_ls':['gl_csdyb_ls'], 'jcpzid':id_dic.get('jkfxpz_ids')})
    csdybid = [csid['id'] for csid in csid_lst]
    # 插入参数对应表
    if csdybid:
        ModSql.yw_pzsj_001.execute_sql(db, "insert_dr_jcpz_fxgzcs",{'table_name_csdyb':['gl_csdyb'],'table_name_csdyb_ls':['gl_csdyb_ls'], 'csdybid':csdybid})
    
    # 响应动作导入
    # 删除动作执行主机
    ModSql.yw_pzsj_001.execute_sql(db, "del_dr_jcpz_dzzxzj",{'table_name_dzzxzj':['gl_dzzxzj'], 'table_name_xydzpz':['gl_xydzpz'], 'jcpzid':id_dic.get('jkfxpz_ids')})
    # 删除响应动作参数信息
    ModSql.yw_pzsj_001.execute_sql(db, "del_dr_jcpz_xydzcs",{'table_name_csdyb':['gl_csdyb'],'table_name_xydzpz':['gl_xydzpz'], 'jcpzid':id_dic.get('jkfxpz_ids')})
    # 删除响应动作配置
    ModSql.yw_pzsj_001.execute_sql(db, "del_dr_jcpz_xydzpz",{'table_name_xydzpz':['gl_xydzpz'], 'jcpzid':id_dic.get('jkfxpz_ids')})
    
    # 将临时表中的响应动作配置插入到正式表
    # 获取响应动作配置
    xydzpz_lst = ModSql.yw_pzsj_001.execute_sql(db, "get_dr_jcpz_xydzpz",{'table_name_xydzpz':['gl_xydzpz_ls'], 'jcpzid':id_dic.get('jkfxpz_ids')})
    xydzpzid = [xy['id'] for xy in xydzpz_lst]
    dzzxzjid_lst = []
    # 插入响应动作配置
    if xydzpzid:
        ModSql.yw_pzsj_001.execute_sql(db, "insert_dr_jcpz_xydzpz",{'table_name_xydzpz':['gl_xydzpz'],'table_name_xydzpz_ls':['gl_xydzpz_ls'], 'xydzpzid':xydzpzid})
        # 获取参数对应表
        csdyb_lst = ModSql.yw_pzsj_001.execute_sql(db, "get_dr_jcpz_csdyb",{'table_name_csdyb_ls':['gl_csdyb_ls'], 'xydzpzid':xydzpzid})
        csdybid = [cs['id'] for cs in csdyb_lst]
        # 插入参数对应表
        ModSql.yw_pzsj_001.execute_sql(db, "insert_dr_jcpz_csdyb",{'table_name_csdyb':['gl_csdyb'],'table_name_csdyb_ls':['gl_csdyb_ls'], 'csdybid':csdybid})
        # 获取执行主机
        dzzxzjid_lst = ModSql.yw_pzsj_001.execute_sql(db, "get_dr_jcpz_zxzj",{'table_name_dzzxzj_ls':['gl_dzzxzj_ls'], 'xydzpzid':xydzpzid})
        dzzxzjid = [dz['id'] for dz in dzzxzjid_lst]
        # 插入执行主机
        ModSql.yw_pzsj_001.execute_sql(db, "insert_dr_jcpz_zxzj",{'table_name_dzzxzj_ls':['gl_dzzxzj_ls'], 'table_name_dzzxzj':['gl_dzzxzj'], 'dzzxzjid':dzzxzjid})
        
        # 查看动作执行主机是否在主机信息表中存在，若不存在，插入到主机信息表中
        zdzjip = [dx['zjip'] for dx in dzzxzjid_lst]
        # 查询主机ip在正式表中是否存在
        count = ModSql.yw_pzsj_001.execute_sql(db, "get_dr_zjxxcount",{'table_name_zjxx':['gl_zjxx'],'zdzjip':zdzjip})[0].count
        if count == 0:
            ModSql.yw_pzsj_001.execute_sql(db, "insert_dr_zjxx",{'table_name_zjxx':['gl_zjxx'],'table_name_zjxx_ls':['gl_zjxx_ls'],'zdzjip':zdzjip})
    
def dr_sydx(param,db):
    """
    # 导入适用对象
    """
    # 删除参数对应表
    ModSql.yw_pzsj_001.execute_sql(db, "del_dr_csdyb",param)
    # 删除计划任务表中的信息
    ModSql.yw_pzsj_001.execute_sql(db, "del_dr_jhrw",param)
    # 删除对象采集配置
    ModSql.yw_pzsj_001.execute_sql(db, "del_dr_dxcjpz",param)
    
    # 将临时表中的适用对象插入到正式表
    # 查询对象采集配置表中的ID
    dxcjpz_lst = ModSql.yw_pzsj_001.execute_sql_dict(db, "get_dr_dxcjpz",param)
    dxcjpzid = [dx['id'] for dx in dxcjpz_lst]
    param['dxcjpzid'] = dxcjpzid
    param['zt'] = '1'
    # 循环对象采集配置ID，插入到对象采集配置表中
    ModSql.yw_pzsj_001.execute_sql(db, "insert_dr_dxcjpz",param)
    # 循环对象采集配置ID，插入到计划任务表
    ModSql.yw_pzsj_001.execute_sql(db, "insert_dr_jhrw",param)
    # 循环对象采集配置ID，查询计划任务表信息
    jhrw_list = ModSql.yw_pzsj_001.execute_sql_dict(db, "get_dr_jhrw_qy",param)
    # 导入当日执行计划任务
    for l in jhrw_list:
        del_waitexec_task(l.get('id'),db)
        ins_waitexec_task(l.get('id'),db)
    # 循环对象采集配置表ID，查询参数对应表信息
    csdyb_lst = ModSql.yw_pzsj_001.execute_sql_dict(db, "get_dr_csdyb",param)
    csdybid = [cs['id'] for cs in csdyb_lst]
    param['csdybid'] = csdybid
    # 循环参数对应表_临时ID，插入到参数对应表
    if csdybid:
        ModSql.yw_pzsj_001.execute_sql(db, "insert_dr_csdyb",param)
    
    # 查询对象采集配置表中的主机IP在主机信息表中是否有，若没有，从临时表中查询并插入
    zdzjip = [dx['zdzjip'] for dx in dxcjpz_lst]
    param['zdzjip'] = zdzjip
    # 查询主机ip在正式表中是否存在
    count = ModSql.yw_pzsj_001.execute_sql(db, "get_dr_zjxxcount",param)[0].count
    if count == 0:
        ModSql.yw_pzsj_001.execute_sql(db, "insert_dr_zjxx",param)
    
def dr_crcs(param,db):
    """
    # 导入传入参数表的内容
    """
    if param.get('id') == None:
        return
    # 将正式表中的动作代码删除
    ModSql.yw_pzsj_001.execute_sql(db, "del_dr_crcs",param)
    # 将临时表中的动作代码插入到正式表
    ModSql.yw_pzsj_001.execute_sql(db, "insert_dr_crcs",param)
    # 原始数据的获取
    ModSql.yw_pzsj_001.execute_sql(db, "get_dr_crcs",param)
    
    
def dr_blob(param,db):
    """
    # 导入blob表的内容
    """
    if param.get('id') == None:
        return
    # 将正式表中的动作代码删除
    ModSql.yw_pzsj_001.execute_sql(db, "del_dr_sj",param)
    # 将临时表中的动作代码插入到正式表
    ModSql.yw_pzsj_001.execute_sql(db, "insert_dr_in",param)
    # 原始数据的获取
    ModSql.yw_pzsj_001.execute_sql(db, "get_dr_in",param)
    
def dr_jbxx(id_dic,table,id_obj,db,param,scbz=None):
    """
    # 将临时表数据转到正式表
    """
    #id_dic = {'jkdx_ids':jkdx_ids,'fxgz_ids':fxgz_ids,'xydz_ids':xydz_ids,'sjcjpz_ids':sjcjpz_ids,'jkfxpz_ids':jkfxpz_ids,'yzjycspz_ids':yzjycspz_ids,'yzjypz_ids':yzjypz_ids,'jcxxpz_ids':jcxxpz_ids}
    if type(id_dic) == str:
        id_dic = json.loads(id_dic)
    # 如果没有对象id，那说明正式表和临时表都没有数据，那么直接返回即可
    if id_dic.get(id_obj) == None or id_dic.get(id_obj) == []:
        return False
    # 监控对象导入
    # 查询临时表监控对象
    ls = ModSql.yw_pzsj_001.execute_sql_dict(db, "get_dr_sj",{'table_name':[table+'_ls'],'id_lst':id_dic.get(id_obj),'lb':param,'scbz':scbz})
    # 如果临时表中没有内容，说明没有可导入的内容，直接返回
    if len(ls) == 0:
        return False
    # 查询正式表监控对象
    zs = ModSql.yw_pzsj_001.execute_sql_dict(db, "get_dr_sj",{'table_name':[table],'id_lst':id_dic.get(id_obj),'lb':param,'scbz':scbz})
    # 比对两个列表
    diff_id = compare_id(ls,zs)
    # 标记正式表中有数据但是删除标志是1，这时候插入的话会主键冲突，所以需要先将其状态改为0，然后在更新数据
    scbz_id_lst = []
    # 插入正式表中不存在的数据
    for diff in diff_id:
        count = 0
        if scbz:
            # 查询在正式表中有没有数据
            count = ModSql.yw_pzsj_001.execute_sql_dict(db, "get_scbz_count",{'table_name':[table],'scbz':'1','id':diff})[0]['count']
        if count:
            # 如果在正式表中有数据，那么将正式表的状态改成0
            ModSql.yw_pzsj_001.execute_sql(db, "update_scbz",{'table_name':[table],'scbz':'0','id':diff})
            scbz_id_lst.append(diff)
        else:
            # 插入数据
            ModSql.yw_pzsj_001.execute_sql(db, "insert_dr_sj",{'table_name_zs':[table],'table_name_ls':[table+'_ls'],'id':diff})
    # 比对两个列表的唯一码,获取id相同，唯一码不同的列表
    diff_wym_id = compare_wym(ls,zs)
    # 加上正式表和临时表都存在但是正式表删除标志是1的数据
    diff_wym_id.extend(scbz_id_lst)
    # 更新正式表的内容
    update_drdx(diff_wym_id,table,ls,db)
        
def update_drdx(diff_id,table,data,db):
    """
    # 根据id更新正式表的内容
    """
    if len(data) == 0:
        return
    # 获取正式表的所有字段名称
    column = list(data[0].keys())
    # 更新数据
    for d in data:
        if d.get('id') in diff_id:
            # 更新数据
            # 需要更新的list
            update_column = []
            # 组织要更新的数据
            for col in column:
                update_column.append((col,d.get(col) if d.get(col) else ''))
            # 更新数据
            ModSql.yw_pzsj_001.execute_sql(db, "update_dr_sj",{'table_name':[table],'col':update_column,'id':d.get('id')})
        
    
def compare_wym(left,right):
    """
    # 比较两个list的wym不同，并返回id的列表
    """
    left_ = copy.deepcopy(left)
    right_ = copy.deepcopy(right)
    left_id = [l['id'] for l in left_]
    right_id = [r['id'] for r in right_]
    # 查找两个临时表存在，正式表也存在的数据
    same_id = list(set(left_id).intersection(set(right_id)))
    # 修改唯一码是None的情况
    for l in left_:
        if l['wym'] == None:
            l['wym'] = get_uuid()
    for r in right_:
        if r['wym'] == None:
            r['wym'] = get_uuid()
    # 比较唯一码
    left_wym = [l['wym'] for l in left_]
    right_wym = [r['wym'] for r in right_]
    right_wym.extend(left_wym)
    # 这个地方在获取唯一码的时候，如果是导入的数据，唯一码是不存在的。
    # 加个判断防止发生异常，以保证将带导入的数据导入到正式表中。
    left_wym_id = {l['wym']:l['id'] for l in left_}
    right_wym_id = {r['wym']:r['id'] for r in right_}
    all_wym_id = dict(left_wym_id, **right_wym_id)
    # 比较两侧唯一码不同的数据
    diff_wym = list(set(right_wym).difference(set(left_wym)))
    # 获取唯一码不同数据对应的id列表
    diff_wym_id = [all_wym_id.get(d) for d in diff_wym]
    # 获取临时表中存在，但唯一码不同的id列表
    diff = list(set(same_id).intersection(set(diff_wym_id)))
    
    return diff
    
def compare_id(left,right):
    """
    # 比较两个list的id不同，并返回id的列表
    """
    left_id = [l['id'] for l in left]
    right_id = [r['id'] for r in right]
    # 若临时表中在，正式表中不在那么执行插入操作
    diff = list(set(left_id).difference(set(right_id)))
    return diff
    
def get_yzjy_ywxx(gl_yzjypz,id,gl_blob,db):
    """
    # 获取阈值校验业务信息
    """
    data = {}
    # 查询业务列表
    yw_lst = ModSql.yw_pzsj_001.execute_sql_dict(db, "data_ssyw")
    fs_lst = ModSql.yw_pzsj_001.execute_sql_dict(db, "data_kzjyfs")
    yw_dict ={}
    fs_dict ={}
    for y in yw_lst:
        yw_dict[y['value']] = y['text']
    for y in fs_lst:
        fs_dict[y['value']] = y['text']
    #业务配置基本信息查询
    sql_para = {'ywpz_id':id}
    nr = ModSql.yw_pzsj_001.execute_sql_dict(db, "yzjypz_select",{'table_name_yzjypz':[gl_yzjypz],'id':id})
    if nr:
        nr = nr[0]
    else:
        return data
    ssyw = nr['ssywid']
    wjlx = nr['wjlx']
    lsdrfs = nr['lsdrfs']
    kzjyfs = nr['kzjyfs']
    #原信息列表所需字段
    ywmc = yw_dict[ssyw]
    #若扩展校验方式为空，则置为空
    if kzjyfs=='' or kzjyfs == None:
        kzjyfs_mc=''
    else:
        kzjyfs_mc = fs_dict[kzjyfs]
    lsdrfs_mc = fs_dict[lsdrfs]
    # sqlid list
    sqlid_name_lst = ['kkmxsqlid','kkmxcxsqlid','kzjyid','lsdrid','YC_ALLPASS_SQLID','YC_ALLCANCEL_SQLID','YC_SINGLE_SQLID']

    for sqlid_name in sqlid_name_lst:
        sql_para = {'ywpz_id':id,'sqlid_name':[sqlid_name],'table_name_yzjypz':[gl_yzjypz],'table_name_blob':[gl_blob]}
        nr = ModSql.yw_pzsj_001.execute_sql_dict(db, "blob_select",sql_para)
        if nr:
            nr = nr[0]
            sql_nr = pickle.loads(nr['nr'].read())
            data[sqlid_name] = sql_nr
        else:
            data[sqlid_name] = ''
    # 将结果放到返回值中
    data['ssyw'] = ssyw
    data['ywmc'] = ywmc
    data['wjlx'] = wjlx
    data['lsdrfs'] = lsdrfs
    data['kzjyfs'] = kzjyfs

    # 原信息列表：[{所属业务：业务名称字典.get(所属业务ID)，文件类型：文件类型，
    #               流水导入方式：模块执行方式字典.get(流水导入方式)，扩展校验方式：
    #               模块执行方式字典.get(扩展校验方式)}]
    yxxlb = "[{所属业务："+ywmc+"，文件类型："+wjlx+"，流水导入方式："+lsdrfs_mc+"，扩展校验方式："+kzjyfs_mc+"}]"
    data['yxxlb'] = yxxlb

    # 将查询到的结果反馈给view
    return data
            
def get_jkpz_xydzcs(gl_xydzpz,gl_hsxxb,gl_csdyb,gl_crcs,id,db):
    """
    # 获取监控配置响应动作参数
    """
    xydzcs_lst = []
    # 获取响应动作
    xydz = ModSql.yw_pzsj_001.execute_sql_dict(db,"get_jcpz_xydz",{'table_name_xydzpz':[gl_xydzpz],'table_name_hsxxb':[gl_hsxxb], 'id':id})

    for xz in xydz:
        # 查询响应动作下的响应动作参数
        xydzcs = ModSql.yw_pzsj_001.execute_sql_dict(db,"get_jcpz_xydz_crcs",{'table_name_crcs':[gl_crcs],'table_name_csdyb':[gl_csdyb], 'xydzid':xz['dzid'],'xydzpzid':xz['xydzid']})
        # 循环响应动作参数，然后添加上相应动作的字段信息
        for x in xydzcs:
            if x:
                xydzcs_lst.append(dict(x, **xz))
    return xydzcs_lst
    
def get_jkpz_xydz(gl_xydzpz,gl_hsxxb,gl_jkfxpz,gl_dzzxzj,gl_zjxx,id,db):
    """
    # 获取监控配置响应动作
    """
    # 查询交易列表
    jbxx = ModSql.yw_pzsj_001.execute_sql_dict(db, "get_jcpz_xydzcs", {'table_name_xydzpz':[gl_xydzpz],'table_name_hsxxb':[gl_hsxxb], 'table_name_jkfxpz':[gl_jkfxpz],'id':id})
    # 执行主机字典
    zxzj_dic = {}
    if jbxx:
        # 根据本页响应动作查询对应执行主机信息 
        zxzj_lst = ModSql.yw_pzsj_001.execute_sql_dict(db, "get_jcpz_zxzj", { 'xydzidlst': [ obj['id'] for obj in jbxx ],'table_name_xydzpz':[gl_xydzpz],'table_name_dzzxzj':[gl_dzzxzj], 'table_name_zjxx':[gl_zjxx] })
        for obj in zxzj_lst:
            if obj['xydzid'] not in zxzj_dic:
                zxzj_dic[ obj['xydzid'] ] = []
            zxzj_dic[ obj['xydzid'] ].append( '%s(%s)' % ( obj['mc'], obj['zjip'] ) )
    # 分析触发
    fxjgcf_lst = get_bmwh_bm( '10012', db=db )
    # 分析触发字典
    fxjgcf_dict = dict( [(xx['value'], xx['text']) for xx in fxjgcf_lst ] )
    # 对结果集中状态进行翻译
    for obj in jbxx:
        obj['fxjgcfmc'] = fxjgcf_dict.get( obj['fxjgcf'], obj['fxjgcf'] )
        obj['dzzxzj'] = zxzj_dic.get( obj['id'], '' )
    
    return jbxx
            
def get_sydx(zbid,gl_crcs,gl_dxcjpz,gl_dxdy,gl_zjxx,id,gl_csdyb,db):
    """
    # 获取适用对象
    """
    data = {'rows':[], 'csz':[]}
    # 获取适用对象的grid的列（也就是参数值）
    csxx = ModSql.yw_pzsj_001.execute_sql_dict(db, "get_csxx", {'table_name':gl_crcs,'zbid':zbid})
    data['csz'].extend([{'csdm':'dxmc', 'cssm':'对象名称'},{'csdm':'zdzj', 'cssm':'指定主机'},{'csdm':'dxzt', 'cssm':'状态'}])
    data['csz'].extend(csxx)
    # 获取适用对象
    data['rows'].extend(ModSql.yw_pzsj_001.execute_sql_dict(db, "get_sydxs", {'table_name_dxcjpz':gl_dxcjpz,'table_name_dxdy':gl_dxdy,'table_name_zjxx':gl_zjxx,'cjpzid':id}))
    for r in data['rows']:
        # 查询参数
        cs = ModSql.yw_pzsj_001.execute_sql_dict(db, "get_csdyb", {'ssid':r['id'],'table_name_crcs':gl_crcs,'table_name_csdy':gl_csdyb,'zbid':zbid})
        for c in cs:
            if c['csz'] == '' or c['csz'] == None:
                r[c['csdm']] = c['mrz']
            else:
                r[c['csdm']] = c['csz']
    return data
def bbdb_detail(leftJkdx,rightJkdx,mc_dic,sort_lst,pop_zd,sxmc):
    """
    # 左右两侧数据比较,比较基本信息
    """
    lJkdx,rJkdx = get_xxbd(leftJkdx,rightJkdx)
    leftJkdx = get_sjzz( lJkdx[0],mc_dic,pop_zd,sort_lst)
    rightJkdx = get_sjzz( rJkdx[0],mc_dic,pop_zd,sort_lst)
    sorted(leftJkdx,key=lambda dic:dic[sxmc] if dic[sxmc] else '')
    sorted(rightJkdx,key=lambda dic:dic[sxmc] if dic[sxmc] else '')
    leftJkdxRs = {'leftJkdx':leftJkdx,'diff':lJkdx[0]['diff']}
    rightJkdxRs = {'rightJkdx':rightJkdx,'diff':rJkdx[0]['diff']}
    return leftJkdxRs,rightJkdxRs
        
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
    
 