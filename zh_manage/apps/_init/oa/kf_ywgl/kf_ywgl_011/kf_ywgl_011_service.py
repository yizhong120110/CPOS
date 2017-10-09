# -*- coding: utf-8 -*-
# Action: 数据库模型管理B层
# Author: jind
# AddTime: 2015-02-02
# Standard: 注释仅能以“#”开头，sql可以是“--”；注释不能同代码在同一行

import traceback
from sjzhtspj import ModSql,get_sess_hydm,logger
from sjzhtspj.common import get_uuid,update_wym,ins_czrz,get_sjktbxx,get_strftime
from sjzhtspj.const import ZDLX_DIC,SYLX_DIC,ORACLE_KEYWORDS_LST

def index_service( data ):
    """
    # 获取业务名称
    # @param data:返回页面的结果集
    """
    ywid = data['ywid']
    sjktbxx_dic = get_sjktbxx( ywid )
    # 是否需要同步
    sfxytb = sjktbxx_dic['sfxytb']
    if sfxytb:
        # 同步信息
        tbxx_dic = sjktbxx_dic['tbxx_dic']
        # 本次同步的表ID
        update_table_id = sjktbxx_dic ['update_table_id']     
        # 需从数据库模型定义中删除的表信息
        drop_table = sjktbxx_dic ['drop_table']
        # 需从数据库字段表中删除的表字段
        drop_table_column = sjktbxx_dic ['drop_table_column']
        # 需从数据库字段表中更新的字段信息
        update_table_column = sjktbxx_dic ['update_table_column']
        # 需从数据库字段表中增加的表字段
        ins_table_column = sjktbxx_dic ['ins_table_column']
        # 需从数据库模型定义中更新表描述的字典
        update_table_ms = sjktbxx_dic ['update_table_ms']
        # 需从数据库索引表中删除的索引
        drop_table_index = sjktbxx_dic ['drop_table_index']
        # 需插入到数据库索引表中的索引信息
        ins_table_index = sjktbxx_dic ['ins_table_index']
        # 需更新的索引信息 
        update_table_index = sjktbxx_dic ['update_table_index']
        # 需从数据库约束表中删除的约束
        drop_table_unique = sjktbxx_dic ['drop_table_unique']
        # 需插入到数据库约束表中的约束信息
        ins_table_unique = sjktbxx_dic ['ins_table_unique'] 
        # 需更新的约束信息
        update_table_unique = sjktbxx_dic ['update_table_unique']
        # 数据表ID、名称字典
        sjb_id_mc_dic = sjktbxx_dic['sjb_id_mc_dic']
        # 数据表名称、描述字典
        sjb_mc_ms_dic = sjktbxx_dic['sjb_mc_ms_dic'] 
        # 本次删除的数据表名称
        drop_table_mc = []
        # 本次更新的数据表名称
        update_table_mc = []
        # 无法识别的字段类型
        nonsupport_type = sjktbxx_dic['nonsupport_type'] 
        with sjapi.connection() as db:
            # 若系统中不存在的表，需将数据库模型定义、字段表、约束表、索引表、版本控制表对应的数据全部删除
            if drop_table:
                # 删除数据库模型定义
                ModSql.kf_ywgl_011.execute_sql(db, "del_sjkmxdy",{'drop_table':drop_table})
                # 删除数据库字段表
                ModSql.kf_ywgl_011.execute_sql(db, "del_sjkzdb_by_tabid",{'drop_table':drop_table})
                # 删除数据库索引表
                ModSql.kf_ywgl_011.execute_sql(db, "del_sjksy_by_tabid",{'drop_table':drop_table})
                # 删除数据库约束表
                ModSql.kf_ywgl_011.execute_sql(db, "del_sjkys_by_tabid",{'drop_table':drop_table})
                # 删除BLOB管理表
                ModSql.common.execute_sql(db,'del_blob',{'ssid_lst':drop_table,'lx':'sjk'})
                # 删除版本控制
                ModSql.common.execute_sql(db,'del_bbkz',{'ssid_lst':drop_table,'lx':'sjk'})
                
            # 删除数据库字段表中多余记录    
            if drop_table_column:
                ModSql.kf_ywgl_011.execute_sql(db, "del_sjkzdb_by_id",{'id_lst':drop_table_column})

            # 删除数据库索引表中多余记录    
            if drop_table_index:
                ModSql.kf_ywgl_011.execute_sql(db, "del_sjksy_by_id",{'id_lst':drop_table_index})
                
            # 删除数据库约束表中多余记录    
            if drop_table_unique:
                ModSql.kf_ywgl_011.execute_sql(db, "del_sjkys_by_id",{'id_lst':drop_table_unique})
                
            # 新增数据库字段信息记录
            for bid,lst in ins_table_column.items():
                for zdxx in lst:
                    sql_data = { 'id':get_uuid(),'sjb_id':bid,'zdmc':zdxx.get( 'zdmc','' ),'zdms':zdxx.get( 'zdms','' ),'zdlx':zdxx.get( 'zdlx','' ),'zdcd':zdxx.get( 'zdcd','' ),'xscd':zdxx.get( 'xscd','' ),'sfkk':zdxx.get( 'sfkk','' ),'iskey':zdxx.get( 'iskey','' ),'mrz':zdxx.get( 'mrz','' ) }        
                    ModSql.kf_ywgl_011.execute_sql(db, "insert_sjkzdb",sql_data)
                
            # 新增数据库索引信息记录
            for bid,lst in ins_table_index.items():
                for syxx in lst:
                    sql_data = { 'id':get_uuid(),'sssjb_id':bid,'symc':syxx.get( 'symc','' ),'syzd':syxx.get( 'syzd','' ),'sylx':syxx.get( 'sylx','' ),'sfwysy':syxx.get( 'sfwysy','' ) }        
                    ModSql.kf_ywgl_011.execute_sql(db, "insert_sjksy",sql_data)
                
            # 新增数据库约束信息记录
            for bid,lst in ins_table_unique.items():
                for ysxx in lst:
                    sql_data = { 'id':get_uuid(),'sssjb_id':bid,'ysmc':ysxx.get( 'ysmc','' ),'yszd':ysxx.get( 'yszd','' ) }        
                    ModSql.kf_ywgl_011.execute_sql(db, "insert_sjkys",sql_data)
                
            # 需更新的数据库模型定义信息    
            for bid,bms in update_table_ms.items():
                sql_data = {'sjbmcms':bms,'id':bid}
                ModSql.kf_ywgl_011.execute_sql(db, "update_sjbms",sql_data)
            # 需更新数据库字段信息 
            for id,zdxx in update_table_column.items():
                zdxx_lst = [ ( k, v ) for k,v in zdxx.items() ] 
                ModSql.kf_ywgl_011.execute_sql(db, "update_sjbzdxx",{'zdxx_lst':zdxx_lst,'id':id})
            # 需更新数据库索引信息
            for id,syxx in update_table_index.items():
                syxx_lst = [ ( k, v ) for k,v in syxx.items() ] 
                ModSql.kf_ywgl_011.execute_sql(db, "update_sjbsyxx",{'syxx_lst':syxx_lst,'id':id})
            # 需更新数据库约束信息
            for id,ysxx in update_table_unique.items():
                sql_data = { 'yszd':ysxx.get('yszd',''),'id':id }
                ModSql.kf_ywgl_011.execute_sql(db, "update_sjbysxx",sql_data )
                
            # 登记同步流水信息    
            # 获取该业务的数据库模型同步次数
            tbcs = ModSql.kf_ywgl_011.execute_sql( db, "get_tbcs",{'ywid':ywid} )[0].tbcs
            # 将同步次数+1，登记同步流水
            tbcs = tbcs + 1
            for sjbid,tbxx in tbxx_dic.items():
                sjbxx_dic = tbxx[0]
                lsid = get_uuid()
                sql_data = { 'id':lsid,'sjbid':sjbid,'sjbmc':sjbxx_dic.get('sjbmc',''),'tblx':sjbxx_dic.get('sjbtblx'),'tbr':'auto','tbrq':get_strftime()[:10],'tbsj':get_strftime()[11:],'tbcs':tbcs,'ssywid':ywid}   
                ModSql.kf_ywgl_011.execute_sql( db, "insert_sjktblsb",sql_data )
                
                sjbxx_lst = tbxx[1:]
                for dic in sjbxx_lst:
                    sql_data = { 'id':get_uuid(),'tblx':dic.get( 'tblx','' ),'tbnrlx':dic.get( 'tbnrlx','' ),'tbnrmc':dic.get( 'tbnrmc','' ),'tbnrsx':dic.get( 'tbnrsx','' ),'tbqsxz':dic.get( 'tbqsxz','' ),'tbhsxz':dic.get( 'tbhsxz','' ),'sstblsid':lsid}
                    ModSql.kf_ywgl_011.execute_sql( db, "insert_sjktbxxb",sql_data )
            for id in update_table_id:
                update_wym( db,'sjk',id)
            
        # 本次删除的数据表名称
        drop_table_mc = []
        update_table_mc = []
        for id in drop_table:
            drop_table_mc.append( sjb_id_mc_dic.get( id ,'' ) )
        
        # 本次更新的数据表名称
        for id in update_table_id:
            update_table_mc.append( sjb_id_mc_dic.get( id ,'' ) )
        data['drop_table_mc'] = drop_table_mc
        data['update_table_mc'] = update_table_mc    
        data['nonsupport_type'] = nonsupport_type
    data['sfxytb'] = sfxytb
    data['ZDLX_DIC'] = ZDLX_DIC
    data['SYLX_DIC'] = SYLX_DIC
    data['ORACLE_KEYWORDS_LST'] = ORACLE_KEYWORDS_LST
    return data

