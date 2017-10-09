# -*- coding: utf-8 -*-
# Action: 生成Memcache中的存储结构
# Author: gaorj
# AddTime: 2015-03-09
# Standard: 注释仅能以“#”开头，sql可以是“--”；注释不能同代码在同一行
import os
import cpos.esb.basic.resource.rdb
from cpos.esb.basic.config import settings
from cpos.esb.basic.busimodel.transutils import pickle_loads


def main(lx, key):
    """
    lx:  交易节点（JYJD）交易（JY） 业务（YW） 函数（HS） 子流程（ZLC） 通讯节点（TXJD）
    key: 交易节点UUID    交易码     业务简称   函数UUID   子流程UUID    通讯节点代码
    """
    with connection() as db:
        data = {}
        if lx == 'JYJD':
            sql = """
                select a.bm, b.nr
                from gl_jddy a, gl_blob b
                where a.dm_id = b.id
                    and a.id = %(id)s
            """
            d = {'id': key}
            rs = db.execute_sql(sql, d)
            rs = rs[0] if len(rs) else None
            if rs:
                data = {'mc': rs.bm+"()", 'dm': pickle_loads(rs.nr) if rs.nr else ''}
        elif lx == 'JY' or lx == 'ZLC':
            if lx == 'JY':
                # 根据交易码查询交易UUID
                sql = "select id from gl_jydy where jym = %(jym)s"
                d = {'jym': key}
                rs = db.execute_sql(sql, d)
                rs = rs[0] if len(rs) else None
                key = rs.id if rs else ''
            
            # 流程dic
            lc_dic = {}
            # 查询节点/子流程名称、节点类型、filename和functionname
            sql = """
                select a.id, coalesce(b.id, c.id) as nodeid, coalesce(b.bm, c.bm) as bm, coalesce(b.jdmc, c.mc) as mc
                    , a.jdlx as jdlx_bj, b.jdlx as jdlx_jd, b.filename, b.functionname, b.type
                from gl_lcbj a left join gl_jddy b on a.jddyid = b.id
                    left join gl_zlcdy c on a.jddyid = c.id
                where a."""+('sszlcid' if lx=='ZLC' else 'ssjyid')+""" = %(id)s
            """
            d = {'id': key}
            rs_lcbj = db.execute_sql(sql, d)
            
            # 流程走向
            sql = """
                select a.qzjdlcbjid as source, a.hzjdlcbjid as target, a.fhz as value, b.jddyid
                from gl_lczx a, gl_lcbj b
                where a.hzjdlcbjid = b.id
                and a.ssid = %(id)s
            """
            d = {'id': key}
            rs_connector = db.execute_sql(sql, d)
            
            # 查询节点要素
            sql = """
                select a.jddyid, a.lb, a.bm, a.ysmc, a.mrz, a.ly
                    , case when d.csdm is null then '1' else '2' end as gslb
                from gl_jdys a left join (
                        select distinct csdm from gl_csdy where lx = '5'
                    ) d on a.bm = d.csdm
                    , gl_jddy b, gl_lcbj c
                where a.jddyid = b.id
                    and b.id = c.jddyid
                    and (a.lb = '1' or a.lb = '2')
                    and c."""+('sszlcid' if lx=='ZLC' else 'ssjyid')+""" = %(id)s
            """
            d = {'id': key}
            rs_jdys = db.execute_sql(sql, d)
            
            for row in rs_lcbj:
                # 节点ID
                if row['jdlx_jd'] in ('3', '10'):
                    nodeid = 'start'
                elif row['jdlx_jd'] in ('4', '11'):
                    nodeid = 'end'
                else:
                    nodeid = row['nodeid']
                
                cs = {}
                # 不同类型的处理
                if row['jdlx_jd'] is None:
                    lclx = 'flow'
                elif row['jdlx_jd'] in ('2', '7'):
                    lclx = 'pyc'
                    # 2系统节点，7通讯节点
                    functioname = 'pre_node' if row['jdlx_jd'] == '2' else ('call_node' if row['jdlx_jd'] == '7' else '')
                    cs = {'modname': os.path.join(settings.OPS_ROOT ,'trans' ,'node.py'), 'funcname': functioname, 'tpye': 'py'}
                elif row['jdlx_jd'] == '12':
                    lclx = 'java'
                elif row['filename'] is not None:
                    lclx = 'c'
                    cs = {'modname': row['filename'], 'funcname': row['functionname'], 'tpye': row['type']}
                else:
                    lclx = 'py'
                fhz = {}
                for item in rs_connector:
                    if item['source'] == row['id']:
                        if item['jddyid'] in ("jystart", "zlcstart"):
                            fhz[item['value']] = "start"
                        elif item['jddyid'] in ("jyend", "zlcend"):
                            fhz[item['value']] = "end"
                        else:
                            fhz[item['value']] = item['jddyid']
                lc_dic[nodeid] = {
                    'lx': lclx,   # 类型c/py/pyc/flow
                    'jdbm': row['bm'],  # 节点编码
                    'jdmc': row['mc'],  # 节点名称
                    'fhz': fhz,  # 返回值
                    'srys': {item['bm']:item['mrz'] for item in rs_jdys if item['lb'] == '1'} if lclx == 'c' else {},   # 输入要素
                    'scys': {item['bm']:item['mrz'] for item in rs_jdys if item['lb'] == '2'} if lclx == 'c' else {},   # 输出要素
                    'cs': cs
                }
            
            # 对于子流程，直接返回流程dic
            if lx == 'ZLC':
                return lc_dic
            
            # 查询交易基本信息
            sql = """
                select a.jym, a.jymc, a.dbjdid, a.jbjdid, a.zt, a.timeout, b.ywbm
                from gl_jydy a,gl_ywdy b
                where a.id = %(id)s
                and a.ssywid = b.id
            """
            d = {'id':key}
            rs_jy = db.execute_sql(sql, d )
            rs_jy = rs_jy[0] if len(rs_jy) else None
            # 查询交易参数
            sql = """
                select csdm, value
                from gl_csdy
                where zt = '1'
                    and ssid = %(id)s
            """
            d = {'id': key}
            rs_cs = db.execute_sql(sql, d)
            
            if rs_jy:
                data = {
                    'jydm': rs_jy.jym,      # 交易码
                    'jymc': rs_jy.jymc,     # 交易名称
                    'jylc':lc_dic,          # 流程dic
                    'jydb': rs_jy.dbjdid,   # 交易打包节点UUID
                    'jyjb': rs_jy.jbjdid,   # 交易解包节点UUID
                    'jycs': {item['csdm']:item['value'] for item in rs_cs}, # 交易参数
                    'jyzt': rs_jy.zt,       # 交易状态
                    'cssj': rs_jy.timeout,  # 超时时间
                    'jyssyw': rs_jy.ywbm  # 所属业务
                }
        elif lx == 'YW':
            # 查询业务基本信息
            sql = "select id, ywmc from gl_ywdy where ywbm = %(ywbm)s"
            d = {'ywbm': key}
            rs_yw = db.execute_sql(sql, d)
            rs_yw = rs_yw[0] if len(rs_yw) else None
            
            # 查询业务参数
            sql = """
                select csdm, value
                from gl_csdy
                where zt = '1'
                    and ssid = %(id)s
            """
            d = {'id': rs_yw.id}
            rs_cs = db.execute_sql(sql, d )
            
            # 查询业务公共函数
            sql = "select id from gl_yw_gghs where ssyw_id = %(id)s"
            d = {'id': rs_yw.id}
            rs_hs = db.execute_sql(sql, d)
            
            # 查询打印模板
            sql = "select id from gl_dymbdy where ssyw_id = %(id)s"
            d = {'id': rs_yw.id}
            rs_dy = db.execute_sql(sql, d)
            
            if rs_yw:
                data = {
                    'ywdm': key,     # 业务编码
                    'ywmc': rs_yw.ywmc,     # 业务名称
                    'ywcs': {item['csdm']:item['value'] for item in rs_cs}, # 业务参数
                    'ywhsqd': [row['id'] for row in rs_hs],     # 业务公共函数
                    'ywdypzqd': [row['id'] for row in rs_dy],   # 打印配置
                    'ywyzpz': {}    # 业务阈值配置
                }
        elif lx == 'HS':
            # 查询业务公共函数
            sql = """
                select a.mc, b.nr, 'py' as dmlx
                from gl_yw_gghs a, gl_blob b
                where a.nr_id = b.id
                    and a.id = %(id)s
            """
            d = {'id': key}
            rs = db.execute_sql(sql, d)
            rs = rs[0] if len(rs) else None
            
            # 无记录，查询打印模板定义
            if not rs:
                sql = """
                    select a.mbmc as mc, b.nr, 'str' as dmlx
                    from gl_dymbdy a, gl_blob b
                    where a.nr_id = b.id
                        and a.id = %(id)s
                """
                d = {'id': key}
                rs = db.execute_sql(sql, d)
                rs = rs[0] if len(rs) else None
            
            # 无记录，查询函数信息表
            if not rs:
                sql = """
                    select a.hsmc as mc, b.nr, case when a.dmlx = '2' then 'str' else 'py' end as dmlx
                    from gl_hsxxb a, gl_blob b
                    where a.nr_id = b.id
                        and a.id = %(id)s
                """
                d = {'id': key}
                rs = db.execute_sql(sql, d)
                rs = rs[0] if len(rs) else None
            
            if rs:
                data = {
                    'mc': rs.mc,    # 函数名称
                    'dm': pickle_loads(rs.nr) if rs.nr else '',    # 函数代码
                    'dmlx': rs.dmlx # 代码类型py/str
                }
        elif lx == 'HS_SHELL':
            # shell 类型的函数
            # 无记录，查询函数信息表
            sql = """
                select a.hsmc as mc, b.nr, 'shell' as dmlx
                from gl_hsxxb a, gl_blob b
                where a.dmlx = '2'
                    and a.nr_id = b.id
                    and a.id = %(id)s
            """
            d = {'id': key}
            rs = db.execute_sql(sql, d)
            rs = rs[0] if len(rs) else None
            
            if rs:
                data = {
                    'mc': rs.mc,    # 函数名称
                    'dm': pickle_loads(rs.nr) if rs.nr else '',    # 函数代码
                    'dmlx': rs.dmlx # 代码类型py/str
                }
        elif lx == 'TXJD':
            sql = """
                select b.nr
                from gl_txgl a, gl_blob b
                where a.jcjymhsid = b.id
                    and a.bm = %(bm)s
            """
            d = {'bm': key}
            rs = db.execute_sql(sql, d)
            rs = rs[0] if len(rs) else None
            
            if rs:
                data = {
                    'mc': key + '()',   # 函数名称
                    'dm': pickle_loads(rs.nr) if rs.nr else '',    # 函数代码
                    'jdcs': {}  # 参数dic
                }
    return data

if __name__ == '__main__':
    data = main('JYJD', '118925588c7841ed80c029a5fd472187')
    print(data)
