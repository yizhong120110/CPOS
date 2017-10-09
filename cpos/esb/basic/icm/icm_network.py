# -*- coding: utf-8 -*-
import cpos.esb.basic.icm.icm_spec as icm_spec
from cpos.foundation.tcp.servers import SelectServer
from cpos.foundation.tcp.clients import SelectClient
from multiprocessing import Pool
from cpos.foundation.tpool.tpool import AutoScaledPool
from cpos.esb.basic.application.app_rpclog import env_get
from cpos.esb.basic.config import settings
from cpos.esb.basic.resource.logger import *
icm_ip = settings.ICM_IP
icm_port = settings.ICM_PORT
icm_thread_pool_size_start = settings.ICM_THREAD_POOL_SIZE_START
icm_thread_pool_size_ceiling = settings.ICM_THREAD_POOL_SIZE_CEILING
icm_thread_max_queued_task = settings.ICM_THREAD_MAX_QUEUED_TASK


def icm_thread_request (parameter):
    #icm_request_accept(parameter)
    peer = parameter['peer']
    frame = parameter['frame']

    sync = True
    if frame.frame_type == 0x05:
        # TP处理完成第一步后，不需要等待第二步的返回值
        sync = False
    ack_frame = parameter['cb'](frame,sync)
    if peer == None:
        return

    ack_frame.sequance = frame.sequance
    ack_frame.frame_type = 0x02

    logger.ods('ICM -> ICPs %s'%(str(ack_frame),),lv='dev',cat='basic.icm.icm_network' )

    try:
        peer.push_outbound(ack_frame)
        peer.shutdown()
    except:
        logger.ods('ignore error on sending back msg. 2' ,lv='info',cat='basic.icm.icm_network' )


def icm_request_accept(parameter):
    peer = parameter['peer']
    frame = parameter['frame']

    commnode_id,message_body = icm_spec.icm_decode_frame_payload(frame.payload)
    ack_frame = icm_spec.build_icm_frame(commnode_id,b'Requests accepted.')
    ack_frame.sequance = frame.sequance
    ack_frame.frame_type = 0x03
    logger.ods('ICM(ACCEPTED) -> ICPs %s'%(str(ack_frame),),lv='dev',cat='basic.icm.icm_network' )
    try:
        peer.push_outbound(ack_frame)
    except:
        logger.ods('ignore error on sending back msg. 3' ,lv='warning',cat='basic.icm.icm_network' )



def icm_request_refuse(parameter):
    peer = parameter['peer']
    frame = parameter['frame']

    commnode_id,message_body = icm_spec.icm_decode_frame_payload(frame.payload)
    ack_frame = icm_spec.build_icm_frame(commnode_id ,b'ICM Internal Error, too many requests, please retry later.')
    ack_frame.sequance = frame.sequance
    ack_frame.frame_type = 0x04
    logger.ods('ICM(REFUSED) -> ICPs %s'%(str(ack_frame),),lv='dev',cat='basic.icm.icm_network' )
    try:
        peer.push_outbound(ack_frame)
    except:
        logger.ods('ignore error on sending back msg. 4' ,lv='info',cat='basic.icm.icm_network' )
    #peer.shutdown()

def start_tcp_icm_server (cb, icmip=icm_ip, icmport=icm_port, \
        icm_pool_start=icm_thread_pool_size_start, icm_pool_ceiling=icm_thread_pool_size_ceiling, \
        icm_queued_task=icm_thread_max_queued_task):
    ap = AutoScaledPool(icm_pool_start,icm_pool_ceiling,icm_thread_request)
    #server = SelectServer(host=icm_ip, port=icm_port,frame_decoder = icm_spec.icm_decode_frame)
    #ap = AutoScaledPool(10,20,icm_thread_request)

    errcount = 0
    server = None
    while True:
        try:
            # 在try中再次创建server，是为了避免server出错后，导致icm进程重启，带来1分钟的无法提供服务
            server = SelectServer(host=icmip, port=icmport,frame_decoder = icm_spec.icm_decode_frame)
            while env_get('keep_running',True):
                in_frame_with_peer = server.pop_inbound_clear()
                if in_frame_with_peer is not None:
                    if ap.get_queued_task_count() > (icm_queued_task):
                        icm_request_refuse({'peer':SelectClient(peer=in_frame_with_peer['peer']) ,
                            'frame':in_frame_with_peer['frame']})
                    else:
                        icm_request_accept({'peer':SelectClient(peer=in_frame_with_peer['peer']) ,
                            'frame':in_frame_with_peer['frame']})

                        logger.ods('icm server before add_task' ,lv='dev',cat='basic.icm.icm_network' )
                        ap.add_task({'cb':cb,'peer':SelectClient(peer=in_frame_with_peer['peer']) ,
                            'frame':in_frame_with_peer['frame']})

                        #icm_request_accept({'server':server ,'in_frame_with_peer':in_frame_with_peer})
                        #server.close_peer(in_frame_with_peer['peer'])
                    logger.ods('accepted queued_task_count:(%s)'%(ap.get_queued_task_count()) ,lv='dev',cat='basic.icm.icm_network' )
                    errcount = 0
            break
        except Exception as e:
            errcount += 1
            logger.oes ("ICM accept failed, retry.[%s]"%(errcount) ,lv='error',cat = 'basic.icm.icm_network')
            if errcount > 5:
                errmsg = "ICM except count is %s, not try again."%(errcount)
                logger.ods (errmsg ,lv='info',cat = 'basic.icm.icm_network')
                raise RuntimeError(errmsg)
        finally:
            if server:
                server.shutdown()

