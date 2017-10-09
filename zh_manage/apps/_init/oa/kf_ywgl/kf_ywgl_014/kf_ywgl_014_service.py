# -*- coding: utf-8 -*-
# Action: 流程-自动化测试编码
# Author: liuhh
# AddTime: 2015-2-15
# Standard: 注释仅能以“#”开头,sql可以是“--”；注释不能同代码在同一行

import pickle,copy,json,cx_Oracle,traceback
from sjzhtspj import ModSql,get_sess_hydm,logger
from sjzhtspj.common import update_wym,get_strftime, get_uuid,binary_to_hex,db_hex_to_binary,to_binary
from sjzhtspj.const import CSALLB_MC_DIC
from sjzhtspj.esb import transaction_test


def get_zdcslb_service(csalids, csal):
    """
    # 获取流程-测试案例定义列表的信息
    """
    with sjapi.connection() as db:
        if csal == '' or csal == None:
            csalids_lb = csalids.split(',')
            # 根据测试案例定义表所属ID查询测试案例的信息列表
            zdcslb = ModSql.kf_ywgl_014.execute_sql_dict(db, "get_zdcs_lb", {"csalids":csalids_lb})
            #判断结果
            if not zdcslb:
                return {"rows":[]}
            else:
                for item in zdcslb:
                    key = item["lb"]
                    item["lbvalue"] =  CSALLB_MC_DIC[key]
                return {'rows':zdcslb}
        else:
            # 根据所属业务id和类型来获取测试案例。
            csal = csal.split(',')
            zdcslb = ModSql.kf_ywgl_014.execute_sql_dict(db, "get_csal_byywid", {"ywid":csal})
            for al in zdcslb:
                if al['lb'] == '1':
                    al['lbvalue'] = '交易'
                elif al['lb'] == '2':
                    al['lbvalue'] = '子流程'
                elif al['lb'] == '3':
                    al['lbvalue'] = '节点'
            return {'rows':zdcslb}

