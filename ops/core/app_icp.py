# -*- coding: utf-8 -*-
"""
    这个文件的存在目的是为了简化部分二次开发
    二次开发仅开发真正的业务处理逻辑文件即可，通过-T对应的值，导致数据库中的client_type，然后获得相应的处理逻辑代码
    要求：gl_jcxxpz.jcmc=gl_txgl.bm
    python34 app_icp.py -p 5614 -T jnfstpos_app -i b13bdf8529ff4f5b89b12cef1ad5b493 -t 10 -w 600
"""
from ops.core.logger import logger
from ops.core.app import RpclogEApp ,get_shell_args
from ops.core.rdb_icpocm import get_txxx ,get_txcs


# 通过指定参数的方式启动icp
#options ,args = get_shell_args()
#icpsname = args[-1]
# 使用client_type作为唯一标识，然后查询数据库，得到相关信息
options ,args = get_shell_args()
selfname = options['client_type']


class ICP(RpclogEApp):
    """
        接收到三方的报文后，转发核心ICM
    """
    def jobResponder (self):
        try:
            # 二次开发者实现的监听代码
            txxxdic = get_txxx(selfname)
            main( get_txcs(selfname, txbm = txxxdic['bm']), txxxdic['bm'] )
        except:
            logger.oes( 'ICP启动异常' ,lv = 'error',cat = 'ops.app_icp')
        self.stopping()
        return True

    def on_start (self):
        txxxdic = get_txxx(selfname)
        # 引用放在这里，是为了能够在启动时就检查模块是否配置错误
        exec("from %s import main"%(txxxdic['txwj']) ,globals())

        RpclogEApp.on_start(self)
        # 这是附加一个线程
        self.register_thread('jobResponder',self.jobResponder)

ICP(appname=selfname).run()
