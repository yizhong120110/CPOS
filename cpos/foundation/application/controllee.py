# -*- coding: utf-8 -*-
"""
    一个E每次仅处理一个任务
    在keep_running为True的情况下，会一直汇报
    cmd_processing_thread_keep_running为True时，任务处理线程一直执行
    工作进程的超时时间应该在E中自行控制
"""
from optparse import OptionParser
import copy
import os
import time
import queue
import random

from .framework import *
from .env import *
from .controllertookit import now
from . import controller_spec as frame_spec
from ..tcp.clients import SelectClient
from ..substrate.utils.logger import logger


class ControlleeApp(Application):

    def __init__(self, client_type, clientid, server_port, interval_time, max_waittime=600,
                 working_callback=None, app_host='127.0.0.1', startwork=False):
        Application.__init__(self)
        # client_type ,clientid, server_port, interval_time 这些应该是必输项
        # app_host 一般不会跨服务器
        self.client_data = {}
        self.client_data['client_type'] = client_type
        self.client_data['clientid'] = clientid
        self.client_data['app_host'] = app_host
        self.client_data['server_port'] = server_port
        self.client_data['interval_time'] = interval_time
        # 在没有任务后，继续等待多久，单位秒
        self.client_data['max_waittime'] = max_waittime
        # 工作线程的处理逻辑
        if working_callback:
            self.working_callback = working_callback
        # 可以控制这个参数，确定是否一直运行
        self.keep_running = True
        # 初始化env中的汇报时间值
        sleep_time = ( (os.getpid()%10*0.1)**2 * random.randint(1,9) * 0.1 + random.random() ) * interval_time*0.5
#        env_set('upd_time', now() - interval_time * random.randint(1,9) * 0.1 )
        env_set('upd_time', now() - sleep_time )
        self.eQueue = queue.Queue(1)
        # 需要在启动之初就开始工作，不通过父进程来分发任务
        if startwork == True:
            self.start_work("start")

    def generate_controllee_info(self, msg=''):
        # msg 要汇报的信息， 默认空
        # 是否在等待任务，默认为1，当收到任务后，变为0
        iswait = 1 if env_get('keep_waiting', 'yes') == 'yes' else 0
        message = frame_spec.bfm( self.client_data['client_type'], self.client_data['clientid'], os.getpid(), iswait, msg)
        logger.ods("将要发生到管理进程的内容为"+str(message), lv='dev', cat='foundation.controllee')
        return message

    def reporting_thread(self):
        logger.ods("%s" % ('E-reporting_thread汇报线程启动'), lv='info', cat='foundation.controllee')
        # 这里应该还有其他的条件  todo
        # 收到停止命令后，应该先停止汇报线程，在处理的任务应该执行完成后再完全停止进程
        while self.keep_running:
            # 自动停止控制进程，当长时间没有R端控制时停止该进程
            time_now = now()
            # 这一部分没有作为单独的线程存在，是因为sleep时不能够收到停止命令，直接停止线程
            if env_get('keep_waiting', 'yes') == 'yes' and (time_now - env_get('work_stoptime', time_now)) >= self.client_data['max_waittime']:
                logger.ods("%s" % ('管理进程长时间没有发送指令，reporting_thread 线程自动停止'), lv='info', cat='foundation.controllee')
                self.stopping()

            ttt = time_now - env_get('upd_time', time_now)

            if ttt >= self.client_data['interval_time']:
                logger.ods("尝试连接tcp", lv='dev', cat='foundation.controllee')

                self.controllee_client = None
                try:
                    logger.ods("向管理进程进行常规汇报", lv='dev', cat='foundation.controllee')
                    self.controllee_client = SelectClient( self.client_data['app_host'], self.client_data['server_port'],
                                                           frame_decoder=frame_spec.decode_frame)

                    self.controllee_client.push_outbound(self.generate_controllee_info())

                    in_frame = self.controllee_client.pop_inbound()
                    while not in_frame:
                        # 这个是client段必须的，测试中验证了
                        # #######################################################
                        # 这段代码放开后会导致server端在do_select_comm时丢失发消息的对象，出现异常
                        # 1秒或者更短的时间内没有完成汇报，退出
                        if (now() - time_now) >= min(self.client_data['interval_time'] ,1):
                            # 如果接收报文的时间超过一个时间间隔，退出
                            break
                        # #######################################################
                        # No need to log this situation, its normal, and happends alot.
                        #logger.ods ("[%s]%s"%(self.client_data['clientid'],'in_frame为none，继续接收') ,lv='dev',cat = 'foundation.controllee')
                        in_frame = self.controllee_client.pop_inbound()
                    # 这里是真正做传输的内容域

                    if not in_frame:
                        logger.ods("Controlle timeout while waiting for response from controller, Ignored.",
                                   lv='warning', cat='foundation.controllee')
