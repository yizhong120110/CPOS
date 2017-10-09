# -*- coding: utf-8 -*-
# Action: 版本提交 service
# Author: zhangzf
# AddTime: 2015-1-13
# Standard: 注释仅能以“#”开头，sql可以是“--”；注释不能同代码在同一行

import copy,json,pickle
from sjzhtspj import ModSql,get_sess_hydm
from sjzhtspj.common import get_strftime,get_uuid,ins_czrz,get_bcxx,set_zdfqpzsm,update_jhrw

def last_bbxx_service(lx, id, gridid):
    """
    # 版本提交页面url
    """
    
    # 版本信息
    bbxx = {}
    # 查询最新的版本信息
    with sjapi.connection() as db:
        bbxx_lst = ModSql.kf_ywgl_023.execute_sql_dict(db, "get_last_version", {'lx':lx, 'id':id})
        if bbxx_lst:
            bbxx = bbxx_lst[0]
        else:
            bbxx['bbh'] = 0
            bbxx['tjr'] = ''
            bbxx['tjsj'] = ''
            bbxx['wym'] = ''
    
    # 将提交内容的类型,提交内容的id放到bbxx中
    bbxx['lx'] = lx
    bbxx['id'] = id
    bbxx['gridid'] = gridid
    
    return bbxx

def bbtj_service(lx,id,tjms):
    """
    # 版本提交方法
    """
    
    # blob管理表id
    blob_id = get_uuid()
    # 版本控制表id
    bbkz_id = get_uuid()
    result = {}
    with sjapi.connection() as db:
        result = get_bcxx(db, lx, id)
        if result['state'] == True:
            return {'state':True, 'msg':'没有要提交的内容，请重新确认！'}
    bbnr = pickle.dumps(result['bbnr'])
    # 将版本信息插入到BLOB表和版本控制表中
    with sjapi.connection() as db:
        sql_data = {'blobid':blob_id, 'czr':get_sess_hydm(),'czsj':get_strftime(),'nr':bbnr, 'lx':lx}
        ModSql.common.execute_sql(db, "add_blob", sql_data)
        sql_data = {'id':bbkz_id, 'lx':lx, 'ssid':id, 'bbh':result['bbh'], 'tjr':get_sess_hydm(), 'tjsj':get_strftime(), 'tjms':tjms, 'nr_id':blob_id, 'wym':result['wym']}
        ModSql.kf_ywgl_023.execute_sql(db, "add_bbkz", sql_data)
        # 记录操作内容
        ins_czrz(db,'【版本提交：'+ lx +','+ bbkz_id + ',' + str(result['bbh']) +'】', gnmc = '版本控制管理_提交' )
    
    result['state'] = True
    result['msg'] = '提交成功'
    return result
    
def bbhy_index_service( lx,id,gridid):
    """
    # 版本还原,查询上一版本信息
    """
    with sjapi.connection() as db:
        bbxx = ModSql.kf_ywgl_023.execute_sql_dict(db,"get_new_bbxx",{'id':id,'lx':lx})
        if bbxx:
            bbxx = bbxx[0]
        else:
            bbxx = {}
            bbxx['bbh'] = 0
            bbxx['tjr'] = ''
            bbxx['tjsj'] = ''
            bbxx['wym'] = ''
    # 将提交内容的类型,提交内容的id放到bbxx中
    bbxx['lx'] = lx
    bbxx['id'] = id
    bbxx['gridid'] = gridid
    return bbxx

