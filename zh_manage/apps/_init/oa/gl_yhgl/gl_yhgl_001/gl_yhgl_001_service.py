# -*- coding: utf-8 -*-
# Action: 用户管理
# Author: houpp
# AddTime: 2015-05-14
# Standard: 注释仅能以“#”开头，sql可以是“--”；注释不能同代码在同一行

from sjzhtspj import ModSql
from sjzhtspj.common import get_bmwh_bm, get_uuid, get_sess_hydm, get_strftime, get_strftime2, ins_czrz,cal_md5
from sjzhtspj import  get_sess

def yhgl_service():
    # 初始化返回值
    data = {'xb_lst': [], 'bm_lst':[]}
    # 追加请选择选项
    data['xb_lst'].insert( 0, {'value': '-1',  'text': '请选择'} )
    # 数据库链接
    with sjapi.connection() as db:
        # 执行性别查询
        data['xb_lst'].extend(get_bmwh_bm( '10026', db=db ))
        #获取部门列表
        bm_list = ModSql.gl_yhgl_001.execute_sql_dict(db,"data_bm_rs")
        bm_dic = {'fjdid':'0'}
        bm_tree(bm_list,'0',bm_dic)
        if bm_dic.get('children'):
            data['bm_lst'] = bm_dic['children']
        return data

def bm_tree(lst,pId,k):
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
            bm_tree(lst,l['id'],l)

