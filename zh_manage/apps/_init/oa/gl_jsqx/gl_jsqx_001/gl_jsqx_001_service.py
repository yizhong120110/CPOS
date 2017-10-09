# -*- coding: utf-8 -*-
# Action: 角色权限管理
# Author: houpp
# AddTime: 2015-06-02
# Standard: 注释仅能以“#”开头，sql可以是“--”；注释不能同代码在同一行

from sjzhtspj import ModSql
from sjzhtspj.common import  get_sess_hydm, get_strftime, get_strftime2, ins_czrz

def jslst_service():
    """
    # 获取角色列表
    :return:
    """
    # 初始化返回值
    data = {'total':0,'rows':[]}
    # 数据库链接
    with sjapi.connection() as db:
        # 查询角色列表
        lbxx = ModSql.gl_jsqx_001.execute_sql_dict(db, "data_js_rs")
        # 将总条数放到结果集中
        data['total'] = len(lbxx)
        # 将查询详情结果放到结果集中
        data['rows'] = lbxx
        # 将查询到的结果反馈给view
        return data

def data_service(params):
    """
    # 获取菜单列表
    :param params:
    :return:
    """
    # 初始化返回值
    data = {'total': 0, 'rows': [],'exist_lst':[]}
    #角色id
    sql_data = {'jsid': params['jsid']}
    # 数据库链接
    with sjapi.connection() as db:
        # 获取角色已有菜单权限
        jsqx_lst = ModSql.gl_jsqx_001.execute_sql_dict(db, "get_cdqxExit", sql_data)
        jsqx_lst = [row['qxid'] for row in jsqx_lst]
        # 根节点列表初始化
        gjd_dic = {'fjdid':'0'}
        sql_data = {'fjdid':'0'}
        # 获取菜单列表
        cd_lst = ModSql.gl_jsqx_001.execute_sql_dict(db, "data_cd_rs")
        # 调用递归函数
        data_tree(cd_lst,'0',gjd_dic)
        # 将查询详情结果放到结果集中
        if gjd_dic.get('children'):
            # 调用递归函数，标注原有菜单为选中状态
            get_checked(jsqx_lst,gjd_dic)
            data['rows'] = gjd_dic['children']
        #角色已有列表
        data['exist_lst'] = jsqx_lst
        # 获取数据总数
        lbxx_lst = ModSql.gl_jsqx_001.execute_sql_dict(db, "data_sjcd_rs",sql_data)
        data['total'] = len(lbxx_lst)
        # 将查询到的结果反馈给view
        return data

def get_checked(exit_lst,y_dic):
    """
    # 标注选中
    :param exit_lst:已有列表
    :param y_dic:传入的字典
    :param new_dic:返回的字典
    :return:
    """
    if y_dic.get('children'):
        for m in y_dic.get('children'):
            if m['id'] in exit_lst:
                m['checked'] = True
                m['selected'] = True
            get_checked(exit_lst,m)

def data_tree(lst,pId,k):
    """
    # 获取树结构
    :return:
    """
    aLst=[]
    for m in lst:
        if m['fjdid'] == pId:
            aLst.append(m)
    if aLst:
        k['children']=aLst
        for l in aLst:
            data_tree(lst,l['id'],l)

def cdlst_service(params):
    """
    # 获取菜单树
    :return:
    """
    # 初始化返回值
    data = {'total':0,'rows':[]}
    cdids = params['cdids'].split(',')
    sql_data = { 'cdids':cdids}
    # 数据库链接
    with sjapi.connection() as db:
        # 获取菜单列表
        cd_lst = ModSql.gl_jsqx_001.execute_sql_dict(db, "data_cd_rs")
        data_dic = {'fjdid':'0'}
        lst = []
        # 获取角色已有菜单权限
        sql_data = {'jsid':params['jsid']}
        jsqx_lst = ModSql.gl_jsqx_001.execute_sql_dict(db, "get_cdqxExit", sql_data)
        jsqx_lst = [row['qxid'] for row in jsqx_lst]
        if jsqx_lst:
            # 调用递归获取父节点列表
            get_fjdidlb(cd_lst,jsqx_lst,lst)
        last = []
        for i in lst:
            last.extend(i)
        if last:
            # 获取所有节点列表，包含父节点和拥有的权限的节点
            jsqx_lst.extend(last)
            # 节点列表去重
            jsqx_lst = list(set(jsqx_lst))
        sql_data = {'ids':jsqx_lst}
        # 获取最终菜单节点的信息
        jsqx_lst= ModSql.gl_jsqx_001.execute_sql_dict(db, "data_cd_lst", sql_data)
        # 调用递归函数，展示拥有的菜单，包含层级关系
        data_tree(jsqx_lst,'0',data_dic)
        if data_dic.get('children'):
            data1 = data_dic['children']
            data['rows'] = data1
        # 将查询到的结果反馈给view
        return data