def cs_start_service(data,pc):
    """
    # 点击开始测试的时候,向临时表中的增加信息
    """
    last_jd_scys = {}
    # 返回给前台的执行结果
    zxjg_return = {'zxjg':'', 'jgsm':'','csal_id':'','test_data':[]}
    csal_data = copy.deepcopy(data)
    with sjapi.connection() as db:
        row = json.loads(data)
        # 开始测试的测试案例的类型
        lx = row['lb']
        # 测试案例的定义的ID
        id = row['id']
        zxjg_return['csal_id'] = id
        # 测试案例中的所属ID,根据“所属类别”，分别对应交易定义表ID、子流程表ID和节点定义表ID
        ssid = row['ssid']
        # 测试案例所属业务id
        ssywid = row['ssywid']
        demoxx_dic = {}
        #类别
        #1:交易测试案例
        #2:子流程测试案例
        #3:节点测试案例
        #4:通讯子流程测试案例
        if lx=='1' or lx== '2' or lx=='4':
            # 获取执行案例的执行步骤
            csalzxbzidlb = ModSql.kf_ywgl_014.execute_sql_dict(db, "get_csalzxbzidlb", {"id":id})[0]
            # 取得执行案例中的执行步骤的ids
            zxbzids = csalzxbzidlb["jdcsalzxbzlb"].split(',')
            # 如果类型为子流程或交易的时候
            # 获取节点测试案例执行步骤的列表
            csalzxbz =  ModSql.kf_ywgl_014.execute_sql_dict(db, "get_csalzxbz", {"jdcsalzxbzlb":zxbzids}) if zxbzids else []
            if len(csalzxbz) < 1:
                return {'state':False, 'msg':'测试案例异常，未获取到测试案例执行步骤。'}
            # 清空执行步骤的日志流水号
            if csalzxbz:
                ModSql.kf_ywgl_014.execute_sql_dict(db, "update_csalzxbz", {"jdcsalzxbzlb":zxbzids})
            # 获取节点ID和布局ID的对应信息
            jdbuxx = []
            if lx == '1':
                # 交易
                jdbuxx =  ModSql.kf_ywgl_014.execute_sql_dict(db, "get_jy_jdbudyxx", {"ssjyid":ssid})
            else:
                # 子流程
                jdbuxx =  ModSql.kf_ywgl_014.execute_sql_dict(db, "get_zlc_jdbudyxx", {"sszlcid":ssid})
            #  bj_dic = {节点ID:布局ID,节点ID2:布局ID2,…}
            sortlst = []
            # 按照执行步骤进行排序
            if csalzxbz:
                for i in zxbzids:
                    jdxxlb_lst = [row for row in csalzxbz if row["id"] == i]
                    if jdxxlb_lst:
                        sortlst.append( jdxxlb_lst[0] )
            csalzxbz = copy.deepcopy(sortlst)
            bj_dic = {}
            
            for row in jdbuxx:
                bj_dic[row["jddyid"]] = row["id"]
            # bzxx_lst = [[步骤ID,类型,所属定义ID,返回值,是否跳过]]
            bzxx_lst = []
            # 如果是子流程的话，测试案例的执行步骤里是没有开始和结束节点的。
            # 这个时候我们要手动的将子流程的流程布局的zlcstart和zlcend放到测试案例执行步骤里
            if lx == '2':
                bzxx_lst.append([bj_dic.get('zlcstart'), '1', 'zlcstart', '0', '0'])
            for row in csalzxbz:
                ssdyid = row["ssdyid"]
                fhz = row["fhz"]
                # 查询出所属定义id的对应的节点是否是开始，结束节点。如果是的话下面data中的第3个元素就是jystart或者jyend
                jdid = ModSql.kf_ywgl_014.execute_sql_dict(db, "get_jd_lx", {"jdid":row["ssdyid"]})
                if jdid:
                    jdlx = jdid[0]['jdlx']
                    if jdlx == '9':
                        ssdyid = 'jystart'
                        # 交易的开始节点，出来的返回值默认都是0
                        fhz = '0'
                    elif jdlx == '8':
                        ssdyid = 'jyend'
                # 获取测试案例执行步骤的期望输出值
                data = [row["id"], row["lx"], ssdyid, fhz, row["sftg"]]
                bzxx_lst.append(data)
            # 如果是子流程的话，测试案例的执行步骤里是没有开始和结束节点的。
            # 这个时候我们要手动的将子流程的流程布局的zlcstart和zlcend放到测试案例执行步骤里
            if lx == '2':
                bzxx_lst.append([bj_dic.get('zlcend'), '1', 'zlcend', '0', '0'])
            # 循环开始的位置
            inx = 1
            # 循环的结束位置
            endx = len(bzxx_lst)
            # 循环查看执行的步骤的有效性
            # 判断除去开始节点和结束节点的流程走向是否正确
            # 如果是通讯子流程的话无需进行执行步骤的校验
            if lx != '4':
                for i in range(inx,endx):
                    sslb = lx
                    sqlparam = {"fhz":bzxx_lst[i-1][3], "qzjdlcbjid":bj_dic.get(bzxx_lst[i-1][2]) ,"hzjdlcbjid":bj_dic.get(bzxx_lst[i][2]), "sslb":sslb ,"ssid": ssid}
                    redata =  ModSql.kf_ywgl_014.execute_sql_dict(db, "validate_jybzyxx", sqlparam)
                    # 没有查询到数据的时候,说明步骤的有效性不对
                    if not redata:
                        sql_zxycjg = {"id":get_uuid(),"pc":pc,"csal_id":id,"lx":"3","zxjg":"3","jgsm":"测试案例异常，请确定测试案例执行顺序与流程图是否一致。" }
                        # 若未查询到数据,向临时表中插入执行结果为异常的数据,且本测试案例执行完毕
                        result =  ModSql.kf_ywgl_014.execute_sql_dict(db, "add_zdhcslsb_zxycjg", sql_zxycjg)
                        zxjg_return['zxjg'] = '失败'
                        zxjg_return['jgsm'] = '测试案例异常，请确定测试案例执行顺序与流程图是否一致。'
                        return {'state':True,'msg':'测试结束','zxjg':zxjg_return}
            elif lx == '4':
                # 如果是通讯测试案例，需要判断打解包节点是否发生了变化。
                # 获取通讯测试案例的打解包节点 bj_dic
                change = False
                for bz in csalzxbz:
                    # 如果步骤的id在流程布局里没有，说明步骤发生变化了。
                    if not bj_dic.get(bz.get('ssdyid')):
                        change = True
                if change:
                    sql_zxycjg = {"id":get_uuid(),"pc":pc,"csal_id":id,"lx":"3","zxjg":"3","jgsm":"测试案例异常，打解包发生变化，请重新保存测试案例。" }
                    # 若未查询到数据,向临时表中插入执行结果为异常的数据,且本测试案例执行完毕
                    result =  ModSql.kf_ywgl_014.execute_sql_dict(db, "add_zdhcslsb_zxycjg", sql_zxycjg)
                    zxjg_return['zxjg'] = '失败'
                    zxjg_return['jgsm'] = '测试案例异常，打解包发生变化，请重新保存测试案例。'
                    return {'state':True,'msg':'测试结束','zxjg':zxjg_return}
            # 如果测试案例的类型是子流程的话开始和结束节点是没有用处的，所以将其删除
            if lx == '2':
                bzxx_lst = bzxx_lst[1:-1]
            # 从demo数据表中,获取数据表的简称的信息
            if csalzxbzidlb["demoid"] != '' and csalzxbzidlb["demoid"] != None:
                demoids = csalzxbzidlb["demoid"].split(',')
                # 对demoid去重
                demoids = list(set(demoids))
                demoids_copy = copy.deepcopy(demoids)
                inx = 0
                for i in demoids_copy:
                    if i == '' or i == None or i == 'None':
                        del demoids[inx]
                    inx+=1
                demo_sjbjc = ModSql.kf_ywgl_014.execute_sql_dict(db, "get_demo_sjb", {"demoids":demoids}) if demoids else []
                # 获取对应上级ID数组
                sjid_list = {row['id']:row['sjbjc'] for row in demo_sjbjc}
                # 获取表的主键字段,循环sjid_lst  [{'sjbmc': 'LIUHH', 'zdmc': 'abc'},{'sjbmc': 'LIUHH', 'zdmc': 'abc'}]
                # 组织数据结构:{上级ID:[数据表简称,[字段名:字段值,…]]}
                for key in sjid_list.keys():
                    # demo数据表的字段名字段值
                    k_v = {}
                    demo_mz = ModSql.kf_ywgl_005.execute_sql_dict(db, "get_demo_sj", {"sjbjc": sjid_list[key], 'demojbxxid': demoids[0]})
                    zd = []
                    for d in demo_mz:
                        if d['iskey'] == '1':
                            zd.append(d['zdm'])
                        k_v[d.get('zdm')] = d.get('zdz')
                    demoxx_dic[key] = [demo_mz[0]['sjbjc'],zd,k_v]
                logger.info('========插入demo数据=========')
                # 遍历循环动态的插入到对应数据表中
                for row in demoxx_dic.keys():
                    
                    dic_zdmzdz = demoxx_dic[row][2]
                    values = "''"
                    if ",".join((map(str,dic_zdmzdz.values()))) != '':
                        values ="'" + "','".join((map(str,dic_zdmzdz.values()))) + "'"
                    values = values.replace("'None'","''")
                    sql = """
                        insert into %(db_name)s (%(keys)s)
                        values (%(values)s)
                    """ % {'db_name':demoxx_dic[row][0].replace('-',''), 'keys':",".join(dic_zdmzdz.keys()), 'values':values}
                    db.execute(sql)
                    db.commit()
            zxjg_return['test_data'] = demoxx_dic
            # 循环的游标
            bz_index = 0
            # 循环执行步骤列表中每一个步骤,获取该步骤的信息及输入要素
            for bz in csalzxbz:
                #定义存储返回值列表:
                fhz_lst = []
                #定义存储日志key列表:
                rzkey_lst = []
                # 输入要素
                srys_dic = {}
                # 输出要素
                scys_dic = {}
                # 执行结果
                zxjg = "1"
                # 节点类型
                jdlx = ""
                # 结果说明
                jgsm = "测试成功"
                bzid = bz['id']
                # 核心返回的内容
                hx_re = {}
                bzys = ModSql.kf_ywgl_014.execute_sql_dict(db, "get_bzysxx", {"jdcsalzxbz":bzid}) if bzid else []
                
                for bzy in bzys:
                    if bzy['lx'] == '1':
                        srys_dic[bzy['ysdm']] = bzy['ysz']
                    elif bzy['lx'] == '2':
                        scys_dic[bzy['ysdm']] = bzy['ysz']
                # 如果跳过查询此步骤的节点名称,则向日志数据库中插入信息
                if bz['sftg'] == '1':
                    # 节点或者子流程名称
                    mc = ''
                    # 查询节点名称
                    if bz['lx'] == 1 or bz['lx'] == '1':
                        mc = ModSql.kf_ywgl_014.execute_sql_dict(db, "get_jdmc", {"id":bz['ssdyid']})[0]['mc']
                    else:
                        mc = ModSql.kf_ywgl_014.execute_sql_dict(db, "get_zlcmc", {"id":bz['ssdyid']})[0]['mc']
                    rz1 = '节点['+mc+']为跳过<br>'
                    # 步骤名称，步骤描述
                    rz2 = '[' + bz['mc'] if bz['mc'] else '' + ']  ' + '[' + bz['ms'] if bz['ms'] else '' + ']'
                    # 返回值
                    rz3 = '预置输出要素：'+str(scys_dic)+'，返回值：'+ bz['fhz'] if bz['fhz'] else ''
                    # 将预置的输出要素信息插入到临时表中
                    for k,v in scys_dic.items():
                        ModSql.kf_ywgl_014.execute_sql(db, "add_zdhcslsb_yzscysxx", {"id":get_uuid(),"pc":pc,"csal_id":id,"lx":"1","ysdm":k,"ysz":str(v),'bzid':bzid})
                    # 组织信息放到返回值列表、日志key列表中 bzxx_lst = [[步骤ID,类型,所属定义ID,返回值,是否跳过]]
                    fhz_lst.append((bzxx_lst[bz_index][1],bzxx_lst[bz_index][2],bzxx_lst[bz_index][3]))
                    rzkey_lst.extend([rz1,rz2,rz3])
                # 若此步骤不为跳过,则根据步骤类型,调用不同核心方法进行处理
                elif bz['sftg'] == '0':
                    trans_dict = copy.deepcopy(srys_dic)
                    trans_dict['JDDYID'] = bzxx_lst[bz_index][2]
                    # 核心返回的信息
                    hx_re = {}
                    # ssjy（所属交易代码，lx为jd或zlc时必填,jd时是bm字段的值，zlc时暂定业务下随便一交易的bm字段的值，该地方还在等核心信息，todo）
                    ssjy = ''
                    hxlx = ''
                    # 是否来自交易的单步调试( 子流程时为False，并且把ssyw传给核心 )
                    lzjy = True
                    # 所属业务uuid
                    ssyw = ''
                    nodeid = bz['ssdyid']
                    # 超时时间
                    timeout = None
                    if bz['lx'] == '1' or bz['lx'] == 1:
                        # 节点 
                        hxlx = 'jd'
                    elif bz['lx'] == '2' or bz['lx'] == 2:
                        # 子流程
                        hxlx = 'zlc'
                        
                    if lx == '1':
                        # 如果测试案例的类型是交易
                        rs = ModSql.common.execute_sql_dict(db, "get_jydy", {"id":ssid})
                        ssjy = rs[0]['jym'] if rs else None
                        timeout = rs[0]['timeout'] if rs else None
                        if bz['lx'] == '1' or bz['lx'] == 1:
                            jdlx = ModSql.kf_ywgl_014.execute_sql_dict(db, "get_jdmc", {"id":nodeid})[0]['jdlx']
                        elif bz['lx'] == '2' or bz['lx'] == 2:
                            # 当执行节点是子流程时，传递子流程编码
                            zlcxx_lst = ModSql.common.execute_sql_dict(db, "get_zlcdy", {'id': nodeid})
                            if zlcxx_lst:
                                trans_dict['SYS_ZLCBM'] = zlcxx_lst[0]['bm']
                    elif lx == '2' or lx == '4':
                        # 如果是子流程或者是通讯子流程的话参数还没有确定: 传子流程uuid，并将
                        ssjy = ssid
                        # 是否来自交易的单步调试( 子流程时为False，并且把ssyw传给核心 )
                        lzjy = False
                        # 所属业务
                        ssyw = ssywid
                    if lx == '4':
                        nodeid = ssjy
                        # 当执行节点是子流程时，传递子流程编码
                        zlcxx_lst = ModSql.common.execute_sql_dict(db, "get_zlcdy", {'id': ssjy})
                        if zlcxx_lst:
                            trans_dict['SYS_ZLCBM'] = zlcxx_lst[0]['bm']
                            ssjy = zlcxx_lst[0]['bm']
                    if lx == '2':
                        if bz['lx'] == '2':
                            # 当执行节点是子流程时，传递子流程编码
                            zlcxx_lst = ModSql.common.execute_sql_dict(db, "get_zlcdy", {'id': nodeid})
                            if zlcxx_lst:
                                trans_dict['SYS_ZLCBM'] = zlcxx_lst[0]['bm']
                                ssjy = zlcxx_lst[0]['bm']
                        elif bz['lx'] == '1':
                            # 当执行节点是子流程时，传递子流程编码
                            zlcxx_lst = ModSql.common.execute_sql_dict(db, "get_zlcdy", {'id': ssjy})
                            if zlcxx_lst:
                                trans_dict['SYS_ZLCBM'] = zlcxx_lst[0]['bm']
                    # 查询业务编码
                    rs = ModSql.common.execute_sql(db, "get_ywdy", {'ywid': ssywid})
                    ywbm = rs[0].ywbm if rs else None
                    # 节点、子流程、交易码解出测试发起函数
                    # lx,节点或者子流程的id，节点或者子流程的交易代码，空，其他参数字典
                    trans_dict['SYS_CSSJ'] = timeout
                    trans_dict = dict(trans_dict, **last_jd_scys)
                    # 将数据库中的十六进制数据转换为二进制发送到核心
                    to_binary(trans_dict)
                    # 组织发送到核心的数据
                    hx_re = transaction_test( hxlx,nodeid,ssjy = ssjy, jsddbw = None, lzjy = lzjy, ssyw = ywbm, pdic = trans_dict )
                    # 核心返回的内容
                    logger.info('核心返回的内容')
                    logger.info(hx_re)
                    if hx_re == None:
                        # 删除demo中的数据
                        del_test_data_service(row)
                        return {'state':False,'msg':'通讯超时'} 
                    # 如果没有执行结果，就默认为空
                    if not hx_re.get('SYS_JYJDZXJG'):
                        hx_re['SYS_JYJDZXJG'] = ''
                    # 将核心返回的内容转为十六进制
                    binary_to_hex(hx_re)
                    # 无用的字段删除,方便循环插入输出要素
                    scys_re = copy.deepcopy(hx_re)
                    del scys_re['JDDYID']
                    last_jd_scys = copy.deepcopy(scys_re)
                    # 删除['SYS_CLBZ', 'SYS_DZXJDDM', 'SYS_ISDEV', 'SYS_ZLCDEV', 'SYS_JYLX', 'msgxh']这些key
                    del_key = ['SYS_CLBZ', 'SYS_DZXJDDM', 'SYS_ISDEV', 'SYS_ZLCDEV', 'SYS_JYLX', 'msgxh','SYS_XTLSH']
                    for d in del_key:
                        if last_jd_scys.get(d):
                            del last_jd_scys[d]
                    # 将核心反馈的输出要素信息插入到临时表中 (%(id)s, %(pc)s, %(csal_id)s, %(lx)s,%(ysdm)s,%(ysz)s)
                    for k,v in scys_re.items():
                        ModSql.kf_ywgl_014.execute_sql(db,"add_zdhcslsb_yzscysxx",{'id':get_uuid(),'pc':pc,'csal_id':id,'lx':'1','ysdm':k,'ysz':str(v),'bzid':bzid})
                    # 组织信息放到返回值列表、日志key列表中
                    fhz_lst.append((bzxx_lst[bz_index][1],bzxx_lst[bz_index][2],hx_re['SYS_JYJDZXJG']))
                    rzkey_lst.append(hx_re['SYS_XTLSH'])
                    # 节点名称
                    jdmc = ''
                    # 获取执行步骤的节点名称
                    if bz['lx'] == '1':
                        # 查询节点名称
                        jdmc = ModSql.kf_ywgl_014.execute_sql_dict(db, "get_jd_lx", {"jdid":bz['ssdyid']})
                        if jdmc:
                            jdmc = jdmc[0]['jdmc']
                    else:
                        jdmc = ModSql.kf_ywgl_014.execute_sql_dict(db, "get_zlcmc", {"id":bz['ssdyid']})
                        if jdmc:
                            jdmc = jdmc[0]['mc']
                    # 若测试案例类别为通讯子流程,则比对核心返回的返回值与此步骤的返回值是否一致
                    if lx == '4':
                        # 核心返回的返回值与此步骤的返回值如果不一样不一致,则将执行结果置为失败,并不再执行后序步骤,跳出执行步骤的循环
                        if '000000' != hx_re['SYS_RspCode']:
                            zxjg = "0" 
                            zxjg_return['zxjg'] = '失败'
                            zxjg_return['jgsm'] = '【' + jdmc + '】：' + hx_re['SYS_RspInfo']
                            jgsm = '【' + jdmc + '】：' + hx_re['SYS_RspInfo']
                    else :
                        # 判断返回值是否一样
                        if jdlx != '8' and jdlx != '9' and bzxx_lst[bz_index][3] != hx_re['SYS_JYJDZXJG']:
                            zxjg = "0" 
                            jgsm = '【' + jdmc + '】：' + "【SYS_JYJDZXJG】与期望值不一致"
                        # 判断响应内容是否一样
                        if scys_dic['SYS_RspCode'] != hx_re['SYS_RspCode']:
                            zxjg = "0" 
                            if jgsm == '测试成功':
                                jgsm = '【' + jdmc + '】：' + " 【SYS_RspCode】与期望值不一致"
                            else:
                                jgsm = jgsm + " 【SYS_RspCode】与期望值不一致"
                            # 将测试成功这几个字替换为空
                            jgsm = jgsm.replace('测试成功','')
                rzkey_lst_blob = str(rzkey_lst)
                # 将执行日志信息更新到临时表中 (%(id)s, %(pc)s, %(csal_id)s, %(lx)s,%(ysdm)s,%(ysz)s
                sql_data = {'id':get_uuid(),'pc':pc,'csal_id':id,'lx':'2','lb':str(fhz_lst),'rzlb':rzkey_lst_blob,'bzid':bzid,'zxjg':zxjg}
                ModSql.kf_ywgl_014.execute_sql(db,"add_zdhcslsb_rzlb",sql_data)
                # 将执行日志信息更新到临时表中
                sql_data = {'id':get_uuid(),'pc':pc,'csal_id':id,'lx':'3','zxjg':zxjg,'jgsm':jgsm,'rzlb':rzkey_lst_blob,'bzid':bzid}
                ModSql.kf_ywgl_014.execute_sql(db,"add_zdhcslsb_zxjg",sql_data)
                if hx_re:
                    # 更新日志流水号
                    ModSql.kf_ywgl_014.execute_sql(db,"update_rzlsh",{'rzlsh':hx_re['SYS_XTLSH'], 'jdcsalzxbzid':bzid})
                
                zxjg_return['zxjg'] = '成功' if zxjg == '1' else '失败'
                zxjg_return['jgsm'] = jgsm 
                bz_index+=1
                # 如果执行失败的话就直接结束改测试案例的执行。
                if zxjg != '1':
                    break
        # 如果是3:节点测试案例
        elif lx == '3':
            # 获取执行案例的执行步骤
            csalzxbzidlb = ModSql.kf_ywgl_014.execute_sql_dict(db, "get_csalxx", {"csaldyid":id})
            if len(csalzxbzidlb) < 1:
                return {'state':False,'msg':'节点未获取到测试案例执行步骤。','zxjg':'0'}
            csalzxbzidlb = csalzxbzidlb[0]
            # 获取所属业务id
            ywid = ModSql.kf_ywgl_014.execute_sql_dict(db, "get_ssywid", {"csaldyid":id})[0]['ssywid']
            # 查询业务编码
            rs = ModSql.common.execute_sql(db, "get_ywdy", {'ywid': ywid})
            ywbm = rs[0].ywbm if rs else None
            ysxx = ModSql.kf_ywgl_014.execute_sql_dict(db, "getysxx", {"jdcsalzxbzlb":[csalzxbzidlb['id']],'lx':'1'})
            # 输出要素
            ysxx_l = ModSql.kf_ywgl_014.execute_sql_dict(db, "getysxx", {"jdcsalzxbzlb":[csalzxbzidlb['id']],'lx':'2'})
            if csalzxbzidlb["demoid"] != None and csalzxbzidlb["demoid"] != '':
                # 从demo数据表中,获取数据表的简称的信息
                demoids = csalzxbzidlb["demoid"].split(',')
                demo_sjbjc = ModSql.kf_ywgl_014.execute_sql_dict(db, "get_demo_sjb", {"demoids":demoids}) if demoids else []
                # 获取对应上级ID数组
                sjid_list = {row['id']:row['sjbjc'] for row in demo_sjbjc}
                # 获取表的主键字段,循环sjid_lst  [{'sjbmc': 'LIUHH', 'zdmc': 'abc'},{'sjbmc': 'LIUHH', 'zdmc': 'abc'}]
                # 组织数据结构:{上级ID:[数据表简称,[字段名:字段值,…]]}
                demoxx_dic = {}
                for key in sjid_list.keys():
                    # demo数据表的字段名字段值
                    k_v = {}
                    demo_mz = ModSql.kf_ywgl_005.execute_sql_dict(db, "get_demo_sj", {"sjbjc": sjid_list[key], 'demojbxxid': demoids[0]})
                    zd = []
                    for d in demo_mz:
                        if d['iskey'] == '1':
                            zd.append(d['zdm'])
                        k_v[d.get('zdm')] = d.get('zdz')
                    demoxx_dic[key] = [demo_mz[0]['sjbjc'],zd,k_v]
                # 组织数据
                """demoxx_dic = {
                    上级ID:[数据表简称,[主键字段名称1,主键字段名称2…],{字段名:字段值,…}],
                    上级ID:[数据表简称,[主键字段名称1,主键字段名称2…],{字段名:字段值,…}],
                    …
                }"""
                # 遍历循环动态的插入到对应数据表中
                for row in demoxx_dic.keys():
                    dic_zdmzdz = demoxx_dic[row][2]
                    values = "''"                   
                    if ",".join((map(str,dic_zdmzdz.values()))) != '':
                        values ="'" + "','".join((map(str,dic_zdmzdz.values()))) + "'"
                    sql = """
                        insert into %(db_name)s (%(keys)s)
                        values (%(values)s)
                    """ % {'db_name':demoxx_dic[row][0], 'keys':",".join(dic_zdmzdz.keys()), 'values':values}
                    db.execute(sql)
                    db.commit()
            # 组织向核心发送的字典
            trans_dict = {
                'JDDYID':csalzxbzidlb["ssdyid"],
                'DEMOID':csalzxbzidlb["demoid"]
            }
            # 输出要素
            scys_dic = {}
            # 循环添加输入要素
            for xx in ysxx:
                trans_dict[xx['ysdm']] = xx['ysz']
             # 循环添加输出要素
            for xx in ysxx_l:
                scys_dic[xx['ysdm']] = xx['ysz']
            # 根据测试案例id查询所属交易的交易码、超时时间
            rs = ModSql.kf_ywgl_014.execute_sql_dict(db, "get_jymby_csal", {"id":id})
            ssjy = rs[0]['jym'] if rs else None
            # 如果查询不到交易码，说明，这个节点来自子流程
            
            timeout = rs[0]['timeout'] if rs else None
            # 所属交易的交易码
            re_trans_dict = {'JDDYID':'','SYS_JYJDZXJG':'','SYS_XTLSH':''}
            # lx,节点或者子流程的id，节点或者子流程的交易代码，空，其他参数字典
            trans_dict['SYS_CSSJ'] = timeout
            # 将数据库中的十六进制数据转换为二进制发送到核心
            to_binary(trans_dict)
            re_trans_dict = transaction_test('jd',csalzxbzidlb['ssdyid'],ssjy = id, jsddbw = None,lzjy = False,ssyw = ywbm,pdic = trans_dict)
            # 将核心返回的内容转为十六进制
            binary_to_hex(re_trans_dict)
            zxjg = '1'
            # 测试案例定义表的日志key
            ModSql.kf_ywgl_014.execute_sql(db,"update_csalkey",{'id':id,'rzlsh':str([re_trans_dict.get('SYS_XTLSH')])})
            # 自动化测试临时表 rzlb为空
            sql_param = {'id':get_uuid(),'pc':pc,'csal_id':id, 'lx':'2','lb':str((csalzxbzidlb["ssdyid"],re_trans_dict.get('SYS_JYJDZXJG'))),'rzlb':str([re_trans_dict.get('SYS_XTLSH')]),'bzid':'','zxjg':''}
            ModSql.kf_ywgl_014.execute_sql(db,"add_zdhcslsb_rzlb",sql_param)
            # 将核心返回的要素代码，要素值插入到自动化测试临时表
            scys_re = copy.deepcopy(re_trans_dict)
