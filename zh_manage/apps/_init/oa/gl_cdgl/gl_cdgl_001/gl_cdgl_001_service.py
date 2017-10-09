# -*- coding: utf-8 -*-
# Action: 菜单管理
# Author: houpp
# AddTime: 2015-05-26
# Standard: 注释仅能以“#”开头，sql可以是“--”；注释不能同代码在同一行

from sjzhtspj import ModSql
from sjzhtspj.common import get_bmwh_bm,get_uuid, get_sess_hydm, get_strftime, get_strftime2, ins_czrz
from sjzhtspj import  get_sess

def index_service(params):
    """
    # 页面初始加载（包含按钮权限）
    :return:
    """
    # 登录用户ID
    yhid = get_sess('hyid')
    # 初始化返回值
    data = {'an_lst':[]}
    # 数据库链接
    with sjapi.connection() as db:
        sql_data={'cddm':params['cddm'],'yhid':yhid}
        # 获取菜单对应的按钮列表
        # anqx_lst = ModSql.gl_cdgl_001.execute_sql_dict(db, "get_anqx",sql_data)
        anqx_lst = ModSql.common_anqx.execute_sql_dict(db, "get_anqx",sql_data)

        data['an_lst']=anqx_lst
    return  data

def lst_service(params):
    # 初始化返回值
    data = {'sjcd_lst': [],'cdfl_lst': [],'dlxt_lst':[],'gnxx':{},'cdxx':{}}
    data['cdfl_lst'].insert(0, {'value': '-1', 'text': '请选择'})
    data['dlxt_lst'].insert(0, {'value': '-1', 'text': '请选择'})
    # 数据库链接
    with sjapi.connection() as db:
        # 菜单分类列表
        data['cdfl_lst'].extend(get_bmwh_bm( '10025', db=db ))
        # 登录系统列表获取
        data['dlxt_lst'].extend(get_bmwh_bm('10005',db=db))
        # 根节点列表初始化
        gjd_dic = {'fjdid':'0'}
        # 获取菜单列表
        cd_lst = ModSql.gl_cdgl_001.execute_sql_dict(db, "data_cd_rs")
        # 调用递归函数
        cd_tree(cd_lst,'0',gjd_dic)
        # 将查询详情结果放到结果集中
        if gjd_dic.get('children'):
            data['sjcd_lst'] = gjd_dic['children']
        if params['cdid']:
             cd_lst= ModSql.gl_cdgl_001.execute_sql_dict(db, "get_cdxx_edit", {'id':params['cdid']})
             if len(cd_lst):
                 data['cdxx']=cd_lst[0]
                 data['state']=True
             else:
                 data['msg']='查询编辑菜单信息失败'

        elif params['gnid']:
            gn_lst= ModSql.gl_cdgl_001.execute_sql_dict(db, "get_gnxx_edit", {'id':params['gnid']})
            if len(gn_lst):
                data['gnxx'] =gn_lst[0]
                data['state']=True
            else:
                data['msg']='查询编辑按钮信息失败'
        else:
            data['state']=True
        return data

def data_service():
    # 初始化返回值
    data = {'total': 0, 'rows': []}
    # 数据库链接
    with sjapi.connection() as db:
        # 根节点列表初始化
        gjd_dic = {'fjdid':'0'}

        sql_data = {'fjdid':'0'}
        # 获取菜单列表
        cd_lst = ModSql.gl_cdgl_001.execute_sql_dict(db, "data_cd_rs")
        # 调用递归函数
        cd_tree(cd_lst,'0',gjd_dic)
        # 将查询详情结果放到结果集中
        if gjd_dic.get('children'):
            data['rows'] = gjd_dic['children']
        # 获取数据总数
        lbxx_lst = ModSql.gl_cdgl_001.execute_sql_dict(db, "data_sjcd_rs",sql_data)
        data['total'] = len(lbxx_lst)
        # 将查询到的结果反馈给view
        return data

def cd_tree(lst,pId,k):
    """
    # 获取部门树结构
    :return:
    """
    aLst=[]
    for m in lst:
        if m['fjdid'] == pId:
            aLst.append(m)
    if aLst:
        k['children']=aLst
        for l in aLst:
            cd_tree(lst,l['id'],l)

def get_childid(db,lst,child_lst):
    """
    # 递归获取子节点id
    :param db: 数据库连接db
    :param lst: 孩子列表
    :return: 孩子id列表
    """
    # 获取孩子ID
    for k in lst:
        child_lst.append(k['id'])
        if k.get('children'):
            get_childid(db ,k['children'],child_lst)

