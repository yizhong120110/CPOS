# -*- coding: utf-8 -*-
from cpos.foundation.substrate.utils.logger import \
    logger,logger_enable_console,logger_set_root
from cpos.esb.basic.config import settings
import os
# 设置的默认目录，每个app启动的时候应该自行赋值
logger_set_root(logger,os.path.join(settings.APPLOGPATH, "devdebug"))
logger_enable_console(logger,settings.LOG_ENABLE_CONSOLE)
logger.filter(settings.LOG_FILTER)
logger.level(settings.LOG_LEVEL)