def data_service( sql_data):
    """
    # 获取数据库模型列表展示数据
    # @param ywid:业务ID
    # @param rn_start:开始的rownum
    # @param rn_end:结束的rownum
    """
    # 初始化返回值
    data = {'total':0, 'rows':[]}
    with sjapi.connection() as db:
        # 查询数据库模型总记录
        total = ModSql.kf_ywgl_011.execute_sql(db, "get_sjkmx_count",sql_data)[0].count
        # 查询数据库模型信息
        jbxx = ModSql.kf_ywgl_011.execute_sql_dict(db, "get_sjkmxxx",sql_data)
        # 将总条数放到结果集中
        data['total'] = total
        # 将查询详情结果放到结果集中
        data['rows'] = jbxx
    return data
        
def data_sjb_add_service( ywid,data,sjbmc,sjbmcms ):
    """
    # 新增数据表
    # @param ywid:业务ID
    # @param data:数据表的字段信息
    # @param sjbmc:数据表名称
    # @param sjbmcms:数据表名称描述
    """
    with sjapi.connection() as db:
        # 校验数据表名称在数据库模型定义表是否存在
        count = ModSql.kf_ywgl_011.execute_sql(db, "check_sjbmc_by_sjkmx",{'sjbmc':sjbmc})[0].count
        count1 = ModSql.kf_ywgl_011.execute_sql(db, "check_sjbmc_by_oracle",{'sjbmc':sjbmc})[0].count
        if count != 0 or count1 != 0:
            msg = '数据表名称[%s]已经存在，请重新输入'%sjbmc
            return {'state':False,'msg':msg}
        sql = " create table %s ( "%sjbmc
        # 用来存放创建数据表及字段注释SQL
        zs_subsql_lst = []
        # 为表增加注释SQ
        zs_subsql_lst.append( "comment on table %s is '%s'"%( sjbmc,sjbmcms) )
        # 用来存放创建字段的SQL
        subsql_lst = []
        # 主键字段
        iskey_lst = []
        # 日志信息字段
        for zdxx_dic in data:
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
        sql = sql + ",".join( subsql_lst ) + " ,constraint PK_%s primary key ( %s )"%( sjbmc,",".join( iskey_lst ) ) + " )" 
        # 执行建表sql
        db.execute( sql )
        # 为表及字段增加注释,本来想将所有增加的SQL拼接起来进行执行，但是一直报无效的字符，找不到具体原因，拼接后的SQL拿到数据库中也可以直接执行，通过代码执行就报错
        for sql in zs_subsql_lst:
            db.execute( sql )
            
        # 登记数据表内容
        sjbid = get_uuid()
        sql_data = {'id':sjbid,'sjbmc':sjbmc,'sjbmcms':sjbmcms,'ssyw_id':ywid,'czr':get_sess_hydm(),'czsj':get_strftime() } 
        ModSql.kf_ywgl_011.execute_sql(db, "insert_sjkmxdy",sql_data)
        
        # 登记字段信息
        for zdxx_dic in data:
            sql_data = {'id':get_uuid(),'sjb_id':sjbid,'zdmc':zdxx_dic['zdmc'].upper(),'zdms':zdxx_dic['zdms'],'zdlx':zdxx_dic['zdlx'],'zdcd':zdxx_dic['zdcd'],'xscd':zdxx_dic['xscd'],'sfkk':zdxx_dic['sfkk'],'iskey':zdxx_dic['iskey'],'mrz':zdxx_dic['mrz']}
            ModSql.kf_ywgl_011.execute_sql(db, "insert_sjkzdb",sql_data)
            
        # 数据表创建成功后，获取系统自动为表创建的索引    
        rs = ModSql.kf_ywgl_011.execute_sql_dict(db, "get_oracle_sy",{'sjbmc':sjbmc})
        # 索引信息[[索引名称，索引字段，索引类型，是否唯一索引]]
        syxx_lst = []
        for dic in rs:
            flag = True
            for index,items in enumerate( syxx_lst ):
                #若索引名称已在列表中，说明是联合索引，需将索引字段进行拼接
                if dic['symc'] == items[0]:
                    syxx_lst[index][1] = syxx_lst[index][1] + "|" + dic['syzd']
                    flag = False
                    break
            # 说明索引名称在列表中不存在，进行添加
            if flag:
                syxx_lst.append( [ dic['symc'],dic['syzd'],dic['sylx'],dic['sfwysy'] ] )
        for lst in syxx_lst:
            sql_data = {'id':get_uuid(),'sssjb_id':sjbid,'symc':lst[0],'syzd':lst[1],'sylx':lst[2],'sfwysy':lst[3] }  
            ModSql.kf_ywgl_011.execute_sql(db, "insert_sjksy",sql_data)
        ins_czrz( db, '数据表新增：数据表名称[%s]，数据表名称描述[%s]，字段信息：%s' % (sjbmc, sjbmcms, data), gnmc = '数据表管理_新增' )
        update_wym( db,'sjk',sjbid )
        return {'state':True,'msg':'新增成功'}
        
