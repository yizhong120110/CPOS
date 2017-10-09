# -*- coding: utf-8 -*-
# Action: 交易流程编辑
# Author: gaorj
# AddTime: 2015-01-13
# Standard: 注释仅能以“#”开头，sql可以是“--”；注释不能同代码在同一行

import pickle, re, binascii, json, traceback
from sjzhtspj.esb import transaction_test
from sjzhtspj.esb import memcache_data_del
from sjzhtspj.esb import readlog
from sjzhtspj import ModSql, get_sess_hydm, logger
from sjzhtspj.common import get_uuid, py_check, get_strftime, update_wym, get_node_ys, format_log, get_strfdate2, ins_czrz, change_log_msg
from sjzhtspj.const import JDYS_LB_DIC, JDYS_LY_DIC


def index_service(params):
    """
    # 交易流程编辑
    """
    data = {
        'lx': params['lx'],
        'id': params['id'],
        'mc': params['mc'],
        'yw_data': [],
        'beai_data': [],
        'ptk_data': [],
        'jd_data': [],
        'ywsjb': [],
        'ywmc': ''
    }
    with sjapi.connection() as db:
        # 查询业务ID、流程编码、唯一码
        if params['lx'] == 'zlc':
            rs = ModSql.common.execute_sql_dict(db, "get_zlcdy", {'id': params['id']})
            data['ywid'] = rs[0]['ssywid'] if rs else ''
            data['lcbm'] = rs[0]['bm'] if rs else ''
            rs_wym = ModSql.kf_ywgl_005.execute_sql_dict(db, "get_zlc_wym", {'id': params['id']})
        else:
            rs = ModSql.common.execute_sql_dict(db, "get_jydy", {'id': params['id']})
            data['ywid'] = rs[0]['ssywid'] if rs else ''
            data['lcbm'] = rs[0]['jym'] if rs else ''
            rs_wym = ModSql.kf_ywgl_005.execute_sql_dict(db, "get_jy_wym", {'id': params['id']})
        data['wym'] = rs_wym[0]['wym1'] if rs_wym else ''
        data['wym_bbk'] = rs_wym[0]['wym2'] if rs_wym else ''
        
        # 查询业务数据表
        ywsjb = ModSql.kf_ywgl_005.execute_sql_dict(db, "get_ywsjb", {'ywid': data['ywid']})
        data['ywsjb'] = ywsjb
        
        # 查询所有的业务
        yw_data = ModSql.kf_ywgl_005.execute_sql_dict(db, "get_ywlb")
        data['yw_data'] = yw_data
        
        # 查询BEAI通讯子流程
        beai_data = ModSql.kf_ywgl_005.execute_sql_dict(db, "get_beai")
        data['beai_data'] = beai_data
        
        # 查询业务通讯子流程
        txk_data = ModSql.kf_ywgl_005.execute_sql_dict(db, "get_ywtxzlc")
        data['txk_data'] = txk_data
        
        # 查询业务普通子流程
        ptk_data = ModSql.kf_ywgl_005.execute_sql_dict(db, "get_ywptzlc")
        data['ptk_data'] = ptk_data
        
        # 查询交易流程布局用到的节点
        jd_data = ModSql.kf_ywgl_005.execute_sql_dict(db, "get_jd_jy")
        
        # 查询子流程流程布局用到的节点
        for row in ModSql.kf_ywgl_005.execute_sql_dict(db, "get_jd_zlc"):
            if row['id'] not in [jd['id'] for jd in jd_data]:
                jd_data.append(row)
        
        # 按节点名称排序
        data['jd_data'] = sorted(jd_data, key=lambda x:x['jdmc'])
        # 所属业务名称
        for yw in yw_data:
            if yw['id'] == data['ywid']:
                data['ywmc'] = yw['ywmc']
                break
    
    return data

def repository_data_service(type, ywid):
    """
    # 获取节点库数据
    """
    with sjapi.connection() as db:
        data = []
        if type == 'beai':
            # 查询BEAI通讯子流程
            data = ModSql.kf_ywgl_005.execute_sql_dict(db, "get_beai")
            for row in data:
                row['type'] = 'zlc'
        elif type == 'txk':
            # 查询业务通讯子流程
            data = ModSql.kf_ywgl_005.execute_sql_dict(db, "get_ywtxzlc", {'ywid': ywid})
            for row in data:
                row['type'] = 'zlc'
        elif type == 'ptk':
            # 查询业务普通子流程
            ptk_data = ModSql.kf_ywgl_005.execute_sql_dict(db, "get_ywptzlc", {'ywid': ywid})
            for row in ptk_data:
                row['type'] = 'zlc'
            # 查询交易流程布局用到的节点
            jd_data = ModSql.kf_ywgl_005.execute_sql_dict(db, "get_jd_jy", {'ywid': ywid})
            # 查询子流程流程布局用到的节点
            for row in ModSql.kf_ywgl_005.execute_sql_dict(db, "get_jd_zlc", {'ywid': ywid}):
                if row['id'] not in [jd['id'] for jd in jd_data]:
                    jd_data.append(row)
            # 按节点名称排序
            jd_data = sorted(jd_data, key=lambda x:x['jdmc'])
            for row in jd_data:
                row['type'] = 'jd'
            data = ptk_data + jd_data
        
        return data

def node_edit_service(params):
    """
    # 节点编辑
    """
    # 节点ID
    nodeid = params['nodeid']
    # 流程布局ID
    bjid = params['bjid']
    # 节点类型
    jdlx = params['jdlx']
    
    data = {
        'nodeid': nodeid,
        'bjid': bjid,
        'jdlx': jdlx,
        'jdmc': '',
        'bm': '',
        'nr': '',
        'jdys_lb': JDYS_LB_DIC,
        'jdys_ly': JDYS_LY_DIC
    }
    with sjapi.connection() as db:
        # 查询节点名称及代码内容
        rs_jd = ModSql.kf_ywgl_005.execute_sql_dict(db, "get_jdxx", {'id': nodeid}) if nodeid else []
        rs_jd = rs_jd[0] if rs_jd else {}
        
        data['bm'] = rs_jd.get('bm', '')
        data['jdmc'] = rs_jd.get('jdmc', '')
        data['jdlx'] = rs_jd.get('jdlx', jdlx)
        data['nr'] = pickle.loads(rs_jd.get('nr').read()) if rs_jd.get('nr') else ''
    
    return data

