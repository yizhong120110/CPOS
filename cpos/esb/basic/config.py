# -*- coding: utf-8 -*-

#1、读取config目录下有哪些文件
#2、将文件列表中的config_local单独拿出来
#3、取出每个文件中的固定名称的列表
#4、将列表中的变量绑定到settings上
#5、不能有重复的变量出现
import os
import glob
import copy
from cpos.foundation.conf.core import Settings ,settings


def get_settings(fileslst,modulepath,globalsettings):
    cfg_local = []
    mod_reg_lst = []
    for filepath in fileslst:
        mod_reg = os.path.split(filepath)[-1].split('.')[0]
        if mod_reg == "config_local":
            # 最后处理
            cfg_local = [(mod_reg ,filepath)]
            continue
        else:
            mod_reg_lst.append( (mod_reg ,filepath) )
    mod_reg_lst += cfg_local
    
    for mod_reg ,filepath in mod_reg_lst:
        tt = Settings()
        modname = '%s.%s'%(modulepath, mod_reg)
        print("注册配置模块", modname)
        bef_reg = copy.deepcopy(set(tt._dict.keys()))
        tt.register(modname)
        regi_objs = list(set(list(tt._dict.keys())) - bef_reg)

        for var_tt in regi_objs:
            if globalsettings._dict.get(var_tt):
                if mod_reg!="config_local": 
                    raise RuntimeError("【%s】中的【%s】变量名重复，请检查修改"%(modname,var_tt))
                else:
                    print("【%s】中的【%s】变量名重复，将直接覆盖"%(modname,var_tt))
            globalsettings._dict[var_tt] = tt._dict.get(var_tt)
    return globalsettings
    

fileslst = glob.glob(os.path.abspath(os.path.join(os.path.split(__file__)[0],'configs', 'config_*.py')))
settings = get_settings(fileslst, 'cpos.esb.basic.configs', settings)
