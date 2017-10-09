# -*- coding: utf-8 -*-
"""
   md5加密
"""

import hashlib
def cal_md5( obj, encoding='utf-8', isUpper = False ):
    """
    # 计算传入对象的md5值
    # 先将传入对象做str()处理，再计算
    """
    if isUpper:
        return hashlib.md5(str(obj).encode(encoding) ).hexdigest().upper()
    else:
        return hashlib.md5(str(obj).encode(encoding) ).hexdigest()