def data_sjb_add_except_service( sjbmc ):
    """
    # 新增数据表异常处理
    # @param sjbmc:数据表名称
    """        
    # 因为创建表时不需要提交操作，所以当出现异常时，若数据表已经创建，通过回滚操作无法将该表删除，只能通过SQL去删除
    with sjapi.connection() as db:
        # 首先查询oracle系统表，判断该表是否已创建
        count = ModSql.kf_ywgl_011.execute_sql(db, "check_table_create",{'sjbmc':sjbmc})[0].count
        # 说明数据表已创建，需执行SQL删除,数据表删除时会将注释也删除的，不需要再执行SQL注释SQL
        if count != 0:
            sql = " drop table %s"%( sjbmc )
            db.execute( sql )
            
def data_zd_add_service( sjbid,sjbmc,zdmc,zdms,zdlx,zdcd,xscd,sfkk,iskey,mrz ):
    """
    # 新增表字段
    # @param sjbid:数据表ID
    # @param sjbmc:数据表名称
    # @param zdmc:字段名称
    # @param zdms:字段描述
    # @param zdlx:字段类型
    # @param zdcd:字段长度
    # @param xscd:小数长度
    # @param sfkk:是否可空
    # @param iskey:是否主键
    # @param mrz:默认值
    """  
    # 删除字段回滚SQL
    rollback_zd_sql = ''
    # 回滚原主键SQL
    rollback_yzj_sql = ''
    # 回滚现主键SQL
    rollback_xzj_sql = ''
    result = {'state':False, 'msg':''}
    try:
        with sjapi.connection() as db:
            # 校验字段名称是否已存在
            count = ModSql.kf_ywgl_011.execute_sql(db, "check_zdmc",{'zdmc':zdmc,'sjbid':sjbid})[0].count
            if count != 0 :
                result['msg'] = '字段名称[%s]已经存在，请重新输入'%zdmc
                return result
            # 拼接创建字段SQL 
            sql = ''
            if zdlx in ( 'CHAR','VARCHAR2','NCHAR','NVARCHAR2','RAW','FLOAT'):
                sql = " alter table %s add %s %s ( %d ) "%( sjbmc,zdmc,zdlx,zdcd )
            elif zdlx == 'DECIMAL':
                if xscd:
                    sql = "alter table %s add %s %s ( %d,%d )"%( sjbmc,zdmc,zdlx,zdcd,xscd )
                else:
                    sql = " alter table %s add %s %s ( %d ) "%( sjbmc,zdmc,zdlx,zdcd )
            elif zdlx in ( 'DATE', 'LONG', 'BLOB', 'CLOB', 'NCLOB', 'BFILE', 'INTEGER', 'LONG RAW','REAL'):
                sql = "  alter table %s add %s %s"%( sjbmc,zdmc,zdlx )
            elif zdlx == 'NUMBER':
                if zdcd:
                    if xscd:
                        sql = "alter table %s add %s %s ( %d,%d )"%( sjbmc,zdmc,zdlx,zdcd,xscd )
                    else:
                        sql = " alter table %s add %s %s ( %d ) "%( sjbmc,zdmc,zdlx,zdcd )
                else:
                    sql = "  alter table %s add %s %s"%( sjbmc,zdmc,zdlx )
            # 如果有默认值
            if mrz:
                sql += " default '%s' "%(  mrz  )
            # 字段是否可空 1:是 0:否
            if sfkk == '0': 
                sql += " not null "
            db.execute( sql )
            # 字段添加成功，后面执行若出现问题，可通过此SQL将添加的字段删除
            rollback_zd_sql = " alter table %s drop( %s )"%( sjbmc,zdmc )
            # 添加创建注释SQL,注释无需回滚，字段删除后会自动删除
            zs_sql = "comment on column %s.%s is '%s'"%( sjbmc,zdmc,zdms )
            db.execute( zs_sql )
            
            # 如果该字段为主键 1:是 0：否
            if iskey == '1':
                # 查询该表的主键信息
                rs = ModSql.kf_ywgl_011.execute_sql_dict(db, "get_zjxx",{'sjbmc':sjbmc})
                # 主键名称
                zjmc = rs[0]['zjmc']
                # 主键字段
                zjzd = [ dic['zjzd'] for dic in rs ]
                # 删除该表原有的主键
                sql = "alter table %s drop constraint %s"%( sjbmc,zjmc)
                db.execute( sql )
                # 主键回滚SQL:
                rollback_yzj_sql = "alter table %s add constraint %s primary key ( %s )"%( sjbmc,zjmc,",".join( zjzd ))
                # 创建主键
                zjzd.append( zdmc )
                sql = "alter table %s add constraint %s primary key ( %s )"%( sjbmc,zjmc,",".join( zjzd ) )
                db.execute( sql )
                # 主键回滚SQL:
                rollback_xzj_sql = "alter table %s drop constraint %s"%( sjbmc,zjmc )
                #主键字段发生变化后,其对应索引的索引字段也会改变,索引需要同步
                rs = ModSql.kf_ywgl_011.execute_sql_dict(db, "get_oracle_sy",{'sjbmc':sjbmc,'symc':zjmc})
                # 主键约束对应索引的索引字段
                syzd_lst = []
                for dic in rs:
                    syzd_lst.append( dic['syzd'] )
                syzd_str = "|".join( syzd_lst )
                # 更新主键约束对应索引的索引字段
                sql_data = {'syzd':syzd_str,'sjbid':sjbid,'symc':zjmc}
                ModSql.kf_ywgl_011.execute_sql_dict(db, "upd_syxx",sql_data)
                
            sql_data = {'id':get_uuid(),'sjb_id':sjbid,'zdmc':zdmc,'zdms':zdms,'zdlx':zdlx,'zdcd':zdcd,'xscd':xscd,'sfkk':sfkk,'iskey':iskey,'mrz':mrz }
            ModSql.kf_ywgl_011.execute_sql(db, "insert_sjkzdb",sql_data)
            # 更新唯一码
            update_wym( db,'sjk',sjbid )
            # 登记操作日志
            ins_czrz( db,'数据表[%s]新增[%s]字段' % ( sjbmc,zdmc ), gnmc = '数据表管理_新增字段'  )
            # 更新数据库模型操作人、操作时间
            update_sjb( db,sjbid )
            result['state'] = True
            result['msg'] = '新增成功'
    except:
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        ret_err_msg = error_msg[error_msg.find('cx_Oracle'):]
        result['msg'] = '新增失败！异常错误提示信息[%s]' % ret_err_msg
        if rollback_xzj_sql or rollback_yzj_sql or rollback_zd_sql:
            with sjapi.connection() as db:
                # 回滚需注意顺序，若主键已修改，需将修改后的主键先删除，恢复到原来的主键，最后再将字段删除
                if rollback_xzj_sql:
                    #说明主键已修改，需将现在的主键约束还原回去
                    # 先把后台增加的主键约束删除
                    db.execute( rollback_xzj_sql )
                if rollback_yzj_sql:
                    #说明原主键已删除，但新的主键没有创建出来,需将原来的主键还原
                    db.execute( rollback_yzj_sql )
                if rollback_zd_sql:
                    # 将新增的字段也删除
                    db.execute( rollback_zd_sql )
    return result

