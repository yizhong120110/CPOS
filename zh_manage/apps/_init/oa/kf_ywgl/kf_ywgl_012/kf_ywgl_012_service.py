# -*- coding: utf-8 -*-
# Action: 数据库表信息查看 service
# Author: zhangchl
# AddTime: 2014-12-30
# Standard: 注释仅能以“#”开头，sql可以是“--”；注释不能同代码在同一行
# Explain: 由于本功能特殊，所以允许将sql下载此py中

from sjzhtspj import ModSql, settings
from sjzhtspj.common import ins_czrz
from sjzhtspj.const import STRING_ZD_LST


def index_service( data_dic ):
    """
    # 数据库表信息查看：主页面
    """
    # 反馈信息
    sjkmxdy_dic = {'sjkmxdy_id':data_dic['sjkmxdy_id'], 'sjbmc':'', 'sjbms':'', 'sjbzwmc':''}
    data = {'sjkmxdy_dic':sjkmxdy_dic, 'dg_columns': [], 'error_msg': '', 'demojbxxid': data_dic['demojbxxid'], 'lx': data_dic['lx']}
    # 数据库操作
    with sjapi.connection() as db:
        # 获取数据表名称
        sjkmxdy_obj = ModSql.kf_ywgl_012.execute_sql( db, 'index_sjbmc', data_dic )[0]
        # 判断是否存在此表信息
        if sjkmxdy_obj:
            # 数据表名称
            sjkmxdy_dic['sjbmc'] = sjkmxdy_obj.sjbmc.upper()
            # 数据表中文名称
            sjkmxdy_dic['sjbms'] = sjkmxdy_obj.sjbmcms
            
            # 获取数据表中文名
            zwmc_dic = { 'sjbmc': sjkmxdy_dic['sjbmc'] }
            sjkmxdy_zwmc_obj = sjkmxdy_obj = ModSql.kf_ywgl_012.execute_sql( db, 'index_zwmc', zwmc_dic )[0]
            if sjkmxdy_zwmc_obj:
                sjkmxdy_dic['sjbzwmc'] = sjkmxdy_zwmc_obj.comments
            
            # 获取表字段及描述
            # sfkk（是否可空）: N(不可空)，Y(可空)
            # zjtype（主键类型）：s（是），f（否）
            zd_ms_obj_lst = ModSql.kf_ywgl_012.execute_sql_dict( db, 'index_zd_ms', zwmc_dic )
            
            # 赋值
            data['sjkmxdy_dic'] = sjkmxdy_dic
            data['dg_columns'] = zd_ms_obj_lst
        else:
            # 传入的id不对时做出操作，系统正常情况下是不会发生这种现象
            data['error_msg'] =  "<script>alert('此数据模型不存在');</script>"
    
    return data

def data_service( data_dic ):
    """
    # 数据库表信息查看：获取显示数据
    """
    # 反馈信息
    data = {'total':0, 'rows':[]}
    # 数据库操作
    with sjapi.connection() as db:
        # 对date数据类型特殊处理
        # 字段名称，字段描述，字段长度，是否可控，数据类型, 小数位数, 总位数
        zd_date_lst = []
        for zdxx in data_dic['zdxx_str'].split('|'):
            if zdxx.strip(' ') != '':
                zdxx_lst = zdxx.split(',')
                if zdxx_lst[4] == 'DATE':
                    zd_date_lst.append( zdxx_lst[0] )
        # 定义查询字段信息
        sel_zdmc_str = ','.join( [ ( "TO_CHAR(%s, 'YYYY-MM-DD') as %s" % ( zdmc, zdmc ) if zdmc in zd_date_lst else zdmc ) for zdmc in data_dic['zdmc_str'].split(',') ] )
        
        # 存在查询条件
        subsql = ''
        sql_dic = {}
        if data_dic['search_value']:
            subsql = " and %s = :%s " % ( data_dic['search_name_sel'], data_dic['search_name'] )
            sql_dic[data_dic['search_name']] = data_dic['search_value']
        
        # 查询总条数  
        sql_count = """
           select count(1) as count
           from %s
           where 1 = 1 %s
        """ % ( data_dic['sjbmc'], subsql )
        total = db.execute( sql_count, sql_dic ).fetchone()['count']
        
        # 获取当前页面显示信息
        # 排序
        if data_dic['sjbzj_str']:
            subsql += """
                    order by %s
            """ % data_dic['sjbzj_str']
        sql_data = """
            select  %s
            from (
                select %s, rownum rn
                from (
                    select %s
                    from %s
                    where 1 = 1 %s
                )
            )
            where rn >= :rn_start and rn <= :rn_end
        """ % ( data_dic['zdmc_str'], data_dic['zdmc_str'], sel_zdmc_str, data_dic['sjbmc'], subsql )
        sql_dic.update( { 'rn_start': data_dic['rn_start'], 'rn_end': data_dic['rn_end'] } )
        data_row = db.execute( sql_data, sql_dic ).fetchall()
        # 组织反馈值
        data['total'] = total
        data['rows'] = data_row
        
    return data

