# -*- coding: utf-8 -*-
# 用于处理主动冲正且立等执行完成，需要自己检查执行结果
from cpos.esb.app.jr.jr_cz import main as call_jycz
# 示例 call_jycz({"ylsh":"999906" ,'czlsh':'19985'}) 或者 call_jycz({"ylsh":"999906"})
# 需要先做jy_cz的insert
#    with connection() as con:
#        sql = """ insert into JY_CZ( rq, ylsh, cs, czwz, zt, updtime )
#                   values ( %(jyrq)s , %(lsh)s , %(cs)s , %(czwz)s , %(zt)s , %(updtime)s )"""
#        d = dict( jyrq="20151010" , lsh="999906" , cs=0 , czwz=0 , zt="1", updtime='20151010173355' )
#        con.execute_sql( sql , d )
# 以及更新jy_ls的zt值为88（交易执行异常）