def data_zd_edit_service( sjbid,sjbmc,zdmc,zdms,zdlx,zdcd,xscd,sfkk,iskey,mrz,zdid ):
    """
    # 修改表字段
    # @param sjbid:数据表ID
    # @param sjbmc:数据表名称
    # @param zdmc:字段名称
    # @param zdms:字段描述
    # @param zdlx:字段类型
    # @param zdcd:字段长度
    # @param xscd:小数长度
    # @param sfkk:是否可空
    # @param iskey:是否主键
    # @param mrz:默认值
    # @param zdid:字段ID
    """  
    # 修改字段回滚SQL
    rollback_zd_sql = ''
    # 回滚原主键SQL
    rollback_yzj_sql = ''
    # 回滚现主键SQL
    rollback_xzj_sql = ''
    # 回滚字段描述SQL
    rollback_zdms_sql = ''
    result = {'state':False, 'msg':''}
    try:
        with sjapi.connection() as db:
            # 查询原字段信息,以便进行回滚
            rs = ModSql.kf_ywgl_011.execute_sql_dict( db,"get_zdxx",{'id':zdid} )[0]
            yzdms = rs['zdms']
            yzdlx = rs['zdlx']
            yzdcd = rs['zdcd'] or ''
            yxscd = rs['xscd'] or ''
            ysfkk = rs['sfkk']
            yiskey = rs['iskey']
            ymrz = rs['mrz'] or ''
            if ysfkk == '1' and sfkk == '0':
                # 若原字段为可空，本次要修改为不可空，需校验此表中该字段的值是否有空值
                count = ModSql.kf_ywgl_011.execute_sql( db,"check_null_data",{'zdmc_lst':[zdmc],'tname_lst':[sjbmc]} )[0].count
                if count != 0:
                    result['msg'] = '该字段数据存在空数据，不可变更为非空!'
                    return result
            # 若原字段为主键字段，本次修改为非主键字段，需校验此表中是否还存在主键字段
            if yiskey == '1' and iskey == '0':
                count = ModSql.kf_ywgl_011.execute_sql( db,"get_zjzd_count",{'sjbid':sjbid,'zdmc':zdmc} )[0].count
                if count == 0:
                    result['msg'] = '请先为此表选择其他主键字段，再修改本字段的主键属性!'
                    return result
            # 若字段的以下属性进行了修改
            if zdlx != yzdlx or (zdcd != yzdcd and zdlx not in ( 'DATE', 'LONG', 'BLOB', 'CLOB', 'NCLOB', 'BFILE', 'INTEGER', 'LONG RAW','REAL') ) or xscd != yxscd or sfkk != ysfkk or mrz != ymrz:
                # 拼接修改字段SQL
                sql = ''
                if zdlx in ( 'CHAR','VARCHAR2','NCHAR','NVARCHAR2','RAW','FLOAT'):
                    sql = " alter table %s modify %s %s ( %d ) "%( sjbmc,zdmc,zdlx,zdcd )
                elif zdlx == 'DECIMAL':
                    if xscd:
                        sql = "alter table %s modify %s %s ( %d,%d )"%( sjbmc,zdmc,zdlx,zdcd,xscd )
                    else:
                        sql = " alter table %s modify %s %s ( %d ) "%( sjbmc,zdmc,zdlx,zdcd )
                elif zdlx in ( 'DATE', 'LONG', 'BLOB', 'CLOB', 'NCLOB', 'BFILE', 'INTEGER', 'LONG RAW','REAL'):
                    sql = "  alter table %s modify %s %s"%( sjbmc,zdmc,zdlx )
                elif zdlx == 'NUMBER':
                    if zdcd:
                        if xscd:
                            sql = "alter table %s modify %s %s ( %d,%d )"%( sjbmc,zdmc,zdlx,zdcd,xscd )
                        else:
                            sql = " alter table %s modify %s %s ( %d ) "%( sjbmc,zdmc,zdlx,zdcd )
                    else:
                        sql = "  alter table %s modify %s %s"%( sjbmc,zdmc,zdlx )
                # 如果有默认值
                if mrz:
                    sql += " default '%s' "%(  mrz  )
                else:
                    sql += " default '' "
                # 字段是否可空 1:是 0:否
                if ysfkk == '1' and sfkk == '0': 
                    if(zdlx == yzdlx and zdlx in ('BLOB', 'CLOB', 'NCLOB', 'BFILE', 'LONG RAW','REAL','LONG') ):
                        sql = "alter table %s modify %s not null"%( sjbmc,zdmc )
                    else:
                        sql += " not null "
                elif ysfkk == '0' and sfkk == '1':
                    if(zdlx == yzdlx and zdlx in ('BLOB', 'CLOB', 'NCLOB', 'BFILE', 'LONG RAW','REAL','LONG') ):
                        sql = "alter table %s modify %s null"%( sjbmc,zdmc )
                    else:
                        sql += " null "
                db.execute( sql )
                
                # 字段修改成功，后面执行若出现问题，可通过此SQL将修改的字段恢复
                if yzdlx in ( 'CHAR','VARCHAR2','NCHAR','NVARCHAR2','RAW','FLOAT'):
                    rollback_zd_sql = " alter table %s modify %s %s ( %d ) "%( sjbmc,zdmc,yzdlx,yzdcd )
                elif yzdlx == 'DECIMAL':
                    if xscd:
                        rollback_zd_sql = "alter table %s modify %s %s ( %d,%d )"%( sjbmc,zdmc,yzdlx,yzdcd,yxscd )
                    else:
                        rollback_zd_sql = " alter table %s modify %s %s ( %d ) "%( sjbmc,zdmc,yzdlx,yzdcd )
                elif yzdlx in ( 'DATE', 'LONG', 'BLOB', 'CLOB', 'NCLOB', 'BFILE', 'INTEGER', 'LONG RAW','REAL'):
                    rollback_zd_sql = "  alter table %s modify %s %s"%( sjbmc,zdmc,yzdlx )
                elif yzdlx == 'NUMBER':
                    if yzdcd:
                        if yxscd:
                            rollback_zd_sql = "alter table %s modify %s %s ( %d,%d )"%( sjbmc,zdmc,yzdlx,yzdcd,yxscd )
                        else:
                            rollback_zd_sql = " alter table %s modify %s %s ( %d ) "%( sjbmc,zdmc,yzdlx,yzdcd )
                    else:
                        rollback_zd_sql = "  alter table %s modify %s %s"%( sjbmc,zdmc,yzdlx )
                # 如果有默认值
                if ymrz:
                    rollback_zd_sql += " default '%s' "%(  ymrz  )
                # 字段是否可空 1:是 0:否
                if ysfkk == '0' and sfkk == '1': 
                    if(zdlx == yzdlx and zdlx in ('BLOB', 'CLOB', 'NCLOB', 'BFILE', 'LONG RAW','REAL','LONG') ):
                        rollback_zd_sql = "alter table %s modify %s not null"%( sjbmc,zdmc )
                    else:
                        rollback_zd_sql += " not null "
                elif ysfkk == '1' and sfkk == '0': 
                    if(zdlx == yzdlx and zdlx in ('BLOB', 'CLOB', 'NCLOB', 'BFILE', 'LONG RAW','REAL','LONG') ):
                        rollback_zd_sql = "alter table %s modify %s null"%( sjbmc,zdmc )
                    else:
                        rollback_zd_sql += " null "
            
            # 若字段描述修改了
            if zdms != yzdms:
                # 添加创建注释SQL,注释无需回滚，字段删除后会自动删除
                zs_sql = "comment on column %s.%s is '%s'"%( sjbmc,zdmc,zdms )
                db.execute( zs_sql )
                rollback_zdms_sql = "comment on column %s.%s is '%s'"%( sjbmc,zdmc,yzdms )
            
            # 若字段的主键属性修改了
            if iskey != yiskey:
                rs = ModSql.kf_ywgl_011.execute_sql_dict(db, "get_zjxx",{'sjbmc':sjbmc})
                # 主键名称
                zjmc = rs[0]['zjmc']
                # 主键字段
                zjzd = [ dic['zjzd'] for dic in rs ]
                # 删除该表原有的主键
                sql = "alter table %s drop constraint %s"%( sjbmc,zjmc)
                db.execute( sql )
                # 主键回滚SQL:
                rollback_yzj_sql = "alter table %s add constraint %s primary key ( %s )"%( sjbmc,zjmc,",".join( zjzd ))
                # 若是否主键属性由是修改为否,需从主键列表中删除
                if yiskey == '1' and iskey == '0':
                    zjzd.remove( zdmc )
                # 若是否主键属性由否修改为是,需追加到主键列表中
                elif yiskey == '0' and iskey == '1':
                    zjzd.append( zdmc )
                    # 为追寻创建主键时，字段的顺序为创建表时字段创建的先后，需将主键字段进行排序
                    rs = ModSql.kf_ywgl_011.execute_sql_dict(db, "get_zjzd_order",{'sjbmc':sjbmc,'zjzd':zjzd})
                    zjzd = [ dic['zdmc'] for dic in rs]
                sql = "alter table %s add constraint %s primary key ( %s )"%( sjbmc,zjmc,",".join( zjzd ) )
                db.execute( sql )
                # 主键回滚SQL:
                rollback_xzj_sql = "alter table %s drop constraint %s"%( sjbmc,zjmc )
                
                #主键字段发生变化后,其对应索引的索引字段也会改变,索引需要同步
                #rs = ModSql.kf_ywgl_011.execute_sql_dict(db, "get_oracle_sy",{'sjbmc':sjbmc,'symc':zjmc})
                rs = ModSql.kf_ywgl_011.execute_sql_dict(db, "get_oracle_sy",{'sjbmc':sjbmc})
                # 主键约束对应索引的索引字段
                syxx_dic = {}
                for dic in rs:
                    if dic['symc'] not in syxx_dic.keys():
                        syxx_dic[dic['symc']] = [dic['syzd']]
                    else:
                        syxx_dic[dic['symc']].append(dic['syzd'])
                # 更新主键约束对应索引的索引字段
                for symc,syzd in syxx_dic.items():
                    syzd_str = "|".join( syzd )
                    sql_data = {'syzd':syzd_str,'sjbid':sjbid,'symc':symc}
                    ModSql.kf_ywgl_011.execute_sql_dict(db, "upd_syxx",sql_data)
                    
            # 编辑前的信息查询
            zdxx_bjq = ModSql.kf_ywgl_011.execute_sql_dict(db, "select_zdxx",{'id': zdid})[0]
            # 更新字段信息
            sql_data = {'id':zdid,'zdms':zdms,'zdlx':zdlx,'zdcd':zdcd,'xscd':xscd,'sfkk':sfkk,'iskey':iskey,'mrz':mrz }
            ModSql.kf_ywgl_011.execute_sql_dict(db, "update_zdxx",sql_data)
            # 更新唯一码
            update_wym( db,'sjk',sjbid )
            # 编辑后的信息查询
            zdxx_bjh = zdxx_bjq.copy()
            zdxx_bjh.update({'xscd':xscd,'zdlx':zdlx,'zdms':zdms,'sfkk':sfkk,'mrz':mrz,'iskey':iskey,'zdcd':zdcd})
            # 登记操作日志
            ins_czrz( db,'数据表[%s]编辑[%s]字段：编辑前：%s，编辑后：%s' % ( sjbmc,zdmc,zdxx_bjq,zdxx_bjh), gnmc = '数据表管理_编辑字段' )
            # 更新数据库模型操作人、操作时间
            update_sjb( db,sjbid )
            result['state'] = True
            result['msg'] = '编辑成功'
    except:
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        ret_err_msg = error_msg[error_msg.find('cx_Oracle'):]
        result['msg'] = '编辑失败！异常错误提示信息[%s]' % ret_err_msg
        if rollback_xzj_sql or rollback_yzj_sql or rollback_zd_sql:
            with sjapi.connection() as db:
                # 回滚需注意顺序，若主键已修改，需将修改后的主键先删除，恢复到原来的主键，最后再将字段删除
                if rollback_xzj_sql:
                    #说明主键已修改，需将现在的主键约束还原回去
                    # 先把后台增加的主键约束删除
                    db.execute( rollback_xzj_sql )
                if rollback_yzj_sql:
                    #说明原主键已删除，但新的主键没有创建出来,需将原来的主键还原
                    db.execute( rollback_yzj_sql )
                if rollback_zd_sql:
                    # 将修改的字段还原
                    db.execute( rollback_zd_sql )
                if rollback_zdms_sql:
                    # 将修改的字段描述还原
                    db.execute( rollback_zd_sql )
    return result
    
