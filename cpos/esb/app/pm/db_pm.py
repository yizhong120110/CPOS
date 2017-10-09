# -*- coding: utf-8 -*-
"""  
    从数据库中获得进程配置信息
"""
import cpos.esb.basic.resource.rdb
from cpos.esb.basic.resource.functools import get_hostname
from cpos.esb.basic.busimodel.transutils import get_xtcs
from cpos.esb.basic.config import settings
ctrl_re_pm = settings.CTRL_RE_PM


def get_jcpzxx(jclx=None):
    """
        pm 使用的数据库操作相关代码
        对于某些类型，是使用配置项中提供的启动参数，db中仅提供数量
        可以单独查询某个类型的进程配置信息
    """
    d = {}
    with connection() as con:
        # jclx：REH中的类别
        # jcsl：REH中的数量
        # qdml：REH中的启动文件名称
        # txwjmc：REH中的启动参数，仅一个
        sql = " select jclx, jcsl ,qdml ,txwjmc from gl_jcxxpz where sszj_ip = %(hostname)s and zt = '1' and jcsl != '0' "
        di = {'hostname':get_hostname()}
        if jclx:
            sql += " and jclx=%(jclx)s"
            di.update({'jclx':jclx})
        rs = con.execute_sql( sql, di )
        for row in rs:
            jclx = row['jclx']
            jcsl = row['jcsl']
            qdml = row['qdml'] or ''
            txwjmc = row['txwjmc'] or ''
            if ctrl_re_pm['init_config'].get(jclx):
                # 系统提供的函数，这里只是设置数量
                d[jclx] = ctrl_re_pm['init_config'][jclx]
            else:
                # 需要提供启动的文件名称及参数
                d[jclx] = {"appfilepath":str(qdml),"apparg":list(str(txwjmc).split(','))}
            d[jclx]["count"] = int(jcsl)
            d[jclx]["interval"] = ctrl_re_pm["interval"]
    return d


def get_interval():
    """
        获得数据库轮询的间隔时间
    """
    try:
        return int(get_xtcs("INTERVAL_PM" ,'10'))
    except:
        return 10

if __name__=="__main__":
    print(get_jcpzxx("filelp"))