def send_to_icm(commnode_id,msgbuff ,noreply=False ,frame_type=0x01, icmip=icm_ip, icmport=icm_port):
    """
        提供给icp，用于向icm发送消息
        return None : 服务器端未处理.
        非None,服务器端已接受(或已处理完成)
    """
    if not isinstance(msgbuff ,bytes):
        logger.ods('发送的报文【%s】必须是bytes类型'%str(msgbuff) ,lv='warning',cat='basic.icm.icm_network' )
        raise RuntimeError("发送的报文【msgbuff】必须是bytes类型")
    
    client = SelectClient(host=icmip, port=icmport,frame_decoder = icm_spec.icm_decode_frame)
    # 这是发送报文
    client.push_outbound( icm_spec.build_icm_frame( commnode_id,msgbuff ,frame_type=frame_type) )

    cnt = 0
    try:
        while True:
            in_frame = client.pop_inbound()
            if in_frame:
                cnt += 1
                logger.ods('in_frame count [%s]'%(cnt), lv='dev',cat='basic.icm.icm_network' )
                commnode_id,message_body = icm_spec.icm_decode_frame_payload(in_frame.payload)
                if in_frame.frame_type == 0x02:
                    logger.ods('Received [message_body].', lv='dev',cat='basic.icm.icm_network' )
                    return message_body

                if in_frame.frame_type == 0x03:
                    accepted = True
                    logger.ods('Received [ACCEPTED].' + str(message_body), lv='dev',cat='basic.icm.icm_network' )
                    if noreply:
                        return 'NOREPLY'
                    else:
                        continue

                if in_frame.frame_type == 0x04:
                    logger.ods('Received [REFUSED].' + str(message_body), lv='info',cat='basic.icm.icm_network' )
                    return None

                logger.ods('Received unsupported data frame.' + str(message_body), lv='dev',cat='basic.icm.icm_network' )
    finally:
        client.shutdown()


def send_to_icm_reply(commnode_id,msgbuff, icmip=icm_ip, icmport=icm_port):
    """
        提供给icp，用于向icm发送消息，有返回值
    """
    return send_to_icm(commnode_id,msgbuff, icmip=icmip, icmport=icmport)


def send_to_icm_noreply(commnode_id,msgbuff ,trycnt=5):
    """
        提供给icp，用于向icm发送消息，无返回值
        出错了，应该尝试几次，如果还是失败，只能抛异常
    """
    while trycnt>0:
        try:
            return send_to_icm(commnode_id,msgbuff ,noreply=True)
        except:
            trycnt -= 1
            if trycnt <= 0:
                raise


def send_to_icm_noreply_2(commnode_id,msgbuff):
    """
        提供给icp，用于向icm发送消息，无返回值
        这种方式保证一定先处理TP的01，然后不等待02的返回值
        这个对于TP的数量有依赖，没有空闲的TP，会导致01也收不到
    """
    return send_to_icm(commnode_id,msgbuff ,frame_type=0x05)


if __name__ == '__main__':
    import time
    msg = 0
    def _test_cb (frame,sync = True):
        print ('f-----------------')
        time.sleep(5)
        return frame
        
    start_tcp_icm_server(_test_cb)
