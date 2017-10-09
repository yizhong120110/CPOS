# -*- coding: utf-8 -*-
"""  
    rdc
      业务处理：执行数据分析的类函数
      启动方式为 python34 app.py -p 10012 -T rdcapp -i 1000_1 -t 3 -w 10 hexstr
      python34 app.py 80037D710028580800000066756E636E616D657101580D0000006765745F7669727475616C28297102580300000077796D7103582100000037333038663133616535616134376231393336656532316139656436373439393071045809000000636C6173736E616D6571055817000000436F6D7075746572287A6A69702C6478636A707A6964297106580900000066756E63706172616D71077D710858040000006671706C710958020000003333710A580A000000636C617373706172616D710B7D710C2858040000007A6A6970710D58040000007473676C710E58080000006478636A707A6964710F58200000003733303866313361653561613437623139333665653231613965643637343939711075752E -p 5612 -T 7308f13ae5aa47b1936ee21a9ed674990 -i 87b8280a37904b04b7d3824cebfe4c46 -t 5 -w 10
      这个进程属于一次性的进程，不需要重复加载代码
      停止时，直接kill自己即可
"""
try:
    from . import loader
except:
    import loader
from cpos.esb.basic.resource.logger import logger
from cpos.esb.basic.application.app_rpclog import env_get
from cpos.esb.basic.application.app_ctrle import EApp
from cpos.esb.basic.application.app_interval import interval
from cpos.esb.basic.config import settings
from cpos.esb.basic.resource.dycall import dcallpy ,scall
import os
import pickle


def rdc_main(parmsdic):
    # 初始化环境
    filename = settings.TRANS_ENV_INIT
    dr = dcallpy(os.path.split(filename)[-1] ,root=os.path.dirname(filename))
    # 加载代码文件
    filename = settings.ZH_MANAGE_PY
    dr = dcallpy(os.path.split(filename)[-1] ,root=os.path.dirname(filename),runtime = dr)
    
    dr.np["parmsdic"] = parmsdic
    
    func_str = "%s(**parmsdic['classparam']).%s(**parmsdic['funcparam'])"%( parmsdic['classname'].split("(")[0] ,parmsdic['funcname'].split("(")[0] )
    logger.ods ("被调用的函数串为：%s"%(func_str) ,lv='dev',cat = 'app.rdc')
    # 调用函数
    dr = scall(func_str,runtime = dr)


def working_callback(msgload):
    # 通过pickle后的hex串来传输参数字典
    args_hexstr = (env_get('ProcessArgs') or [''])[-1]
    logger.ods ("启动任务处理：%s"%(args_hexstr) ,lv='info',cat = 'app.rdc')
    parmsdic = {}
    if args_hexstr:
        try:
            parmsdic = pickle.loads(bytes().fromhex(args_hexstr)) 
        except:
            pass
    if parmsdic:
        logger.ods ("解析得到的参数为：%s"%(str(parmsdic)) ,lv='info',cat = 'app.rdc')

        try:
            # 先做一下
            rdc_main(parmsdic)

            fqpl = int(parmsdic['fqpl'])
            while interval.run(fqpl,env_get('keep_running',True)):
                # 按照发起间隔处理
                rdc_main(parmsdic)
        except:
            logger.oes ("处理异常：" ,lv='error',cat = 'app.rdc')

    else:
        logger.ods ("没有获得到启动参数，或解析参数失败：%s"%(args_hexstr) ,lv='info',cat = 'app.rdc')
    return True


# 启动之初就激活E的工作线程
EApp(working_callback=working_callback,appname="RDC",startwork=True).run()