def node_edit_submit_service(params):
    """
    # 节点编辑
    """
    hydm = get_sess_hydm()
    # 节点ID
    nodeid = params['nodeid']
    # 节点类型
    jdlx = params['jdlx']
    # 节点编码
    jdbm = params['jdbm']
    # 节点名称
    jdmc = params['jdmc']
    # 节点逻辑代码
    jdnr = params['jdnr']
    # 原节点名称
    yjdmc = ''
    
    result = {'state':False, 'msg':'', 'nodeid': ''}
    
    # 校验函数内容的合法性
    jdnr_def = "def " + jdbm + "():\n" + jdnr
    jdnr_def = jdnr_def.replace( '\n', '\n    ' )
    error_msg = py_check(jdnr_def)
    if error_msg:
        result['msg'] = "代码有语法错误：\n" + error_msg
        return result
    
    with sjapi.connection() as db:
        # 去除#注释
        jdnr_nocmt = re.sub(r'#.*', '', jdnr)
        
        # 识别代码中的返回值
        fhz_lst = []
        for fhz in re.findall(r'^\s*return\s+(.*?)\s*$', jdnr_nocmt, re.MULTILINE):
            try:
                fhz = str(eval(fhz))
                if fhz and fhz not in fhz_lst:
                    fhz_lst.append(fhz)
            except:
                pass
        
        # 识别所有的要素（输入和输出）
        # jyzd.xxx 形式
        ys_lst = re.findall(r'\bjyzd\b\.\b(\w+)\b', jdnr_nocmt)
        # jyzd['xxx'] 形式
        for ys in re.findall(r'\bjyzd\b\[\s*(.+?)\s*\]', jdnr_nocmt):
            try:
                ys = str(eval(ys))
                if ys and ys not in ys_lst:
                    ys_lst.append(ys)
            except:
                pass
        
        # 识别代码中的输入要素
        srys_lst = []
        # jyzd.xxx 形式
        pattern_lst = [
            # jyzd.xxx == 123
            r'^[^#]*\bjyzd\.(\S+?)\b\s*(?:>=|<=|==|!=|>|<)\s*.*?\s*$',
            # 123 == jyzd.xxx
            r'^[^#]+?\s*(?:>=|<=|==|!=|>|<)\s*\bjyzd\.(\S+?)\b.*$',
            # a = jyzd.xxx
            r'^\s*\b.*?\s*=\s*\bjyzd\.(\S+?)\b.*$'
        ]
        for pattern in pattern_lst:
            for srys in re.findall(pattern, jdnr_nocmt, re.MULTILINE):
                if srys not in srys_lst:
                    srys_lst.append(srys)
        # jyzd['xxx'] 形式
        pattern_lst = [
            # jyzd['xxx'] == 123
            r'^[^#]*\bjyzd\[\s*(.+?)\s*\]\s*(?:>=|<=|==|!=|>|<)\s*.*?\b.*',
            # 123 == jyzd['xxx']
            r'^[^#]+?\s*(?:>=|<=|==|!=|>|<)\s*\bjyzd\[\s*(.+?)\s*\].*$',
            # a = jyzd['xxx']
            r'^\s*\b.*?\s*=\s*\bjyzd\[\s*(.+?)\s*\].*$'
        ]
        for pattern in pattern_lst:
            for srys in re.findall(pattern, jdnr_nocmt, re.MULTILINE):
                try:
                    srys = str(eval(srys))
                    if srys and srys not in srys_lst:
                        srys_lst.append(srys)
                except:
                    pass
        
        # 识别代码中的输出要素
        scys_lst = []
        # jyzd.xxx 形式
        for scys, value in re.findall(r'^\s*jyzd\.(\S+?)\b\s*[+-]?=[^=]\s*(.*?)\s*$', jdnr_nocmt, re.MULTILINE):
            if scys not in scys_lst:
                scys_lst.append(scys)
        # jyzd['xxx'] 形式
        for scys, value in re.findall(r'^\s*jyzd\[\s*(.+?)\s*\]\s*[+-]?=[^=]\s*(.*?)\s*$', jdnr_nocmt, re.MULTILINE):
            try:
                scys = str(eval(scys))
                if scys and scys not in scys_lst:
                    scys_lst.append(scys)
            except:
                pass
        
        for ys in ys_lst:
            # 未分类的剩余要素
            if ys not in scys_lst and ys not in srys_lst:
                srys_lst.append(ys)
        
        # 要素或返回值超过50位，不能保存
        if [k for k in (srys_lst+scys_lst+fhz_lst) if len(k) > 50]:
            result['msg'] = "代码中有长度超过50位的要素或返回值，\n请修改后再保存"
            return result
        
        # 节点逻辑代码转为二进制
        jdnr = pickle.dumps(jdnr)
        
        insert = True
        # 如果存在节点ID
        if nodeid:
            rs = ModSql.kf_ywgl_005.execute_sql(db, "check_jdid", {'id': nodeid})
            # 节点定义表中存在此节点
            if rs:
                yjdmc = rs[0].jdmc
                insert = False
                # 更新节点定义表
                sql_data = {'id': nodeid, 'jdmc': jdmc, 'czr': hydm, 'czsj': get_strftime()}
                ModSql.kf_ywgl_005.execute_sql(db, "update_jddy", sql_data)
                # 更新BLOB表
                sql_data = {'nodeid': nodeid, 'czr': hydm, 'czsj':get_strftime(), 'nr': jdnr}
                ModSql.kf_ywgl_005.execute_sql(db, "update_blob_jd", sql_data)
        
        # 否则新增
        if insert:
            # 检查节点编码是否已存在
            sql_data = {'bm': jdbm}
            rs = ModSql.kf_ywgl_005.execute_sql(db, "check_jddm", sql_data)
            if rs:
                result['msg'] = '节点编码[%s]已经存在，请重新输入' % jdbm
                return result
            
            # 插入节点定义表
            nodeid = nodeid or get_uuid()
            dm_id = get_uuid()
            sql_data = {'id': nodeid, 'bm': jdbm, 'jdlx': jdlx, 'jdmc': jdmc, 'dm_id': dm_id, 'czr': hydm, 'czsj': get_strftime()}
            ModSql.kf_ywgl_005.execute_sql(db, "insert_jddy", sql_data)
            # 插入BLOB表
            sql_data = {'blobid': dm_id, 'lx':'gl_jddy', 'czr': hydm, 'czsj':get_strftime(), 'nr': jdnr}
            ModSql.common.execute_sql(db, "add_blob", sql_data)
        
        # 查询出原有节点要素的备注
        rs_jdys = ModSql.common.execute_sql_dict(db, "get_jdys_new", {'ids': [nodeid]})
        jdys_dic = {(row['lb'], row['bm']): row for row in rs_jdys}
        # 删除此节点原有的节点要素（包含自动识别的输入要素、自动识别的输出要素、返回值）
        sql_data = {'jddyid': nodeid}
        ModSql.kf_ywgl_005.execute_sql(db, "del_jdys_for_update", sql_data)
        # 新节点要素信息
        new_jdys_lst = []
        # 插入新的节点要素（输入要素）
        for srys in srys_lst:
            sql_data = {
                'id': jdys_dic.get(('1', srys), {}).get('id') or get_uuid(), 
                'lb': '1', 
                'bm': srys, 
                'ysmc': jdys_dic.get(('1', srys), {}).get('ysmc', ''), 
                'jddyid': nodeid, 
                'mrz': '', 
                #'gslb': '1', 
                'ly': '1',
                'jkjy': jdys_dic.get(('1', srys), {}).get('jkjy'), 
                'ssgzmc': jdys_dic.get(('1', srys), {}).get('ssgzmc'), 
                'zjcs': jdys_dic.get(('1', srys), {}).get('zjcs')
            }
            ModSql.kf_ywgl_005.execute_sql(db, "insert_jdys", sql_data)
            # 追加
            new_jdys_lst.append( ('1',srys) )
        # 插入新的节点要素（输出要素）
        for scys in scys_lst:
            sql_data = {
                'id': jdys_dic.get(('2', scys), {}).get('id') or get_uuid(), 
                'lb': '2', 
                'bm': scys, 
                'ysmc': jdys_dic.get(('2', scys), {}).get('ysmc', ''), 
                'jddyid': nodeid, 
                'mrz': '', 
                #'gslb': '1', 
                'ly': '1', 
                'jkjy': jdys_dic.get(('2', scys), {}).get('jkjy'), 
                'ssgzmc': jdys_dic.get(('2', scys), {}).get('ssgzmc'), 
                'zjcs': jdys_dic.get(('2', scys), {}).get('zjcs')
            }
            ModSql.kf_ywgl_005.execute_sql(db, "insert_jdys", sql_data)
            # 追加
            new_jdys_lst.append( ('2',scys) )
        # 插入新的节点要素（返回值）
        for fhz in fhz_lst:
            sql_data = {
                'id': jdys_dic.get(('3', fhz), {}).get('id') or get_uuid(), 
                'lb': '3', 
                'bm': fhz, 
                'ysmc': jdys_dic.get(('3', fhz), {}).get('ysmc', ''), 
                'jddyid': nodeid, 
                'mrz': '', 
                #'gslb': '1', 
                'ly': '1', 
                'jkjy': jdys_dic.get(('3', fhz), {}).get('jkjy'), 
                'ssgzmc': jdys_dic.get(('3', fhz), {}).get('ssgzmc'), 
                'zjcs': jdys_dic.get(('3', fhz), {}).get('zjcs')
            }
            ModSql.kf_ywgl_005.execute_sql(db, "insert_jdys", sql_data)
            # 追加
            new_jdys_lst.append( ('3',fhz) )
        
        # 更新唯一码
        update_wym(db, 'jd', nodeid)
        
        # 查询当前唯一码和最新版本唯一码
        rs = ModSql.kf_ywgl_005.execute_sql_dict(db, "get_jd_wym", {'id': nodeid})
        wym = rs[0]['wym1'] if rs else ''
        wym_bbk = rs[0]['wym2'] if rs else ''
        
        # 新增行员操作日志
        if insert:
            nr = '交易编辑-节点新增:节点编码：%s,节点名称：%s,要素信息：%s' % ( jdbm, jdmc, str( new_jdys_lst ) )
        else:
            old_xx = '节点编码：%s,节点名称：%s,要素信息：%s' % ( jdbm, yjdmc, str( sorted( jdys_dic.keys() ) )  )
            now_xx = '节点编码：%s,节点名称：%s,要素信息：%s' % ( jdbm, jdmc, str(new_jdys_lst)  )
            nr = '交易编辑-节点编辑:编辑前：[%s]，编辑后：[%s]' % ( old_xx, now_xx )
        ins_czrz(db, nr, pt='kf', gnmc='交易编辑-节点%s' % ( '新增' if insert else '编辑' ))
        
        # 清除memcache
        memcache_data_del([nodeid])
        
        result['wym'] = wym
        result['wym_bbk'] = wym_bbk
        result['nodeid'] = nodeid
        result['state'] = True
        result['msg'] = '保存成功'
    
    return result