#                        # 可能是同级子进程过多，导致管理进程不能处理汇报信息，按汇报间隔睡眠一段时间
#                        time.sleep( random.randint(1, int(self.client_data['interval_time']*0.5)))
##                        sleep_time = ( (os.getpid()%10*0.1)**2 * random.randint(1,9) * 0.1 + random.random() ) * self.client_data['interval_time']*0.5
##                        logger.ods("sleep_time: %s"%(sleep_time),
##                                   lv='dev', cat='foundation.controllee')
##                        time.sleep(sleep_time)
##                        # 修改后可以立即进行一次汇报
##                        time_now = time_now - self.client_data['interval_time']
                        continue

                    in_frame = frame_spec.decode_frame_message(in_frame.message)
                    logger.ods("%s %s" % ('接收到的反馈信息 ：', in_frame), lv='dev', cat='foundation.controllee')

                    # 判断收到信息中若是clientid 和pid都是0，表示异常，停止进程
                    # 没有任务 (clientid,clientpid)==('1',1)
                    # 停止任务 (clientid,clientpid)==('0',0)
                    # 普通任务 (clientid,clientpid)==('99',99)
                    if (in_frame.clientid, in_frame.clientpid) == ('0', 0):
                        # 停掉此进程
                        logger.ods("[%s]%s" % (self.client_data['clientid'], '管理进程发出关闭命令'), lv='info', cat='foundation.controllee')
                        # 这是准备停止的标志
                        self.stopping()
                    elif (in_frame.clientid, in_frame.clientpid) == ('1', 1):
                        # 没有获得新任务，可能是当前进程中有任务没有处理完成，也有可能是因为没有任务了
                        logger.ods("[%s]%s" % (self.client_data['clientid'], '管理进程没有发出新指令'), lv='dev', cat='foundation.controllee')
                    elif (in_frame.clientid, in_frame.clientpid) == ('99', 99):
                        # 获得新任务
                        logger.ods("[%s]%s %s" % (self.client_data['clientid'], '管理进程发出新指令', str(in_frame.msgload)), lv='info', cat='foundation.controllee')
                        # 开始工作
                        self.start_work(in_frame.msgload)
                    logger.ods("本次常规汇报正常结束", lv='dev', cat='foundation.controllee')
                except:
                    # 一般连接不上的错误是可以忽略的，只在dev模式下输出
                    logger.oes("常规汇报中出现异常", lv='dev', cat='foundation.controllee')
                finally:
                    logger.ods("更新汇报时间", lv='dev', cat='foundation.controllee')
                    # 汇报时间
                    env_set('upd_time', time_now)

                    # 信息汇报接收完毕后，关闭tcp连接
                    if self.controllee_client:
                        self.controllee_client.shutdown()
                    logger.ods("%s" % ('已关闭tcp连接'), lv='dev', cat='foundation.controllee')

                    # 每次汇报间隔达到时，就处理一下缓存的日志，将其保存到本地，目的是为了能够及时的做缓存日志的转移
                    # 直接使用logger的对象都有root_has_pid，对于tlog，不需要做这样的处理
                    logger.flush_fbdic()
            else:
                # 等待一个汇报间隔
                time.sleep(ttt)
        logger.ods("[%s]汇报线程停止完毕" % (self.client_data['clientid']), lv='info', cat='foundation.controllee')
        return True

    def cmd_processing_thread(self):
        # 业务处理线程
        logger.ods("业务处理线程cmd_processing_thread启动", lv='info', cat='foundation.controllee')
        # 将业务参数传递过去 ， rdcs 的参数在数据结构中
        while env_get("cmd_processing_thread_keep_running", True):
            # 启动后，应该处理任务，也可能没有任务可以处理
            msgload = self.eQueue.get()
            logger.ods("cmd_processing_thread 收到一个任务，进行处理", lv='info', cat='foundation.controllee')
            if msgload:
                rs = False
                while rs != True:
                    try:
                        logger.ods("working_callback 启动", lv='info', cat='foundation.controllee')
                        rs = self.working_callback(msgload)
                        logger.ods("working_callback 工作结束", lv='info', cat='foundation.controllee')
                    except:
                        logger.oes("working_callback 处理出现异常：", lv='error', cat='foundation.controllee')
                # 工作结束，登记一下时间
                self.job_done()
        logger.ods("%s: port[ %s ]" % ('业务处理线程停止', self.client_data['server_port']), lv='info', cat='foundation.controllee')
        return True

    def on_start(self):
        Application.on_start(self)
        # 汇报线程
        self.register_thread('reporting_thread', self.reporting_thread)
        # 工作线程
        self.register_thread('cmd_processing_thread', self.cmd_processing_thread)

    def stopping(self):
        """
            停止命令来自R端，停止完成有些准备时间
        """
        env_set('cmd_processing_thread_keep_running', False)
        self.keep_running = False
        # 这个是为了提供给其他附加的线程使用的
        env_set('keep_running', False)
        # 在工作线程内，eQueue中获得不到消息时会阻塞线程，这里需要解除阻塞
        if self.eQueue.empty():
            self.eQueue.put('')
        logger.ods('stopping处理结束', lv='info', cat='foundation.controllee')

    def start_work(self, msgload):
        """
            开工啦
        """
        env_set('keep_waiting', 'no')
        self.eQueue.put(msgload)

    def job_done(self):
        """
            干完活了
        """
        env_set('keep_waiting', 'yes')
        env_set('work_stoptime', now())

    def working_callback(self, msgload):
        """
            回调函数
            输入是client端汇报信息后收到的反馈内容
            需要对这些内容是什么样的逻辑处理
        """
        return True