def get_fjdidlb(ylst,jd_lst,lst):
    """
    # 获取父节点列表
    :return:
    """
    aLst=[]
    for m in ylst:
        if m['id'] in jd_lst:
            aLst.append(m)
    if aLst:
        fjdid_lst = [k['fjdid'] for k in aLst]
        lst.append(fjdid_lst)
        get_fjdidlb(ylst,fjdid_lst,lst)
    else:
        return  lst

def gnlb_service(params):
    """
    # 获取功能列表
    :return:
    """
    # 初始化返回值
    data = {'total': 0, 'rows': []}
    # 获取菜单id
    sql_data = {'sscdid':params['cdid'],'jsid':params['jsid']}
    # 数据库链接
    with sjapi.connection() as db:
        gnlb_lst = []
        # 获取角色已有功能权限
        sql_data = {'cdid':params['cdid'],'jsid':params['jsid']}
        jsqx_lst = ModSql.gl_jsqx_001.execute_sql_dict(db, "get_anqxExit", sql_data)
        jsqx_lst = [row['qxid'] for row in jsqx_lst]

        # 获取菜单对应的功能列表
        if params['cdid']:
            sql_data = {'sscdid':params['cdid']}
            gnlb_lst = ModSql.gl_jsqx_001.execute_sql_dict(db, "data_gnlb_rs",sql_data)
        for row in gnlb_lst:
            if row['id'] in jsqx_lst:
                row['checked'] = True
                row['selected'] = True
        data['rows'] = gnlb_lst
        # 获取功能列表总数
        data['total'] = len(gnlb_lst)
        # 将查询到的结果反馈给view
        return data

def add_cdqx_service(params):
    """
    # 增加菜单权限
    :return:
    """
     # 初始化返回值
    result = {'state':False, 'msg':""}
    #菜单权限ID列表
    ids = []
    # 用户ID和角色列表
    if params['ids']:
        ids = params['ids'].split(',')
    sql_data = { 'ids':ids,'jsid':params['jsid']}
    # 操作人
    czr = get_sess_hydm()
    # 操作时间
    czsj=get_strftime()

    # 数据库链接
    with sjapi.connection() as db:

        #角色原有菜单权限
        sql_data = {'jsid':params['jsid']}
        rs  = ModSql.gl_jsqx_001.execute_sql_dict(db,"get_cdqxExit",sql_data)

        #菜单权限id列表
        qxid_lst = [ k['qxid']  for k in rs]
        # 新增的菜单权限列表
        qxid_addLst = [k for k in ids if k not in qxid_lst]
        # 删除的菜单权限列表
        qxid_deLst = [k for k in qxid_lst if k not in ids ]

        if len(qxid_addLst) == 0 and len(qxid_deLst) == 0:
            result['msg'] = '权限分配未发生变化'
            return result

        #删除角色原有权限表
        if qxid_lst:
            sql_data = {'ids':qxid_lst,'jsid':params['jsid']}
            ModSql.gl_jsqx_001.execute_sql_dict(db,"delete_jsqxpz",sql_data)
            # 删除拥有原有角色的用户对应的用户权限
            sql_data = {'ids':qxid_lst,'jsid':params['jsid']}
            ModSql.gl_jsqx_001.execute_sql_dict(db,"delete_yhqxpz",sql_data)

        #新增的权限id列表
        if ids:
            for l in ids:
                sql_data = {'qxid': l, 'jsid': params['jsid'],'czr':czr,'czsj': czsj}
                ModSql.gl_jsqx_001.execute_sql_dict(db,"insert_jsqxpz",sql_data)
                # 拥有该角色的用户增加对应的权限
                #  获取用户id
                sql_data = {'jsid': params['jsid']}
                yh_lst = ModSql.gl_jsqx_001.execute_sql_dict(db,"get_yh",sql_data)
                if yh_lst:
                    for m in yh_lst:
                        # 新增用户权限
                        sql_data = {'yhid':m['yhid'],'qxid':l,'jsid':params['jsid'],'czr':czr,'czsj': czsj}
                        ModSql.gl_jsqx_001.execute_sql_dict(db,"insert_yhqxpz",sql_data)
                else:
                    continue

        #获取角色名称，用于登记操作日志
        sql_para = {'id':params['jsid']}
        jscm_rs = ModSql.gl_jsqx_001.execute_sql_dict(db,"get_jsmc",sql_para)
        jsmc = ','.join([k['mc'] for k in jscm_rs])
        #登记操作日志
        rznr = '角色权限管理-增加菜单权限：角色信息：角色名称:[%s],原权限列表:%s,新权限列表:%s' \
        % (jsmc, qxid_lst,ids)
        ins_czrz(db,rznr,'gl','角色权限管理-增加菜单权限')

        #成功后返回成功信息
        result['msg'] = '菜单权限分配成功'
        result['state'] = True
    # 将查询到的结果反馈给view
    return result

