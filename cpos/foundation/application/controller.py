# -*- coding: utf-8 -*-
"""
    进程管理server端
    启动时会指定要启动几个controllee，同时生成一个信息维护列表，该列表用于登记每个controllee的汇报信息
    在初次启动时，可能存在两种情况，1、有controllee已经启动了需要接管；2、没有任何的controllee需要被接管
        针对这两种情况，controller启动后需要空转一段时间，以便controllee能够汇报信息，接受管理
        这个空转，实际上也是适合于正常运转时的汇报间歇，在空转的同时维护controllee信息列表，控制超时时间
    controllee和controller的信息交互采用"同步等待"，数据包是对等交互的
        当controllee向controller发送汇报信息时，同时获得一个返回信息，可以是空结构，也可以是指令结构
        controller不能够主动的将消息推送到controllee，必须等待controllee主动获取消息
    controller在启动后，应该立即提供一个port，作为TCP的连接server，用于接收controllee的汇报信息
        利用controllee汇报的信息来更新自己内部维护的信息列表
        controllee汇报信息时应该有一个唯一标识id，用于在controller的信息列表中标识自己
        同时，该id应该是可以被重启后的controller获得的，以便于controller能够重新接管之前的controllee
    存在一种情况，E汇报给R的clientid没有被R初始化，说明不是R应该默认管理的，对于这种情况，直接返回clientid='0'，clientpid=0
        然后由E接收后自己stop自己
    任务管理是按type来处理的，限制了每个type的最大个数；当type不存在时，加入的指令没有用
"""
from .framework import Application
from .controllertookit import ControllerTookit
from . import controller_spec as frame_spec
from ..tcp.servers import SelectServer
from ..substrate.utils.logger import logger
from ..substrate.utils.functools import kill_process