def bbhy_add_service(lx,id):
    """
    # 版本还原
    """
    with sjapi.connection() as db:
        # 先查询版本信息
        bbxx = ModSql.kf_ywgl_023.execute_sql_dict(db,"get_bbxx",{'lx':lx,'id':id})[0]
        bbxx['nr'] = pickle.loads(bbxx['nr'].read()) if bbxx['nr'] else ''
        if lx == 'jy':
            # 删除流程布局表
            ModSql.kf_ywgl_023.execute_sql(db,"delete_lcbj",{'cxtj':[('ssjyid',id)]})
            # 删除流程走向表
            ModSql.kf_ywgl_023.execute_sql(db,"delete_lczx",{'id':id})
            # 更新交易定义表
            sql_data = bbxx['nr']['gl_jydy'][0]
            sql_data['id'] = id
            sql_data['wym'] = bbxx['wym']
            sql_data['czr'] = get_sess_hydm()
            sql_data['czsj'] = get_strftime()
            # 查询没有还原之前的交易信息
            bd_jy = ModSql.kf_ywgl_023.execute_sql_dict(db,"get_jyxx",{'id':id})[0]
            # 这个地方是为了解决版本控制没有对自动发起配置说明控制，所以导致之前的版本提交是没有自动发起配置说明的。
            # 加这句代码是为了，让已经上线的项目不报错
            sql_data['zdfqpzsm'] = set_zdfqpzsm(sql_data)
            ModSql.kf_ywgl_023.execute_sql(db,"update_jydy",sql_data)
            
            # 更新计划任务
            upd_dic = { 'id':get_uuid(), 'zdfqpz': sql_data['zdfqpz'] if sql_data['zdfqpz'] else '','zdfqpzsm': sql_data['zdfqpzsm'], 'rwlx': 'jy','ssid': sql_data['id'],'zt': sql_data['zt'] }
            # 调用公共函数 第二个参数是原状态，第三个是原自动发起配置。此时正式表中不存在计划任务，所以元状态为1（启用），自动发起配置应当都是空。
            update_jhrw( db, bd_jy.get('zt'), bd_jy.get('zdfqpz'), upd_dic = upd_dic)
            
            # 如果还原后的自动发起配置为空，则将计划任务表的内容删除掉
            if not upd_dic['zdfqpz']:
                ModSql.common.execute_sql_dict(db,'del_jhrw_byssid',{'ssid':sql_data['id']})
            
            # 插入流程布局表
            for lc in bbxx['nr']['gl_lcbj']:
                lc['czpzid'] = lc.get('czpzid', '')
                ModSql.kf_ywgl_023.execute_sql(db,"insert_lcbj",lc)
             # 插入流程走向表
            for zx in bbxx['nr']['gl_lczx']:
                ModSql.kf_ywgl_023.execute_sql(db,"insert_lczx",zx)
        elif lx == 'zlc':    
            # 删除流程布局表
            ModSql.kf_ywgl_023.execute_sql(db,"delete_lcbj",{'cxtj':[('sszlcid',id)]})
            # 删除流程走向表
            ModSql.kf_ywgl_023.execute_sql(db,"delete_lczx",{'id':id})
            # 插入流程布局表
            for lc in bbxx['nr']['gl_lcbj']:
                lc['czpzid'] = lc.get('czpzid', '')
                ModSql.kf_ywgl_023.execute_sql(db,"insert_lcbj",lc)
             # 插入流程走向表
            for zx in bbxx['nr']['gl_lczx']: 
                ModSql.kf_ywgl_023.execute_sql(db,"insert_lczx",zx)
            # 更新子流程定义表
            zlcxx_dic = bbxx['nr']['gl_zlcdy'][0]
            zlcxx_dic['id'] = id
            zlcxx_dic['wym'] = bbxx['wym'] or ''
            zlcxx_dic['czr'] = get_sess_hydm()
            zlcxx_dic['czsj'] = get_strftime()
            ModSql.kf_ywgl_023.execute_sql(db,"update_zlcdy",zlcxx_dic)
        elif lx == 'jd':
            # 更新节点定义表
            jdxx_dic = bbxx['nr']['gl_jddy'][0]
            jdxx_dic['id'] = id
            jdxx_dic['wym'] = bbxx['wym'] or ''
            jdxx_dic['czr'] = get_sess_hydm()
            jdxx_dic['czsj'] = get_strftime()
            ModSql.kf_ywgl_023.execute_sql(db,"update_jddy",jdxx_dic)
            # 先删除所有的要素信息，在全部添加
            if len(bbxx['nr']['gl_jdys']) > 0:
                ModSql.kf_ywgl_023.execute_sql(db,"del_jdys", {'id': bbxx['nr']['gl_jdys'][0]['jddyid']})
            for ysxx in bbxx['nr']['gl_jdys']:
                ModSql.kf_ywgl_023.execute_sql(db,"add_jdys", ysxx)
            bbxx['nr']['DATA'] = pickle.dumps(bbxx['nr']['DATA'])
            # 更新BLOB管理表
            sql_data = {'nr':bbxx['nr']['DATA'], 'czr':get_sess_hydm(),'czsj':get_strftime(),'zdlst':['dm_id'],"tabname":['gl_jddy'],"pkid":id}
            ModSql.common.execute_sql(db,"edit_blob",sql_data)
        elif lx == 'gghs':
            if len(bbxx['nr']['gl_yw_gghs']) > 0:
                # 更新业务公共函数表
                bbxx['nr']['gl_yw_gghs'][0]['id'] = id
                bbxx['nr']['gl_yw_gghs'][0]['czr'] = get_sess_hydm()
                bbxx['nr']['gl_yw_gghs'][0]['czsj'] = get_strftime()
                bbxx['nr']['gl_yw_gghs'][0]['wym'] = bbxx['wym'] or ''
                ModSql.kf_ywgl_023.execute_sql(db,"update_gghs",bbxx['nr']['gl_yw_gghs'][0])
            bbxx['nr']['DATA'] = pickle.dumps(bbxx['nr']['DATA'])
            # 更新BLOB管理表
            sql_data = {'nr':bbxx['nr']['DATA'], 'czr':get_sess_hydm(),'czsj':get_strftime(),'zdlst':['nr_id'],"tabname":['gl_yw_gghs'],"pkid":id}
            ModSql.common.execute_sql(db,"edit_blob",sql_data)
        elif lx == 'sjk':
            # 删除数据库字段表
            ModSql.kf_ywgl_011.execute_sql(db,"del_sjkzdb_by_tabid",{'drop_table':[id]})
            # 删除数据库索引
            ModSql.kf_ywgl_011.execute_sql(db,"del_sjksy_by_tabid",{'drop_table':[id]})
            # 删除数据库约束
            ModSql.kf_ywgl_011.execute_sql(db,"del_sjkys_by_tabid",{'drop_table':[id]})
            bbxx['nr']['gl_sjkmxdy'][0]['wym'] = bbxx['wym']
            bbxx['nr']['gl_sjkmxdy'][0]['czr'] = get_sess_hydm()
            bbxx['nr']['gl_sjkmxdy'][0]['czsj'] = get_strftime()
            bbxx['nr']['gl_sjkmxdy'][0]['id'] = id
            ModSql.kf_ywgl_023.execute_sql(db,"update_sjkmxdy",bbxx['nr']['gl_sjkmxdy'][0])
            # 插入数据库索引
            for syxx in bbxx['nr']['gl_sjksy']:
                ModSql.kf_ywgl_011.execute_sql(db,"insert_sjksy",syxx)
            # 插入数据库字段
            for zdxx in bbxx['nr']['gl_sjkzdb']:
                ModSql.kf_ywgl_011.execute_sql(db,"insert_sjkzdb",zdxx)
            # 插入数据库约束
            for ysxx in bbxx['nr']['gl_sjkys']:
                ModSql.kf_ywgl_011.execute_sql(db,"insert_sjkys",ysxx)

        # 记录操作内容
        ins_czrz(db,'【版本还原：'+ lx +','+ id + ',' + str(bbxx['bbh']) +'】', gnmc = '版本控制管理_还原' )
                
