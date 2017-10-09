# -*- coding: utf-8 -*-
"""
    这个文件的存在目的是为了简化部分二次开发
    二次开发仅开发真正的业务处理逻辑文件即可，通过-T对应的值，导致数据库中的client_type，然后获得相应的处理逻辑代码
    要求：gl_jcxxpz.jcmc=gl_txgl.bm
    python34 app_ocm.py -p 5614 -T jnfs_app -i b13bdf8529ff4f5b89b12cef1ad5b493 -t 10 -w 600
"""
from ops.core.logger import logger
from ops.core.app import RpclogEApp ,get_shell_args
from ops.core.rpc import start_ocm_server
from ops.core.rdb_icpocm import get_txxx
import sys


# 使用client_type作为唯一标识，然后查询数据库，得到相关信息
options ,args = get_shell_args()
selfname = options['client_type']


def apply_request_on_ocps (comm_message):
    """
        从RMQ上收到字典后要处理的内容
        根据获得的消息，去找到相应的代码文件，然后执行main函数
    """
    try:
        rs = main(**comm_message)
        # 返回值必须是字典的形式
        return {"rsbuff":rs}
    except:
        return {"rsbuff":"存在语法错误: "+str(sys.exc_info())}


################################################ 下面的部分是OCM的主体代码，一般不需要修改


class OCM(RpclogEApp):
    """
        OCM的通用调用，通过client_type找到相关的信息
    """
    def service (self ,received):
        # 这里不能够输出日志，有可能存在文件，输出文件内容时会很大
        # buff才是二次开发者操作的变量，封装一下的目的是为了保证二次开发传递的参数都在一个字典value中
        comm_message = received.getcontent()["buff"]
        return apply_request_on_ocps(comm_message), self.keep_running

    def jobResponder (self):
        try:
            # 这里用于从RMQ上获得消息
            txxxdic = get_txxx(selfname)
            # zhangchl 和 shihx 确认 此处需要使用通讯文件名称，是和ops.trans.node.py 中
            # call_node的 message_to_ocm(senddic,jyzd.TXWJMC,int(jyzd.TIMEOUT)+5) TXWJMC 遥相呼应
            start_ocm_server([txxxdic['txwjmc']] ,self.service)
        except:
            logger.oes( 'OCM启动异常' ,lv = 'error',cat = 'ops.app_icp')
        self.stopping()
        return True

    def on_start (self):
        txxxdic = get_txxx(selfname)
        # 引用放在这里，是为了能够在启动时就检查模块是否配置错误
        exec("from %s import main"%(txxxdic['txwj']) ,globals())

        RpclogEApp.on_start(self)
        # 这是附加一个线程
        self.register_thread('jobResponder',self.jobResponder)

OCM(appname=selfname).run()
