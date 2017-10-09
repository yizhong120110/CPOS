# -*- coding: utf-8 -*-
import cpos.esb.basic.rpc.rpc_transaction as rtrans

def transaction_test(lx,id,ssjy=None,jsddbw=None,lzjy=True,ssyw=None,pdic=None,timeout_interval=60 ):
    """
        # lx（类型，必填，jd-节点;zlc-子流程;jysb-交易码解出函数）、
        # id（ID，必填，memcache存储数据的key）、
        # ssjy（所属交易代码，lx为jd或zlc时必填）、
        # jsddbw（接收到的报文，lx为jysb时必填）、
        # lzjy 是否来自交易的单步调试
        # ssyw 测试所属业务，在lzjy为False时必填
        # pdic（其他参数字典，k-v结构，核心处理时会更新到jyzd中，以jyzd.K获取）
    """
    check_flag = False
    if lx in ('jd','zlc') and lzjy:
        if ssjy is None:
            raise RuntimeError("交易类单步调试 需要提供【ssjy】")
        else:
            check_flag = True
    if lx == 'jysb' and lzjy:
        if jsddbw is None or not isinstance(jsddbw ,bytes):
            raise RuntimeError("交易类单步调试 需要提供【jsddbw】，类型为bytes")
        else:
            check_flag = True
    if lx in ('jd','zlc') and not lzjy:
        if ssjy is None or ssyw is None:
            raise RuntimeError("子流程类单步调试 需要提供【ssjy，ssyw】")
        else:
            check_flag = True
    if lx in ('zlc') and not ( pdic and pdic.get('SYS_ZLCBM','')):
        raise RuntimeError("子流程类单步调试 需要提供【SYS_ZLCBM】")
    if not check_flag:
        raise RuntimeError("参数配置不合法")
    # SYS_ISDEV（标记为测试模式，取值固定为True）
    jyzd = {'SYS_ISDEV':'yes'}
    # SYS_CLBZ（处理步骤，节点、子流程测试时取值02；交易码解出测试时取值01）
    if lx == 'jysb':
        jyzd['SYS_CLBZ'] = '01'
        # SYS_TXJBID 通讯解包节点id（交易码解出测试时必填）
        jyzd['SYS_TXJBID'] = id
    else:
        jyzd['SYS_CLBZ'] = '02'
        if lx == 'zlc':
            jyzd['SYS_JYLX'] = '02'
        else:
            jyzd['SYS_JYLX'] = '03'
        # SYS_DEVJDID（节点、子流程测试时分别为节点UUID、子流程UUID，否则为None）
        jyzd['SYS_DZXJDDM'] = id
        # SYS_JYM(交易码，节点、子流程时必填，其他时None)
        jyzd['SYS_JYM'] = ssjy

        if lzjy:
            jyzd['SYS_ZLCDEV'] = 'no'
        else:
            jyzd['SYS_ZLCDEV'] = 'yes'
            jyzd['SYS_YWDM'] = ssyw
    # SYS_JSDDBW 接收到的报文（交易码解出测试时必填，节点类型的交易解包函数也可能会用到）
    jyzd['SYS_JSDDBW'] = jsddbw

    # 其他执行节点、子流程、交易码解出函数执行时需要的k-v
    if pdic:
        jyzd.update(pdic)

    print("ops.transaction_test send：",jyzd)
    jyzd = rtrans.send_trans_with_protocol(jyzd,timeout_interval=timeout_interval, try_once=True)
    print("requests：",jyzd)

    return jyzd



def test_transaction_test():
    from cpos.esb.app.tp.transaction import main
    # 通讯解包函数
    jyzd = transaction_test(lx='jysb',id='ltdls_tx',ssjy=None,jsddbw='lt001aaaaaa20150226',pdic=None )
#    print('处理前 报文字典的情况：', repr(jyzd))
#    main(jyzd)
    print('处理后 报文字典的情况：', repr(jyzd))
    print("*****************通讯解包函数 结束*******************************")
    
    # 正常的节点
    jyzd = transaction_test(lx='jd',id='zzdsf_gm_ltjfycl的UUID',ssjy='lt001',jsddbw='lt001aaaaaa20150226',pdic={'SYS_CSSJ':60} )
#    print('处理前 报文字典的情况：', repr(jyzd))
#    main(jyzd)
    print('处理后 报文字典的情况：', repr(jyzd))
    print("*****************正常的节点 结束*******************************")

    # 解包节点
    jyzd = transaction_test(lx='jd',id='unpack_beai_540003_32位UUID',ssjy='lt001',jsddbw='lt001aaaaaa20150226',pdic={'SYS_CSSJ':60} )
#    print('处理前 报文字典的情况：', repr(jyzd))
#    main(jyzd)
    print('处理后 报文字典的情况：', repr(jyzd))
    print("*****************解包节点 结束*******************************")
    # 打包节点
    jyzd = transaction_test(lx='jd',id='pack_beai_540003_32位UUID',ssjy='lt001',jsddbw='lt001aaaaaa20150226',pdic={'SYS_CSSJ':60} )
#    print('处理前 报文字典的情况：', repr(jyzd))
#    main(jyzd)
    print('处理后 报文字典的情况：', repr(jyzd))
    print("*****************打包节点 结束*******************************")

    # 子流程中的节点
    jyzd = transaction_test(lx='jd',id='dsyw_pack_beai_510001的节点ID',ssjy='lt001',jsddbw='lt001aaaaaa20150226',pdic={'SYS_CSSJ':60} )
#    print('处理前 报文字典的情况：', repr(jyzd))
#    main(jyzd)
    print('处理后 报文字典的情况：', repr(jyzd))
    print("*****************子流程中的节点 提供交易码测试 结束*******************************")
    # 子流程
    jyzd = transaction_test(lx='zlc',id='ltjf_zlc的UUID',ssjy='lt001',jsddbw='lt001aaaaaa20150226',pdic={'SYS_CSSJ':60} )
#    print('处理前 报文字典的情况：', repr(jyzd))
#    main(jyzd)
    print('处理后 报文字典的情况：', repr(jyzd))
    print("*****************交易中的子流程 结束*******************************")

    jyzd = transaction_test(lx='jd',id='dsyw_pack_beai_510001的节点ID',ssjy='ltjf_zlc的UUID',jsddbw='lt001aaaaaa20150226',lzjy=False,ssyw='ltdls',pdic={'SYS_CSSJ':60} )
#    print('处理前 报文字典的情况：', repr(jyzd))
#    main(jyzd)
    print('处理后 报文字典的情况：', repr(jyzd))
    print("*****************子流程中测试节点 结束*******************************")

    jyzd = transaction_test(lx='zlc',id='ltjf_zlc的UUID_2',ssjy='ltjf_zlc的UUID',jsddbw='lt001aaaaaa20150226',lzjy=False,ssyw='ltdls',pdic={'SYS_CSSJ':60} )
#    print('处理前 报文字典的情况：', repr(jyzd))
#    main(jyzd)
    print('处理后 报文字典的情况：', repr(jyzd))
    print("*****************子流程中测试子流程 结束*******************************")


def test_send():
    jyzd = {'SYS_ISDEV':True, 'SYS_CLBZ':'01','SYS_JSDDBW':'lt001aaaaaa20150226','SYS_TXJBID':'ltdls_tx'}
    print("*******************888888",jyzd)
    rm = rtrans.send_trans_with_protocol(jyzd)
#    print ('total responds : ' + str(rm._data['content']) )
    jyzd = rm._data['content']
    print("*******************888888",jyzd)


if __name__=="__main__":
    test_send()