def data_service(sql_data):
    """
    # 获取用户列表,展示登录用户所在部门及子部门的所有用户
    :return:
    """
    # 初始化返回值
    data = {'total': 0, 'rows': []}
    # 清理为空的查询条件
    search_lst = ['dlzh', 'xm', 'sj', 'xb','bm']
    for k in list(sql_data.keys()):
        if k in search_lst and sql_data[k] == '':
            del sql_data[k]
    # 获取登录行员的ID
    hyid = get_sess('hyid')
    # 数据库链接
    with sjapi.connection() as db:
        # 获取部门列表
        bm_lst = ModSql.gl_yhgl_001.execute_sql_dict(db, "data_bm_rs")
        # 获取登录行员所在部门的信息
        dlhy_bm = ModSql.gl_yhgl_001.execute_sql_dict(db, "get_bmid_rs",{'yhid':hyid})
        if len(dlhy_bm):
            childid_lst=[]
            # 获取所选部门下的孩子部门id
            children_dic = {'fjdid':dlhy_bm[0]['id']}
            # 调用递归函数
            data_tree(bm_lst,dlhy_bm[0]['id'],children_dic)
            if children_dic.get('children'):
                get_childid(children_dic['children'],childid_lst)
            childid_lst.append(dlhy_bm[0]['id'])
            # 部门列表（包含子部门和所选部门）
            sql_bmids_data = {'ids':childid_lst}
            if len(sql_data) and sql_data.get('bm') :
                # 根据部门ID获取部门编码
                jg_bm = ModSql.gl_yhgl_001.execute_sql_dict(db, "get_jgbm", {'bmid':sql_data['bm']})[0]
                # 获取机构编码获取机构的长编码
                hy_cbm = ModSql.gl_yhgl_001.execute_sql_dict(db, "get_cbm", {'jgbm':jg_bm['jgbm']})[0]
                # 获取部门及子部门下的部门信息
                bmxx_lst = ModSql.gl_yhgl_001.execute_sql_dict(db, "get_bmxx", {'cbm':hy_cbm['cbm']})
                bmid_lst = [bmid['id'] for bmid in bmxx_lst]
                bm_sql={'bmids':bmid_lst}
                sql_data.update(bm_sql)

            sql_data.update(sql_bmids_data)

            yhlst = ModSql.gl_yhgl_001.execute_sql_dict(db, "data_rs",sql_data)
            # 获取总行数
            count = ModSql.gl_yhgl_001.execute_sql(db, "data_rs_count",sql_data)[0].count
            data['rows'] = yhlst
            data['total'] = count
        # 将查询到的结果反馈给view
        return data

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
    :param db: 数据库连接db
    :param lst: 孩子列表
    :return: 孩子id列表
    """
    # 获取孩子ID
    for k in lst:
        child_lst.append(k['id'])
        if k.get('children'):
            get_childid(k['children'],child_lst)

def data_add_service(params):
    """
    # 新增用户管理
    :param sql_data:
    :return:
    """
    result = {'state':False, 'msg':''}
    #获取用户id
    yhid = get_uuid()
    #操作人
    czr = get_sess_hydm()
    # 操作时间
    czsj = get_strftime()
    #加密后的密码
    csmm = '123456' # 初始密码
    mm = cal_md5(csmm)
    with sjapi.connection() as db:
        # 校验登录账号是否存在
        sql_data = {'dlzh': params['dlzh']}
        rs = ModSql.gl_yhgl_001.execute_sql(db, "check_zlzh", sql_data)
        if rs:
            result['msg'] = '行业代码[%s]已经存在，请重新输入' % params['dlzh']
            return result

        # 插入用户基本信息表
        sql_data = {
        'id':yhid,
        'dlzh': params['dlzh'],
        'xm': params['xm'],
        'mm': mm,
        'xb': params['xb'],
        'sj': params['sj'],
        'csrq': params['csrq'],
        'dh': params['dh'],
        'dzyx': params['dzyx'],
        'bz': params['bz'],
        'sfsc':params['sfsc'],
        'czr':czr,
        'czsj':czsj
        }
        ModSql.gl_yhgl_001.execute_sql(db, "insert_yhxx", sql_data)
        if params['ssbm'] and params['ssbm'] != '-1':
            #插入用户部门配置表
            sql_data = {
            'yhid': yhid,
            'bmid':params['ssbm'],
            'czr':czr,
            'czsj':czsj,
            'zt':'1'
            }
            ModSql.gl_yhgl_001.execute_sql(db, "insert_yhbmpz", sql_data)

        sql_data = {'ids':params['ids'], 'yhid': yhid, 'dlzh': params['dlzh'], 'czr':czr, 'czsj':czsj}
        # 编辑用户角色
        edit_js = edit_js_service(db,sql_data)
        if edit_js['state']:
            #登记操作日志
            rznr = '用户管理-用户新增：用户名称[%s]，用户账号: [%s],用户角色列表%s' % (params['xm'], params['dlzh'],edit_js['ids'])
            ins_czrz(db,rznr,'gl','用户管理-用户新增')
            result['state'] = True
            result['msg'] = '新增成功'

    return result

def data_edit_service(params):
    """
    #更新用户信息
    :param params:
    :return:
    """
    result = {'state':False, 'msg':''}
    #操作人
    czr = get_sess_hydm()
    # 操作时间
    czsj = get_strftime()
    with sjapi.connection() as db:
        # 获取编辑前用户信息
        sql_data={'id': params['id']}
        old_data = ModSql.gl_yhgl_001.execute_sql(db, "get_yhxx_edit", sql_data)
        sql_data_edit = {
            'id': params['id'],   # 主键
            'mc': params['mc'], # 姓名
            'xb': params['xb'], # 性别
            'sj': params['sj'], # 手机
            'csrq': params['csrq'], # 出生日期
            'dh': params['dh'], # 电话
            'dzyx': params['dzyx'], # 电子邮箱
            'sm': params['sm'], # 备注
            'czr':czr, # 操作人
            'czsj':czsj # 操作时间
        }
        # 更新用户信息表
        ModSql.gl_yhgl_001.execute_sql(db, "update_yhxx", sql_data_edit)

        sql_data = {
            'yhid': params['id'], # 用户id
        }
        # 判断用户部门配置信息是否存在
        rs = ModSql.gl_yhgl_001.execute_sql(db, "check_yhbmpz", sql_data)
        if rs:
            if params['ssbm'] and params['ssbm'] != '-1':
                sql_data = {
                    'yhid': params['id'], # 用户id
                    'bmid': params['ssbm'], # 所属部门
                    'czr':czr, # 操作人
                    'czsj':czsj # 操作时间
                 }
                #更新用户部门配置表
                ModSql.gl_yhgl_001.execute_sql(db, "update_yhbmpz", sql_data)
            else:
                sql_data = {
                    'yhid': params['id'], # 用户id
                }
                #删除用户部门配置表
                ModSql.gl_yhgl_001.execute_sql(db, "delete_yhbmpz_bj", sql_data)
        else:
            if params['ssbm'] and params['ssbm'] != '-1':
                sql_data = {
                        'yhid': params['id'], # 用户id
                        'bmid': params['ssbm'], # 所属部门
                        'zt': '1',
                        'czr':czr, # 操作人
                        'czsj':czsj # 操作时间
                     }
                #插入用户部门配置表
                ModSql.gl_yhgl_001.execute_sql(db, "insert_yhbmpz", sql_data)

        # 更新用户角色
        sql_data = {'ids':params['ids'], 'yhid': params['id'],'dlzh':  params['dlzh'], 'czr':czr, 'czsj':czsj}
        # 编辑用户角色
        edit_js = edit_js_service(db,sql_data)
        if edit_js['state']:
            # 记录行员日常运维流水
            # 获取登记内容
            rznr = '用户管理-用户编辑：原用户信息[%s]，编辑后用户信息: [%s], 用户原角色%s ,用户更新后角色%s' \
                   % ( str(old_data),sql_data_edit,edit_js['jsid_lst'], edit_js['ids'] )
            # 调用公共函数保存数据库
            ins_czrz(db,rznr,'gl','用户管理-用户编辑')
            result['state'] = True
            result['msg'] = '编辑成功'

    return result

def data_resetMm_service(params):
    """
    # 密码重置
    :param params:
    :return:
    """
    result = {'state':False, 'msg':''}
    #操作人
    czr = get_sess_hydm()
    # 操作时间
    czsj = get_strftime()
    #用户ID列表
    ids = params['yhid'].split(',')
    yhmc_lst = []
    #加密后的密码
    csmm = '123456' # 初始密码
    mm = cal_md5(csmm)
    with sjapi.connection() as db:
        if ids:
            for k in ids:
                sql_data = {
                    'id': k,   # 用户id
                    'mm': mm, # 密码
                    'czr': czr, # 操作人
                    'czsj': czsj # 操作时间
                }
                # 重置用户密码
                ModSql.gl_yhgl_001.execute_sql(db, "update_yhxxMm", sql_data)

        sql_data ={'ids':ids }
        #查询用户信息
        rs  = ModSql.gl_yhgl_001.execute_sql_dict(db,"select_yh_rz",sql_data)
        #拼操作日志中的字符串: 用户名称（行员代码，原密码）
        rz = ', '.join(['%s(%s,%s)' % (k['mc'], k['dlzh'],k['mm']) for k in rs])

        # 记录行员日常运维流水
        # 获取登记内容
        rznr = '用户管理-重置密码：用户信息：【'+ rz +'】'
        # 调用公共函数保存数据库
        ins_czrz(db,rznr,'gl','用户管理-密码重置')
        result['state'] = True
        result['msg'] = '重置密码成功'

    return  result

def delete_service(sql_data):
    """
    #删除用户
    :return:
    """
    # 初始化返回值
    result = {'state':False, 'msg':''}
    #用户ID列表
    ids = sql_data['ids'].split(',')
    sql_para = { 'ids':ids}
    # 数据库链接
    with sjapi.connection() as db:
        #查询用户信息
        rs  = ModSql.gl_yhgl_001.execute_sql_dict(db,"select_yh_rz",sql_para)
        #拼操作日志中的字符串: 用户名称（用户id）
        rz = ', '.join(['%s(%s)' % (k['mc'], k['dlzh']) for k in rs])

        #删除用户权限配置表
        ModSql.gl_yhgl_001.execute_sql_dict(db,"delete_yhqxpz",sql_para)
        #删除用户角色配置表
        ModSql.gl_yhgl_001.execute_sql_dict(db,"delete_yhjspz",sql_para)
        #删除用户部门配置表
        ModSql.gl_yhgl_001.execute_sql_dict(db,"delete_yhbmpz",sql_para)
        # 删除角色信息表
        sql_para.update({'czr':get_sess_hydm(), 'czsj':get_strftime()})
        ModSql.gl_yhgl_001.execute_sql_dict(db,"delete_pl",sql_para)

        #登记操作日志
        rznr = '用户管理-删除：待删除用户信息：【'+ rz +'】'
        ins_czrz(db,rznr,'gl','用户管理-删除用户')

        #成功后返回成功信息
        result['msg'] = '删除记录成功'
        result['state'] = True
    # 将查询到的结果反馈给view
    return result

def data_js_service(params):
    """
    # 获取用户角色和用户权限数据
    :param params:
    :return:
    """
    # 初始化返回值
    result = {'state':False, 'msg':'','rows':[], 'total':0 }
    #用户id
    sql_data = { 'yhid':params['yhid'] }
    # 数据库链接
    with sjapi.connection() as db:
        # 查询用户角色信息列表
        yhjsxx = ModSql.gl_yhgl_001.execute_sql_dict(db, "data_jsxx_rs", sql_data)

        # 将查询详情结果放到结果集中
        result['rows'] = yhjsxx
        result['total'] = len(yhjsxx)
         #成功后返回成功信息
        result['msg'] = '查询数据成功'
        result['state'] = True
        # 将查询到的结果反馈给view
        return result

def data_qx_service(params):
    """
    # 获取用户权限数据
    :param params:
    :return:
    """
    # 初始化返回值
    result = {'state':False, 'msg':'', 'rows':[], 'total':0 }
    #用户id
    sql_data = { 'yhid':params['yhid'] }
    # 数据库链接
    with sjapi.connection() as db:
        lst=[]
        # 获取菜单列表
        cd_lst = ModSql.gl_yhgl_001.execute_sql_dict(db, "data_cd_rs")
        data_dic = {'fjdid':'0'}
        # 获取用户拥有权限列表
        yhqx_lst= ModSql.gl_yhgl_001.execute_sql_dict(db, "data_qx_rs", sql_data)
        qx_lst = [row['id'] for row in yhqx_lst]
        if qx_lst:
            get_fjdidlb(cd_lst,qx_lst,lst)
        last = []
        for i in lst:
            last.extend(i)
        if last:
            qx_lst.extend(last)
            qx_lst = list(set(qx_lst))
        if qx_lst:
            sql_data = {'ids':qx_lst}
            yhqx_lst= ModSql.gl_yhgl_001.execute_sql_dict(db, "data_cd_lst", sql_data)
            # 调用递归函数，展示拥有的菜单，包含层级关系
            tree_view(yhqx_lst,'0',data_dic)
            if data_dic.get('children'):
                data1 = data_dic['children']
                result['rows'] = data1
            result['total'] = len(yhqx_lst)
         #成功后返回成功信息
        result['msg'] = '查询数据成功'
        result['state'] = True
        # 将查询到的结果反馈给view
        return result

def tree_view(lst,pId,k):
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
            tree_view(lst,l['id'],l)

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

def data_jslst_service(params):
    """
    # 获取角色列表
    :return:
    """
    #初始化返回值
    result = {'state': False, 'msg': '', 'rows': [], 'total': 0}
    #用户id
    sql_data = {'yhid': params['yhid']}

    # 数据库链接
    with sjapi.connection() as db:
        # 查询用户已有角色列表
        yhyyjs_lst = ModSql.gl_yhgl_001.execute_sql_dict(db, "get_exitJs", sql_data)
        yhyyjs_lst = [row['jsid'] for row in yhyyjs_lst]

        #获取角色列表
        jsxx_lst = ModSql.gl_yhgl_001.execute_sql_dict(db, "get_jsxxlst", sql_data)
        for row in jsxx_lst:
            if row['id'] in yhyyjs_lst:
                row['checked'] = True
                row['selected'] = True
        # 将查询详情结果放到结果集中
        result['rows'] = jsxx_lst
        result['total'] = len(jsxx_lst)

        # 将查询到的结果反馈给view
        return result

def edit_js_service(db,params):
    """
    # 编辑用户角色
    :param params:
    :return:
    """
     # 初始化返回值
    result = {'state':False, 'msg':'', 'jsid_lst':[], 'ids':[]}
    ids = []
    # 用户ID和角色列表
    if params['ids']:
        ids = params['ids'].split(',')

    sql_para = {'yhid': params['yhid'] }
    #查询用户已有角色信息
    rs  = ModSql.gl_yhgl_001.execute_sql_dict(db,"get_exitJs",sql_para)

    # 获取已有角色对应的权限
    #角色id列表
    jsid_lst = [ k['jsid']  for k in rs]
    if jsid_lst:
        sql_para = { 'ids':jsid_lst}
        #获取原有角色对应的权限ID
        qx_jsLst = ModSql.gl_yhgl_001.execute_sql_dict(db,"get_jsQx",sql_para)
        qx_jsLst = [k['qxid'] for k in qx_jsLst ]
        if qx_jsLst:
            #全部删除用户原有角色对应的权限
            sql_para = {'qx_delLst': qx_jsLst,'yhid': params['yhid'],'jsids':jsid_lst}
            #删除用户权限配置数据
            ModSql.gl_yhgl_001.execute_sql_dict(db,"delete_qxpz",sql_para)

        # 删除原有用户角色配置数据
        sql_para = {'jsid_deLst': jsid_lst,'yhid': params['yhid']}
        #删除用户角色配置数据
        ModSql.gl_yhgl_001.execute_sql_dict(db,"delete_jspz",sql_para)

    if len(ids):
        #新增用户角色配置数据
        for k in ids:
            sql_para = {'jsid': k, 'yhid': params['yhid'],'czr':params['czr'],'czsj': params['czsj']}
            ModSql.gl_yhgl_001.execute_sql_dict(db,"add_yhjs",sql_para)

        # 新增用户权限数据
        sql_para = { 'ids':ids}
        #获取选择的角色对应的权限ID
        qx_Lst = ModSql.gl_yhgl_001.execute_sql_dict(db,"get_jsQx",sql_para)
        if len(qx_Lst):
            for l in qx_Lst:
                sql_para = {'qxid': l['qxid'], 'yhid': params['yhid'],'jsid':l['jsid'],'czr':params['czr'],'czsj': params['czsj']}
                ModSql.gl_yhgl_001.execute_sql_dict(db,"add_yhqx",sql_para)

    #获取用户名称，用于登记操作日志
    sql_para = {'id':params['yhid']}
    ymcm_rs = ModSql.gl_yhgl_001.execute_sql_dict(db,"get_yhmc",sql_para)
    yhmc = ','.join([k['mc'] for k in ymcm_rs])
    #登记操作日志
    rznr = '用户管理-编辑角色：用户信息：用户名称:[%s],用户代码:[%s],原角色列表:%s,新角色列表:%s' \
           % (yhmc, params['dlzh'],jsid_lst,ids)
    ins_czrz(db,rznr,'gl','用户管理-编辑用户角色')

    #成功后返回成功信息
    result['jsid_lst'] = jsid_lst
    result['ids'] = ids
    result['msg'] = '查询数据成功'
    result['state'] = True
    # 将查询到的结果反馈给view
    return result

def get_yhxx_service(id):
    """
    # 获取用户信息
    :return:
    """
    # 初始化返回值
    data = {'state':True, 'msg':'','yhxx':{},'xb_lst': [], 'bm_lst':[]}
    # 追加请选择选项
    data['xb_lst'].insert( 0, {'value': '-1',  'text': '请选择'} )

    # 数据库链接
    with sjapi.connection() as db:
        # 执行性别查询
        data['xb_lst'].extend(get_bmwh_bm( '10026', db=db ))
        #获取部门列表
        bm_list = ModSql.gl_yhgl_001.execute_sql_dict(db,"data_bm_rs")
        bm_dic = {'fjdid':'0'}
        bm_tree(bm_list,'0',bm_dic)
        if bm_dic.get('children'):
            data['bm_lst'] = bm_dic['children']

        if id:
            # 获取对象属性
            yh_lst = ModSql.gl_yhgl_001.execute_sql_dict(db, "get_yhxx_edit", {'id':id})
            if len(yh_lst):
                 data['yhxx']=yh_lst[0]
            else:
                 data['msg']='查询编辑菜单信息失败'
                 data['state']=False
    return data

def check_qx_service(params):
    """
    # 判断所属部门
    :param params:
    :return:
    """
    # 获取当前登录行员的机构编码
    jgbm = get_sess('jgbm')
    # 初始化
    data={'state':False,'msg':''}
    # 数据库链接
    with sjapi.connection() as db:
        # 获取登录行员所在机构的长编码
        hy_cbm = ModSql.gl_yhgl_001.execute_sql_dict(db, "get_cbm", {'jgbm':jgbm})[0]
        # 获取行员所在当前部门及子部门下的部门信息
        bmxx_lst = ModSql.gl_yhgl_001.execute_sql_dict(db, "get_bmxx", {'cbm':hy_cbm['cbm']})
        bmid_lst = [bmid['id'] for bmid in bmxx_lst]
        if params['bmid'] not in bmid_lst:
            data['msg']='所属部门只能选择登录行员所在的部门或者子部门，不可以越级操作'
        else:
            data['state']=True
    return data