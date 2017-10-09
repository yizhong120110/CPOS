# -*- coding: utf-8 -*-
# Action: 用户权限管理
# Author: houpp
# AddTime: 2015-05-28
# Standard: 注释仅能以“#”开头，sql可以是“--”；注释不能同代码在同一行

from sjzhtspj import ModSql
from sjzhtspj.common import get_uuid, get_sess_hydm, get_strftime, get_strftime2, ins_czrz

def bmlst_service():
    """
    # 获取部门列表
    :return:
    """
    # 初始化返回值
    data = {'total':0,'rows':[]}
    # 数据库链接
    with sjapi.connection() as db:
        # 根节点列表初始化
        gjd_dic = {'fjdid':'0'}
        # 获取菜单列表
        bm_lst = ModSql.gl_yhqx_001.execute_sql_dict(db, "get_bmid_rs")
        # 调用递归函数
        data_tree(bm_lst,'0',gjd_dic)
        # 将查询详情结果放到结果集中
        if gjd_dic.get('children'):
            data['rows'] = gjd_dic['children']
        data['total'] = len(gjd_dic)
        # 将查询到的结果反馈给view
        return data

def yhlst_service(params):
    """
    # 获取用户列表
    :return:
    """
    # 初始化返回值
    data = {'total': 0, 'rows':[]}
    yh_lst = []
    # 数据库链接
    with sjapi.connection() as db:

        # 搜索字段名和搜索值
        search_data = {}
        search_name = params['search_name']
        search_value = params['search_value']
        if search_name and search_value:
            search_data['search_name'] = search_name
            search_data['search_value'] = search_value

        # 获取部门列表
        bm_lst = ModSql.gl_yhqx_001.execute_sql_dict(db, "get_bmid_rs")
        if params['bmids']:
            childid_lst=[]
            # 获取所选部门下的孩子部门id
            for k in params.get('bmids').split(','):
                children_dic = {'fjdid':k}
                # 调用递归函数
                data_tree(bm_lst,k,children_dic)
                if children_dic.get('children'):
                    get_childid(children_dic['children'],childid_lst)
                childid_lst.append(k)
            # 部门列表（包含子部门和所选部门）
            sql_data = {'ids':childid_lst}
            yhlst = ModSql.gl_yhqx_001.execute_sql_dict(db, "get_bmyh_rs",dict(sql_data,**search_data))
            data['rows'] = yhlst
            data['total'] = len(yhlst)
        # 将查询到的结果反馈给view
        return data

def data_service(params):
    # 初始化返回值
    data = {'total': 0, 'rows': [],'exist_lst':[]}
    #用户id
    sql_data = {'yhid': params['yhid']}
    # 数据库链接
    with sjapi.connection() as db:
        # 获取用户已有菜单权限
        yhyyqx_lst = ModSql.gl_yhqx_001.execute_sql_dict(db, "get_cdqxExit", sql_data)
        yhyyqx_lst = [row['qxid'] for row in yhyyqx_lst]
         # 根节点列表初始化
        gjd_dic = {'fjdid':'0'}
        sql_data = {'fjdid':'0'}
        # 获取菜单列表
        cd_lst = ModSql.gl_yhqx_001.execute_sql_dict(db, "data_cd_rs")
        # 调用递归函数
        data_tree(cd_lst,'0',gjd_dic)
        # 将查询详情结果放到结果集中
        if gjd_dic.get('children'):
            # 调用递归函数，标注原有菜单为选中状态
            get_checked(yhyyqx_lst,gjd_dic)
            data['rows'] = gjd_dic['children']
        #用户已有列表
        data['exist_lst'] = yhyyqx_lst
        # 获取数据总数
        lbxx_lst = ModSql.gl_yhqx_001.execute_sql_dict(db, "data_sjcd_rs",sql_data)
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

def get_childid(lst,child_lst):
    """
    # 递归获取子节点id
    :param lst: 孩子列表
    :return: 孩子id列表
    """
    # 获取孩子ID
    for k in lst:
        child_lst.append(k['id'])
        if k.get('children'):
            get_childid(k['children'],child_lst)