def node_ys_service(params):
    """
    # 节点要素获取
    """
    # 节点ID
    nodeid = params['nodeid']
    # 类别（1:输入要素 2:输出要素 3:返回值（编码字段存放返回值））
    lb = params['lb']
    
    data = {'total': 0, 'rows': []}
    with sjapi.connection() as db:
        ys = get_node_ys(db, nodeid, '1', lb)
        for row in ys:
            row['gslbmc'] = JDYS_LB_DIC.get(row['gslb'], row['gslb'])
            row['ly'] = JDYS_LY_DIC.get(row['ly'], row['ly'])
        
        data['total'] = len(ys)
        data['rows'] = ys
    
    return data

def node_ys_edit_service(params):
    """
    # 节点要素编辑
    """
    # 节点ID
    nodeid = params['nodeid']
    # 节点要素ID
    id = params['id']
    # 类别（1:输入要素 2:输出要素 3:返回值（编码字段存放返回值））
    lb = params['lb']
    # 要素编码
    bm = params['bm']
    # 要素名称
    ysmc = params['ysmc']
    # 默认值
    mrz = params['mrz']
    
    result = {'state': False, 'msg': ''}
    with sjapi.connection() as db:
        # 查询节点要素
        sql_data = {'jddyid': nodeid, 'id': id, 'bm': bm, 'lb': lb}
        rs = ModSql.kf_ywgl_005.execute_sql(db, "check_jdys", sql_data)
        if rs:
            lable = ''
            if lb == '1':
                lable = '输入要素'
            elif lb == '2':
                lable = '输出要素'
            result['msg'] = lable + '[%s]已经存在，请重新输入' % bm
            return result
        
        # 查询节点ID
        rs = ModSql.kf_ywgl_005.execute_sql(db, "get_jdid", {'id': id})
        jddyid = rs[0].jddyid if rs else None
        
        # 更新要素定义表
        sql_data = {'id':id, 'bm':bm, 'ysmc':ysmc, 'mrz':mrz}
        ModSql.kf_ywgl_005.execute_sql(db, "update_jdys", sql_data)
        
        # 更新唯一码
        update_wym(db, 'jd', jddyid)
        
        result['state'] = True
        result['msg'] = '修改成功'
    
    return result

def node_ys_add_service(params):
    """
    # 节点要素新增
    """
    # 节点ID
    nodeid = params['nodeid']
    # 流程布局ID
    bjid = params['bjid']
    # 类别（1:输入要素 2:输出要素 3:返回值（编码字段存放返回值））
    lb = params['lb']
    # 要素编码
    bm = params['bm']
    # 要素名称
    ysmc = params['ysmc']
    ## 归属类别（'1': '节点使用', '2': '系统默认', '3': '系统参数表', '4': '业务参数表', '5': '交易参数表'）
    #gslb = params['gslb']
    # 默认值
    mrz = params['mrz']
    
    result = {'state': False, 'msg': '', 'nodeid': ''}
    with sjapi.connection() as db:
        nodeid = nodeid or get_uuid()
        result['nodeid'] = nodeid
        
        # 查询节点要素
        sql_data = {'jddyid': nodeid, 'bm': bm, 'lb': lb}
        rs = ModSql.kf_ywgl_005.execute_sql(db, "check_jdys", sql_data)
        if rs:
            lable = ''
            if lb == '1':
                lable = '输入要素'
            elif lb == '2':
                lable = '输出要素'
            result['msg'] = lable + '[%s]已经存在，请重新输入' % bm
            return result
        
        # 插入要素定义表
        sql_data = {
            'id':get_uuid(), 
            'lb':lb, 
            'bm':bm, 
            'ysmc':ysmc, 
            'jddyid':nodeid, 
            'mrz':mrz, 
            #'gslb':gslb, 
            'ly': '2', 
            'jkjy': '', 
            'ssgzmc': '', 
            'zjcs': ''
        }
        ModSql.kf_ywgl_005.execute_sql(db, "insert_jdys", sql_data)
        
        # 更新唯一码
        update_wym(db, 'jd', nodeid)
        
        result['state'] = True
        result['msg'] = '新增成功'
    
    return result

def node_ys_del_service(params):
    """
    # 节点要素删除
    """
    result = {'state':False, 'msg':''}
    ids = params['ids'].split(',')
    ids_data = {'ids': ids}
    
    with sjapi.connection() as db:
        # 查询业务下的子流程
        ModSql.kf_ywgl_005.execute_sql(db, "del_jdys", ids_data)
        result['state'] = True
        result['msg'] = '删除成功'
    
    return result