def gnlb_service(params):
    """
    # 获取功能列表
    :return:
    """
    # 初始化返回值
    data = {'total': 0, 'rows': []}
    # 获取菜单id
    sql_data = {'sscdid':params['cdid']}
    # 数据库链接
    with sjapi.connection() as db:
        # 获取菜单对应的功能列表
        gnlb_lst = ModSql.gl_cdgl_001.execute_sql_dict(db, "data_gnlb_rs",sql_data)
        data['rows'] = gnlb_lst
        # 获取功能列表总数
        data['total'] = len(gnlb_lst)
        # 将查询到的结果反馈给view
        return data

def data_add_service(params):
    """
    # 新增菜单
    :param params:
    :return:
    """
    result = {'state':False, 'msg':''}
    #获取菜单id
    cdid = get_uuid()
    #操作人
    czr = get_sess_hydm()
    # 操作时间
    czsj = get_strftime()
    with sjapi.connection() as db:
        # 校验菜单代码是否存在
        sql_data = {'cddm': params['cddm'], 'fjdid':params['sjcd']}
        rs = ModSql.gl_cdgl_001.execute_sql(db, "check_cddm", sql_data)
        if rs:
            result['msg'] = '菜单代码[%s]已经存在，请重新输入' % params['cddm']
            return result
        # 校验菜单名称是否存在
        sql_data = {'cdmc': params['cdmc'], 'fjdid':params['sjcd']}
        rs = ModSql.gl_cdgl_001.execute_sql(db, "check_cdmc", sql_data)
        if rs:
            result['msg'] = '菜单名称[%s]已经存在，请重新输入' % params['cdmc']
            return result


        # 插入菜单基本信息表
        sql_data = {
            'id':cdid,
            'cddm':params['cddm'],
            'cdmc': params['cdmc'],
            'url':params['url'],
            'cdfl': params['cdfl'],
            'sjcd':params['sjcd'],
            'ssxt':params['ssxt'],
            'bz':params['bz'],
            'pxh':params['pxh'],
            'scbz':'0',
            'ly':'1',
            'zt':'1',
            'czr':czr,
            'czsj':czsj
        }
        ModSql.gl_cdgl_001.execute_sql(db, "insert_cdxx", sql_data)

        #登记操作日志
        rznr = '菜单管理-菜单新增：菜单名称[%s]，菜单id: [%s],' % (params['cdmc'],cdid )
        ins_czrz(db,rznr,'gl','菜单管理-菜单新增')
        result['state'] = True
        result['msg'] = '新增成功'

    return result

def data_edit_service(params):
    """
    # 编辑菜单
    :param params:
    :return:
    """
    result = {'state':False, 'msg':''}
    #操作人
    czr = get_sess_hydm()
    # 操作时间
    czsj = get_strftime()
    with sjapi.connection() as db:
        # 查询编辑前的信息
        sql_data = {'id':params['cdid']}
        old_data = ModSql.gl_cdgl_001.execute_sql_dict(db, "get_cdxx_edit",sql_data )[0]

        # 校验菜单名称是否存在
        sql_data = {'cdmc': params['cdmc'], 'id':params['cdid'], 'fjdid':params['sjcd']}
        rs = ModSql.gl_cdgl_001.execute_sql(db, "check_cdmc", sql_data)
        if rs:
            result['msg'] = '菜单名称[%s]已经存在，请重新输入' % params['cdmc']
            return result

        # 校验所属上级菜单选择的是否正确
        # 排除自己
        if params['sjcd'] == params['cdid']:
            result['msg'] = '所属上级菜单不能选择自己，请重新选择'
            return result
        # 排除孩子
        children_dic = {'fjdid':params['cdid']}
        childid_lst=[]
        # 获取菜单列表
        cd_lst = ModSql.gl_cdgl_001.execute_sql_dict(db, "data_cd_rs")
        # 调用递归函数
        cd_tree(cd_lst,params['cdid'],children_dic)
        if children_dic.get('children'):
            get_childid(db,children_dic['children'],childid_lst)

        if params['sjcd']  in childid_lst:
            result['msg'] = '所属上级菜单不能选择自己的子菜单，请重新选择'
            return result

        # 更新菜单基本信息表
        sql_data = {
            'id':params['cdid'],
            'cdmc': params['cdmc'],
            'url':params['url'],
            'cdfl': params['cdfl'],
            'sjcd':params['sjcd'],
            'ssxt':params['ssxt'],
            'bz':params['bz'],
            'pxh':params['pxh'],
            'czr':czr,
            'czsj':czsj
        }
        ModSql.gl_cdgl_001.execute_sql(db, "update_cdxx", sql_data)

        #登记操作日志
        rz_data = {'old_data':str(old_data), 'new_data':sql_data}
        rznr = '菜单管理-菜单更新：编辑前信息[%(old_data)s],编辑后信息[%(new_data)s]' % rz_data
        ins_czrz(db,rznr,'gl','菜单管理-菜单更新')
        result['state'] = True
        result['msg'] = '编辑成功'

    return result

