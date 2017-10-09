# -*- coding: utf-8 -*-

import cpos.esb.basic.resource.rdb
from cpos.esb.basic.resource.logger import logger
from cpos.esb.basic.busimodel.transutils import get_xtcs


def get_cjzb( hostname ):
    # 反馈的数据结构为:
    #   [{'发起频率':'发起频率','类名':'类名','函数名称':'','类参数':{},'函数参数':{},'唯一码':'对象采集配置id+bbh'}]
    #   [{'fqpl':'','classname':'','funcname':'','classparam':{},'funcparam':{},'wym':''}]
    logger.ods ("获取主机对应的采集指标列表api函数" ,lv='dev',cat = 'esb.app.rdcs.rdcs')
    with connection() as con:
        # 函数参数信息
        sql_hs_cs = """select d.csdm, a.csz, d.mrz, b.id as dxcjpzid from gl_csdyb a, gl_dxcjpz b, gl_cjpzb c, gl_crcs d
                where a.ssid = b.id
                and b.sscjpzid = c.id
                and c.zbid = d.ssid
                and d.id = a.crcsid
                and c.lx = '1'
                and b.cjpzzt = '1'
                and b.dxzt = '1'
                and b.scbz = '0'
                and b.zdzjzt = '1'
                and b.zdzjip = %(hostname)s"""
        logger.ods ("查询本主机对应的采集函数参数列表sql:%s" % sql_hs_cs ,lv='dev',cat = 'esb.app.rdcs.rdcs')
        d = dict(hostname=hostname)
        rs = con.execute_sql(sql_hs_cs, d)
        rs_hs_cs = rs
        # 对象id 对应参数字典
        dxcjpzid_to_cs_dic = {}
        for obj in rs_hs_cs:
            if obj['dxcjpzid'] not in dxcjpzid_to_cs_dic:
                dxcjpzid_to_cs_dic[obj['dxcjpzid']] = {}
            dxcjpzid_to_cs_dic[obj['dxcjpzid']][obj['csdm']] = obj['csz'] if obj['csz'] else ( obj['mrz'] if obj['mrz'] else '' ) 
        # 对象信息
        sql = """select b.zdfqpz as fqpl, c.sslbbm as classname, 
                c.zbbm as funcname, a.id as dxcjpzid, a.zdzjip as zjip,
                a.bbh
                from gl_dxcjpz a, gl_cjpzb b, gl_jkzb c
                where b.lx = '1'
                and a.sscjpzid = b.id
                and b.zbid = c.id
                and a.cjpzzt = '1'
                and a.dxzt = '1'
                and a.scbz = '0'
                and a.zdzjzt = '1'
                and a.zdzjip = %(hostname)s"""
        logger.ods ("查询本主机对应的采集指标列表sql:%s" % sql ,lv='dev',cat = 'esb.app.rdcs.rdcs')
        rs = con.execute_sql(sql, d)
        
        # 组织反馈信息
        rs_lst = []
        for row in rs:
            # 类参数
            classparam = { 'zjip': row['zjip'], 'dxcjpzid': row['dxcjpzid'] }
            # 函数参数
            funcparam = dxcjpzid_to_cs_dic.get( row['dxcjpzid'], {} )
            # 唯一码
            wym = row['dxcjpzid'] + str(row['bbh'])
            rs_lst.append( { 'fqpl':row['fqpl'],'classname':row['classname'],'funcname':row['funcname'],
            'classparam':classparam,'funcparam':funcparam,'wym':wym } )
    return rs_lst


def get_interval():
    """
        获得数据库轮询的间隔时间
    """
    try:
        return int(get_xtcs("INTERVAL_RDCS" ,'10'))
    except:
        return 10

if __name__ == '__main__':
    rs_lst = get_cjzb('tsgl')
    print ( '>>>>>>>rs_lst:', rs_lst )
