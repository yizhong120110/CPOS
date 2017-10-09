# -*- coding: utf-8 -*-
from cpos.esb.basic.config import settings
from cpos.esb.basic.resource.logger import logger

if settings.MEMCACHE_TYPE == "aliyun":
    import bmemcached as memcache
else:
    from cpos.foundation.cache import memcache


def get_memclient():
    memclient = None
    try:
        if settings.MEMCACHE_TYPE == "aliyun":
            memclient = memcache.Client( *settings.MEMCACHE_PARAMS )
        else:
            memclient = memcache.Client(settings.MEMCACHE_IPS, settings.MEMCACHE_DEBUG, settings.MEMCACHE_TIMEOUT)

        # 判断是否能够连接到memcache中
        try:
            memclient.get("testOK")
            logger.ods ("memclient创建成功" ,lv='dev',cat = 'resource.cache')
        except:
            logger.ods ("memclient创建失败" ,lv='warning',cat = 'resource.cache')
        return memclient
    except:
        logger.oes ("memclient创建出现异常" ,lv='error',cat = 'resource.cache')
    return memclient


def memcache_data_del(key_lst):
    """
        # 数据key_lst[memcache数据的key1,memcache数据的key2,..]
    """
    boolbean = True
    memclient = None
    if memclient is None:
        memclient = get_memclient()
    if memclient:
        for keystr in key_lst:
            # 没有连接对象的时候，不用删除
            try:
                memclient.delete(keystr)
            except:
                # 有一个失败也返回False
                boolbean = False
        try:
            memclient.disconnect_all()
        except:
            pass
    return boolbean


def test_memcache_data_del():
    mclt = get_memclient()
    aalst = ['aaaaa','pack_beai_540003_32位UUID']
    print("----------------------删除之前---------------------")
    for kstr in aalst:
        print(mclt.get(kstr))
    print(memcache_data_del(aalst))
    print("----------------------删除之后---------------------")
    for kstr in aalst:
        print(mclt.get(kstr))

if __name__=="__main__":
    test_memcache_data_del()