def bbxxck_data_service( sql_data ):
    """
    # 版本信息查看数据获取
    """
    # 版本类型字典，key：类型，value[0]:字段名称，value[1]：数据表名
    bblx_dic = { 
        'jy'  : [ 'b.jymc',  'gl_jydy'  ],
        'zlc' : [ 'b.mc',    'gl_zlcdy' ],
        'jd'  : [ 'b.jdmc',  'gl_jddy'  ],
        'sjk' : [ 'b.sjbmc', 'gl_sjkmxdy' ],
        'gghs': [ 'b.mc',  'gl_yw_gghs' ] }
    if sql_data['bbh']:
        sql_data['bbh'] = sql_data['bbh'].split(',')
    with sjapi.connection() as db:
        # 查询版本信息总条数
        sql_data['mkey'] = [bblx_dic[sql_data['lx']][0]]
        sql_data['mVal'] = [bblx_dic[sql_data['lx']][1]]
        count = ModSql.kf_ywgl_023.execute_sql_dict(db,"get_bbxxck_count",sql_data)[0]['count']
        # 查询版本信息
        bbxx = ModSql.kf_ywgl_023.execute_sql_dict(db,"get_bbxxck_data",sql_data)
        return {'total':count,'rows':bbxx}
        
def bbxx_data_service(id,lx,bbh):
    """
    # 版本信息查看
    """
    with sjapi.connection() as db:
        sql_data = {'id':id, 'lx':lx, 'bbh':bbh}
        bbxx = ModSql.kf_ywgl_023.execute_sql_dict(db,"get_bbnr",sql_data)
        for gh in bbxx:
            gh['nr'] = pickle.loads(gh['nr'].read()) if gh['nr'] else ''
        if lx == 'jy':
            for bx in bbxx:
                del bx['nr']['gl_jydy'][0]['id']
                del bx['nr']['gl_jydy'][0]['ssywid']
            mc_dic = {'jym':'交易码', 'jymc':'交易名称', 'jyms':'交易描述', 'zt':'交易状态', 'zdfqpz':'自动发起配置', 'zdfqpzsm':'自动发起配置说明','timeout':'交易超时时间','dbjdmc':'打包节点名称','jbjdmc':'解包节点名称'}
            sort_dic = {'jym':'1', 'jymc':'2', 'jyms':'3', 'zt':'4', 'zdfqpz':'5', 'zdfqpzsm':'6','timeout':'7','dbjdmc':'8','jbjdmc':'9'}
            # 组织版本信息的内容，适用到easyui中grid的data
            bbxx_dg1 = []
            # 由于之前的版本提交没有加自动发起配置说明，所以为了解决线上不出错，只能是手动添加。没有什么实际意义。
            bbxx[0]['nr']['gl_jydy'][0]['zdfqpzsm'] = set_zdfqpzsm(bbxx[0]['nr']['gl_jydy'][0])
            for k, v in bbxx[0]['nr']['gl_jydy'][0].items():
                if k in mc_dic.keys():
                    bbxx_dg1.append( {'id':k, 'sxnr':v, 'sxmc':mc_dic.get(k),'sort':sort_dic.get(k)} )
            # 将内容排序
            bbxx_dg1 = sorted(bbxx_dg1, key = lambda x:x['sort'])
            # 组织返回的数据结构    
            bbdata = {
                'nr':{
                    'bbnr':bbxx[0]['nr']['DATA'],
                    'hsnr':'',
                    'bbxx':bbxx_dg1,
                    'bbh':bbxx[0]['bbh']
                }
            }
            url = "kf_ywgl/kf_ywgl_023/kf_ywgl_023_bbck_jy.html"
            rs = bbdata
        elif lx == 'zlc':
            # 将无用的字段名称去除
            for bx in bbxx:
                del bx['nr']['gl_zlcdy'][0]['id']
                del bx['nr']['gl_zlcdy'][0]['ssywid']
                del bx['nr']['gl_zlcdy'][0]['lb']
            mc_dic = {'lb':'类型', 'bm':'子流程编码', 'mc':'子流程名称', 'ms':'子流程描述'}
            # 组织版本信息的内容，适用到easyui中grid的data
            bbxx_dg1 = []
            for k, v in bbxx[0]['nr']['gl_zlcdy'][0].items():
                if k in mc_dic.keys():
                    bbxx_dg1.append( {'id':k, 'sxnr':v, 'sxmc':mc_dic.get(k)} )
            bbxx_dg1 = sorted(bbxx_dg1, key = lambda x:x['id'])
            # 组织返回的数据结构    
            bbdata = {
                'nr':{
                    'bbnr':bbxx[0]['nr']['DATA'],
                    'hsnr':'',
                    'bbxx':bbxx_dg1,
                    'bbh':bbxx[0]['bbh']
                }
            }
            url = "kf_ywgl/kf_ywgl_023/kf_ywgl_023_bbck_jy.html"
            rs = bbdata
        elif lx=='gghs':
            # 将无用的字段名称去除
            for bx in bbxx:
                del bx['nr']['gl_yw_gghs'][0]['id']
                del bx['nr']['gl_yw_gghs'][0]['ssyw_id']
                del bx['nr']['gl_yw_gghs'][0]['nr_id']
            mc_dic = {'mc':'函数名称', 'hsms':'函数描述'}
            sort_dic = {'mc':'1', 'hsms':'2'}
            # 组织版本信息的内容，适用到easyui中grid的data
            bbxx_dg1 = []
            for k, v in bbxx[0]['nr']['gl_yw_gghs'][0].items():
                if k in mc_dic.keys():
                    bbxx_dg1.append( {'id':k, 'sxnr':v, 'sxmc':mc_dic.get(k), 'sort':sort_dic.get(k)} )
            # 将内容排序
            bbxx_dg1 = sorted(bbxx_dg1, key = lambda x:x['sort'])
            # 组织返回的数据结构    
            bbdata = {
                'nr':{
                    'hsnr':json.dumps(bbxx[0]['nr']['DATA']),
                    'bbnr':'',
                    'bbxx':bbxx_dg1,
                    'bbh':bbxx[0]['bbh']
                }
            }
            url = "kf_ywgl/kf_ywgl_023/kf_ywgl_023_bbck_jy.html"
            rs = bbdata
        elif lx=='sjk':
            # 组织返回的数据结构    
            bbdata = {
                'nr':{
                    'gl_sjkzdb':bbxx[0]['nr']['gl_sjkzdb'],
                    'gl_sjksy':bbxx[0]['nr']['gl_sjksy'],
                    'gl_sjkys':bbxx[0]['nr']['gl_sjkys'],
                    'bbh':bbxx[0]['bbh']
                }
            }
            url = "kf_ywgl/kf_ywgl_023/kf_ywgl_023_bbck_sjk.html"
            rs = bbdata
        elif lx=='jd':
            # 将无用的字段名称去除
            for bx in bbxx:
                del bx['nr']['gl_jddy'][0]['id']
                del bx['nr']['gl_jddy'][0]['dm_id']
                del bx['nr']['gl_jddy'][0]['functionname']
                del bx['nr']['gl_jddy'][0]['type']
                del bx['nr']['gl_jddy'][0]['filename']
                del bx['nr']['gl_jddy'][0]['jdms']
            mc_dic = {'id':id, 'jdmc':'节点名称', 'jdlx':'节点类型', 'bm':'编码'}
            sort_dic = {'id':'5', 'jdmc':'1', 'jdlx':'2', 'bm':'3'}
            # 从节点要素中筛选的输入要素
            # 第一个版本的输入要素
            srys0 = []
            # 第一个版本的输出要素
            scys0 = []
            # 第一个版本的返回值
            fhz0 = []
            for nr in bbxx[0]['nr']['gl_jdys']:
                if nr['lb'] == '1':
                    srys0.append(nr)
                elif nr['lb'] == '2':
                    scys0.append(nr)
                elif nr['lb'] == '3':
                    fhz0.append(nr)
            # 将归属类别和来源转换为中文
            srys0 = passysxx(srys0)
            scys0 = passysxx(scys0)
            # 节点要素
            jddy0 = []
            for k, v in bbxx[0]['nr']['gl_jddy'][0].items():
                if k in mc_dic.keys():
                    jddy0.append( {'id':k, 'sxnr':v, 'sxmc':mc_dic.get(k), 'sort':sort_dic.get(k)} )
            # grid结果按id排序，使得版本信息下的两个版本是有序的。
            jddy0 = sorted(jddy0, key = lambda x:x['sort'])
            # 组织返回的数据结构  
            bbdata = {
                'nr':{
                    'gl_jddy':jddy0,
                    'gl_srys':srys0,
                    'gl_scys':scys0,
                    'gl_fhz':fhz0,
                    'bbh':bbxx[0]['bbh']
                },
                'data_nr':json.dumps(bbxx[0]['nr']['DATA']),
            }
            url = "kf_ywgl/kf_ywgl_023/kf_ywgl_023_bbck_jd.html"
            rs = bbdata
    return {'url':url,'rs':rs}
    