def data_sy_add_service( sjbid,sjbmc,symc,syzd,sylx,sfwysy ):
    """
    # 新增表字段
    # @param sjbid:数据表ID
    # @param sjbmc:数据表名称
    # @param symc:索引名称
    # @param syzd:索引字段
    # @param sylx:索引类型
    # @param sfwysy:是否唯一索引
    """  
    # 回滚SQL
    rollback_sql = ""
    result = {'state':False, 'msg':''}
    try:
        with sjapi.connection() as db:
            # 校验索引名称是否已存在
            count = ModSql.kf_ywgl_011.execute_sql( db,'check_symc',{'symc':symc})[0].count
            if count != 0 :
                result['msg'] = '索引名称[%s]已经存在，请重新输入'%symc
                return result
            # 校验索引字段是否已存在
            count = ModSql.kf_ywgl_011.execute_sql( db,'check_syzd',{'syzd':syzd,'sjbid':sjbid})[0].count
            if count != 0 :
                result['msg'] = '索引字段[%s]已建立索引，请重新选择'%syzd
                return result
            # 拼接创建索引SQL
            if sylx == 'NORMAL':
                sql = "create %s index %s on %s (%s)"%( 'unique' if sfwysy == 'UNIQUE' else '',symc,sjbmc,",".join( syzd.split("|") ) );
            elif sylx == 'NORMAL/REV':
                sql = "create %s index %s on %s (%s) reverse"%( 'unique' if sfwysy == 'UNIQUE' else '', symc,sjbmc,",".join( syzd.split("|") ) );
            elif sylx == 'BITMAP':
                sql = "create  bitmap index %s on %s (%s) "%( symc,sjbmc,",".join( syzd.split("|") ) );
            db.execute( sql )
            rollback_sql = " drop index %s"%( symc )  
            # 登记索引
            sql_data = { 'id':get_uuid(),'sssjb_id':sjbid,'symc':symc,'syzd':syzd,'sylx':sylx,'sfwysy':sfwysy }        
            ModSql.kf_ywgl_011.execute_sql(db,'insert_sjksy',sql_data)
            # 更新唯一码
            update_wym( db,'sjk',sjbid )
            # 登记操作日志
            ins_czrz( db,'数据表[%s]新增[%s]索引' % ( sjbmc,symc ), gnmc = '数据表管理_新增索引'  )
            # 更新数据库模型操作人、操作时间
            update_sjb( db,sjbid )
            result['state'] = True
            result['msg'] = '新增成功'
    except:
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        ret_err_msg = error_msg[error_msg.find('cx_Oracle'):]
        result['msg'] = '新增失败！异常错误提示信息[%s]' % ret_err_msg
        if rollback_sql:
            with sjapi.connection() as db:
                db.execute( rollback_sql )
    return result
    