def node_fhz_update_service(fhzid, bz):
    """
    # 编辑节点返回值备注
    """
    with sjapi.connection() as db:
        # 更新节点返回值备注
        ModSql.kf_ywgl_005.execute_sql(db, "update_jdys_fhzbz", {'id': fhzid, 'ysmc': bz})
        
        return {'state': True, 'msg': '更新成功'}

def node_yycs_service(params):
    """
    # 节点引用次数
    """
    # 节点ID
    nodeid = params['nodeid']
    
    data = {'total': 0, 'rows': []}
    with sjapi.connection() as db:
        # 查询节点引用次数
        rs_yycs = ModSql.kf_ywgl_005.execute_sql_dict(db, "count_jdyycs", {'jddyid': nodeid})
        
        data['total'] = len(rs_yycs)
        data['rows'] = rs_yycs
    
    return data

def lc_save_service(params):
    """
    # 流程保存
    """
    lx = params['lx']
    id = params['id']
    lcbm = params['lcbm']
    nodes = params['nodes']
    conns = params['conns']
    # 需要关联的字段
    zd = 'sszlcid' if lx == 'zlc' else 'ssjyid'
    
    nodes_dic = {item['bjid']:item for item in nodes}
    
    with sjapi.connection() as db:
        # 查询流程布局表中的节点ID
        rs_lcbj = ModSql.kf_ywgl_005.execute_sql_dict(db, "get_lcbj_nodeid", {'zd': [zd], 'id': id})
        
        # 前台提交的所有布局ID
        ids_nodes = set(nodes_dic.keys())
        # 目前流程布局表中的节点ID
        ids_lcbj = {row['id'] for row in rs_lcbj}
        
        # 更新已在流程布局表中的节点坐标位置
        for bjid in (ids_nodes & ids_lcbj):
            sql_data = {
                'id': bjid,
                'x': nodes_dic[bjid]['x'],
                'y': nodes_dic[bjid]['y']
            }
            ModSql.kf_ywgl_005.execute_sql_dict(db, "update_lcbj_wz", sql_data)
        
        # 向节点定义表（或子流程定义表）、流程布局表插入新的记录
        for bjid in (ids_nodes - ids_lcbj):
            sql_data = {
                'id': bjid,
                'x': nodes_dic[bjid]['x'],
                'y': nodes_dic[bjid]['y'],
                'jddyid': nodes_dic[bjid]['nodeid'],
                'ssid': id
            }
            if nodes_dic[bjid].get('type') == 'zlc':
                sql_data['jdlx'] = '2'
            else:
                jdlx_dic = {'start_zlc':'3', 'end_zlc':'4', 'start_jy':'5', 'end_jy':'6'}
                sql_data['jdlx'] = jdlx_dic.get(nodes_dic[bjid].get('type'), '1')
            
            # 插入流程布局表
            sql_data['zd'] = [zd]
            ModSql.kf_ywgl_005.execute_sql_dict(db, "insert_lcbj", sql_data)
        
        # 删除流程布局表中的记录
        for bjid in (ids_lcbj - ids_nodes):
            # 删除流程布局表中的记录
            ModSql.kf_ywgl_005.execute_sql_dict(db, "delete_lcbj", {'id': bjid})
        
        # 更新流程走向
        rs_lczx = ModSql.common.execute_sql_dict(db, "get_lczx", {'id': id})
        lczx_dic = {(row['qzjdlcbjid'], row['hzjdlcbjid'], row['fhz']): row for row in rs_lczx}
        ModSql.kf_ywgl_005.execute_sql_dict(db, "delete_lczx", {'ssid': id})
        for conn in conns:
            sql_data = {
                'id': lczx_dic.get((conn['source'], conn['target'], conn['label']), {}).get('id') or get_uuid(),
                'fhz': conn['label'] or '',
                'qzjdlcbjid': conn['source'],
                'hzjdlcbjid': conn['target'],
                'sslb': '2' if lx == 'zlc' else '1',
                'ssid': id
            }
            ModSql.kf_ywgl_005.execute_sql_dict(db, "insert_lczx", sql_data)
        
        # 更新唯一码
        lx = 'zlc' if lx == 'zlc' else 'jy'
        update_wym(db, lx, id)
        
        if lx == 'zlc':
            rs = ModSql.kf_ywgl_005.execute_sql_dict(db, "get_zlc_wym", {'id': id})
        else:
            rs = ModSql.kf_ywgl_005.execute_sql_dict(db, "get_jy_wym", {'id': id})
        wym = rs[0]['wym1'] if rs else ''
        wym_bbk = rs[0]['wym2'] if rs else ''
        
        # 清除memcache
        memcache_data_del([lcbm])
        
        return {'state': True, 'msg': '保存成功', 'wym': wym, 'wym_bbk': wym_bbk}

def get_wym_service(lx, id):
    """
    # 获取唯一码
    """
    with sjapi.connection() as db:
        if lx == 'zlc':
            rs = ModSql.kf_ywgl_005.execute_sql_dict(db, "get_zlc_wym", {'id': id})
        elif lx == 'jy':
            rs = ModSql.kf_ywgl_005.execute_sql_dict(db, "get_jy_wym", {'id': id})
        elif lx == 'jd':
            rs = ModSql.kf_ywgl_005.execute_sql_dict(db, "get_jd_wym", {'id': id})
        else:
            rs = []
        wym = rs[0]['wym1'] if rs else ''
        wym_bbk = rs[0]['wym2'] if rs else ''
        
        return {'state': True, 'msg': '', 'wym': wym, 'wym_bbk': wym_bbk}

def dbts_ys_data_service(params):
    """
    # 单步调试要素
    """
    # 交易ID/子流程ID
    lcid = params['lcid']
    # 节点ID
    nodeid = params['nodeid']
    # 节点类型（'strat_jy':交易开始节点，'strat_zlc':子流程开始节点，'end_jy':交易结束节点，'end_zlc':子流程结束节点，'jd':节点，'zlc':子流程）
    type = params['type']
    # 类别 1输入要素，2输出要素，3返回值
    lb = params['lb']
    
    data = {'total': 0, 'rows': []}
    with sjapi.connection() as db:
        if type in ('start_zlc', 'start_jy'):
            rs = ModSql.common.execute_sql(db, "get_jydy", {'id': lcid})
            nodeid = rs[0].jbjdid if rs else None
        elif type in ('end_zlc', 'end_jy'):
            rs = ModSql.common.execute_sql(db, "get_jydy", {'id': lcid})
            nodeid = rs[0].dbjdid if rs else None
        # 获取要素
        node_lx = '2' if type == 'zlc' else '1'
        ys = get_node_ys(db, nodeid, node_lx, lb) if nodeid else []
        ys_set = {k['bm'] for k in ys}
        
        data['rows'] = [{'jdysbm':bm, 'value':''} for bm in sorted(ys_set)]
        data['total'] = len(data['rows'])
        return data

