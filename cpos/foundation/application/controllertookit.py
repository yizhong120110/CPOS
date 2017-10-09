# -*- coding: utf-8 -*-
"""
    ControllerTookit
    为Controller提供一些操作方法，可以使其完成同controllee的数据交互，启停controllee
    主要是提供一些基础性的操作方法，具体的组合应用在controller中实现
        1、创建一个新的controllee
        2、启动一个controllee
        3、维护controllee的汇报信息
        4、确保在controllee汇报超时时能够重启controllee
        5、设置controllee的返回消息
        6、获得指定的controllee的对象
"""
import copy
import uuid
import threading
import time
from .env import env_get
from ..substrate.utils.logger import logger


def now():
    return time.time()


class ControllerTookit(object):

    def __init__(self):
        # 所有的controllee的登记信息汇总  将client会使用的内容放到clientcfg中，避免冲突
        # {'clientid':{'type':'type_name','updatetime':'','clientcfg':{}}}
        self.controllees = {}
        # 按照controllee的类别来维护，确定要给哪类的controllee发送消息，只有所有内容都发送完成后，才能够停止进程
        # 每个类别的controllee能够启动多少个，其配置信息 {'type_name':{'count':n ,'interval':n ,'message_list':[]}}
        self.controllees_config = {}
        self.einfo_guard = threading.RLock()
        # 允许几个时间间隔的汇报延时
        self._updatetime_count = 4

    def add_controllee(self, clientid, client_type, client_config={}):
        """
            增加一个新的clientid，说明这个是要启动的，可以是动态控制的
        """
        with self.einfo_guard:
            if self.controllees_config.get(client_type, None) is None:
                logger.ods("%s %s" % ("没有找到这个类别，不能处理", clientid), lv='dev', cat='foundation.controllertookit')
                return None
            if self.get_controllees_count_by_type(client_type) >= self.controllees_config[client_type]['count']:
                logger.ods("%s %s" % ("已经达到该类的最大数量，不能添加", clientid), lv='dev', cat='foundation.controllertookit')
                return None
            # 初始化配置，类型、E端需要的信息
            if not self.controllees.get(clientid):
                self.controllees[clientid] = {'type': client_type, 'clientcfg': client_config}
                # controllee的最后汇报时间，最开始时也应有赋值
                self.controllees[clientid]['starttime'] = now()
                self.controllees[clientid]['updatetime'] = now()
                self.controllees[clientid]['updatetime_count'] = self._updatetime_count
                logger.ods("%s %s" % ("子进程添加成功", clientid), lv='dev', cat='foundation.controllertookit')
            # 已经有了的直接无视
            return clientid

    def add_client(self, app_port, client_type, cfg):
        """
            添加新的被管理的client
            避免不同的type启动时计算出相同的id号
        """
        # return self.add_controllee("%s_%s_%s"%(app_port ,client_type,\
        # self.get_controllees_count_by_type(client_type)+1),\
        # client_type ,cfg)
        return self.add_controllee(uuid.uuid4().hex, client_type, cfg)

    def register_configs(self, cfgs):
        """
            将配置的字典注册到controllee_configs
        """
        for client_type, cfg in cfgs.items():
            self.add_controllee_configs(client_type, cfg)
        return True

    def add_controllee_configs(self, client_type, config={}):
        """
            增加E类型的配置信息
        """
        with self.einfo_guard:
            if self.controllees_config.get(client_type, None):
                # 类别已存在，不能再次添加
                return False
            if config.get('count', None) is None:
                raise RuntimeError("controller启动失败，配置项中缺少必要的参数【count】")
            if config.get('interval', None) is None:
                raise RuntimeError("controller启动失败，配置项中缺少必要的参数【interval】")
            # 初始化配置项，暂时仅有count、interval
            self.controllees_config[client_type] = {"count": config['count'], "interval": config['interval'], "init_config": config}
            # 任务分发使用到的列表
            self.controllees_config[client_type]['message_list'] = []
            return True

    def update_controllees_count_by_type(self, client_type, value):
        """
            调整client_type对应的数量，这个可以动态调整
        """
        with self.einfo_guard:
            if self.controllees_config.get(client_type, None) and isinstance(value, int):
                # 类别不存在，不能处理
                self.controllees_config[client_type]['count'] += value
                return True
            return False

    def append_controllees_message_by_type(self, client_type, value, istop=False):
        """
            向client_type中的message_list中添加消息
        """
        with self.einfo_guard:
            if self.controllees_config.get(client_type, None):
                # 类别不存在，不能处理
                if istop:
                    # 将消息放到top位置
                    self.controllees_config[client_type]['message_list'] = [value] + self.controllees_config[client_type]['message_list']
                else:
                    self.controllees_config[client_type]['message_list'] += [value]
                return True
            return False

    def isnext_closemsg_by_type(self, client_type):
        """
            判断下个消息是不是关闭命令
        """
        with self.einfo_guard:
            if not self.controllees_config.get(client_type, None):
                # 类别不存在，不能处理，相当于关闭命令
                return True
            if len(self.controllees_config[client_type]['message_list']) > 0:
                msg = self.controllees_config[client_type]['message_list'][0]
                if msg[0] == '0' and msg[1] == 0:
                    return True
            return False

    def clear_controllees_message_by_type(self, client_type):
        """
            将client_type中的message_list清空
        """
        with self.einfo_guard:
            if self.controllees_config.get(client_type, None):
                # 类别不存在，不能处理
                self.controllees_config[client_type]['message_list'] = []
                return True
            return False

    def get_controllees_message_by_type(self, client_type):
        """
            通过client_type获得下一个指令信息
            # 一个系统指令，控制是否停止；一个普通的指令，用于任务处理
        """
        with self.einfo_guard:
            if self.controllees_config.get(client_type, None) and len(self.controllees_config[client_type]['message_list']):
                # 类别不存在，不能处理
                result = self.controllees_config[client_type]['message_list'].pop(0)
                return result
            return None

    def get_clientids_by_type(self, client_type):
        """
            通过client_type获得当前已经启动的clientid
        """
        with self.einfo_guard:
            rslst = []
            for clientid, cfg in self.controllees.items():
                if cfg['type'] == client_type:
                    # 排序优先级：汇报次数正常的，启动更早的
                    rslst.append( (cfg["updatetime_count"] ,cfg["starttime"]*-1 ,clientid) )
            return copy.deepcopy( [c for a ,b ,c in sorted(rslst ,reverse=True)] )

    def get_controllees_count_by_type(self, client_type):
        """
            通过client_type获得当前已经要求启动的个数
        """
        return len(self.get_clientids_by_type(client_type))

    def check_controllees_aliving(self):
        """
            确定R的配置信息，保证R可以死亡
            所有的client_type.count应该为0，client_type.message_list是否为[]不重要
        """
        with self.einfo_guard:
            for client_type, cfg in self.controllees_config.items():
                if cfg['count']:
                    return True
            if self.controllees:
                # 当前还有存活的进程
                return True
            return False

    def makesure_controllees_alive(self, controllee_start, controllee_stop, app_port, controllee_max=False):
        """
            检查self.controllees中的每一个，判断updatetime的时间差，如果够大，则重启对应的controllee
            启动controllee不需要做pid登记，启动后的controllee会在汇报信息时将pid上报
            controllee_start:回调函数，启动client进程的方式
            controllee_stop: 回调函数，强制停止client进程的方式
            controllee_all_living：所有的子进程都要达到max值
        """
        with self.einfo_guard:
            # 检查有没有需要停止的，使用list是因为后面要做pop
            for clientid, cfg in list(self.controllees.items()):
                # 先检查是不是超时了，如果超时了，那么应该直接重启、更新时间，没有超时就跳过
                # 固定是interval的四倍时间，还要保证不是自己的type直接关闭
                time_out_interval = self.controllees_config.get(cfg['type'])
                if not time_out_interval:
                    logger.ods("%s %s %s" % ("不存在的client_type移除进程", cfg['type'], clientid), lv='info', cat='foundation.controllertookit')
                    self.del_controllee(clientid)
                elif (now()-cfg['updatetime']) >= time_out_interval["interval"]:
                    # 该汇报的时候没有汇报，延迟次数减一，更新汇报时间
                    cfg['updatetime'] = now()
                    cfg['updatetime_count'] -= 1

                # 将超过延迟次数的被管理进程移除掉
                if 0 >= cfg['updatetime_count']:
                    # 移除进程，不管是新启动的还没有汇报，还是之前汇报过现在超时了，都应该被移除掉
                    logger.ods("%s %s" % ("移除进程", clientid), lv='info', cat='foundation.controllertookit')
                    self.del_controllee(clientid)
                    # 通过pid决定是启动一个新的，还是restart
                    if cfg.get('clientpid'):
                        # 这里应该是杀死指定的进程
                        logger.ods("%s %s" % ("进程超时，需要移除", clientid), lv='info', cat='foundation.controllertookit')
                        # 停止进程
                        try:
                            controllee_stop(cfg["clientpid"], params=cfg.get("clientcfg", {}))
                            logger.ods("进程停止完毕", lv='dev', cat='foundation.controllertookit')
                        except:
                            logger.oes("进程停止出现异常：", lv='error', cat='foundation.controllertookit')

            for client_type, cfg in self.controllees_config.items():
                # 检查任务处理列表，如果还有待处理任务，且同类进程未到达max，启动新的
                # 当前有多少个消息
                msg_count = len(self.controllees_config[client_type]['message_list'])
                # 最大能够起几个
                max_client_count = self.controllees_config[client_type]['count']
                # 活着几个
                aliving_count = self.get_controllees_count_by_type(client_type)

                # 当要求所有子进程都要启动时，在达到30秒后，进行补充
                if controllee_max and (now()-float(env_get("_controller_start", "%0.5f" % now()))) >= 30:
                    msg_count = max_client_count
                # 如果还有消息且没有达到最大，可以启动新的
                t_count = min(max_client_count, msg_count) - aliving_count
                if t_count > 0:
                    logger.ods("被管理类型 %s 将要进行增加进程数[ %s ][ max_cnt %s ,aliving %s ]" % (client_type, t_count ,max_client_count ,aliving_count)
                                    , lv='info', cat='foundation.controllertookit')
                    for i in range(t_count):
                        # 还没有达到最大值，可以继续启动
                        clientid = self.add_client(app_port, client_type, cfg['init_config'])
                        # 启动一个新的进程
                        logger.ods("%s %s" % ("启动一个新的进程", clientid), lv='dev', cat='foundation.controllertookit')
                        # 固定提供这几个参数 子进程编号(父进程不管理非法编号)clientid ,父进程管理端口app_port ,汇报间隔interval, 初始化参数params
                        try:
                            controllee_start(clientid, app_port, cfg["interval"], client_type, cfg['init_config'])
                        except:
                            logger.oes("进程启动出现异常：", lv='error', cat='foundation.controllertookit')
                        # 启动后应该更新一下时间，否则会连续启动多个
                        cfg['updatetime_count'] = self._updatetime_count
                        logger.ods("进程启动完毕", lv='dev', cat='foundation.controllertookit')
            return True

    def update(self, in_frame):
        """
            in_frame为报文格式为class的实例
            clientid、clientpid是为了保证框架运行的
        """
        with self.einfo_guard:
            clientid = in_frame.clientid
            if self.controllees.get(clientid):
                self.controllees[clientid]['updatetime'] = now()
                self.controllees[clientid]['updatetime_count'] = self._updatetime_count
                self.controllees[clientid].update({'clientpid': in_frame.clientpid})
                return True
            else:
                # 需要判断是不是自己管理的类型，在是的情况下，如果没有达到最大个数，添加clientid
                client_type = in_frame.client_type
                clientid = self.add_controllee(clientid, client_type, self.get_controllees_config_by_client_type(client_type))
                if clientid:
                    # 增加成功
                    self.controllees[clientid].update({'clientpid': in_frame.clientpid})
                # 不在管理范围内且增加失败，不处理
                return None

    def get_controllee_info(self, clientid):
        """
            返回一个client的信息
        """
        return self.controllees.get(clientid, None)

    def get_controllees_config_by_client_type(self, client_type):
        """
            返回一个client_type的信息
        """
        return self.controllees_config.get(client_type, None)

    def get_controllees(self):
        """
            返回当前维护的所有的client信息
        """
        return self.controllees

    def get_controllees_config(self):
        """
            返回当前维护的所有的client_type信息
        """
        return copy.deepcopy(self.controllees_config)

    def del_controllee(self, clientid):
        """
            不在维护指定的clientid
        """
        with self.einfo_guard:
            if self.controllees.get(clientid):
                self.controllees.pop(clientid)
            return True

    def del_controllees_config(self, client_type):
        """
            不在维护指定的client_type
        """
        with self.einfo_guard:
            if self.controllees_config.get(client_type):
                self.close_client_type(client_type)
                self.controllees_config.pop(client_type)
            return True

    def add_msg_for_e(self, client_type, value, increase=False, max_e_num=20):
        """
            为E增加一个普通任务 (clientid,clientpid)==('99',99)
            increase==True：有msg留存，就增加一个新的E，client_type到最大值是同msg数量一致的
        """
        self.append_controllees_message_by_type(client_type, ('99', 99, value, None))
        if client_type:
            with self.einfo_guard:
                # 当前有多少个消息
                msg_count = len(self.controllees_config[client_type]['message_list'])
                # 最大能够起几个
                max_client_count = self.controllees_config[client_type]['count']
                # 活着几个
                aliving_count = self.get_controllees_count_by_type(client_type)
                new_max = max([msg_count, max_client_count, aliving_count])
                new_max = min([max_e_num, new_max])
                self.controllees_config[client_type]['count'] = new_max
                logger.ods('进程max数量调整 %s --> %s %s' % (max_client_count, new_max, client_type), lv='info', cat='foundation.controllertookit')

    def add_closemsg_for_e(self, client_type, value):
        """
            为E增加一个停止任务 (clientid,clientpid)==('0',0)
        """
        self.append_controllees_message_by_type(client_type, ('0', 0, None, value), istop=True)

    def reduce_controllee_by_type(self, client_type, count=1):
        """
            减少某类type的client数量，一次减少count个，这是从最大数量上往下减少
        """
        with self.einfo_guard:
            if self.controllees_config.get(client_type, None) is None:
                return False

            # 减少的数量不能够超过当前type的最大数量
            count = min(self.controllees_config[client_type]['count'], count)
            # 减少最大值
            self.update_controllees_count_by_type(client_type, -1*count)
            # 比较最大值和client列表，如果列表超过最大值，则应该从列表中移除多余的
            # 使用修改后的值来做比较
            clientids = self.get_clientids_by_type(client_type)
            tt_count = self.controllees_config[client_type]['count'] - len(clientids)
            if 0 > tt_count:
                # 超出max值了，需要减少，多几个就减少几个
                for clientid in clientids[tt_count:]:
                    self.del_controllee(clientid)
            return True

    def close_client_type(self, client_type):
        """
            停止某个type的所有子进程
            停止R，先要停止E
        """
        with self.einfo_guard:
            if self.controllees_config.get(client_type, None) is None:
                return False
            # 清空此类的任务命令
            self.clear_controllees_message_by_type(client_type)
            # 给子进程发停止命令
            aliving_count = self.get_controllees_count_by_type(client_type)
            self.update_controllees_count_by_type(client_type, aliving_count-self.controllees_config[client_type]['count'])
            # 这些是活着的进程，还有可能启动的数量不够max值
            for i in range(aliving_count):
                self.add_closemsg_for_e(client_type, "管理进程收到停止命令")
                self.update_controllees_count_by_type(client_type, -1)
            return True

    def close_all_type(self):
        """
            停止管理的所有子进程
        """
        for client_type in list(self.controllees_config.keys()):
            self.close_client_type(client_type)
        return True

    def upload_jcpzxx(self, jcpzxx_dic):
        """
            进行进程信息配置的管理，是组合完成的，相当于简化操作
        """
        try:
            ctrl_typeinfo_dic = self.get_controllees_config()
            for key, value in jcpzxx_dic.items():
                ctrl_typeinfo_value = ctrl_typeinfo_dic.get( key, '')
                # 先判断进程类型的配置信息是否需要调整
                if not ctrl_typeinfo_value:
                    logger.ods( '增加进程类型：%s %s' % (key, str(value)), lv='info', cat='foundation.controllertookit')
                    # 仅增加类型，不增加任务
                    self.add_controllee_configs(key, config=value)
                else:
                    # 进程类型存在，检查数量是否要更新
                    ctrl_cnt = ctrl_typeinfo_value.get('count', 0)
                    db_cnt = int(value.get('count', 0))
                    # 判断数据库的数量和配置数量是否一致
                    upd_num = db_cnt - ctrl_cnt
                    # 更新进程启动数量
                    if upd_num > 0:
                        logger.ods('进程max数量增加 %s --> %s %s' % (ctrl_cnt, db_cnt, key), lv='info', cat='foundation.controllertookit')
                        self.update_controllees_count_by_type( key, upd_num)
                    elif 0 > upd_num:
                        logger.ods('进程max数量减少 %s --> %s %s' % (ctrl_cnt, db_cnt, key), lv='info', cat='foundation.controllertookit')
                        self.reduce_controllee_by_type(key, count=abs(upd_num))
                    else:
                        logger.ods( '进程max数量不需要调整 %s --> %s %s' % (ctrl_cnt, db_cnt, key), lv='dev', cat='foundation.controllertookit')
            # 从管理的类型列表中移除db中不存在的类别
            remove_type = list(set(ctrl_typeinfo_dic.keys())-set(jcpzxx_dic.keys()))
            for key in remove_type:
                logger.ods( '移除进程类型：%s' % key, lv='info', cat='foundation.controllertookit')
                self.del_controllees_config(key)
            logger.ods( "本次进程管理处理完成", lv='dev', cat='foundation.controllertookit')
            return True
        except:
            return False