def data_sy_del_service( sjbid,sjbmc,syid ):
    """
    # 新增表字段
    # @param sjbid:数据表ID
    # @param sjbmc:数据表名称
    # @param syid:索引ID
    """  
    # 删除索引回滚SQL
    rollback_sql = ""
    result = {'state':False, 'msg':''}
    try:
        with sjapi.connection() as db:
            # 查询索引信息
            syxx = ModSql.kf_ywgl_011.execute_sql_dict( db,'get_syxx',{'id':syid} )[0]
            # 索引名称
            symc = syxx['symc']
            # 索引字段
            syzd = syxx['syzd']
            # 索引类型
            sylx = syxx['sylx']
            # 是否唯一索引
            sfwysy = syxx['sfwysy']
            # 查询该表的主键字段
            rs = ModSql.kf_ywgl_011.execute_sql_dict(db, "get_zjxx",{'sjbmc':sjbmc})
            # 主键字段列表
            zjzd_lst = []
            for dic in rs:
                zjzd_lst.append( dic['zjzd'] )
            # 如果索引字段与主键字段一致,说明该索引为主键索引，无法删除
            if syzd == "|".join( zjzd_lst ):
                result['msg'] = '[%s]为主键索引，不可删除'%symc
                return result
                
            # 查询该索引是否为唯一约束的索引
            count = ModSql.kf_ywgl_011.execute_sql( db,'check_yszd',{'sjbid':sjbid,'yszd':syzd} )[0].count
            if count != 0:
                result['msg'] = '[%s]为唯一约束索引，不可删除'%symc
                return result
            # 删除索引
            sql = "drop index %s"%( symc )
            db.execute( sql )
            # 拼接回滚SQL
            if sylx == 'NORMAL':
                rollback_sql = "create %s index %s on %s (%s)"%( 'unique' if sfwysy == 'UNIQUE' else '',symc,sjbmc,",".join( syzd.split("|") ) );
            elif sylx == 'NORMAL/REV':
                rollback_sql = "create %s index %s on %s (%s) reverse"%( 'unique' if sfwysy == 'UNIQUE' else '', symc,sjbmc,",".join( syzd.split("|") ) );
            elif sylx == 'BITMAP':
                rollback_sql = "create  bitmap index %s on %s (%s) "%( symc,sjbmc,",".join( syzd.split("|") ) );

            # 删除数据库索引表
            ModSql.kf_ywgl_011.execute_sql( db,'del_sjksy_by_id',{'id_lst':[syid]})
            # 更新唯一码
            update_wym( db,'sjk',sjbid )
            # 登记操作日志
            ins_czrz( db,'数据表[%s]删除[%s]索引' % ( sjbmc,symc ), gnmc = '数据表管理_删除索引' )
            # 更新数据库模型操作人、操作时间
            update_sjb( db,sjbid )
            result['state'] = True
            result['msg'] = '删除成功'
    except:
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        ret_err_msg = error_msg[error_msg.find('cx_Oracle'):]
        result['msg'] = '删除失败！异常错误提示信息[%s]' % ret_err_msg
        if rollback_sql:
            with sjapi.connection() as db:
                db.execute( rollback_sql )
    return result
    