class ControllerApp(Application):

    def __init__(self, app_port, controllee_start=None, controllee_stop=None,
                 controllee_change_callback=None, controller_idle_callback=None, app_host='127.0.0.1', controllee_max=False):
        Application.__init__(self)
        self.controller_server = SelectServer(host=app_host, port=app_port, frame_decoder=frame_spec.decode_frame)
        self.app_port = app_port
        # 初始化工具类
        self.ctk = ControllerTookit()
        # 可以控制这个参数，确定是否一直运行
        self.keep_running = True
        # 子进程是否启动达到max值
        self.controllee_max = controllee_max

        # 如果有指定controllee_start和controllee_stop，就使用新的
        if controllee_start:
            self.controllee_start = controllee_start
        # E的重启-停止部分
        if controllee_stop:
            self.controllee_stop = controllee_stop
        else:
            self.controllee_stop = kill_process
        # 收到E的汇报信息时要做的处理
        if controllee_change_callback:
            self.controllee_change_callback = controllee_change_callback
        # 没有收到E的汇报信息时要做的处理
        if controller_idle_callback:
            self.controller_idle_callback = controller_idle_callback

    def controller_thread(self):
        # 除了明确的接收到停止命令，还要保证ctk自检通过，才能停止本进程
        while self.keep_running or self.ctk.check_controllees_aliving():
            try:
                # 这样处理的目的是，防止client端主动放弃连接，导致do_select_comm错误
                in_frame_with_peer = self.controller_server.pop_inbound()
            except:
                in_frame_with_peer = None
            if in_frame_with_peer is not None:
                logger.ods("线程controller_thread收到子进程的汇报，进行处理", lv='dev', cat='foundation.controller')
                in_frame = frame_spec.decode_frame_message(in_frame_with_peer['frame'].message)
                logger.ods("收到的汇报内容为："+str(in_frame), lv='dev', cat='foundation.controller')

                # 当前任务没有处理完成，接着处理
                rstuple = (in_frame.client_type, in_frame.clientid, in_frame.clientpid, in_frame.iswait, None, None)

                # 收到信息就应该登记汇报时间，如果处理结果为None，则说明不是自己的client
                updaters = self.ctk.update( in_frame)
                e = self.ctk.get_controllee_info( in_frame.clientid)
                if updaters is None:
                    # 不是自己的client，直接停止
                    sendrs, isself = self.get_message_for_controllee(e)
                    rstuple = (in_frame.client_type, sendrs[0], sendrs[1], in_frame.iswait, sendrs[2], sendrs[3])
                # 是自己的client，要做一下工作状态的区分
                # client的任务已经处理完成，可以接受新的任务
                # 如果不是在等待任务的状态，也应该判断下一个是不是停止命令，如果是，也应该将任务下发，否则，常驻型的E将不能被停止
                elif in_frame.iswait == 1 or self.ctk.isnext_closemsg_by_type(e['type']):
                    sendrs, isself = self.get_message_for_controllee(e)
                    # 反馈处理应该提供一个id，然后根据id获得后续的处理
                    try:
                        logger.ods("controllee_change_callback 进行处理", lv='dev', cat='foundation.controller')
                        self.controllee_change_callback( in_frame.msgload, self.ctk, e['type'])
                    except:
                        logger.oes("controllee_change_callback 处理出现异常：", lv='error', cat='foundation.controller')

                    # 收到信息就应该有反馈
                    rstuple = (in_frame.client_type, sendrs[0], sendrs[1], in_frame.iswait, sendrs[2], sendrs[3])
                # 最后剩余一种，自己的client、正在工作、没有收到关闭命令的情况

                try:
                    logger.ods("将要返回给被管理子进程的内容为："+str(in_frame_with_peer['peer']), lv='dev', cat='foundation.controller')
                    self.controller_server.push_outbound(in_frame_with_peer['peer'], frame_spec.bfm( *rstuple))
                except:
                    logger.oes("消息返回出现异常：", lv='error', cat='foundation.controller')
            else:
                if self.keep_running:
                    kr = True
                    try:
                        result, kr = self.controller_idle_callback(self.ctk)
                    except:
                        logger.oes("controller_idle_callback 处理出现异常：", lv='error', cat='foundation.controller')
                    if kr == False:
                        logger.ods("回调函数处理结果要求停止本进程", lv='info', cat='foundation.controller')
                        self.stopping()
                self.ctk.makesure_controllees_alive(self.controllee_start, self.controllee_stop, self.app_port, self.controllee_max)
        self.controller_thread_stopped()
        return True

    def on_start(self):
        Application.on_start(self)
        self.register_thread('controller_thread', self.controller_thread)

    def controller_thread_stopped(self):
        """
            进程停止完成，做信息输出
        """
        logger.ods("%s port[ %s ]" % ("管理线程controller_thread停止完毕", self.app_port), lv='info', cat='foundation.controller')

    def stopping(self):
        """
            R端的停止，需要先停E端，停止是一个过程性操作
        """
        logger.ods('stopping处理开始', lv='info', cat='foundation.controller')
        self.ctk.close_all_type()
        self.keep_running = False
        logger.ods('stopping处理结束', lv='info', cat='foundation.controller')

    def controllee_change_callback(self, msgload, ctk, client_type):
        """
            回调函数
            输入是client端发送的str
            输出是server端处理后的str结果
        """
        return None

    def controller_idle_callback(self, ctk):
        """
            回调函数，可能会有一些server给client发消息的逻辑处理
            这里的第二个返回值决定了进程是否继续运行
        """
        return None, True

    def controllee_start(self, clientid, app_port, interval, client_type, params={}):
        """
            这是个回调函数，如果没有提供的话，则使用这个
        """
        pass

    def get_message_for_controllee(self, e):
        """
            为某个E获得返回值信息
            非正常的client (clientid,clientpid)==('0',0)
            没有任务 (clientid,clientpid)==('1',1)
            停止任务 (clientid,clientpid)==('0',0)
            普通任务 (clientid,clientpid)==('99',99)
        """
        # 如果e的返回值是None，则说明不是自己的client
        if e:
            msg = self.ctk.get_controllees_message_by_type(e['type'])
            if msg is None:
                # 没有任务了
                return ('1', 1, None, None), True
            # 有任务可以处理
            return msg, True
        else:
            # 不是正常的client时，直接返回0,0，让其停止
            return ('0', 0, "clientid is wrong", None), False