def data_add_service( data_dic ):
    """
    # 数据库模型 表信息 新增 提交
    """
    # 反馈信息
    result = {'state':False, 'msg':''}
    # 主键字段集合lst
    zjzd_lst = data_dic['zjzd_str'].split(',')
    # check限定条件数据
    data_check = dict( [ [ zjzd, data_dic['new_dic'].get( zjzd, '' ) ] for zjzd in zjzd_lst ] )
    # 对date数据类型特殊处理
    zd_date_lst = []
    # 需要添加单引号的字段
    string_zdmc_lst = []
    for zdxx in data_dic['zdxx_str'].split('|'):
        if zdxx.strip(' ') != '':
            zdxx_lst = zdxx.split(',')
            if zdxx_lst[4] == 'DATE':
                zd_date_lst.append( zdxx_lst[0] )
            if zdxx_lst[4] in STRING_ZD_LST:
                string_zdmc_lst.append( zdxx_lst[0] )
    
    with sjapi.connection() as db:
        # 判断主键是否重复
        sql_check = """
            select count(1) as count from %s
            where %s
        """ % ( data_dic['czsjbmc'], 
        ' and '.join( [ ( 'TO_CHAR(%s, \'YYYY-MM-DD\')= :%s' % ( zjzd, zjzd ) if zjzd in zd_date_lst else '%s= :%s' % ( zjzd, zjzd ) ) for zjzd in zjzd_lst ] ) )
        rs_check = db.execute(sql_check, data_check).fetchone()['count']
        if rs_check > 0:
            # 数据已经存在
            result['msg'] = '数据[%s]已存在，不允许再次新增' % ( ','.join( sorted( data_check.values() ) ) )
        else:
            # 系统中不存在则插入数据库
            # 对date类型数据进行处理
            new_dic = data_dic['new_dic']
            if settings.DB_TYPE == 'oracle':
                new_dic = dict( [ [ k, ( 'TO_DATE(\'%s\', \'YYYY-MM-DD\')' % ( v ) if k in zd_date_lst else v ) ] for k, v in data_dic['new_dic'].items() ] )
            # 对sql进行处理，是否需要添加单引号
            zdmc_lst = [ "'%(" + zdmc + ")s'" if zdmc not in string_zdmc_lst else "%(" + zdmc + ")s" for zdmc in data_dic['zdmc_lst'] ]
            
            sql_insert = """ 
                insert into %s( %s ) 
                values ( %s ) """ % ( data_dic['czsjbmc'], data_dic['zdmc_str'], ','.join( zdmc_lst ) )
            db.execute(sql_insert % new_dic)
            # 插入字段信息
            rzxx_str = ''
            for k in data_dic['zdmc_lst']:
                rzxx_str = '%s，%s：%s' % ( rzxx_str, k, data_dic['new_dic'][k] )
            ins_czrz( db, '数据模型[%s]中表信息新增：[%s]' % ( data_dic['czsjbmc'], rzxx_str[1:]), gnmc = '数据库管理_表信息新增' )

            # 组织反馈信息
            result['state'] = True
            result['msg'] = '插入成功'
    
    return result