def data_ys_add_service( sjbid,sjbmc,ysmc,yszd ):
    """
    # 新增表字段
    # @param sjbid:数据表ID
    # @param sjbmc:数据表名称
    # @param ysmc:约束名称
    # @param yszd:约束字段
    """  
    # 回滚SQL
    rollback_sql = ""
    result = {'state':False, 'msg':''}
    try:
        with sjapi.connection() as db:
            # 校验约束名称是否已存在
            count = ModSql.kf_ywgl_011.execute_sql( db,'check_ysmc',{'ysmc':ysmc})[0].count
            if count != 0 :
                result['msg'] = '约束名称[%s]已经存在，请重新输入'%ysmc
                return result
            # 校验约束字段是否已存在
            count = ModSql.kf_ywgl_011.execute_sql( db,'check_yszd',{'yszd':yszd,'sjbid':sjbid})[0].count
            if count != 0 :
                result['msg'] = '约束字段[%s]已建立约束，请重新选择'%yszd
                return result
            # 校验约束字段是否为主键字段
            rs = ModSql.kf_ywgl_011.execute_sql_dict( db,'get_zjxx',{'sjbmc':sjbmc})
            # 主键字段
            zjzd = "|".join( [ dic['zjzd'] for dic in rs ] )
            if yszd == zjzd:
                result['msg'] = '约束字段[%s]为主键字段，无需再建立唯一约束，请重新选择'%yszd
                return result
            # 创建约束SQL
            sql = "alter table %s add constraint %s unique （%s）"%( sjbmc,ysmc,",".join( yszd.split("|") ) )
            db.execute( sql )
            # 回滚SQL
            rollback_sql = "alter table %s drop constraint %s"%( sjbmc,ysmc )
            # 登记约束信息
            sql_data = { 'id':get_uuid(),'sssjb_id':sjbid,'ysmc':ysmc,'yszd':yszd }  
            ModSql.kf_ywgl_011.execute_sql_dict( db,'insert_sjkys',sql_data)
            # 因在创建唯一约束时，oracle系统会自动创建该约束的索引，索引名称同约束名称，但若已创建同名的索引，那么在创建约束时，就不会在创建改约束的索引了，此处需查询出该表下所有的索引
            rs = ModSql.kf_ywgl_011.execute_sql_dict( db,'get_oracle_sy',{'sjbmc':sjbmc})
            # 索引信息{索引名称：{syzd：索引字段，索引字段，索引类型，是否唯一索引}}
            syxx_dic = {}
            for dic in rs:
                if dic['symc'] in syxx_dic.keys():
                    syxx_dic[dic['symc']]['syzd'] = syxx_dic[dic['symc']]['syzd'] + '|' + dic['syzd']
                else:
                    syxx_dic[dic['symc']]  ={ 'syzd':dic['syzd'] ,'sylx':dic['sylx'],'sfwysy':dic['sfwysy'] }
            # 查询出数据库索引表中所有索引
            rs = ModSql.kf_ywgl_011.execute_sql_dict( db,'get_sygl',{'sjbid':sjbid})
            # 索引名称列表
            pt_symc_lst = []
            if rs:
                pt_symc_lst = [ dic['symc'] for dic in rs]
            for symc,syxx in syxx_dic.items():
                # 若oracle中的索引在数据库索引表中没有，需要添加到数据库索引表
                if symc not in pt_symc_lst:
                    sql_data = { 'id':get_uuid(),'sssjb_id':sjbid,'symc':symc,'syzd':syxx.get( 'syzd','' ),'sylx':syxx.get( 'sylx','' ),'sfwysy':syxx.get( 'sfwysy','' ) }        
                    ModSql.kf_ywgl_011.execute_sql_dict( db,'insert_sjksy',sql_data )
            # 更新唯一码
            update_wym( db,'sjk',sjbid )
            # 登记操作日志
            ins_czrz( db,'数据表[%s]新增[%s]约束' % ( sjbmc,ysmc ), gnmc = '数据表管理_新增约束' )
            # 更新数据库模型操作人、操作时间
            update_sjb( db,sjbid )
            result['state'] = True
            result['msg'] = '新增成功'
    except:
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        ret_err_msg = error_msg[error_msg.find('cx_Oracle'):]
        result['msg'] = '新增失败！异常错误提示信息[%s]' % ret_err_msg
        if rollback_sql:
            with sjapi.connection() as db:
                db.execute( rollback_sql )
    return result
  
def data_ys_del_service( sjbid,sjbmc,ysid ):
    """
    # 新增表字段
    # @param sjbid:数据表ID
    # @param sjbmc:数据表名称
    # @param ysid:约束ID
    """  
    # 删除约束回滚SQL
    rollback_sql = ""
    result = {'state':False, 'msg':''}
    try:
        with sjapi.connection() as db:
            # 查询约束信息
            ysxx = ModSql.kf_ywgl_011.execute_sql_dict( db,"get_ysxx",{'id':ysid})[0]
            # 约束名称
            ysmc = ysxx['ysmc']
            # 约束字段
            yszd = ysxx['yszd']
            # 删除约束SQL
            sql = "alter table %s drop constraint %s"%( sjbmc,ysmc )
            db.execute( sql )
            # 回滚SQL
            rollback_sql = "alter table %s add constraint %s unique （%s）"%( sjbmc,ysmc,",".join( yszd.split("|") ) )
            # 删除数据表约束表信息
            ModSql.kf_ywgl_011.execute_sql_dict( db,"del_sjkys_by_id",{'id_lst':[ysid]})
            #因在创建约束时，会自动创建索引，所以删除时，也会自动将该索引删除。但是如果再建立约束时，已经创建了与该约束名称同名的索引，那么在删除约束后，该索引不会自动删除，所以需要查询出该表下所有的索引，进行判断
            rs = ModSql.kf_ywgl_011.execute_sql_dict( db,"get_symc",{'sjbmc':sjbmc})
            # 删除多余的索引 
            symc_lst = [ ('symc',dic['symc']) for dic in rs]
            ModSql.kf_ywgl_011.execute_sql_dict( db,"del_sjksy_by_symc",{'symc_lst':symc_lst,'sjbid':sjbid})
        
            # 更新唯一码
            update_wym( db,'sjk',sjbid )
            # 登记操作日志
            ins_czrz( db,'数据表[%s]删除[%s]约束' % ( sjbmc,ysmc ), gnmc = '数据表管理_删除约束'  )
            # 更新数据库模型操作人、操作时间
            update_sjb( db,sjbid )
            result['state'] = True
            result['msg'] = '删除成功'
    except:
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        ret_err_msg = error_msg[error_msg.find('cx_Oracle'):]
        result['msg'] = '删除失败！异常错误提示信息[%s]' % ret_err_msg
        if rollback_sql:
            with sjapi.connection() as db:
                    db.execute( rollback_sql )
    return result
    