def djbjd_data_service(params):
    """
    # 获取打解包节点
    """
    # 节点类型，'8'：打包，'9'：解包
    jdlx = '8' if params['lx'] == 'db' else '9'
    # 交易ID
    jyid = params['jyid']
    
    with sjapi.connection() as db:
        # 查询所有打解包节点
        rs_djbjd = ModSql.kf_ywgl_005.execute_sql_dict(db, "get_djbjd", {'jdlx': jdlx})
        # 查询当前交易的打解包节点
        rs_jydjbjd = ModSql.kf_ywgl_005.execute_sql_dict(db, "get_jyjbjd", {'id': jyid})
        for row in rs_djbjd:
            if rs_jydjbjd and (rs_jydjbjd[0]['dbjdid'] == row['id'] or rs_jydjbjd[0]['jbjdid'] == row['id']):
                # 让前台选中当前设置的打解包
                row['selected'] = True
                break
        return rs_djbjd

def set_djbjd_service(params):
    """
    # 设置打解包节点
    """
    zd = 'jbjdid' if params['lx'] == 'jb' else 'dbjdid'
    
    with sjapi.connection() as db:
        sql_data = {'zd': [zd], 'id': params['lcid'], 'jdid': params['jdid']}
        rs = ModSql.kf_ywgl_005.execute_sql_dict(db, "set_djbjd", sql_data)
        # 更新唯一码
        update_wym(db, 'jy', params['lcid'])
        # 清除memcache
        memcache_data_del([params['lcbm']])
        return {'state': True, 'msg': '保存成功'}

def dbts_bz_data_service(params):
    """
    # 获取其他步骤
    """
    data = {'bz': [], 'ys': {}}
    with sjapi.connection() as db:
        rs = ModSql.kf_ywgl_005.execute_sql_dict(db, "get_bz_ys", {'id': params['nodeid'], 'lx': params['lx']})
        bz_set = {(row['bzid'], row['mc']) for row in rs}
        bz_set = sorted(bz_set, key=lambda x:x[1])
        data['bz'] = [{'bzid':id, 'bzmc':mc} for id, mc in bz_set]
        for row in rs:
            data['ys'].setdefault(row['bzid'], []).append(row)
        return data

def get_ywsjb_service(ywid):
    """
    # 获取业务数据表
    """
    with sjapi.connection() as db:
        rs = ModSql.kf_ywgl_005.execute_sql_dict(db, "get_ywsjb", {'ywid': ywid})
        return rs

def demo_jbxx_data_service(params):
    """
    # 获取Demo基本信息
    """
    # 业务ID
    ywid = params['ywid']
    
    with sjapi.connection() as db:
        rs = ModSql.kf_ywgl_005.execute_sql_dict(db, "get_demo_jbxx", params)
        rs_count = ModSql.kf_ywgl_005.execute_sql(db, "get_demo_jbxx_count", params)[0].count
        return {'rows': rs, 'total': rs_count}

def demo_jbxx_data_add_service(params):
    """
    # 新增Demo基本信息
    """
    with sjapi.connection() as db:
        id = params['id']
        sql_data = {'id': id or get_uuid(), 'mc': params['mc'], 'sjms': params['ms'], 'ssywid': params['ssywid']}
        if id:
            rs = ModSql.kf_ywgl_005.execute_sql_dict(db, "check_demo_jbxx_mc", sql_data)
            if rs:
                return {'state': False, 'msg': '编号名称[%s]已经存在，请重新输入' % params['mc']}
            ModSql.kf_ywgl_005.execute_sql_dict(db, "update_demo_jbxx", sql_data)
        else:
            rs = ModSql.kf_ywgl_005.execute_sql_dict(db, "check_demo_jbxx_mc", {'mc': params['mc'], 'ssywid': params['ssywid']})
            if rs:
                return {'state': False, 'msg': '编号名称[%s]已经存在，请重新输入' % params['mc']}
            ModSql.kf_ywgl_005.execute_sql_dict(db, "insert_demo_jbxx", sql_data)
        return {'state': True, 'msg': '保存成功', 'demo_id': sql_data['id']}

def demo_jbxx_data_del_service(id):
    """
    # 删除Demo基本信息和数据
    """
    result = {'state': False, 'msg': ''}
    with sjapi.connection() as db:
        rs = ModSql.kf_ywgl_005.execute_sql_dict(db, "check_demo_jbxx", {'id': id})
        if rs[0]['count'] > 0:
            result['msg'] = 'Demo已被引用无法删除'
            return result
        ModSql.kf_ywgl_005.execute_sql_dict(db, "delete_demo_jbxx", {'id': id})
        ModSql.kf_ywgl_005.execute_sql_dict(db, "delete_demo_sj", {'id': id})
    return {'state': True, 'msg': '删除成功'}

def demo_sj_data_service(params):
    """
    # 获取Demo数据
    """
    # Demo基本信息ID
    demojbxxid = params['demojbxxid']
    # 数据表名称
    sjbmc = params['sjbmc']
    
    data = {}
    with sjapi.connection() as db:
        sql_data = {'demojbxxid': demojbxxid, 'sjbmc': sjbmc}
        # 查询Demo数据表头
        demojbxxzbzdmc = ModSql.kf_ywgl_005.execute_sql_dict(db, "get_demo_sj_fields", {"sjbmc": sjbmc})
        # 查询Demo数据
        demojbxxzbzd = ModSql.kf_ywgl_005.execute_sql_dict(db, "get_demo_sj", {"sjbjc": sjbmc, 'demojbxxid': demojbxxid})
        # 看是否有表字段值,如果没有直接返回
        if not demojbxxzbzdmc:
            return  {"columns":[], "rows":[], "total": 0}
        # 组织列名
        columns = [{"field":row["zdmc"], "title":row["zdmc"], "width":100} for row in demojbxxzbzdmc]
        # 遍历动态组织前台渲染表格表头和内容
        data = {"columns":[], "rows":[], "total": 0}
        list_dic = {}
        keys = []
        for row in demojbxxzbzd:
            list_dic.setdefault((row['sjid'], row['xssx']), {})[row['zdm'].lower()] = (row['zdz'] if row['zdz'] else '')
            if row['iskey'] == '1':
                keys.append(row['zdm'])
        sjid_xssx_lst = []
        rows = []
        # 按主键排序
        data_sorted = sorted(list_dic.items(), key=lambda x:[x[1].get(k.lower()) for k in list( set( keys ) )])
        for sjid_xssx, row in data_sorted:
            sjid_xssx_lst.append(sjid_xssx)
            rows.append(row)
        data["sjid_xssx"] = sjid_xssx_lst
        data["rows"] = rows
        data['total'] = len(rows)
        data["columns"].append(columns)
        data["keys"] = list(set(keys))
        return data

