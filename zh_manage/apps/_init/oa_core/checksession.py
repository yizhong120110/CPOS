# -*- coding: utf-8 -*-
from sjzhtspj import register, get_sess_hydm, ModSql


@register()
def get_session_hyobj():
    """
    主页访问url
    """
    hydm = get_sess_hydm()
    hyobj = None

    if hydm is not None:
        with sjapi.connection() as db:
            hyobj = ModSql.init.execute_sql(db, "checksession", {'hydm': hydm})[0]
    return hyobj