#            del scys_re['JDDYID']
#            del scys_re['SYS_JYJDZXJG']
#            del scys_re['SYS_XTLSH']
            # 将核心反馈的输出要素信息插入到临时表中 (%(id)s, %(pc)s, %(csal_id)s, %(lx)s,%(ysdm)s,%(ysz)s)
            for k,v in scys_re.items():
                ModSql.kf_ywgl_014.execute_sql(db,"add_zdhcslsb_yzscysxx",{'id':get_uuid(),'pc':pc,'csal_id':id,'lx':'1','ysdm':k,'ysz':str(v),'bzid':''})# bzid为空，节点的没有步骤id
            # 更新完后，后台查询测试案例的输出要素、节点测试案例返回值
            scysxx = ModSql.kf_ywgl_014.execute_sql_dict(db, "getysxx", {"jdcsalzxbzlb":[csalzxbzidlb['id']],'lx':'2'}) if csalzxbzidlb['id'] else []
            csal_fhz = ModSql.kf_ywgl_014.execute_sql_dict(db, "get_jdcsfhz", {"jdcsalzxbzlb":[csalzxbzidlb['id']]}) if csalzxbzidlb['id'] else []
            jgsm = "测试成功"
            # 判断返回值是否一样
            if csal_fhz[0]['fhz'] != re_trans_dict.get('SYS_JYJDZXJG'):
                zxjg = "0" 
                jgsm = "【SYS_JYJDZXJG】与期望返回不一致"
            # 判断响应内容是否一样
            if scys_dic.get('SYS_RspCode') != re_trans_dict.get('SYS_RspCode'):
                zxjg = "0" 
                jgsm = jgsm + "【SYS_RspCode】与期望返回不一致"
                # 将测试成功这几个字替换为空
                jgsm = jgsm.replace('测试成功','')
            # 判定完成后记录临时数据表
            sql_zxycjg = {"id":get_uuid(),"pc":pc,"csal_id":id,"lx":"3","zxjg":zxjg,"jgsm":jgsm }
            result =  ModSql.kf_ywgl_014.execute_sql_dict(db, "add_zdhcslsb_zxycjg", sql_zxycjg)
            zxjg_return['zxjg'] = '成功' if zxjg == '1' else '失败'
            zxjg_return['jgsm'] = re_trans_dict.get('SYS_RspInfo')
    # 测试案例执行结束后删除demo的数据
    # 执行步骤列表循环完毕后，将插入的demo数据删除
    del_test_data_service(csal_data)
    return {'state':True,'msg':'测试结束','zxjg':zxjg_return}   