def del_cd_service(params):
    """
    # 删除菜单
    :return:
    """
     # 初始化返回值
    result = {'state':False, 'msg':""}
    #菜单ID列表
    sql_para = { 'id': params['id']}
    # 数据库链接
    with sjapi.connection() as db:
        # 判断是否是铺底数据
        if params['ly']=='2':
            result['msg'] = '当前菜单[%s]为系统预置数据，不允许删除' % params['cdmc']
            return result
        #查询孩子菜单信息
        rs  = ModSql.gl_cdgl_001.execute_sql_dict(db,"get_zjd",sql_para)
        if rs:
            result['msg'] = '当前菜单[%s]存在子菜单，不允许删除' % params['cdmc']
            return result

        # 删除菜单对应的用户权限
        ModSql.gl_cdgl_001.execute_sql_dict(db,"delete_cdyhqx",sql_para)

        # 删除菜单对应的功能对应的用户权限
        # 获取菜单对应的功能对应的按钮权限
        yhan_lst=ModSql.gl_cdgl_001.execute_sql_dict(db,"get_cdAnYhQx",sql_para)
        if len(yhan_lst):
            ids = [k['qxid'] for k in yhan_lst]
            ModSql.gl_cdgl_001.execute_sql_dict(db,"del_cdAnYhQx",{'ids':ids})

        # 删除菜单对应的角色权限
        ModSql.gl_cdgl_001.execute_sql_dict(db,"delete_cdjsqx",sql_para)

        # 删除菜单对应的功能对应的角色权限
        # 获取菜单对应的功能对应的按钮权限
        jsan_lst=ModSql.gl_cdgl_001.execute_sql_dict(db,"get_cdAnJsQx",sql_para)
        if len(jsan_lst):
            ids = [k['qxid'] for k in jsan_lst]
            ModSql.gl_cdgl_001.execute_sql_dict(db,"del_cdAnJsQx",{'ids':ids})

        # 删除菜单对应功能
        ModSql.gl_cdgl_001.execute_sql_dict(db,"delete_cdgn",sql_para)

        # 删除菜单信息
        sql_para.update({'czr':get_sess_hydm(), 'czsj':get_strftime()})
        ModSql.gl_cdgl_001.execute_sql_dict(db,"delete_cd",sql_para)

        #登记操作日志
        rznr = '菜单管理-删除：待删除菜单信息：菜单名称[%s],菜单ID[%s]'%(params['cdmc'],params['id'])
        ins_czrz(db,rznr,'gl','菜单管理-删除')

        #成功后返回成功信息
        result['msg'] = '删除记录成功'
        result['state'] = True
    # 将查询到的结果反馈给view
    return result

def data_addGn_service(params):
    """
    #  增加功能
    :return:
    """
    result = {'state':False, 'msg':''}
    #获取部门id
    gnid = get_uuid()
    #操作人
    czr = get_sess_hydm()
    # 操作时间
    czsj = get_strftime()
    with sjapi.connection() as db:
        if params['cdid'] == "":
            result['msg'] = '请先选择菜单，再添加对应的功能'
            return result

        # 校验当前菜单下功能代码是否存在
        sql_data = {'cdid': params['cdid'],'gndm': params['gndm']}
        rs = ModSql.gl_cdgl_001.execute_sql(db, "check_gndm", sql_data)
        if rs:
            result['msg'] = '当前菜单[%s]下功能代码[%s]已经存在，请重新输入' % (params['cdmc'],params['gndm'])
            return result
        # 校验当前菜单下功能名称是否存在
        sql_data = {'cdid': params['cdid'],'gnmc': params['gnmc']}
        rs = ModSql.gl_cdgl_001.execute_sql(db, "check_gnmc", sql_data)
        if rs:
            result['msg'] = '当前菜单[%s]下功能名称[%s]已经存在，请重新输入' % (params['cdmc'],params['gnmc'])
            return result

        # 插入功能信息表
        sql_data = {
            'id':gnid,
            'gnmc': params['gnmc'],
            'gndm':params['gndm'],
            'bz':params['bz'],
            'sscdid':params['cdid'],
            'czr':czr,
            'czsj':czsj
        }
        ModSql.gl_cdgl_001.execute_sql(db, "insert_gnxx", sql_data)

        #登记操作日志
        rznr = '菜单管理-功能新增：菜单名称[%s]，功能名称[%s],' % (params['cdmc'],params['gnmc'] )
        ins_czrz(db,rznr,'gl','菜单管理-功能新增')
        result['state'] = True
        result['msg'] = '新增功能成功'

    return result