def demo_sj_data_add_service(params):
    """
    # 新增Demo数据
    """
    # Demo基本信息ID
    demojbxxid = params['demojbxxid']
    # 数据表简称
    sjbjc = params['sjbjc']
    # 数据表中文名称
    sjbms = params['sjbms']
    # 数据
    data = params['data']
    
    with sjapi.connection() as db:
        sql_data = {'demojbxxid': demojbxxid, 'sjbjc': sjbjc}
        rs = ModSql.kf_ywgl_005.execute_sql(db, "check_demo_sj", sql_data)
        if not rs:
            # 插入一条数据级别为“1数据表”的记录
            sjid = get_uuid()
            sql_data = {'id': sjid, 'demojbxxid': demojbxxid, 'sjbjc': sjbjc, 'sjbms': sjbms}
            ModSql.kf_ywgl_005.execute_sql(db, "insert_demo_sj_1", sql_data)
        else:
            sjid = rs[0].id
        
        # 获取最大显示顺序号
        sql_data = {'demojbxxid': demojbxxid, 'sjid': sjid}
        rs = ModSql.kf_ywgl_005.execute_sql(db, "get_demo_sj_max_xh", sql_data)
        xh = rs[0].xssx + 1 if (rs and rs[0].xssx is not None) else 0
        for zdm, zdz in data.items():
            sql_data = {'id': get_uuid(), 'demojbxxid': demojbxxid, 'sjbjc': sjbjc, 'sjbms': sjbms, 'sjid': sjid, 'xssx': xh, 'zdm': zdm, 'zdz': zdz}
            ModSql.kf_ywgl_005.execute_sql(db, "insert_demo_sj_2", sql_data)
        return {'state': True, 'msg': '新增成功'}

def demo_sj_data_pladd_service(params):
    """
    # 新增Demo数据
    """
    # Demo基本信息ID
    demojbxxid = params['demojbxxid']
    # 数据表简称
    sjbjc = params['sjbjc']
    # 数据表中文名称
    sjbms = params['sjbms']
    # 数据
    sql = params['sql']
    sql_list = sql.split(';')
    with sjapi.connection() as db:
        # 将用户输入的sql语句进行校验，看是否可以执行成功。
        try:
            for sql_ in sql_list:
                if sql_:
                    db.execute(sql_)
            db.rollback()
        except:
            db.rollback()
            error_msg = traceback.format_exc()
            return {'state': False, 'msg': 'sql语法错误：'+str(error_msg)}
    # 如果语法正确将数据插入到demo数据表中
    # 拆分数据  insert into A_TEST(A1,A2) values('aa','bb');
    for sql_ in sql_list:
        if sql_:
            sql_kv = split_sql(sql_)
            demo_sj_data_add_service({'demojbxxid': demojbxxid, 'sjbjc': sjbjc, 'sjbms': sjbms, 'data': sql_kv})
    return {'state': True, 'msg': '执行成功'}
def split_sql(sql):
    """
    # 将sql拆分成[{key,value}]形式
    """
    # 看用户输入的values是大写还是小写
    spliter = 'values'
    if sql.find('VALUES') != -1:
        spliter = 'VALUES'
    if sql:
        keys = sql.split(spliter)[0].split('(')[1].replace(')','').replace(' ','').split(',')
        values = eval(sql.split(spliter)[1])
        k_v = {}
        inx = 0
        for v in values:
            if v:
                k_v[keys[inx].upper()] = v
                inx += 1
        return k_v
def demo_sj_data_edit_service(params):
    """
    # 编辑Demo数据
    """
    # Demo数据上级ID
    sjid = params['sjid']
    # 显示顺序
    xssx = params['xssx']
    # 数据
    data = params['data']
    
    with sjapi.connection() as db:
        for zdm, zdz in data.items():
            sql_data = {'sjid': sjid, 'xssx': xssx, 'zdm': zdm, 'zdz': zdz}
            ModSql.kf_ywgl_005.execute_sql(db, "updaet_demo_sj_2", sql_data)
        return {'state': True, 'msg': '编辑成功'}

def demo_sj_data_del_service(params):
    """
    # 删除Demo数据
    """
    # Demo基本信息ID
    demojbxxid = params['demojbxxid']
    # 数据表简称
    sjbjc = params['sjbjc']
    # 数据 [[sjid, xssx], [sjid, xssx], ...]
    data = params['data']
    
    with sjapi.connection() as db:
        for sjid_xssx in data:
            sql_data = {'sjid': sjid_xssx[0], 'xssx': sjid_xssx[1]}
            ModSql.kf_ywgl_005.execute_sql(db, "del_demo_sj_2", sql_data)
        # 判断数据是否已被全部删除
        sql_data = {'sjbjc': sjbjc, 'demojbxxid': demojbxxid}
        rs = ModSql.kf_ywgl_005.execute_sql(db, "get_demo_sj", sql_data)
        # 如果已被全部删除，删除级别为1的记录
        if not rs:
            sql_data = {'id': demojbxxid,'sjbjc': sjbjc}
            ModSql.kf_ywgl_005.execute_sql(db, "delete_demo_sj", sql_data)
        return {'state': True, 'msg': '删除成功'}

def demo_execute_service(params):
    """
    # 执行单步测试
    """
    # 业务ID
    ywid = params['ywid']
    # Demo基本信息ID
    demojbxxid = params['demojbxxid']
    # 节点ID
    nodeid = params['nodeid']
    # 交易ID/子流程ID
    lcid = params['lcid']
    # 节点类型（'strat':开始节点，'end':结束节点，'jd':节点，'zlc':子流程）
    type = params['type']
    # 流程类型 lc/zlc
    lx = params['lx']
    # 输入要素字典
    srys = params['srys']
    
    with sjapi.connection() as db:
        # 将Demo信息插入到对应数据表中
        rs = ModSql.kf_ywgl_005.execute_sql_dict(db, "get_demo_sj_2", {'demojbxxids': [demojbxxid]})
        sjbjc_sjid = set((row['sjbjc'], row['sjid'], row['xssx']) for row in rs)
        demoxx_dic = {sj:[row for row in rs if (row['sjbjc'], row['sjid'], row['xssx']) == sj] for sj in sjbjc_sjid}
        for sjbjc_sjid, data in demoxx_dic.items():
            zdm_lst = sorted(set(item['zdm'] for item in data))
            sql_data = {'tbname': sjbjc_sjid[0], 'fields': ', '.join(zdm_lst), 'values': ':' + ', :'.join(zdm_lst)}
            sql = """
                insert into %(tbname)s (%(fields)s)
                values (%(values)s)
            """ % sql_data
            sql_data = {row['zdm']:row['zdz'] if row['zdz'] is not None else '' for row in data}
            db.execute(sql, sql_data)
        
        # 查询交易/子流程信息
        if lx == 'lc':
            rs_jy = ModSql.common.execute_sql(db, "get_jydy", {'id': lcid})
            ssjy = rs_jy[0].jym if rs_jy else None
            timeout = rs_jy[0].timeout if rs_jy else None
        else:
            rs_zlc = ModSql.common.execute_sql(db, "get_zlcdy", {'id': lcid})
            ssjy = lcid
            timeout = None
        
        # 节点类型为开始节点则取解包节点ID；若节点类型为结束节点则取打包节点ID
        if type == 'start_jy':
            nodeid = rs_jy[0].jbjdid if rs_jy else None
        elif type == 'end_jy':
            nodeid = rs_jy[0].dbjdid if rs_jy else None
        
        type = 'zlc' if type == 'zlc' else 'jd'
        
        # 查询业务编码
        rs = ModSql.common.execute_sql(db, "get_ywdy", {'ywid': ywid})
        ywbm = rs[0].ywbm if rs else None
        
        # 查询输出要素
        node_lx = '2' if type == 'zlc' else '1'
        scys = get_node_ys(db, nodeid, node_lx, '2')
        
        # 发送核心
        lzjy = (lx == 'lc')
        srys['SYS_CSSJ'] = timeout
        # 当执行节点是子流程时，传递子流程编码
        if type == 'zlc' and nodeid:
            zlcxx_lst = ModSql.common.execute_sql_dict(db, "get_zlcdy", {'id': nodeid})
            if zlcxx_lst:
                srys['SYS_ZLCBM'] = zlcxx_lst[0]['bm']
    
    # 将接收到的报文转二进制
    if srys.get('SYS_JSDDBW') and isinstance( srys.get('SYS_JSDDBW'), str ):
        # 十六进制转化为二进制
        try:
            srys['SYS_JSDDBW'] = bytes().fromhex(srys['SYS_JSDDBW'].replace(' ','')) if srys['SYS_JSDDBW'] != 'None' else ''
        except:
            logger.info(traceback.format_exc())
    # 日志中写入节点id
    srys['SYS_JYLOGLEVEL'] = json.dumps( [nodeid] )
    # 写日志
    logger.info('单步调试执行输入要素：')
    logger.info(srys)
    trans_dict = transaction_test(type, nodeid, ssjy=ssjy, jsddbw=None, lzjy=lzjy, ssyw=ywbm, pdic=srys)
    # 写日志
    logger.info('单步调试成功执行完反馈的结果：')
    logger.info(trans_dict)
    # 将返回值中二进制的数据转换为16进制
    if trans_dict:
        for k in list( trans_dict.keys() ):
            # 二进制转换
            if trans_dict.get(k) != None and isinstance( trans_dict[k], bytes ):
                trans_dict[k] = str(binascii.b2a_hex(trans_dict[k]))[2:-1].upper()
            # bytearray类型转换（先转换为二进制，再转16进制）
            elif trans_dict.get(k) != None and isinstance( trans_dict[k], bytearray ):
                trans_dict[k] = str(binascii.b2a_hex( bytes( trans_dict[k]) ) )[2:-1].upper()
        logger.info('单步调试成功执行完反馈的结果(转十六进制后)：')
        logger.info(trans_dict)
    # 判断是否成功过
    if trans_dict and trans_dict.get('SYS_RspCode') == '000000':
        return {
            'state': True, 
            'msg': '执行成功', 
            'trans_dict': trans_dict, 
            'scys': scys
        }
    elif trans_dict:
        return {
            'state': True, 
            'msg': '执行失败！响应内容：<br>%s' % ( trans_dict.get('SYS_RspInfo', '').replace('\n', '<br>') if trans_dict else '' ), 
            'trans_dict': trans_dict, 
            'scys': scys
        }
    else:
        return {
            'state': False, 
            'msg': '交易处理超时或核心服务异常!', 
            'trans_dict': {}, 
            'scys': scys
        }