def get_shell_args():
    """
        获得程序启动使用到的参数
    """
    usage = "usage: %prog  -p AppPort  -T ClientType  -i ClientId  -t Interval [-w WaitTime]"
    parser = OptionParser(usage)
    # add_option可以支持的选项在class Option中定义
    parser.add_option("-p", "--port", dest="app_port", help="管理进程的TCP服务端口", metavar="AppPort", type='int')
    parser.add_option("-T", "--type", dest="client_type", help="管理进程认可的子进程合法类型", metavar="ClientType")
    parser.add_option("-i", "--id", dest="clientid", help="管理进程认可的子进程合法编号", metavar="ClientId")
    parser.add_option("-t", "--time", dest="interval", help="子进程的汇报间隔(秒)", metavar="Interval", type='int')
    parser.add_option("-w", "--waittime", dest="max_waittime", default=600, help="子进程无任务时的存活时间(秒)", metavar="WaitTime", type='int')
    parser.add_option("-s", "--serport", dest="ser_port" ,default=0, help="进程作为server时使用的端口", metavar="IcmPort" ,type='int')
    parser.add_option("-I", "--serip", dest="ser_ip" ,default='', help="进程作为server时使用的IP地址", metavar="ICMIP")
    parser.add_option("-c", "--callback", dest="callback" ,default='service', help="进程作为server时使用的回调函数名", metavar="CallBack")
    parser.add_option("-P", "--protocol", dest="protocol" ,default='', help="RMQ通道关键字", metavar="Protocol")

    (options, args) = parser.parse_args()
    if options.app_port is None or options.client_type is None or options.clientid is None or options.interval is None:
        parser.error("type、port、id、time参数必填")
    options.client_type = options.client_type.strip()
    options.clientid = options.clientid.strip()
    options.ser_ip = options.ser_ip.strip()
    options.callback = options.callback.strip()
    options.protocol = options.protocol.strip()
    return copy.deepcopy(options.__dict__), copy.deepcopy(args)