def data_sjbtbls_service( ywid,ksrq,jsrq,rn_start,rn_end):
    """
    # 获取数据库模型列表展示数据
    # @param ywid:业务ID
    # @param ksrq:开始日期
    # @param jsrq:结束日期
    # @param rn_start:开始的rownum
    # @param rn_end:结束的rownum
    """
    with sjapi.connection() as db:
        # 查询数据库模型总记录
        sql_data = {'ywid':ywid}
        if ksrq and jsrq:
            sql_data.update({'ksrq':ksrq,'jsrq':jsrq})
        total = ModSql.kf_ywgl_011.execute_sql(db, "get_sjbtbls_count",sql_data)[0].count
        # 查询数据库模型信息
        sql_data.update( {'rn_start':rn_start,'rn_end':rn_end} )
        jbxx = ModSql.kf_ywgl_011.execute_sql_dict(db, "get_sjbtbls",sql_data)
        return {'total':total,'rows':jbxx}

def data_tbxx_sjb_service( tblsid,sjbid ):
    """
    # 获取数据表的同步信息
    # @param tblsid:同步流水ID
    # @param sjbid:数据表ID
    """
    data = {}
    with sjapi.connection() as db:
        rs = ModSql.kf_ywgl_011.execute_sql(db, "get_sjbmcms_by_tb",{'tblsid':tblsid})
        if rs:
            rs = rs[0]
            data['tbqsjbmcms'] = rs.tbqsjbmcms
            data['tbhsjbmcms'] = rs.tbhsjbmcms
        else:
            rs = ModSql.kf_ywgl_011.execute_sql(db, "get_sjbmcms",{'sjbid':sjbid})[0]
            data['tbqsjbmcms'] = rs.sjbmcms
            data['tbhsjbmcms'] = rs.sjbmcms
        data['state'] = True
        return data
        
def data_tbxx_sy_service( tblsid ):
    """
    # 获取数据表索引同步信息
    # @param tblsid:同步流水ID
    """
    with sjapi.connection() as db:
        rows = sjk_tbxxzs( db,tblsid,'2' )
        return {'rows':rows,'state':True}
        
def data_tbxx_ys_service( tblsid ):
    """
    # 获取数据表约束同步信息
    # @param tblsid:同步流水ID
    """
    with sjapi.connection() as db:
        rows = sjk_tbxxzs( db,tblsid,'3' )
        return {'rows':rows,'state':True}
        
def data_tbxx_zd_service( tblsid ):
    """
    # 获取数据表字段同步信息
    # @param tblsid:同步流水ID
    """
    with sjapi.connection() as db:
        rows = sjk_tbxxzs( db,tblsid,'1' )
        return {'rows':rows,'state':True}
    
def data_zdgl_service( sjbid ):
    """
    # 获取字段管理数据
    # @param sjbid:数据表ID
    """
    with sjapi.connection() as db:
        rs = ModSql.kf_ywgl_011.execute_sql_dict(db, "get_zdgl",{'sjbid':sjbid})
        return {'rows':rs,'state':True}
        
def data_sygl_service( sjbid ):
    """
    # 获取索引管理数据
    # @param sjbid:数据表ID
    """
    with sjapi.connection() as db:
        rs = ModSql.kf_ywgl_011.execute_sql_dict(db, "get_sygl",{'sjbid':sjbid})
        return {'rows':rs,'state':True}
        
def data_ysgl_service( sjbid ):
    """
    # 获取约束管理数据
    # @param sjbid:数据表ID
    """
    with sjapi.connection() as db:
        rs = ModSql.kf_ywgl_011.execute_sql_dict(db, "get_ysgl",{'sjbid':sjbid})
        return {'rows':rs,'state':True}
        
def data_bef_zd_edit_service( id ):
    """
    # 编辑字段时，获取字段信息
    # @param id:字段ID
    """      
    with sjapi.connection() as db:
        rs = ModSql.kf_ywgl_011.execute_sql_dict(db, "get_zdxx",{'id':id})[0]
        return rs
        
def data_load_zd_service( sjbid ):
    """
    # 新增索引或约束时，获取字段名称下拉框数据
    # @param sjbid:数据表ID
    """  
    with sjapi.connection() as db:
        rs = ModSql.kf_ywgl_011.execute_sql_dict(db, "get_select_zd",{'sjbid':sjbid})        
        return {'zdmc_lst':rs,'state':True}
        
def sjk_tbxxzs(db, tblsid, tbnrlx):
    """
    #根据传入的同步内容类型，获取指定同步流水下具体的同步信息
    # @param tblsid:同步流水ID
    # @param tbnrlx:同步内容类型 1:字段 2:索引 3:约束
    """
    rs = ModSql.kf_ywgl_011.execute_sql_dict(db, "get_sjbtbxx",{'tblsid':tblsid,'tbnrlx':tbnrlx})
    result = {}
    for dic in rs:
        # 对结果集进行处理，先将同一名称的属性变更组织起来
        if dic['tbnrmc'] not in result.keys():
            result[dic['tbnrmc']] = {}
            result[dic['tbnrmc']]['tblx'] = dic['tblx']
        result[dic['tbnrmc']][dic['tbnrsx']+"_q"] = dic['tbqsxz'] or ''
        result[dic['tbnrmc']][dic['tbnrsx']+"_h"] = dic['tbhsxz'] or ''
    # 组织结果集
    tbnrmc = 'zdmc' if tbnrlx == '1' else  'symc' if tbnrlx == '2' else 'ysmc'
    rs = []
    for mc,xx in result.items():
        dic = {tbnrmc: mc}
        dic.update(xx) 
        rs.append(dic)
    return rs
    
def update_sjb(db, sjbid):
    """
        # 更新数据表的操作人、操作时间
    """
    hydm = get_sess_hydm()
    czsj = get_strftime()
    sql_data = {'czr':hydm,'czsj':czsj,'id':sjbid}
    ModSql.kf_ywgl_011.execute_sql( db,'upd_sjkmx',sql_data)