# -*- coding: utf-8 -*-
# Action: 部门管理
# Author: houpp
# AddTime: 2015-05-21
# Standard: 注释仅能以“#”开头，sql可以是“--”；注释不能同代码在同一行

from sjzhtspj import ModSql,get_sess
from sjzhtspj.common import get_bmwh_bm, get_uuid, get_sess_hydm, get_strftime, get_strftime2, ins_czrz

def lst_service(params):
    # 初始化返回值
    data = {'state':False,'msg':'','bmfl_lst': [],'sjbm_lst': [],'bmxx':{},'flag':'0','bmid_login':'' }
    # 追加请选择选项
    data['bmfl_lst'].insert(0, {'value': '-1', 'text': '请选择'})
    # 获取当前登录行员的机构编码
    jgbm = get_sess('jgbm')
    # 获取当前登录行员的机构编码
    bmid_login=get_sess('bmid')
    data['bmid_login']=bmid_login
    # 数据库链接
    with sjapi.connection() as db:
        # 执行查询
        # 部门分类列表
        data['bmfl_lst'].extend(get_bmwh_bm( '10024', db=db ))

        # 根节点列表初始化
        sql_data = {'fjdid':'0'}
        #部门列表
        bm_list = ModSql.gl_bmgl_001.execute_sql_dict(db, "data_bm_rs",sql_data)
        bm_dic = {'fjdid':'0'}
        # 调用递归函数
        bm_tree(bm_list,'0',bm_dic)
        if bm_dic.get('children'):
            data['sjbm_lst'] = bm_dic['children']

        # 获取编辑信息
        if params['bmid']:
            bm_lst = ModSql.gl_bmgl_001.execute_sql_dict(db, "get_bmxx_edit", {'id':params['bmid']})
            if len(bm_lst):
                 data['bmxx']=bm_lst[0]
                 data['state']=True
                 # 如若要编辑的是上级部门，则不允许编辑，传给前台标志flag:1
                 # 获取行员所在当前部门及子部门下的部门信息
                 if jgbm:
                    # 获取登录行员所在机构的长编码
                    hy_cbm = ModSql.gl_yhgl_001.execute_sql_dict(db, "get_cbm", {'jgbm':jgbm})
                    if len(hy_cbm):
                        hy_cbm=hy_cbm[0]
                        # 获取行员所在当前部门及子部门下的部门信息
                        bmxx_lst = ModSql.gl_yhgl_001.execute_sql_dict(db, "get_bmxx", {'cbm':hy_cbm['cbm']})
                        bmid_lst = [bmid['id'] for bmid in bmxx_lst]
                        if params['bmid'] not in bmid_lst:
                            data['flag']='1'
                            # return data
            else:
                 data['msg']='查询编辑菜单信息失败'
        else:
            data['state']=True
        return data

def data_service():
    # 初始化返回值
    data = {'total': 0, 'rows': []}
    # 数据库链接
    with sjapi.connection() as db:
        # 根节点列表初始化
        sql_data = {'fjdid':'0'}
        #部门列表
        bm_list = ModSql.gl_bmgl_001.execute_sql_dict(db, "data_bm_rs",sql_data)
        bm_dic = {'fjdid':'0'}
        # 调用递归函数
        bm_tree(bm_list,'0',bm_dic)
        if bm_dic.get('children'):
            data['rows'] = bm_dic['children']

        # 获取数据总数
        lbxx_lst = ModSql.gl_bmgl_001.execute_sql_dict(db, "data_sjbm_rs",sql_data)
        data['total'] = len(lbxx_lst)
        # 将查询到的结果反馈给view
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