def data_edit_service( data_dic ):
    """
    # 数据库模型 表信息 编辑 提交
    """
    # 反馈信息
    result = {'state':False, 'msg':''}
    
    # 对date数据类型特殊处理
    zd_date_lst = []
    # 需要添加单引号的字段
    string_zdmc_lst = []
    # 遍历所有数据表字段信息
    for zdxx in data_dic['zdxx_str'].split('|'):
        if zdxx.strip(' ') != '':
            zdxx_lst = zdxx.split(',')
            if zdxx_lst[4] == 'DATE':
                zd_date_lst.append( zdxx_lst[0] )
            if zdxx_lst[4] not in STRING_ZD_LST:
                string_zdmc_lst.append( zdxx_lst[0] )
    
    # 对date类型数据进行处理
    if settings.DB_TYPE == 'oracle':
        data_dic['upd_dic'] = dict( [ [ k, ( 'TO_DATE(\'%s\', \'YYYY-MM-DD\')' % ( v ) if k in zd_date_lst else v ) ] for k, v in data_dic['upd_dic'].items() ] )
    # 修改数据表 表数据
    upd_str = ', '.join( [ k + "='%(" + k + ")s'" if k in string_zdmc_lst else k + "=%(" + k + ")s" for k in data_dic['upd_dic'].keys() ] )
    
    # 判断是否有要修改的字段，无则直接返回
    if upd_str == '':
        result['msg'] = '没有可修改的字段，无需保存'
        return result
    
    # 追加上主键信息
    data_dic['upd_dic'].update( data_dic['sjbzjzd_dic'] )
    # 主键限定条件
    zj_lst = []
    for k in data_dic['sjbzjzd_dic'].keys():
        if k in string_zdmc_lst:
            zj_lst.append( k + "='%(" + k + ")s'" )
        else:
            if k in zd_date_lst:
                zj_lst.append( "TO_CHAR(%s, \'YYYY-MM-DD\')" % k + "='%(" + k + ")s'" )
            else:
                zj_lst.append( k + "=%(" + k + ")s" )
    zj_str = ' and '.join( zj_lst )
    
    with sjapi.connection() as db:
        # 信息插叙条件
        serch_ = ''
        for k in data_dic['sjbzjzd_dic'].items():
            serch_ = "%s %s='%s' and" % ( serch_, k[0], k[1] )
        # 修改前信息查询
        sql_select = """
            select * from %s where %s
        """ % ( data_dic['czsjbmc'], serch_[:-3])
        rs_sel = db.execute(sql_select).fetchall()
        sql_upd = """
            update %s set %s
            where %s
        """ % ( data_dic['czsjbmc'], upd_str, zj_str )
        db.execute( sql_upd % data_dic['upd_dic'] )
        rzxx_bjh = ''
        for k in list(data_dic['upd_dic']):
            rzxx_bjh = "%s, '%s': '%s'" % ( rzxx_bjh, k, data_dic['upd_dic'][k] if data_dic['upd_dic'][k] else '' )
        ins_czrz( db, '数据模型[%s]中表信息：修改前[%s]；修改后[%s]' % ( data_dic['czsjbmc'], str(rs_sel[0])[1:-1], rzxx_bjh[1:]), gnmc = '数据库管理_表信息编辑' )
        
        result['state'] = True
        result['msg'] = '修改成功'
    
    return result
    
def data_del_service( data_dic ):
    """
    # 表信息删除 提交
    """
    # 反馈信息
    result = {'state':False, 'msg':''}
    # 组织数据
    ids_lst = data_dic['ids'].split(',')
    # 主键字段列表
    sjbzjzd_lst = []
    # 删除信息列表
    data_lst = []
    # 对date数据类型特殊处理
    zd_date_lst = []
    sjbzj_lst = ids_lst[0].split('~')
    for xx in sjbzj_lst:
        if xx.split('|')[2] == 'DATE':
            zd_date_lst.append( xx.split('|')[0] )
    
    for zjxx in ids_lst:
        # 主键信息列表
        sjbzj_lst = zjxx.split('~')
        
        # 获取主键列表
        if sjbzjzd_lst == []:
            sjbzjzd_lst = [ xx.split('|')[0] for xx in sjbzj_lst ]
        
        # 主键信息字典
        sjbzjxx_dic = dict( [ [xx.split('|')[0],xx.split('|')[1]] for xx in sjbzj_lst ] )
        # 追加到删除列表中
        data_lst.append( sjbzjxx_dic )
    
    # 执行时SQL
    with sjapi.connection() as db:
        # 联合主键限定条件
        zj_sql = ' and '.join( [ ( 'TO_CHAR(%s, \'YYYY-MM-DD\')= :%s' % ( zjzd, zjzd ) if zjzd in zd_date_lst else '%s= :%s' % ( zjzd, zjzd ) ) for zjzd in sjbzjzd_lst ] )
        # 删除sql
        sql_del = """
            delete from %s
            where %s
        """ % ( data_dic['sjbmc'], zj_sql )
        db.execute(sql_del, data_lst)
        # 登记操作日志
        ins_czrz( db, '数据模型[%s]中[%s]已被删除' % ( data_dic['sjbmc'], data_dic['ids'] ), gnmc = '数据库管理_表信息删除' )
        result['state'] = True
        result['msg'] = '删除成功'
    
    return result