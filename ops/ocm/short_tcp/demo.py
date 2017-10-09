# -*- coding: utf-8 -*-
"""
    单独将main函数拆分到一个py文件中，是为了能够利用__name__ == '__main__'进行测试
    使用说明：
    1、在通讯管理中新增配置
        gl_txgl.txwjmc指向main函数所在的py
    2、进程管理中新增配置
        gl_jcxxpz.qdml指向固定的文件ops/core/app_ocm.py的绝对路径
        要求 gl_jcxxpz.jcmc = gl_txgl.bm
    
    特别注意：通讯文件不可以选择一样的文件：
                目前程序设计是以“通讯文件名”为标识 处理通讯请求。
                所以如果不同的客户端通讯配置一样的通讯文件，
                则启动的通讯进程可以处理非进程对应的通讯请求（
                举例：客户端通讯A  配置通讯文件 demo.py  启动进程 A1
                    客户端通讯B  配置通讯文件 demo.py  启动进程 B1
                    A 发起通讯请求 可以被 A1或B1 处理，正确应该只能是由 A1处理
                    B 发起通讯请求 可以被 A1或B1 处理，正确应该只能是有 B1处理 ）
                得出结论是：通讯文件不可以选择一样的文件。
        解决通讯文件可以选择重复文件问题：
            1.ops.trans.node.py : message_to_ocm(senddic,jyzd.TXWJMC,int(jyzd.TIMEOUT)+5)
                                  将“jyzd.TXWJMC”改为“jyzd.TXBM”(通讯编码)
            2.ops.core.app_ocm.py: start_ocm_server([txxxdic['txwjmc']] ,self.service)
                                  将“txxxdic['txwjmc']”改为“txxxdic['bm']”
            3.ops.ocm.通讯类型.xxxxx_app.py: ocpsname = 'xxxxxx_app'
                                  将“xxxxxx_app” 改为“通讯对应的通讯编码”
"""
from ops.core.logger import tlog ,set_tlog_parms


def main( kwd ):
    """
       # kwd 字典
       # IP、PORT、BUF、TIMEOUT、FILENAME
       # FILENAME：文件名称，此字段有值表示有文件需要ftp给三方
    """
    # rzlsh 是本次日志的流水号，可以将其返回，用于查询日志
    rzlsh = set_tlog_parms(tlog ,"ocm_demo" ,kind="ocm_demo",reload_jyzd="yes")
    try:
        tlog.log_info("这是演示用demo")
        # 这里的返回值是演示使用，实际使用看需求
        return {"rsmsg":"OK" ,"rzlsh":rzlsh}
    except:
        tlog.log_exception("出异常了")
        return {"rsmsg":"error" ,"rzlsh":rzlsh}
    finally:
        tlog.close(rzlsh)


if __name__ == '__main__':
    print(main({'a':'b'}))