def get_bm(db,sjbm):
    """
    # 获取最终长编码
    :param db: 数据库连接
    :param sjbm: 上级部门id
    :return:
    """
    # 初始化返回值
    result = {'state':False, 'msg':'','bm':''}
    # 获取父节点对应的编码
    # 1、父节点为根节点
    if sjbm == '0' or sjbm=='':
        bm_max = ModSql.gl_bmgl_001.execute_sql(db, "get_bm_gjd")
        if bm_max[0].get('bm'):
            if bm_max[0].get('bm') <=9:
                bm = '000'+ str(bm_max[0].get('bm'))
            elif bm_max[0].get('bm') >9 and bm_max[0].get('bm') <= 99:
                bm = '00' + str(bm_max[0].get('bm'))
            elif bm_max[0].get('bm') >99 and bm_max[0].get('bm') <=999:
                bm = '0' + str(bm_max[0].get('bm'))
            elif bm_max[0].get('bm') >999 and bm_max[0].get('bm') <=9999:
                bm = bm_max[0].get('bm')
            else:
                result['msg'] = '顶级部门数量已经超过最大限制数9999，不允许添加'
                return result
        else:
            bm='0000'
    else:
        sql_data = {'fjdid': sjbm}
        # 获取父节点编码
        fjd_bm = ModSql.gl_bmgl_001.execute_sql(db, "get_fjdBm",sql_data)
        # 获取父节点下子节点的最大编码
        bm_max = ModSql.gl_bmgl_001.execute_sql(db, "get_maxBm",sql_data)
        if fjd_bm:
            if fjd_bm[0].get('bm') and bm_max[0].get('bm'):
                # 获取编码(父节点编码之后的编码)，转为整形加1
                bm = int(bm_max[0].get('bm')[len(fjd_bm[0].get('bm'))+1:]) + 1
                # 获取最终编码
                if bm <=9:
                    bm = fjd_bm[0].get('bm') +'.'+ '000'+str(bm)
                elif bm >9 and bm <=99:
                    bm = fjd_bm[0].get('bm') +'.'+ '00'+str(bm)
                elif bm >99 and bm <=999:
                    bm = fjd_bm[0].get('bm') +'.'+'0' + str(bm)
                elif bm >999 and bm <=9999:
                    bm = fjd_bm[0].get('bm') +'.'+ str(bm)
                else:
                    result['msg'] = '所选上级部门下子部门已经达到9999，请重新选择'
                    return result
            else:
                if fjd_bm[0].get('bm') :
                    fjd_bm= ','.join([k['bm'] for k in fjd_bm])
                    bm = fjd_bm + '.'+'0001'
    # 返回值
    result['state'] =True
    result['bm'] = bm

    return  result


def data_add_service(params):
    """
    # 新增部门
    :return:
    """
    result = {'state':False, 'msg':''}
    #获取部门id
    bmid = get_uuid()
    #操作人
    czr = get_sess_hydm()
    # 操作时间
    czsj = get_strftime()
    # 初始化编码
    bm = '0000'
    with sjapi.connection() as db:
        # 校验部门代码是否存在
        sql_data = {'bmdm': params['bmdm']}
        rs = ModSql.gl_bmgl_001.execute_sql(db, "check_bmdm", sql_data)
        if rs:
            result['msg'] = '部门代码[%s]已经存在，请重新输入' % params['bmdm']
            return result

        # 校验部门名称是否存在
        sql_data = {'bmmc': params['bmmc']}
        rs = ModSql.gl_bmgl_001.execute_sql(db, "check_bmmc", sql_data)
        if rs:
            result['msg'] = '部门名称[%s]已经存在，请重新输入' % params['bmmc']
            return result
        # 调用函数，获取长编码
        bm_dic = get_bm(db,params['sjbm'])
        if bm_dic.get('state'):
            if bm_dic.get('bm'):
                cbm = bm_dic.get('bm')
        else:
            result['msg'] = bm_dic.get('msg')
            return result

        # 插入部门基本信息表
        sql_data = {
            'id':bmid,
            'bmdm':params['bmdm'],
            'cbm':cbm,
            'bmmc': params['bmmc'],
            'bmfl': params['bmfl'],
            'zfzr': params['zfzr'],
            'dh': params['dh'],
            'cz':params['cz'],
            'dz':params['dz'],
            'sjbm':params['sjbm'],
            'bz':params['bz'],
            'pxh':params['pxh'],
            'scbz':'0',
            'czr':czr,
            'czsj':czsj
        }
        ModSql.gl_bmgl_001.execute_sql(db, "insert_bmxx", sql_data)

        #登记操作日志
        rznr = '部门管理-部门新增：部门名称[%s]，部门代码: [%s],' % (params['bmmc'], params['bmdm'])
        ins_czrz(db,rznr,'gl','部门管理-部门新增')
        result['state'] = True
        result['msg'] = '新增成功'

    return result

