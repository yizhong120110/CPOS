# -*- coding: utf-8 -*-
import cpos.esb.basic.rpc.rpc_transaction as rtrans
from cpos.esb.basic.busimodel.transutils import get_txser_timeout
import time


def do_tp_proc (phase,service_dict ,sync ,logger, p_type=''):
    """
        向TP发送任务处理请求的，这里会控制超时
    """
    # 不是交易超时导致的失败，是其他的问题导致失败了
    rs_msg = b"Timeout@Transaction04"
    try:
        pdic = {}
        logger.ods ("phase：%s  service_dict：%s" %(phase,str(service_dict)) ,lv='dev',cat = 'app.icm')
        if phase == '01':
            # 交易创建时间，用于登记lsz以及判断交易超时
            service_dict['SYS_CTIME'] = "%.05f"%time.time()
            # RMQ上的超时时间，主要是为了TP的01可以有超时
            service_dict['SYS_RPC_CSSJ'] = "%s"%( get_txser_timeout(service_dict['SYS_TXJBID']) or rtrans.wqs_transaction_timeout)
            pdic["timeout_interval"] = int(service_dict['SYS_RPC_CSSJ'])

            # 01使用单独的tp进行处理
            pdic["protocol"] = p_type.lower()

            service_dict = rtrans.send_trans_with_protocol(service_dict ,**pdic)
            if service_dict is None:
                rs_msg = b'Timeout@Transaction00'
            else:
                rs_msg = do_tp_proc(service_dict['SYS_CLBZ'], service_dict ,sync ,logger)

        elif phase == '02':
            timeout_interval = int(service_dict['SYS_CSSJ'])
            # 关于超时时间的控制，需要包含01的用时
            latency_time = timeout_interval - (time.time() - float(service_dict.get("SYS_CTIME",time.time())))
            # 可能存在一种情况，01处理就已经超时了
            # tp中增加了超时处理，直接返回会导致出现“预计流水”的状态不能更新
            if latency_time > 0:
                # 没有超时，还需要继续正常处理，超时的时候，仅需要进行jy_ls的更新
                pdic["timeout_interval"] = latency_time
                service_dict['SYS_RPC_CSSJ'] = "%s"%(latency_time)

            pdic["protocol"] = service_dict.get("SYS_TRANS_TIME_TYPE", "").lower()

            if sync == False:
                pdic["reply"] = "no"
                service_dict = rtrans.send_trans_with_protocol(service_dict ,**pdic)
                rs_msg = b'Accepted@Transaction02'
            else:
                service_dict = rtrans.send_trans_with_protocol(service_dict ,**pdic)
                if service_dict is None:
                    # 执行超时了
                    rs_msg = b'Timeout@Transaction02'
                else:
                    rs_msg = do_tp_proc(service_dict['SYS_CLBZ'], service_dict ,sync ,logger)

        elif phase == '03':
            # 将SYS_YFSDBW发送回去
            message_body = service_dict.get("SYS_YFSDBW",bytes([]))
            if isinstance(message_body ,bytes):
                # 可能存在一种情况，02处理正常完成，但是超时了
                # 也应该直接将处理结果返回，因为jy_ls中是交易完成了
                rs_msg = message_body
            else:
                # SYS_YFSDBW的类型必须是bytes
                rs_msg = b"Timeout@SYS_YFSDBW type must be bytes"
    except:
        logger.oes ("ICM 处理出现异常：" ,lv='error',cat = 'app.icm')
    logger.ods ("处理执行结果为：%s %s" %(phase ,str(rs_msg)) ,lv='dev',cat = 'app.icm')
    return rs_msg


if __name__=="__main__":
    jyzd = {'SYS_CSSJ': '60','SYS_JYM': 'lt001','SYS_JSDDBW': b'lt001aaaaaa20150226', 'SYS_CLBZ': '02', 'SYS_TXJBID':'ltdls_tx'}
    print(do_tp_proc('02',jyzd ,sync).decode('utf8'))