def demo_log_service(rzkeys):
    """
    # 获取单步调试日志
    """
    with sjapi.connection() as db:
        # 由于核心修改xtrq方式，所以此处使用日期就使用当前日志
        rq = get_strfdate2()
        log_all = []
        for lsh in list( set( rzkeys ) ):
            log_lst_dic = readlog(rq, lsh)
            log_all.extend( change_log_msg( log_lst_dic ) )
        log = format_log(log_all)
    
    return {'state': True, 'msg': '', 'log': log}

def demo_save_step_service(params):
    """
    # 保存当前步骤
    """
    with sjapi.connection() as db:
        sql_data = {
            'id': params['bzid'], 
            'lx': '2' if params['lx'] == 'zlc' else '1', 
            'ssdyid': params['nodeid'], 
            'fhz': params['fhz'], 
            'mc': params['mc'], 
            'ms': params['ms'], 
            'sftg': params['sftg'], 
            'demoid': params['demoid'], 
            'rzlsh': params['log_lsh']
        }
        ModSql.kf_ywgl_005.execute_sql(db, "insert_jdcsalzxbz", sql_data)
        # 插入输入要素
        for ysdm, ysz in params['srys'].items():
            # 要素值超出最大长度时，不进行保存
            if ysz and len(ysz.encode('utf8')) > 4000:
                continue
            sql_data = {'id': get_uuid(), 'bzid': params['bzid'], 'lx': '1', 'ysdm': ysdm, 'ysz': ysz}
            ModSql.kf_ywgl_005.execute_sql(db, "insert_jdcsalys", sql_data)
        # 插入输出要素
        for ysdm, ysz in params['scys'].items():
            # 要素值超出最大长度时，不进行保存
            if ysz and len(ysz.encode('utf8')) > 4000:
                continue
            sql_data = {'id': get_uuid(), 'bzid': params['bzid'], 'lx': '2', 'ysdm': ysdm, 'ysz': ysz}
            ModSql.kf_ywgl_005.execute_sql(db, "insert_jdcsalys", sql_data)
        # 删除节点测试案例执行步骤表、节点测试案例要素表数据
        if params['bzid_old']:
            # 检查节点测试案例执行步骤是否被引用
            rs = ModSql.kf_ywgl_005.execute_sql(db, "check_jdcsalzxbz", {'bzid': '%%%s%%'%params['bzid_old']})
            if not rs:
                ModSql.kf_ywgl_005.execute_sql(db, "del_jdcsalzxbz", {'id': params['bzid_old']})
                ModSql.kf_ywgl_005.execute_sql(db, "del_jdcsalys", {'bzid': params['bzid_old']})
        return {'state': True, 'msg': ''}

def demo_del_step_service(bzids_old):
    """
    # 删除保存的步骤
    """
    with sjapi.connection() as db:
        # 删除节点测试案例执行步骤表、节点测试案例要素表数据
        for bzid_old in bzids_old:
            # 检查节点测试案例执行步骤是否被引用
            rs = ModSql.kf_ywgl_005.execute_sql(db, "check_jdcsalzxbz", {'bzid': '%%%s%%'%bzid_old})
            if not rs:
                ModSql.kf_ywgl_005.execute_sql(db, "del_jdcsalzxbz", {'id': bzid_old})
                ModSql.kf_ywgl_005.execute_sql(db, "del_jdcsalys", {'bzid': bzid_old})
        
        return {'state': True, 'msg': ''}

def dbtsjl_service(lcid, lx, bz_bjids, bzids):
    """
    # 查看单步调试记录
    """
    with sjapi.connection() as db:
        # 查询执行步骤
        rs_jdcsalzxbz = ModSql.kf_ywgl_005.execute_sql_dict(db, "get_jdcsalzxbz", {'id_lst': bzids})
        # 查询打解包节点
        rs_jyjbjd = ModSql.kf_ywgl_005.execute_sql_dict(db, "get_jyjbjd", {'id': lcid}) if lx == 'lc' else []
        # 对开始、结束节点名称进行修改
        id_lst = []
        if rs_jyjbjd:
            id_lst.append(rs_jyjbjd[0]['dbjdid'])
            id_lst.append(rs_jyjbjd[0]['jbjdid'])
        
        zlc_jd = {'after_start': False, 'before_end': False}
        rs_jdmc = ModSql.common.execute_sql_dict(db, "get_jdmc", {'id_lst': id_lst}) if id_lst else []
        for row in rs_jdcsalzxbz:
            if row['id'] in [row['id'] for row in rs_jdmc if row['jdlx'] == '9']:
                row['mc'] = '%s[%s]' % ('交易开始', row['mc'])
                row['type'] = 'start'
            elif row['id'] in [row['id'] for row in rs_jdmc if row['jdlx'] == '8']:
                row['mc'] = '%s[%s]' % ('交易结束', row['mc'])
                row['type'] = 'end'
            # 查询前置节点
            rs = ModSql.kf_ywgl_005.execute_sql_dict(db, "get_qzjd", {'jdid': row['id'], 'lcid': lcid})
            if '3' in [row['jdlx'] for row in rs]:
                zlc_jd['after_start'] = True
            # 查询后置节点
            rs = ModSql.kf_ywgl_005.execute_sql_dict(db, "get_hzjd", {'jdid': row['id'], 'lcid': lcid, 'fhz': row['fhz']})
            if '4' in [row['jdlx'] for row in rs]:
                zlc_jd['before_end'] = True
        
        # 按执行步骤排序
        rs_jdcsalzxbz.sort(key=lambda x:bzids.index(x['bzid']))
        # 开始结束节点数
        start_end_len = len([1 for row in rs_jdcsalzxbz if row.get('type') in ('start', 'end')])
        data = {'zxbz': rs_jdcsalzxbz, 'save_as_lc': start_end_len == 2 or (zlc_jd['after_start'] and zlc_jd['before_end'])}
    
    return data

