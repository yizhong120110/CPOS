# -*- coding: utf-8 -*-

def qx_xh_cz( cur, lsh, jyrq, xh ):
    """
    # 交易通讯为通讯失败，无需冲正时，需要将通讯发起前登记的冲正步骤删除
    """
    sql_del = " delete from jy_htrz where lsh = %s and jyrq = '%s' and xh = %s " % ( 
            lsh, jyrq, xh )
    cur.execute( sql_del )
