# -*- coding: utf-8 -*-
import os
userhome = os.environ.get('HOME','')

# OPS 是管理端需要核心加载的代码（或者核心提供给管理端的代码）位置
OPS_ROOT = "%s/src/ops"%(userhome)
# 交易处理环境初始化代码所在路径
TRANS_ENV_INIT = os.path.join(OPS_ROOT ,'envinit.py')

# 通过RMQ传输文件时，文件的目录位置
RPC_FILE_ROOT = "%s/rpc_file"%(userhome)

# 管理平台提供的代码位置
ZH_MANAGE_PY = os.path.join(OPS_ROOT ,'zh_manage','yw_jkgl_001.py')