def data_edit_service(params):
    """
    # 编辑部门信息
    :return:
    """
    result = {'state':False, 'msg':''}
    #操作人
    czr = get_sess_hydm()
    # 操作时间
    czsj = get_strftime()
    with sjapi.connection() as db:
        # 校验部门名称是否存在
        sql_data = {'bmmc': params['bmmc'],'id': params['bmid']}
        rs = ModSql.gl_bmgl_001.execute_sql(db, "check_bmmc", sql_data)
        if rs:
            result['msg'] = '部门名称[%s]已经存在，请重新输入' % params['bmmc']
            return result
        # 校验所属上级部门选择的是否正确
        # 排除自己
        if params['sjbm'] == params['bmid']:
            result['msg'] = '所属上级部门不能选择自己，请重新选择'
            return result
        # 排除孩子
        sql_data = {'fjdid':params['bmid']}
        children_dic = {'fjdid':params['bmid']}
        childid_lst=[]
        #部门列表
        bm_list = ModSql.gl_bmgl_001.execute_sql_dict(db, "data_bm_rs",sql_data)
        bm_tree(bm_list,params['bmid'],children_dic)
        # 调用递归函数
        if children_dic.get('children'):
            get_childid(children_dic['children'],childid_lst)

        if params['sjbm']  in childid_lst:
            result['msg'] = '所属上级部门不能选择自己的子部门，请重新选择'
            return result

        # 获取当前登录行员的机构编码
        jgbm = get_sess('jgbm')
        # 不可越级编辑上级部门
        if jgbm:
            # 获取登录行员所在机构的长编码、
            hy_cbm = ModSql.gl_yhgl_001.execute_sql_dict(db, "get_cbm", {'jgbm':jgbm})
            if len(hy_cbm):
                hy_cbm=hy_cbm[0]
                # 获取行员所在当前部门及子部门下的部门信息
                bmxx_lst = ModSql.gl_yhgl_001.execute_sql_dict(db, "get_bmxx", {'cbm':hy_cbm['cbm']})
                bmid_lst = [bmid['id'] for bmid in bmxx_lst]
                if params['bmid'] not in bmid_lst:
                    result['msg']='只能编辑登录行员所在的部门或者子部门，不可以越级操作'
                    return result

        # 排除上级部门未变更的情况
        # 获取原上级部门id
        sql_data = {'id':params['bmid']}
        fjd = ModSql.gl_bmgl_001.execute_sql(db, "get_sjbmID",sql_data)

        # 获取部门原长编码
        sql_data = {'id':params['bmid']}
        bm_ycbm = ModSql.gl_bmgl_001.execute_sql(db, "get_cbm",sql_data)
        bm_ycbm = bm_ycbm[0].get('cbm')

        if fjd[0].get('fjdid') != params['sjbm'] :
            # 调用函数，获取长编码
            bm_dic = get_bm(db,params['sjbm'])
            if bm_dic.get('state'):
                if bm_dic.get('bm'):
                    cbm = bm_dic.get('bm')
            else:
                result['msg'] = bm_dic.get('msg')
                return result

            # 循环更新子部门长编码
            if childid_lst:
                for k in childid_lst:
                    sql_data = {'id':k}
                    zbm_cbm = ModSql.gl_bmgl_001.execute_sql(db, "get_cbm",sql_data)
                    if zbm_cbm[0].get('cbm'):
                        zbm_cbm = zbm_cbm[0].get('cbm')
                        zbm_cbm = zbm_cbm.replace(zbm_cbm[:len(bm_ycbm)],cbm)
                        sql_data ={'id': k, 'cbm':zbm_cbm, 'czr':czr,'czsj':czsj}
                        # 执行更新子部门编码
                        ModSql.gl_bmgl_001.execute_sql(db, "update_zCbm",sql_data)
        else:
            cbm = bm_ycbm
        # 获取编辑前部门信息
        # 查询编辑前的信息
        sql_data = {'id':params['bmid']}
        old_data = ModSql.gl_bmgl_001.execute_sql_dict(db, "get_bmxx_edit",sql_data )[0]

        # 更新部门基本信息表
        sql_data = {
            'id':params['bmid'],
            'cbm':cbm,
            'bmmc': params['bmmc'],
            'bmfl': params['bmfl'],
            'zfzr': params['zfzr'],
            'dh': params['dh'],
            'cz':params['cz'],
            'dz':params['dz'],
            'sjbm':params['sjbm'],
            'bz':params['bz'],
            'pxh':params['pxh'],
            'czr':czr,
            'czsj':czsj
        }
        ModSql.gl_bmgl_001.execute_sql(db, "edit_bmxx", sql_data)

        #登记操作日志
        rznr = '部门管理-部门更新：部门名称[%s]，部门代码: [%s],编辑前信息[%s],编辑后信息[%s]' \
               % (params['bmmc'], params['bmdm'],str(old_data),sql_data)
        ins_czrz(db,rznr,'gl','部门管理-部门更新')
        result['state'] = True
        result['msg'] = '更新成功'

    return result


