# -*- coding: utf-8 -*-
# Action: 维护系统导出
# Author: zhangzhf
# AddTime: 2015-10-19
# Standard: 注释仅能以“#”开头，sql可以是“--”；注释不能同代码在同一行

import os,copy
from sjzhtspj import ModSql,get_sess_hydm,logger
from sjzhtspj.common import get_uuid,ins_czrz,get_strftime,get_strftime2
from sjzhtspj.esb import send_jr

# 当前库临时表的列表
table_ls = ['GL_DXDY_LS','GL_ZJXX_LS','GL_CJPZB_LS','GL_DXCJPZ_LS','GL_CRCS_LS','GL_CSDYB_LS','GL_HSXXB_LS','GL_JKFXPZ_LS','GL_XYDZPZ_LS','GL_DZZXZJ_LS','GL_JHRWB_LS','GL_JCXXPZ_LS','GL_YZJYPZ_LS','GL_YZJYCSPZ_LS','GL_BLOB_LS']
# 当前库正式表的列表
table_zs = ['GL_DXDY','GL_ZJXX','GL_CJPZB','GL_DXCJPZ','GL_CRCS','GL_CSDYB','GL_HSXXB','GL_JKFXPZ','GL_XYDZPZ','GL_DZZXZJ','GL_JCXXPZ','GL_YZJYPZ','GL_YZJYCSPZ','GL_BLOB']

def data_service():
    """
    # 获取要导出信息的service
    """
    return_data = dc_data()
    data = {'state':True, 'msg':'', 'return_data':return_data, 'have':True}
    
    # 链接数据库
    with sjapi.connection() as db:
        # 标识是否有监控对象
        isHaveJkdx = False
        # 获取监控对象类别
        jkdxlb_lst = ModSql.yw_pzsj_002.execute_sql_dict(db,"get_jklb",{})
        # 循环监控类别列表，依次查询监控类别对应的对象
        for jk in jkdxlb_lst:
            j = {'id': jk['lbmc'], 'czsj': '', 'name':jk['lbmc']+'('+jk['lbbm']+')', 'czr': ''}
            j['children'] = ModSql.yw_pzsj_002.execute_sql_dict(db,"get_jkdx",{'jkdxlb_sql_data':[jk['lbbm']]})
            if j['children']:
                isHaveJkdx = True
            return_data[0]['children'][0]['children'].append(j)
        # 查询分析规则
        fxgz_lst = ModSql.yw_pzsj_002.execute_sql_dict(db,"get_fxgz",{})
        # 查询响应动作
        xydz_lst = ModSql.yw_pzsj_002.execute_sql_dict(db,"get_xydz",{})
        # 数据采集配置
        sjcjpz_lst = ModSql.yw_pzsj_002.execute_sql_dict(db,"get_sjcjpz",{})
        # 查询监控配置
        jkpz_lst = ModSql.yw_pzsj_002.execute_sql_dict(db,"get_jkfxpz",{})
        
        # 查询参数配置
        cspz_lst = ModSql.yw_pzsj_002.execute_sql_dict(db,"get_yzjycspz",{})
        # 查询业务配置
        ywpz_lst = ModSql.yw_pzsj_002.execute_sql_dict(db,"get_yzjypz",{})
        # 查询进程配置
        jcpz_lst = ModSql.yw_pzsj_002.execute_sql_dict(db,"get_jcxxpz",{})
        
        if not jkdxlb_lst and not isHaveJkdx and not fxgz_lst and not xydz_lst and not sjcjpz_lst and not jkpz_lst and not cspz_lst and not ywpz_lst and not jcpz_lst:
            return {'state':False, 'msg':'没有可导出的对象', 'return_data':return_data, 'have':False}
        
        # 组织数据
        
        return_data[0]['children'][1]['children'].extend(fxgz_lst)
        return_data[0]['children'][2]['children'].extend(xydz_lst)
        return_data[0]['children'][3]['children'].extend(sjcjpz_lst)
        return_data[0]['children'][4]['children'].extend(jkpz_lst)
        
        return_data[1]['children'][1]['children'].extend(copy.deepcopy(ywpz_lst))
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
        return_data[2]['children'].extend(jcpz_lst)
        
        data['return_data'] = return_data
    return data

def dc_service(param):
    """
    # 导出的service
    """
    data = {'state':True, 'msg':'导出成功'}
    
    # 删除所有的临时表
    # 链接数据库
    with sjapi.connection() as db:
        logger.info("=======================删除临时表=====================")
        logger.info(table_ls)
        # 删除临时表
        drop_table(db)
        # 将正式表数据导入到临时表中
        for t in table_zs:
            ModSql.yw_pzsj_002.execute_sql(db,"create_ls_table",{'table_name':[t],'table_name_ls':[t+"_ls"]})
        # 计划任务表
        ModSql.yw_pzsj_002.execute_sql(db,"create_jhrw_ls",{})
        logger.info("=======================将正式表内容转到临时表=====================")
        nr = '维护系统导出：系统类型：维护，导出描述：%s，备注信息：%s' % ( param.get('dcms'),param.get('bzxx') )
        state,msg = exe_export(db,'','wh',param.get('dcms'),param.get('bzxx'),'',nr,table_ls)
        data['state'] = state
        data['msg'] = msg
        # 删除临时表,这个地方应该删除临时表，但是导出命令发送到核心。
        # 这个请求是异步的，如果数据过多，核心还没导出结束，这里就删除的话，导出的数据就不完整
        # drop_table(db)
    return data
    
def drop_table(db):
    # 查询存在的临时表
    l = ModSql.yw_pzsj_002.execute_sql_dict(db,"get_table_ls",{'table_name':table_ls})
    table_name_ls = [llt['table_name'] for llt in l]
    # 删除临时表
    for dic in table_name_ls:
        ModSql.common.execute_sql(db,"drop_table",{'tname_lst':[dic]})
            
def exe_export( db,ssid,dclx,dcms,bzxx,ywid,nr,table ):
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
    table_name = ",".join( table )
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
        sql_data = {'id':get_uuid(),'ss_idlb':ssid,'ssywid':ywid,'czlx':'dc','nrlx':dclx,'czr':get_sess_hydm(),'czsj':get_strftime(),'czms':dcms,'wjm':fname,'bz':bzxx,'zt':'1','bfwjm':'','fhr':''}
        ModSql.common.execute_sql( db,"insert_drls",sql_data)
        # 操作日志登记
        nr = '%s，导出流水ID：%s' % ( nr,sql_data['id'] )
        ins_czrz( db, nr ,pt = 'wh' , gnmc = '导出' )
        return True,'导出请求已发送，请稍后到系统参数[db_ftp_uploadPath]配置目录[%s]下，下载文件：【%s】' % ( uploadPath, fname )
    else:
        return False,'导出失败，请检查问题原因'
    
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