def cdlst_service(params):
    """
    # 获取菜单树
    :return:
    """
    # 初始化返回值
    data = {'total':0,'rows':[]}
    cdids = params['cdids'].split(',')
    # 数据库链接
    with sjapi.connection() as db:
        # 获取菜单列表
        cd_lst = ModSql.gl_jsqx_001.execute_sql_dict(db, "data_cd_rs")
        lst = []
        data_dic = {'fjdid':'0'}
        # 获取用户已有菜单权限
        sql_data = {'yhid':params['yhid']}
        yhyyqx_lst = ModSql.gl_yhqx_001.execute_sql_dict(db, "get_cdqxExit", sql_data)
        yhyyqx_lst = [row['qxid'] for row in yhyyqx_lst]
        if yhyyqx_lst:
            get_fjdidlb(cd_lst,yhyyqx_lst,lst)
        last = []
        for i in lst:
            last.extend(i)
        if last:
            # 获取所有节点列表，包含父节点和拥有的权限的节点
            yhyyqx_lst.extend(last)
            # 节点列表去重
            yhyyqx_lst = list(set(yhyyqx_lst))
        sql_data = {'ids':yhyyqx_lst}
        # 获取最终菜单节点的信息
        jsqx_lst= ModSql.gl_yhqx_001.execute_sql_dict(db, "data_cd_lst", sql_data)
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
    sql_data = {'sscdid':params['cdid'],'yhid':params['yhid']}
    # 数据库链接
    with sjapi.connection() as db:
        # 获取用户已有功能权限
        sql_data = {'cdid':params['cdid'],'yhid':params['yhid']}
        yhyyqx_lst = ModSql.gl_yhqx_001.execute_sql_dict(db, "get_anqxExit", sql_data)
        yhyyqx_lst = [row['qxid'] for row in yhyyqx_lst]

        # 获取菜单对应的功能列表
        sql_data = {'sscdid':params['cdid']}
        gnlb_lst = ModSql.gl_yhqx_001.execute_sql_dict(db, "data_gnlb_rs",sql_data)
        for row in gnlb_lst:
            if row['id'] in yhyyqx_lst:
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
    if params['ids']:
        ids = params['ids'].split(',')
    sql_data = { 'ids':ids,'yhid':params['yhid']}
    # 操作人
    czr = get_sess_hydm()
    # 操作时间
    czsj=get_strftime()

    # 数据库链接
    with sjapi.connection() as db:

        #用户原有菜单权限
        sql_data = {'yhid':params['yhid']}
        rs  = ModSql.gl_yhqx_001.execute_sql_dict(db,"get_cdqxExit",sql_data)
        #菜单权限id列表
        qxid_lst = [ k['qxid']  for k in rs]
        # 新增的菜单权限列表
        qxid_addLst = [k for k in ids if k not in qxid_lst]
        # 删除的菜单权限列表
        qxid_deLst = [k for k in qxid_lst if k not in ids ]

        if len(qxid_addLst) == 0 and len(qxid_deLst) == 0:
            result['msg'] = '权限分配未发生变化'
            return result
        #删除用户原有权限表
        if qxid_lst:
            sql_data = {'ids':qxid_lst,'yhid':params['yhid']}
            ModSql.gl_yhqx_001.execute_sql_dict(db,"delete_yhqxpz",sql_data)
        #新增的权限id列表
        if ids:
            for l in ids:
                sql_data = {'qxid': l, 'yhid': params['yhid'],'czr':czr,'czsj': czsj}
                ModSql.gl_yhqx_001.execute_sql_dict(db,"insert_yhqxpz",sql_data)

        #获取用户名称，用于登记操作日志
        sql_para = {'id':params['yhid']}
        ymcm_rs = ModSql.gl_yhqx_001.execute_sql_dict(db,"get_yhmc",sql_para)
        yhmc = ','.join([k['mc'] for k in ymcm_rs])
        #登记操作日志
        rznr = '用户权限管理-增加菜单权限：用户信息：用户名称:[%s],原权限列表:%s,新权限列表:%s' \
        % (yhmc, qxid_lst,ids)
        ins_czrz(db,rznr,'gl','用户权限管理-增加菜单权限')

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
    if params['ids']:
        ids = params['ids'].split(',')
    # 操作人
    czr = get_sess_hydm()
    # 操作时间
    czsj=get_strftime()

    sql_data = { 'ids':ids,'yhid':params['yhid'],'cdid':params['cdid']}
    # 数据库链接
    with sjapi.connection() as db:

        #用户原有按钮权限
        sql_data = {'yhid':params['yhid'],'cdid':params['cdid'] }
        rs  = ModSql.gl_yhqx_001.execute_sql_dict(db,"get_anqxExit",sql_data)

        #按钮权限id列表
        qxid_lst = [ k['qxid']  for k in rs]
        # 新增的按钮权限列表
        qxid_addLst = [k for k in ids if k not in qxid_lst]
        # 删除的按钮列表
        qxid_deLst = [k for k in qxid_lst if k not in ids ]

        if len(qxid_addLst) == 0 and len(qxid_deLst) == 0:
            result['msg'] = '权限分配未发生变化'
            return result
        #删除用户原有权限表
        if qxid_lst:
            sql_data = {'ids':qxid_lst,'yhid':params['yhid']}
            ModSql.gl_yhqx_001.execute_sql_dict(db,"delete_yhqxpz",sql_data)

        #新增的权限id列表
        if ids:
            for l in ids:
                sql_data = {'qxid': l, 'yhid': params['yhid'],'czr':czr,'czsj': czsj}
                ModSql.gl_yhqx_001.execute_sql_dict(db,"insert_yhqxpz",sql_data)

        #获取用户名称，用于登记操作日志
        sql_para = {'id':params['yhid']}
        ymcm_rs = ModSql.gl_yhqx_001.execute_sql_dict(db,"get_yhmc",sql_para)
        yhmc = ','.join([k['mc'] for k in ymcm_rs])

        # 获取菜单名称，用于登记操作日志
        sql_para = {'cdid':params['cdid']}
        cdcm_rs = ModSql.gl_yhqx_001.execute_sql_dict(db,"get_cd_rs",sql_para)
        cdmc = ','.join([k['cdmc'] for k in cdcm_rs])

        #登记操作日志
        rznr = '用户权限管理-增加功能按钮权限：用户名称:[%s],菜单名称[%s],原按钮列表:%s,新按钮列表:%s' \
        % (yhmc, cdmc, qxid_lst,ids)
        ins_czrz(db,rznr,'gl','用户权限管理-增加按钮权限')

        #成功后返回成功信息
        result['msg'] = '按钮权限分配成功'
        result['state'] = True
    # 将查询到的结果反馈给view
    return result