def delete_service(params):
    """
    # 删除部门
    :return:
    """
    # 初始化返回值
    result = {'state':False, 'msg':""}
    #部门ID列表
    sql_para = { 'id': params['id']}
    # 获取当前登录行员的机构编码
    jgbm = get_sess('jgbm')
    # 数据库链接
    with sjapi.connection() as db:
        #查询孩子部门信息
        rs  = ModSql.gl_bmgl_001.execute_sql_dict(db,"get_zjd",sql_para)
        if rs:
            result['msg'] = '当前部门[%s]存在子部门，不允许删除' % params['bmmc']
            return result
        # 查询部门下用户配置信息
        rs  = ModSql.gl_bmgl_001.execute_sql_dict(db,"get_yhbmpz",sql_para)
        if rs:
            result['msg'] = '当前部门[%s]存在用户信息，不允许删除' % params['bmmc']
            return result

        # 获取登录行员所在机构的长编码
        hy_cbm = ModSql.gl_yhgl_001.execute_sql_dict(db, "get_cbm", {'jgbm':jgbm})[0]
        # 获取行员所在当前部门及子部门下的部门信息
        bmxx_lst = ModSql.gl_yhgl_001.execute_sql_dict(db, "get_bmxx", {'cbm':hy_cbm['cbm']})
        bmid_lst = [bmid['id'] for bmid in bmxx_lst]
        if params['id'] not in bmid_lst:
            result['msg']='只能删除登录行员所在的部门或者子部门，不可以越级操作'
            return result

        # 获取待删除信息
        rs  = ModSql.gl_bmgl_001.execute_sql_dict(db,"get_bmxx",sql_para)
        #拼操作日志中的字符串: 部门名称（部门代码）
        rz = ', '.join(['%s(%s)' % (k['bmmc'], k['bm']) for k in rs])

        # 删除部门信息表
        sql_para.update({'czr':get_sess_hydm(), 'czsj':get_strftime()})
        ModSql.gl_bmgl_001.execute_sql_dict(db,"delete_bm",sql_para)

        #登记操作日志
        rznr = '部门管理-删除：待删除部门信息：【'+ rz +'】'
        ins_czrz(db,rznr,'gl','部门管理-删除')

        #成功后返回成功信息
        result['msg'] = '删除记录成功'
        result['state'] = True
    # 将查询到的结果反馈给view
    return result

def get_bmxx_service(id):
    """
    # 获取编辑前的部门信息
    :return:
    """
    # 数据结构
    data = {'state':True, 'msg':'','bmxx':{},'flag':'0'}
    # 获取当前登录行员的机构编码
    jgbm = get_sess('jgbm')
    # 数据库链接
    with sjapi.connection() as db:
        # 获取对象属性
        data['bmxx'] = ModSql.gl_bmgl_001.execute_sql_dict(db, "get_bmxx_edit", {'id':id})[0]
        # 如若要编辑的是上级部门，则不允许编辑，传给前台标志flag:1
        # 获取行员所在当前部门及子部门下的部门信息
        if jgbm:
            # 获取登录行员所在机构的长编码
            hy_cbm = ModSql.gl_yhgl_001.execute_sql_dict(db, "get_cbm", {'jgbm':jgbm})
            if len(hy_cbm):
                hy_cbm=hy_cbm[0]
                # 获取行员所在当前部门及子部门下的部门信息
                bmxx_lst = ModSql.gl_yhgl_001.execute_sql_dict(db, "get_bmxx", {'cbm':hy_cbm['cbm']})
                bmid_lst = [bmid['id'] for bmid in bmxx_lst]
                if id not in bmid_lst:
                    data['flag']='1'

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







