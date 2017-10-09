# -*- coding: utf-8 -*-
from cpos.esb.basic.icm.icm_network import send_to_icm_reply as call_jy_reply
from cpos.esb.basic.icm.icm_network import send_to_icm_noreply as call_jy_noreply
from cpos.esb.basic.icm.icm_network import send_to_icm_noreply_2 as call_jy_noreply_2


#from cpos.esb.app.icm.icm import do_tp_proc
#def call_jy_sync(jym ,JSDDBW ,cssj):
#    """
#        通过函数调用的方式发起交易，同步返回结果
#        测试: print(call_jy_sync('lt001' ,'lt001aaaaaa20150226' ,"60"))
#    """
#    # 交易发起时需要设置一些值
#    jyzd = {'SYS_TXJBID':'call_jy','SYS_CLBZ': '02'}
#    jyzd['SYS_JYM'] = jym
#    jyzd['SYS_JSDDBW'] = JSDDBW
#    jyzd['SYS_CSSJ'] = cssj
#    return do_tp_proc('02',jyzd)

if __name__=="__main__":
    print(call_jy_noreply('ltdls_tx' ,'lt001aaaaaa20150226'))
    print(call_jy_reply('ltdls_tx' ,'lt001aaaaaa20150226'))
