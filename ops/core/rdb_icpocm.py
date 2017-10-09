# -*- coding: utf-8 -*-
""" 
    通讯进程参数信息查询
"""
import ops.core.rdb


def get_txxx( txjclx ):
    """
        通过进程信息表的jclx，获得通讯进程相关的参数
        返回值：
        {'txwj': 'ops.ocm.short_tcp.jnfs_app', 'bm': 'jnfs_app'}
    """
    txjdxx_dic = {}
    with connection() as db:
        sql = """
            select b.fwfx ,b.txlx ,b.txwjmc ,b.bm
            from gl_jcxxpz a ,gl_txgl b
            where a.jcmc = b.bm
            and a.zt = '1' and a.jclx = %(jclx)s
        """
        # 使用sql和dict分离的方式，是为了防止SQL注入
        d = {'jclx':txjclx}
        rs = db.execute_sql( sql ,d )
        obj = rs[0] if rs else None
        if obj:
            wjlj = ['ops']
            if str(obj['fwfx']) == "1":
                wjlj.append("ocm")
            else:
                wjlj.append("icp")
            wjlj.extend([obj['txlx'] ,obj['txwjmc'].split('.')[0]])
            # 通讯文件的路径
            txjdxx_dic["txwj"] = ".".join(wjlj)
            # 通讯的编码，用于获得通讯的参数
            txjdxx_dic.update( {"bm":obj['bm']} )
            txjdxx_dic.update( {"txwjmc":obj['txwjmc'].split('.')[0]} )
    return txjdxx_dic


def get_txcs( txjclx ,txbm = None ):
    """
        txbm 是通讯管理中的唯一标识
        返回值： 使用的界面配置的k-v对
        {'IP': '127.0.0.1'}
    """
    txcs_dic = {}
    # 如果传了txbm，就不用查询了，没有就查询一次
    if txbm == None:
        txxx = get_txxx( txjclx )
        if txxx:
            txbm = txxx["bm"]
        else:
            return txcs_dic

    with connection() as db:
        # 使用sql和dict分离的方式，是为了防止SQL注入
        sql = """
            select csdm ,value as csz 
            from gl_csdy a ,gl_txgl b
            where a.lx = '4' and a.ssid = b.id
            and a.zt = '1'
            and b.bm = %(txbm)s
        """
        rs = db.execute_sql( sql ,{"txbm":txbm} )
        for obj in rs:
            txcs_dic.update({obj['csdm']:obj['csz']})
    return txcs_dic


if __name__ == '__main__':
    print(get_txcs(get_txxx( 'jnfs_app' )["bm"]) )