def del_dbts_service(bzids, demoids):
    """
    # 删除单步调试产生的数据
    """
    with sjapi.connection() as db:
        if bzids:
            # 删除节点测试案例要素
            ModSql.kf_ywgl_005.execute_sql_dict(db, "del_jdcsalys_unuse", {'bzids': bzids})
            # 删除节点测试案例执行步骤
            ModSql.kf_ywgl_005.execute_sql_dict(db, "del_jdcsalzxbz_unuse", {'bzids': bzids})
        # 查询Demo数据（级别2）
        rs_demo_2 = ModSql.kf_ywgl_005.execute_sql_dict(db, "get_demo_sj_2", {'demojbxxids': demoids}) if demoids else []
        
        data_dic = {}
        for row in rs_demo_2:
            if row['iskey'] == '1':
                data_dic.setdefault((row['sjbjc'], row['sjid'], row['xssx']), {})[row['zdm']] = row['zdz'] if row['zdz'] else None
        for k, v in data_dic.items():
            where = ' and '.join('%s = :%s' % (zdm, zdm) for zdm in v)
            sql = """
                delete from %(sjbjc)s
                where (%(where)s)
            """ % {'sjbjc': k[0], 'where': where}
            db.execute(sql, v)
        
        return {'state': True, 'msg': '删除成功'}

def save_jdcsal_service(params):
    """
    # 保存为节点测试案例
    """
    with sjapi.connection() as db:
        csal_id = get_uuid()
        sql_data = {
            'id': csal_id,
            'lb': params['lb'],
            'mc': params['mc'],
            'ms': params['ms'],
            'jdcsalzxbzlb': params['bzid'],
            'ssywid': params['ywid'],
            'sslb': '3',
            'ssid': params['nodeid'],
            'demoid': params['demoid'],
            'rzlsh': params['rzlsh'],
            'zjzxsj': get_strftime(),
            'zjzxr': get_sess_hydm(),
            'ssjy_id': params['lcid']
        }
        ModSql.kf_ywgl_005.execute_sql_dict(db, "insert_csaldy", sql_data)
        # 登记行员日常运维流水
        nr = '流程编辑-保存节点测试案例:节点id[%s], 测试案例id[%s]，测试案例名称[%s]' % ( sql_data['ssid'], sql_data['id'], sql_data['mc'] )
        # 更新节点测试案例执行步骤
        sql_data = {'jdcsaldyid': csal_id, 'bzid': params['bzid']}
        ModSql.kf_ywgl_005.execute_sql_dict(db, "update_jdcsalzxbz_jdcsaldyid", sql_data)
        # 登记行员日常运维流水
        ins_czrz(db, nr, gnmc = '流程编辑_新增节点测试案例' )
        return {'state': True, 'msg': '保存成功'}

def save_csal_service(params):
    """
    # 保存为测试案例
    """
    bzids = ','.join(params['bzids'])
    demoids = ','.join(params['demoids'])
    with sjapi.connection() as db:
        csal_id = get_uuid()
        lb = '1' if params['lx'] == 'lc' else '2'
        sql_data = {
            'id': csal_id,
            'lb': lb,
            'mc': params['mc'],
            'ms': params['ms'],
            'jdcsalzxbzlb': bzids,
            'ssywid': params['ywid'],
            'sslb': lb,
            'ssid': params['lcid'],
            'demoid': demoids,
            'rzlsh': '',
            'zjzxsj': get_strftime(),
            'zjzxr': get_sess_hydm(),
            'ssjy_id': params['lcid']
        }
        ModSql.kf_ywgl_005.execute_sql_dict(db, "insert_csaldy", sql_data)
        # 登记行员日常运维流水
        nr = '流程编辑-保存交易测试案例:流程id[%s],流程类型[%s],测试案例id[%s]，测试案例名称[%s]' % ( 
        sql_data['ssid'], params['lx'], sql_data['id'], sql_data['mc'] )
        # 更新节点测试案例执行步骤
        for bzid in params['bzids']:
            sql_data = {'csaldyid': csal_id, 'bzid': bzid}
            ModSql.kf_ywgl_005.execute_sql_dict(db, "update_jdcsalzxbz_csaldyid", sql_data)
        # 登记行员日常运维流水
        ins_czrz(db, nr, gnmc = '流程编辑_新增交易测试案例' )
        return {'state': True, 'msg': '保存成功'}

def get_node_fhz_service(nodeid, type):
    """
    # 获取节点返回值
    """
    with sjapi.connection() as db:
        node_lx = '1' if type == 'jd' else '2'
        fhz = get_node_ys(db, nodeid, node_lx, '3')
        fhz = [k['bm'] for k in fhz]
        return {'state': True, 'msg': '', 'fhz': fhz}

def get_czpz_service( czpzlx ):
    """
    # 查询冲正配置id列表
    """
    czpz_lst = []
    with connection() as db:
        # 根据冲正配置类型
        if czpzlx == 'jd':
            czpz_lst = ModSql.kf_ywgl_005.execute_sql_dict(db, "get_czpz_lst_jd")
        elif czpzlx == 'zlc':
            czpz_lst = ModSql.kf_ywgl_005.execute_sql_dict(db, "get_czpz_lst_zlc")
    # 处理查询结果集
    for obj in czpz_lst:
        obj['czpzid'] = obj['id']
        obj['text'] = obj['mc']
    
    czpz_lst.insert( 0, { 'czpzid': '', 'text': '请选择' } )
    
    return { 'state': True, 'msg': '查询成功', 'czpz_lst': czpz_lst }

def czpz_sub_service( data_dic ):
    """
    # 冲正配置提交
    """
    with connection() as db:
        # 保存冲正配置
        upd_dic = { 'bzid': data_dic['bzid'], 'czpzid': data_dic['czpzid'] }
        ModSql.kf_ywgl_005.execute_sql_dict( db, "upd_czpz", upd_dic )
        # 更新唯一码
        lx = 'zlc' if data_dic['lx'] == 'zlc' else 'jy'
        update_wym(db, lx, data_dic['jy2zlcid'])
    
    return { 'state': True, 'msg': '保存成功' }
    