def bbdb_data_service(id,lx,bbh1,bbh2,type,jdlx):
    """
    # 版本对比
    """
    # 返回页面的结果集
    bbdata = {}
    # 需跳转的页面
    url = ''
    with sjapi.connection() as db:
        if type != 'bd':
            # 查询版本内容
            sql_data = {'id':id, 'lx':lx, 'bbh1':bbh1, 'bbh2':bbh2}
            bbxx = ModSql.kf_ywgl_023.execute_sql_dict(db,"get_bbdb_data",sql_data)
            for gh in bbxx:
                gh['nr'] = pickle.loads(gh['nr'].read()) if gh['nr'] else ''
            bbxx = sorted(bbxx, key = lambda x:x['bbh'])
        else:
            if not bbh1:
                rs = ModSql.kf_ywgl_023.execute_sql_dict(db, "get_max_bbh", {'id': id})
                bbh1 = rs[0]['bbh'] if rs else ''
            get_bcxx_r = get_bcxx( db, lx, id )
            bbxx = [copy.deepcopy({'nr':get_bcxx_r['bbnr']})]
            sql_data = {'id':id, 'lx':lx, 'bbh1':bbh1}
            rs = ModSql.kf_ywgl_023.execute_sql_dict(db,"get_bdwjdb_data",sql_data)
            for gh in rs:
                gh['nr'] = pickle.loads(gh['nr'].read()) if gh['nr'] else ''
            bbxx.extend(rs)
            # 添加版本号
            bbxx[0]['bbh'] = '本地版本'
            if len(rs) == 0:
                bbxx.append({})
            else:
                bbxx[1]['bbh'] = bbh1
    if lx=='jy':
        if bbxx[1] == {}:
            bbxx[1] = {
                'bbh': '0',
                'nr': {
                    'DATA': '',
                    'gl_jydy': [
                        {
                            'czr': '',
                            'jbjdmc': '',
                            'wym': '',
                            'zdfqpz': '',
                            'dbjdid': '',
                            'jyms': '',
                            'jbjdid': '',
                            'id': '',
                            'zt': '',
                            'jym': '',
                            'jymc': '',
                            'ssywid': '',
                            'dbjdmc': '',
                            'timeout': '',
                            'czsj': ''
                        }
                    ]
                }
            }
        # 将无用的字段名称去除
        for bx in bbxx:
            del bx['nr']['gl_jydy'][0]['id']
            del bx['nr']['gl_jydy'][0]['ssywid']
            del bx['nr']['gl_jydy'][0]['czr']
            del bx['nr']['gl_jydy'][0]['czsj']
            del bx['nr']['gl_jydy'][0]['wym']
            del bx['nr']['gl_jydy'][0]['jbjdid']
            del bx['nr']['gl_jydy'][0]['dbjdid']
        mc_dic = {'jym':'交易码', 'jymc':'交易名称', 'jyms':'交易描述', 'zt':'交易状态', 'zdfqpz':'自动发起配置', 'zdfqpzsm':'自动发起配置说明','timeout':'交易超时时间','dbjdmc':'打包节点名称','jbjdmc':'解包节点名称'}
        sort_dic = {'jym':'1', 'jymc':'2', 'jyms':'3', 'zt':'4', 'zdfqpz':'5', 'zdfqpzsm':'6','timeout':'7','dbjdmc':'8','jbjdmc':'9'}
        
        # 由于2015/09/11改了，版本提交时没有【自动发起配置说明】，那么之前的版本是没有的，所以需要手工加上，这样就避免了用户挨个提交了。
        bbxx[0]['nr']['gl_jydy'][0]['zdfqpzsm'] = set_zdfqpzsm(bbxx[0]['nr']['gl_jydy'][0])
        bbxx[1]['nr']['gl_jydy'][0]['zdfqpzsm'] = set_zdfqpzsm(bbxx[1]['nr']['gl_jydy'][0])
        
        # 比对两个版本中内容不一样的字段
        b0 = bbxx[0]['nr']['gl_jydy'][0]
        b1 = bbxx[1]['nr']['gl_jydy'][0]
        
        bz = ','.join([k for k, v in b0.items() if v != b1.get(k)])
        
        # 组织版本信息的内容，适用到easyui中grid的data
        bbxx_dg1 = [{'id':k, 'sxnr':v, 'sxmc':mc_dic.get(k),'sort':sort_dic.get(k)} for k, v in bbxx[0]['nr']['gl_jydy'][0].items()]
        bbxx_dg2 = [{'id':k, 'sxnr':v, 'sxmc':mc_dic.get(k),'sort':sort_dic.get(k)} for k, v in bbxx[1]['nr']['gl_jydy'][0].items()]
        # 将内容排序
        bbxx_dg1 = sorted(bbxx_dg1, key = lambda x:x['sort'])
        bbxx_dg2 = sorted(bbxx_dg2, key = lambda x:x['sort'])
        # 组织返回的数据结构    
        bbdata = {
            'bbh1':{
                'bbxx':bbxx_dg1,
                'bbh':bbxx[0]['bbh'],
                'bz':bz
            },
            'bbh2':{
                'bbxx':bbxx_dg2,
                'bbh':bbxx[1]['bbh'],
                'bz':bz
            },
            'bbh1_data': json.dumps(bbxx[0]['nr']['DATA']),
            'bbh2_data': json.dumps(bbxx[1]['nr']['DATA'])
        }
        url = "kf_ywgl/kf_ywgl_023/kf_ywgl_023_bbdb_jy.html"
    elif lx=='zlc':
        if bbxx[1] == {}:
            bbxx[1] = {
                'bbh': '0',
                'nr': {
                    'DATA': '',
                    'gl_zlcdy': [
                        {
                            'lb': '',
                            'czsj': '',
                            'ms': '',
                            'id': '',
                            'bm': '',
                            'wym': '',
                            'mc': '',
                            'ssywid': '',
                            'czr': ''
                        }
                    ]
                }
            }
        # 将无用的字段名称去除
        for bx in bbxx:
            del bx['nr']['gl_zlcdy'][0]['id']
            del bx['nr']['gl_zlcdy'][0]['ssywid']
            del bx['nr']['gl_zlcdy'][0]['czr']
            del bx['nr']['gl_zlcdy'][0]['czsj']
            del bx['nr']['gl_zlcdy'][0]['wym']
            del bx['nr']['gl_zlcdy'][0]['lb']
        mc_dic = {'lb':'类型', 'bm':'子流程编码', 'mc':'子流程名称', 'ms':'子流程描述'}
        # 比对两个版本中内容不一样的字段
        b0 = bbxx[0]['nr']['gl_zlcdy'][0]
        b1 = bbxx[1]['nr']['gl_zlcdy'][0]
        bz = ','.join([k for k, v in b0.items() if v != b1[k]])
        # 组织版本信息的内容，适用到easyui中grid的data
        bbxx_dg1 = [{'id':k, 'sxnr':v, 'sxmc':mc_dic.get(k)} for k, v in bbxx[0]['nr']['gl_zlcdy'][0].items()]
        bbxx_dg2 = [{'id':k, 'sxnr':v, 'sxmc':mc_dic.get(k)} for k, v in bbxx[1]['nr']['gl_zlcdy'][0].items()]
        # 将内容排序
        bbxx_dg1 = sorted(bbxx_dg1, key = lambda x:x['id'])
        bbxx_dg2 = sorted(bbxx_dg2, key = lambda x:x['id'])
        # 组织返回的数据结构    
        bbdata = {
            'bbh1':{
                'bbxx':bbxx_dg1,
                'bbh':bbxx[0]['bbh'],
                'bz':bz
            },
            'bbh2':{
                'bbxx':bbxx_dg2,
                'bbh':bbxx[1]['bbh'],
                'bz':bz
            },
            'bbh1_data': json.dumps(bbxx[0]['nr']['DATA']),
            'bbh2_data': json.dumps(bbxx[1]['nr']['DATA'])
        }
        url = "kf_ywgl/kf_ywgl_023/kf_ywgl_023_bbdb_jy.html"
    elif lx=='gghs':
        if bbxx[1] == {}:
            bbxx[1] = {
                'bbh': '0',
                'nr': {
                    'DATA': '',
                    'gl_yw_gghs': [
                        {
                            'hsms': '',
                            'mc': '',
                            'id': '',
                            'czsj': '',
                            'wym': '',
                            'nr_id': '',
                            'czr': '',
                            'ssyw_id': ''
                        }
                    ]
                }
            }
        # 将无用的字段名称去除
        for bx in bbxx:
            del bx['nr']['gl_yw_gghs'][0]['id']
            del bx['nr']['gl_yw_gghs'][0]['ssyw_id']
            del bx['nr']['gl_yw_gghs'][0]['nr_id']
            del bx['nr']['gl_yw_gghs'][0]['czr']
            del bx['nr']['gl_yw_gghs'][0]['czsj']
            del bx['nr']['gl_yw_gghs'][0]['wym']
        mc_dic = {'mc':'函数名称', 'hsms':'函数描述'}
        sort_dic = {'mc':'1', 'hsms':'2'}
        # 比对两个版本中内容不一样的字段
        b0 = bbxx[0]['nr']['gl_yw_gghs'][0]
        b1 = bbxx[1]['nr']['gl_yw_gghs'][0]
        bz = ','.join([k for k, v in b0.items() if v != b1[k]])
        # 组织版本信息的内容，适用到easyui中grid的data
        bbxx_dg1 = [{'id':k, 'sxnr':v, 'sxmc':mc_dic.get(k),'sort':sort_dic.get(k)} for k, v in bbxx[0]['nr']['gl_yw_gghs'][0].items()]
        bbxx_dg2 = [{'id':k, 'sxnr':v, 'sxmc':mc_dic.get(k),'sort':sort_dic.get(k)} for k, v in bbxx[1]['nr']['gl_yw_gghs'][0].items()]
        # 将内容排序
        bbxx_dg1 = sorted(bbxx_dg1, key = lambda x:x['sort'])
        bbxx_dg2 = sorted(bbxx_dg2, key = lambda x:x['sort'])
        # 组织返回的数据结构    
        bbdata = {
            'bbh1':{
                'bbxx':bbxx_dg1,
                'bbh':bbxx[0]['bbh'],
                'bz':bz
            },
            'bbh2':{
                'bbxx':bbxx_dg2,
                'bbh':bbxx[1]['bbh'],
                'bz':bz
            },
            'bbh1_data': json.dumps(bbxx[0]['nr']['DATA']),
            'bbh2_data': json.dumps(bbxx[1]['nr']['DATA'])
        }
        url = "kf_ywgl/kf_ywgl_023/kf_ywgl_023_bbdb_jy.html"
    elif lx=='sjk':
        if bbxx[1] == {}:
            bbxx[1] = {
                'bbh':'0',
                'nr': {
                    'gl_sjksy': [
                    ],
                    'gl_sjkzdb': [
                    ],
                    'gl_sjkys': [
                    ],
                    'gl_sjkmxdy': [
                    ]
                }
            }
        # 比对两个版本中内容不一样的字段
        # 数据库字段表
        bz_sjkzdb_left = []
        bz_sjkzdb_right = []
        left = bbxx[0]['nr']['gl_sjkzdb']
        right = bbxx[1]['nr']['gl_sjkzdb']
        id_left = {k['id'] for k in left}
        id_right = {k['id'] for k in right}
        for k in (id_left-id_right):
            right.append({'id':k,'sjb_id':'','zdmc':'','zdms':'','zdlx':'','zdcd':'','xscd':'','sfkk':'','iskey':'','mrz':''})
        for k in (id_right-id_left):
            left.append({'id':k,'sjb_id':'','zdmc':'','zdms':'','zdlx':'','zdcd':'','xscd':'','sfkk':'','iskey':'','mrz':''})
        left = sorted(left, key = lambda x:x['id'])
        right = sorted(right, key = lambda x:x['id'])
        # 标识循环的行数
        i = 0
        # 循环数据库字段表内容，将不同的字段选取出来。
        for sjkzd in left:
            bz = [k for k, v in sjkzd.items() if v != right[i].get(k)]
            if bz != []:
                bz_sjkzdb_left.append(copy.deepcopy({'id':left[i]['id'], 'bznr':bz}))
                bz_sjkzdb_right.append(copy.deepcopy({'id':right[i]['id'], 'bznr':bz}))
            i = i + 1
        bbxx[0]['nr']['gl_sjkzdb'] = left
        bbxx[1]['nr']['gl_sjkzdb'] = right
        # 数据库索引表
        bz_sjksy_left = []
        bz_sjksy_right = []
        left = bbxx[0]['nr']['gl_sjksy']
        right = bbxx[1]['nr']['gl_sjksy']
        
        id_left = {k['id'] for k in left}
        id_right = {k['id'] for k in right}
        for k in (id_left-id_right):
            right.append({'id':k,'sfwysy':'','syzd':'','sssjb_id':'','sylx':'','symc':''})
        for k in (id_right-id_left):
            left.append({'id':k,'sfwysy':'','syzd':'','sssjb_id':'','sylx':'','symc':''})
        left = sorted(left, key = lambda x:x['id'])
        right = sorted(right, key = lambda x:x['id'])
        # 标识循环的行数
        i = 0
        # 循环数据库字段表内容，将不同的字段选取出来。
        for sjksy in left:
            bz = [k for k, v in sjksy.items() if v != right[i].get(k)]
            if bz != []:
                bz_sjksy_left.append(copy.deepcopy({'id':left[i]['id'], 'bznr':bz}))
                bz_sjksy_right.append(copy.deepcopy({'id':right[i]['id'], 'bznr':bz}))
            i = i + 1
        bbxx[0]['nr']['gl_sjksy'] = left
        bbxx[1]['nr']['gl_sjksy'] = right
        # 数据库约束表
        bz_sjkys_left = []
        bz_sjkys_right = []
        left = bbxx[0]['nr']['gl_sjkys']
        right = bbxx[1]['nr']['gl_sjkys']
        
        id_left = {k['id'] for k in left}
        id_right = {k['id'] for k in right}
        for k in (id_left-id_right):
            right.append({'id':k,'sssjb_id':'','ysmc':'','yszd':''})
        for k in (id_right-id_left):
            left.append({'id':k,'sssjb_id':'','ysmc':'','yszd':''})
        left = sorted(left, key = lambda x:x['id'])
        right = sorted(right, key = lambda x:x['id'])
        # 标识循环的行数
        i = 0
        # 循环数据库字段表内容，将不同的字段选取出来。
        for sjkys in left:
            bz = [k for k, v in sjkys.items() if v != right[i].get(k)]
            if bz != []:
                bz_sjkys_left.append(copy.deepcopy({'id':left[i]['id'], 'bznr':bz}))
                bz_sjkys_right.append(copy.deepcopy({'id':right[i]['id'], 'bznr':bz}))
            i = i + 1
        bbxx[0]['nr']['gl_sjkys'] = left
        bbxx[1]['nr']['gl_sjkys'] = right
        
        # 组织返回的数据结构    
        bbdata = {
            'bbh1':{
                'gl_sjkzdb':bbxx[0]['nr']['gl_sjkzdb'],
                'gl_sjksy':bbxx[0]['nr']['gl_sjksy'],
                'gl_sjkys':bbxx[0]['nr']['gl_sjkys'],
                'bbh':bbxx[0]['bbh'],
                'bz': {
                    'bz_sjksy':bz_sjksy_left,
                    'bz_sjkzdb':bz_sjkzdb_left,
                    'bz_sjkys':bz_sjkys_left
                }
            },
            'bbh2':{
                'gl_sjkzdb':bbxx[1]['nr']['gl_sjkzdb'],
                'gl_sjksy':bbxx[1]['nr']['gl_sjksy'],
                'gl_sjkys':bbxx[1]['nr']['gl_sjkys'],
                'bbh':bbxx[1]['bbh'],
                'bz': {
                    'bz_sjksy':bz_sjksy_right,
                    'bz_sjkzdb':bz_sjkzdb_right,
                    'bz_sjkys':bz_sjkys_right
                }
            }
        }
        url = "kf_ywgl/kf_ywgl_023/kf_ywgl_023_bbdb_sjk.html"
    elif lx=='jd':
        if bbxx[1] == {}:
            bbxx[1] = {
                'bbh': '0',
                'nr': {
                    'DATA': '',
                    'gl_jdys': [],
                    'gl_jddy': [
                        {
                            'dm_id': '',
                            'type': '',
                            'bm': '',
                            'filename': '',
                            'jdms': '',
                            'czr': '',
                            'functionname': '',
                            'jdlx': '',
                            'jdmc': '',
                            'wym': '',
                            'czsj': '',
                            'id': ''
                        }
                    ]
                }
            }
        # 将无用的字段名称去除
        for bx in bbxx:
            del bx['nr']['gl_jddy'][0]['id']
            del bx['nr']['gl_jddy'][0]['dm_id']
            del bx['nr']['gl_jddy'][0]['functionname']
            del bx['nr']['gl_jddy'][0]['type']
            del bx['nr']['gl_jddy'][0]['filename']
            del bx['nr']['gl_jddy'][0]['czr']
            del bx['nr']['gl_jddy'][0]['czsj']
            del bx['nr']['gl_jddy'][0]['wym']
            del bx['nr']['gl_jddy'][0]['jdms']
        mc_dic = {'id':id, 'jdmc':'节点名称', 'jdlx':'节点类型', 'bm':'编码'}
        sort_dic = {'id':'5', 'jdmc':'1', 'jdlx':'2', 'bm':'3', 'jdms':'4'}
        # 从节点要素中筛选的输入要素
        # 第一个版本的输入要素
        srys_left = []
        # 第一个版本的输出要素
        scys_left = []
        # 第一个版本的返回值
        fhz_left = []
        # 第二个版本的输入要素
        srys_right = []
        # 第二个版本的输出要素
        scys_right = []
        # 第二个版本的返回值
        fhz_right = []
        for nr in bbxx[0]['nr']['gl_jdys']:
            if nr['lb'] == '1':
                srys_left.append(nr)
            elif nr['lb'] == '2':
                scys_left.append(nr)
            elif nr['lb'] == '3':
                fhz_left.append(nr)
        for nr in bbxx[1]['nr']['gl_jdys']:
            if nr['lb'] == '1':
                srys_right.append(nr)
            elif nr['lb'] == '2':
                scys_right.append(nr)
            elif nr['lb'] == '3':
                fhz_right.append(nr)
        # 比对两个版本中内容不一样的字段
        # 版本信息
        bz_jddy = ','.join([k for k, v in bbxx[0]['nr']['gl_jddy'][0].items() if v != bbxx[1]['nr']['gl_jddy'][0][k]])
        # 输入要素
        bz_srys_left = []
        bz_srys_right = []
        
        id_left = {k['id'] for k in srys_left}
        id_right = {k['id'] for k in srys_right}
        for k in (id_left-id_right):
            srys_right.append({'id':k,'jddyid':'','lb':'','bm':'','ysmc':'','mrz':'','gslb':'','ly':'','jkjy':'','ssgzmc':'','zjcs':''})
        for k in (id_right-id_left):
            srys_left.append({'id':k,'jddyid':'','lb':'','bm':'','ysmc':'','mrz':'','gslb':'','ly':'','jkjy':'','ssgzmc':'','zjcs':''})
        srys_left = sorted(srys_left, key = lambda x:x['id'])
        srys_right = sorted(srys_right, key = lambda x:x['id'])
        # 标识循环的行数
        i = 0
        # 循环输入要素内容，将不同的字段选取出来。
        for sjkys in srys_left:
            bz = [k for k, v in sjkys.items() if v != srys_right[i].get(k)]
            if bz != []:
                bz_srys_left.append(copy.deepcopy({'id':srys_left[i]['id'], 'bznr':bz}))
                bz_srys_right.append(copy.deepcopy({'id':srys_right[i]['id'], 'bznr':bz}))
            i = i + 1
        
        # 输出要素
        bz_scys_left = []
        bz_scys_right = []
        
        id_left = {k['id'] for k in scys_left}
        id_right = {k['id'] for k in scys_right}
        for k in (id_left-id_right):
            scys_right.append({'id':k,'jddyid':'','lb':'','bm':'','ysmc':'','mrz':'','gslb':'','ly':'','jkjy':'','ssgzmc':'','zjcs':''})
        for k in (id_right-id_left):
            scys_left.append({'id':k,'jddyid':'','lb':'','bm':'','ysmc':'','mrz':'','gslb':'','ly':'','jkjy':'','ssgzmc':'','zjcs':''})
        scys_left = sorted(scys_left, key = lambda x:x['id'])
        scys_right = sorted(scys_right, key = lambda x:x['id'])
        # 标识循环的行数
        i = 0
        # 循环输入要素内容，将不同的字段选取出来。
        for sjkys in scys_left:
            bz = [k for k, v in sjkys.items() if v != scys_right[i].get(k)]
            if bz != []:
                bz_scys_left.append(copy.deepcopy({'id':scys_left[i]['id'], 'bznr':bz}))
                bz_scys_right.append(copy.deepcopy({'id':scys_right[i]['id'], 'bznr':bz}))
            i = i + 1
        
        # 返回值
        bz_fhz_left = []
        bz_fhz_right = []
        
        id_left = {k['id'] for k in fhz_left}
        id_right = {k['id'] for k in fhz_right}
        for k in (id_left-id_right):
            fhz_right.append({'id':k,'jddyid':'','lb':'','bm':'','ysmc':'','mrz':'','gslb':'','ly':'','jkjy':'','ssgzmc':'','zjcs':''})
        for k in (id_right-id_left):
            fhz_left.append({'id':k,'jddyid':'','lb':'','bm':'','ysmc':'','mrz':'','gslb':'','ly':'','jkjy':'','ssgzmc':'','zjcs':''})
        fhz_left = sorted(fhz_left, key = lambda x:x['id'])
        fhz_right = sorted(fhz_right, key = lambda x:x['id'])
        # 标识循环的行数
        i = 0
        # 循环输入要素内容，将不同的字段选取出来。
        for sjkys in fhz_left:
            bz = [k for k, v in sjkys.items() if v != fhz_right[i].get(k)]
            if bz != []:
                bz_fhz_left.append(copy.deepcopy({'id':fhz_left[i]['id'], 'bznr':bz}))
                bz_fhz_right.append(copy.deepcopy({'id':fhz_right[i]['id'], 'bznr':bz}))
            i = i + 1
        # 节点要素
        jddy0 = [{'id':k, 'sxnr':v, 'sxmc':mc_dic.get(k), 'sort':sort_dic.get(k)} for k, v in bbxx[0]['nr']['gl_jddy'][0].items()]
        jddy1 = [{'id':k, 'sxnr':v, 'sxmc':mc_dic.get(k), 'sort':sort_dic.get(k)} for k, v in bbxx[1]['nr']['gl_jddy'][0].items()]
        # grid结果按id排序，使得版本信息下的两个版本是有序的。
        jddy0 = sorted(jddy0, key = lambda x:x['sort'])
        jddy1 = sorted(jddy1, key = lambda x:x['sort'])
        # 将归属类别和来源转换为中文
        srys_left = passysxx(srys_left)
        scys_left = passysxx(scys_left)
        srys_right = passysxx(srys_right)
        scys_right = passysxx(scys_right)
        # 组织返回的数据结构  
        bbdata = {
            'bbh1':{
                'gl_jddy':jddy0,
                'gl_srys':srys_left,
                'gl_scys':scys_left,
                'gl_fhz':fhz_left,
                'bbh':bbxx[0]['bbh'],
                'bz':{
                    'bz_srys':bz_srys_left,
                    'bz_scys':bz_scys_left,
                    'bz_fhz':bz_fhz_left,
                    'bz_jddy':bz_jddy
                }
            },
            'bbh2':{
                'gl_jddy':jddy1,
                'gl_srys':srys_right,
                'gl_scys':scys_right,
                'gl_fhz':fhz_right,
                'bbh':bbxx[1]['bbh'],
                'bz':{
                    'bz_srys':bz_srys_right,
                    'bz_scys':bz_scys_right,
                    'bz_fhz':bz_fhz_right,
                    'bz_jddy':bz_jddy
                }
            },
            'bbh1_data': json.dumps(bbxx[0]['nr']['DATA']),
            'bbh2_data': json.dumps(bbxx[1]['nr']['DATA']),
            'jdlx':jdlx
        }
        url = "kf_ywgl/kf_ywgl_023/kf_ywgl_023_bbdb_jd.html"
    return {'url':url,'rs':bbdata}

def passysxx(ysxx):
    gslb_dic = {'1':'节点使用', '2':'系统默认', '3':'系统参数表', '4':'业务参数表', '5':'交易参数表'}
    ly_dic = {'1':'自动', '2':'手工'}
    # 将归属类别转换为中文
    for srys in ysxx:
        srys['gslb'] = gslb_dic.get(srys['gslb'])
        srys['ly'] = ly_dic.get(srys['ly'])
    return ysxx