def add_gnqx_service(params):
    """
    #  新增按钮功能权限
    :return:
    """
    # 初始化返回值
    result = {'state':False, 'msg':""}
    #按钮权限ID列表
    ids = []
    # 用户ID和角色列表
    if params['ids']:
        ids = params['ids'].split(',')
    # 操作人
    czr = get_sess_hydm()
    # 操作时间
    czsj=get_strftime()

    sql_data = { 'ids':ids,'jsid':params['jsid'],'cdid':params['cdid']}
    # 数据库链接
    with sjapi.connection() as db:

        #角色原有按钮权限
        sql_data = {'jsid':params['jsid'],'cdid':params['cdid'] }
        rs  = ModSql.gl_jsqx_001.execute_sql_dict(db,"get_anqxExit",sql_data)

        #按钮权限id列表
        qxid_lst = [ k['qxid']  for k in rs]
        # 新增的按钮权限列表
        qxid_addLst = [k for k in ids if k not in qxid_lst]
        # 删除的按钮列表
        qxid_deLst = [k for k in qxid_lst if k not in ids ]

        if len(qxid_addLst) == 0 and len(qxid_deLst) == 0:
            result['msg'] = '权限分配未发生变化'
            return result

        #删除角色原有权限表
        if qxid_lst:
            sql_data = {'ids':qxid_lst,'jsid':params['jsid']}
            ModSql.gl_jsqx_001.execute_sql_dict(db,"delete_jsqxpz",sql_data)
            # 删除拥有原有角色的用户对应的用户权限
            sql_data = {'ids':qxid_lst,'jsid':params['jsid']}
            ModSql.gl_jsqx_001.execute_sql_dict(db,"delete_yhqxpz",sql_data)

        #新增的权限id列表
        if ids:
            for l in ids:
                sql_data = {'qxid': l, 'jsid': params['jsid'],'czr':czr,'czsj': czsj}
                ModSql.gl_jsqx_001.execute_sql_dict(db,"insert_jsqxpz",sql_data)
                # 拥有该角色的用户增加对应的权限
                #  获取用户id
                sql_data = {'jsid': params['jsid']}
                yh_lst = ModSql.gl_jsqx_001.execute_sql_dict(db,"get_yh",sql_data)
                if len(yh_lst):
                    for m in yh_lst:
                        # 新增用户权限
                        sql_data = {'yhid':m['yhid'],'qxid':l,'jsid': params['jsid'],'czr':czr,'czsj': czsj}
                        ModSql.gl_jsqx_001.execute_sql_dict(db,"insert_yhqxpz",sql_data)
                else:
                    continue

        #获取角色名称，用于登记操作日志
        sql_para = {'id':params['jsid']}
        jscm_rs = ModSql.gl_jsqx_001.execute_sql_dict(db,"get_jsmc",sql_para)
        jsmc = ','.join([k['mc'] for k in jscm_rs])

        # 获取菜单名称，用于登记操作日志
        sql_para = {'cdid':params['cdid']}
        cdcm_rs = ModSql.gl_jsqx_001.execute_sql_dict(db,"get_cd_rs",sql_para)
        cdmc = ','.join([k['cdmc'] for k in cdcm_rs])
        #登记操作日志
        rznr = '角色权限管理-增加功能按钮权限：角色名称:[%s],菜单名称[%s],原按钮列表:%s,新按钮列表:%s' \
        % (jsmc, cdmc, qxid_lst,ids)
        ins_czrz(db,rznr,'gl','角色权限管理-增加按钮权限')

        #成功后返回成功信息
        result['msg'] = '按钮权限分配成功'
        result['state'] = True
    # 将查询到的结果反馈给view
    return result

