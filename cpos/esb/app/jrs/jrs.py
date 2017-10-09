# -*- coding: utf-8 -*-
from cpos.esb.basic.application.app_rpclog import env_set,env_get,env_pop
from cpos.esb.basic.resource.logger import *
import copy
import json


def send_msg_to_env(cnt_dict):
    """
        将消息放到env中，作为线程间的中转
    """
    client_type = cnt_dict.get('source',None)
    if client_type is None:
        return {"result":"缺少source参数，无法处理"}
    _type_msg_temp = env_get('_type_msg_temp',{})
    if not _type_msg_temp.get(client_type):
        _type_msg_temp[client_type] = []
    _type_msg_temp[client_type].append(json.dumps(cnt_dict))
    env_set('_type_msg_temp',_type_msg_temp)
    # 这里返回None的时候，发起方是不能够获取到返回结果的
    # 处理时，如果直接返回字符串，会在做json处理时出现错误
    return {"result":"send_msg_to_env ok"}


def env_msg_to_r(ctk):
    """
        从env中将暂存的任务放到R的任务清单中
    """
    _type_msg_temp = env_pop('_type_msg_temp',{})
    for client_type ,msglst in _type_msg_temp.items():
        for msgstr in msglst:
            # 添加任务
            logger.ods("收到新任务 client_type %s ,msgstr %s"%(client_type ,msgstr) ,lv = 'info',cat = 'app.jrs')
            ctk.add_msg_for_e(client_type ,msgstr ,increase=True)
    return None ,True