def cs_stop_service(pc):
    """
    # 点击停止测试按钮的时候,修改自动化测试增加临时表中的数据
    """
    with sjapi.connection() as db:
        # 根据数据的批次ID进行删除临时表中的数据
        redata = ModSql.kf_ywgl_014.execute_sql_dict(db, "update_zdhcslsb", {"pc":pc})
    return  redata

def cs_close_service(pc):
    """
    # 点击关闭按钮时删除自动化测试时增加的临时表中的数据
    """
    with sjapi.connection() as db:
        # 根据数据的批次的ID进行删除临时表中的信息
        redata = ModSql.kf_ywgl_014.execute_sql_dict(db, "delete_zdhcslsb", {"pc":pc})
        #判断结果
    return redata

def get_cs_zxjg_service(pc,csalids):
    """
    # 开始测试之后进行,每五秒进行刷新,获取执行测试的结果
    """
    data = []
    csalid_lst = csalids.split(',')
    with sjapi.connection() as db:
        # 根据数据的批次的ID进行删除临时表中的信息
        for csalid in csalid_lst:
            res = ModSql.kf_ywgl_014.execute_sql_dict(db, "get_zxjg", {'pc':pc,'id':csalid})
            if res:
                data.append(res[0])
    return data

def del_test_data_service(data):
    logger.info("删除demo中的数据")
    row = {}
    if type(data) == str:
        row = json.loads(data)
    # 测试案例的定义的ID
    id = row['id']
    # 开始测试的测试案例的类型
    lx = row['lb']
    demoxx_dic = {}
    #类别
    #1:交易测试案例
    #2:子流程测试案例
    #3:节点测试案例
    #4:通讯子流程测试案例
    with sjapi.connection() as db:
        if lx=='1' or lx== '2' or lx=='4':
            # 获取执行案例的执行步骤
            csalzxbzidlb = ModSql.kf_ywgl_014.execute_sql_dict(db, "get_csalzxbzidlb", {"id":id})[0]
            # 执行步骤列表循环完毕后，将插入的demo数据删除
            # 从demo数据表中,获取数据表的简称的信息
            if csalzxbzidlb["demoid"] != '' and csalzxbzidlb["demoid"] != None:
                demoids = csalzxbzidlb["demoid"].split(',')
                demo_sjbjc = ModSql.kf_ywgl_014.execute_sql_dict(db, "get_demo_sjb", {"demoids":demoids}) if demoids else []
                # 获取对应上级ID数组
                sjid_list = {row['id']:row['sjbjc'] for row in demo_sjbjc}
                # 根据上级id获取提取预设数据
                zdmzdz = ModSql.kf_ywgl_014.execute_sql_dict(db, "get_demo_zdmzdz", {"sjid":sjid_list.keys()}) if sjid_list else []
                # 获取表的主键字段,循环sjid_lst  [{'sjbmc': 'LIUHH', 'zdmc': 'abc'},{'sjbmc': 'LIUHH', 'zdmc': 'abc'}]
                # 组织数据结构:{上级ID:[数据表简称,[字段名:字段值,…]]}
                for key in sjid_list.keys():
                    demo_mz = ModSql.kf_ywgl_014.execute_sql_dict(db, "get_demo_zj", {"sjbmc":sjid_list[key]}) if sjid_list[key] else []
                    zd = []
                    for d in demo_mz:
                        zd.append(d['zdmc'])
                    if len(demo_mz) > 0:
                        demoxx_dic[key] = [demo_mz[0]['sjbmc'],zd,[]]
                    list_dic = {}
                    # 组织数据结构:{上级ID:[数据表简称,[字段名:字段值,…],{'':''}]} [{'zdz': None, 'zdm': 'abc', 'sjid': '41'}]
                    for row in zdmzdz:
                        if row['zdz'] == None:
                            row['zdz'] = ''
                        if key == row['sjid']:
                            list_dic.setdefault(row['xssx'], {})[row['zdm']] = row['zdz']
                    demoxx_dic[key][2].extend(list(list_dic.values()))
                # 执行步骤列表循环完毕后，将插入的demo数据删除
                for row in demoxx_dic.keys():
                    db_name = demoxx_dic[row][0]
                    # 循环删除所有的demo数据
                    for zdmzdz_dic in demoxx_dic[row][2]:
                        data = ""
                        sql = """
                            delete from %(db_name)s where
                        """ % {'db_name':db_name}
                        # 循环主键，拼接sql
                        for key in demoxx_dic[row][1]:
                            value = zdmzdz_dic[key]
                            if type(value) == cx_Oracle.LOB:
                                value = value.read()
                            if value==None or value == "":
                                value = "''"
                            data = key + "='" + value + "' and "
                        sql = sql + data[:-4]
                        logger.info(sql)
                        db.execute(sql)
                        db.commit()