def data_editGn_service(params):
    """
    # 编辑功能
    :return:
    """
    result = {'state':False, 'msg':''}
    #操作人
    czr = get_sess_hydm()
    # 操作时间
    czsj = get_strftime()
    with sjapi.connection() as db:
        # 根据菜单id获取菜单名称
        sql_data = {'id': params['cdid']}
        rs_cdmc = ModSql.gl_cdgl_001.execute_sql(db, "get_cdxx", sql_data)
        cdmc = ','.join(['%s'% k['cdmc'] for k in rs_cdmc])

        # 校验当前菜单下功能名称是否存在
        sql_data = {'cdid': params['cdid'],'gnmc': params['gnmc'],'id':params['gnid']}
        rs = ModSql.gl_cdgl_001.execute_sql(db, "check_gnmc", sql_data)
        if rs:
            result['msg'] = '当前菜单[%s]下功能名称[%s]已经存在，请重新输入' % (cdmc,params['gnmc'])
            return result
        # 获取编辑前信息
        # 查询编辑前的信息
        sql_data = {'id':params['gnid']}
        old_data = ModSql.gl_cdgl_001.execute_sql_dict(db, "get_gnxx_edit",sql_data )[0]

        # 更新功能基本信息表
        sql_data = {
            'id':params['gnid'],
            'gnmc': params['gnmc'],
            'bz':params['bz'],
            'czr':czr,
            'czsj':czsj
        }
        ModSql.gl_cdgl_001.execute_sql(db, "update_gnxx", sql_data)

        #登记操作日志
        rz_data = {'cdmc':cdmc, 'old_data':str(old_data), 'new_data':sql_data}
        rznr = '菜单管理-功能更新：菜单名称[%(cdmc)s]，编辑前信息[%(old_data)s],编辑后信息[%(new_data)s]' % rz_data
        ins_czrz(db,rznr,'gl','菜单管理-功能更新')
        result['state'] = True
        result['msg'] = '更新功能成功'

    return result

def del_gn_service(params):
    """
    # 批量删除功能数据
    :param params:
    :return:
    """
    # 初始化返回值
    result = {'state':False, 'msg':""}
    #菜单功能ID列表
    ids = params['ids'].split(',')
    sql_para = { 'ids':ids}
    # 数据库链接
    with sjapi.connection() as db:
        #查询功能信息
        rs  = ModSql.gl_cdgl_001.execute_sql_dict(db,"select_gn_rz",sql_para)
        #拼操作日志中的字符串: 功能名称（功能代码）
        rz = ', '.join(['%s(%s)' % (k['gnmc'], k['gndm']) for k in rs])

        # 删除对应的用户按钮权限
        ModSql.gl_cdgl_001.execute_sql_dict(db,"del_cdAnYhQx",sql_para)

        # 删除对应的角色按钮权限
        ModSql.gl_cdgl_001.execute_sql_dict(db,"del_cdAnJsQx",sql_para)

        #删除功能信息
        sql_para.update({'czr':get_sess_hydm(), 'czsj':get_strftime()})
        ModSql.gl_cdgl_001.execute_sql_dict(db,"delete_gn",sql_para)

        #登记操作日志
        rznr = '菜单管理-功能删除：菜单名称：[%s],' %(params['cdmc']) +' 待删除功能信息：【'+ rz +'】'
        ins_czrz(db,rznr,'gl','菜单管理-功能删除')

        #成功后返回成功信息
        result['msg'] = '删除记录成功'
        result['state'] = True
    # 将查询到的结果反馈给view
    return result





