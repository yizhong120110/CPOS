# -*- coding: utf-8 -*-
import multiprocessing as mt
import sys
import os
import threading
import time
import queue
from ..substrate.interfaces import *
from ..substrate.utils.logger import logger, logger_set_root, logger_enable_console
from ..substrate.utils.signal import signal_func

signal_func()


class AutoScaledPool(Monitored):
    __number = 0

    def __init__(self, pool_init_size=1, pool_ceiling_size=20, proc=None, query_counter_ceiling=10):
        self.pool_size = pool_init_size
        self.pool_ceiling_size = pool_ceiling_size
        self.task_queue = mt.Queue()
        self.task_queue_lock = mt.Lock()
        self._processes = []  # [{process:p,cmd_queue:q,status_queue,last_status:s}]
        self._pguard = threading.RLock()
        self.__class__.__number += 1
        self.proc = proc

        self.query_counter = 0  # timer to reduce the pool size.
        self.query_counter_ceiling = query_counter_ceiling

        self.spawn_process(self.pool_size)

    def get_queued_task_count(self):
        if 'win' in sys.platform:
            # both windows and mac os
            return 0
        return self.task_queue.qsize()

    def _set_queue_message(self, q, s):
        q.put(s)

    def _get_queue_message(self, q):
        message = 'unknow'
        try:
            message = q.get_nowait()
        except queue.Empty as e:
            return message
        return message

    def _pooled_proc(self, task_queue, task_queue_lock, cmd_queue, status_queue):
        while True:
            self._set_queue_message(status_queue, 'free')
            cmd = self._get_queue_message(cmd_queue)
            if cmd == '@close':
                logger.ods('tpool_pooled_proc[%s]:@closed' % str(os.getpid()), lv='info', cat='foundation.tpool')
                break
            try:
                task_queue_lock.acquire()
                task = task_queue.get_nowait()  # wait
            except queue.Empty as e:
                time.sleep(0.01)
                continue
            finally:
                task_queue_lock.release()
            self._set_queue_message(status_queue, 'working')
            logger.ods('tpool_pooled_proc[%s]:working' % str(os.getpid()), lv='info', cat='foundation.tpool')

            try:
                self.proc(task)
            except Exception as e:
                logger.oes('tpool_pooled_proc[%s] proc(task) error:' % (str(os.getpid())), lv='warning', cat='foundation.tpool')

        self._set_queue_message(status_queue, 'closed')
        return 0

    def update_status(self):
        for p in self._processes:
            status = None
            while status != 'unknow':
                status = self._get_queue_message(p['status_queue'])
                if status != 'unknow':
                    p['status'] = status

        if_do_clean = True
        while if_do_clean:
            for p in self._processes:
                if p['status'] == 'closed':
                    p['cmd_queue'].close()
                    p['cmd_queue'].join_thread()
                    p['status_queue'].close()
                    p['status_queue'].join_thread()
                    self._processes.remove(p)
                    if_do_clean = True
                    break
                else:
                    if_do_clean = False

    def count_free_process(self):
        self.update_status()
        cnt = 0
        for p in self._processes:
            if p['status'] == 'free':
                cnt += 1
        return cnt

    def get_free_process(self):
        self.update_status()
        for p in self._processes:
            if p['status'] == 'free':
                return p

    def count_total_process(self):
        return len(self._processes)

    def shrink_pool(self):
        fp = self.get_free_process()
        if fp:
            self._set_queue_message(fp['cmd_queue'], '@close')
            # fp['process'].join()

    def add_task(self, task_parameter):
        self.update_status()
        fp_count = self.count_free_process()

        logger.ods('New task adding to AutoScaledPool. (fp:%d / tp:%d task:%s).'
                   % (fp_count, self.count_total_process(), task_parameter),
                   lv='dev', cat='foundation.tpool')

        if self.query_counter >= self.query_counter_ceiling:
            if self.count_total_process() > self.pool_size:
                self.shrink_pool()
            logger.ods('Shrunk AutoScaledPool. (%d).'
                       % (self.count_total_process()),
                       lv='info', cat='foundation.tpool')
            logger.ods('total_process: %s' % (str(self._processes)), lv='dev', cat='foundation.tpool')
            self.query_counter = 0

        if fp_count >= int(self.count_total_process() * 0.5) and\
                fp_count > 1:  # despawn count
            self.query_counter += 1

        # y = 1.4 * X + 1
        if fp_count == 0 and self.count_total_process() < self.pool_ceiling_size:  # spawn
            new_pool_size = int(self.count_total_process() * 1.4) + 1
            if new_pool_size >= self.pool_ceiling_size:
                new_pool_size = self.pool_ceiling_size
            logger.ods('Enlarge AutoScaledPool (%d -> %d).'
                       % (self.count_total_process(), new_pool_size),
                       lv='info', cat='foundation.tpool')
            self.spawn_process(new_pool_size)
            self.query_counter = 0
        try:
            try:
                task_parameter['peer'].sock.get_inheritable()
            except:
                task_parameter['peer'] = None
            logger.ods('before task_queue put', lv='info', cat='foundation.tpool')
            self.task_queue.put(task_parameter)
        except Exception as e:
            logger.ods('Adding task to task_queue failed!',
                       lv='info', cat='foundation.tpool')
        logger.ods('task_queue size after add_task (%d) (fp:%d / tp:%d)' % (
            self.get_queued_task_count(), fp_count, self.count_total_process()),
            lv='info', cat='foundation.tpool')

    def spawn_process(self, pool_size):
        with self._pguard:
            if len(self._processes) >= pool_size:
                # poolsize is already exceeded the new size . no need to spawn any new connection.

                logger.ods('poolsize is already exceeded(or equal to) the new size .'
                           'no need to spawn any new process.',
                           lv='warning', cat='foundation.tpool')
                return

            logger.ods('poolsize exceeded to the new size %d -> %d' % (len(self._processes), pool_size),
                       lv='info', cat='foundation.tpool')
            ori_pool_size = len(self._processes)
            self.setname('#'.join(['AutoScaledPool', str(pool_size),
                                   str(self.__class__.__number)]))

            for i in range(ori_pool_size, pool_size):
                cmd_queue = mt.Queue()
                cmd_queue.put('@init')
                status_queue = mt.Queue()
                # @init->free|working->@close->closed
                # p = Process(target=self._pooled_proc,
                #    args=(self.task_queue,cmd_queue,status_queue),daemon=True)
                p = mt.Process(target=self._pooled_proc,
                               args=(self.task_queue, self.task_queue_lock, cmd_queue, status_queue), daemon=True)

                self._processes.append({'process': p, 'status_queue': status_queue,
                                        'cmd_queue': cmd_queue, 'status': '@init'})
                p.start()


#####################################################
def test_proc_enlarge(p):
    time.sleep(10)
    print('>>>>>>>>>' + str(p))


def test_auto_enlarge():
    ap = AutoScaledPool(1, 40, test_proc_enlarge)
    for i in range(100000):
        # time.sleep(0.01)
        if ap.get_queued_task_count() > 100:  # only works on LINUX!!!!
            print('queued task size ' + str( ap.get_queued_task_count()))
            print("Workload is too heavy~! , refuse request.")
            ####
            time.sleep(1)
        time.sleep(0.2)
        ap.add_task({'job': 100})
        # break;
    time.sleep(100)

#######################################################


def test_proc_shrink(p):
    time.sleep(0.4)
    print("run test_proc_shrink")


def test_auto_shrink():
    ap = AutoScaledPool(20, 40, test_proc_shrink)
    for i in range(100000):
        # time.sleep(0.01)
        if ap.get_queued_task_count() > 100:    # only works on LINUX!!!!
            print('queued task size ' + str( ap.get_queued_task_count()))
            print("Workload is too heavy~! , refuse request.")
            ####
            time.sleep(1)
        time.sleep(0.1)
        ap.add_task({'job': 100})
        # break;
    time.sleep(100)

if __name__ == '__main__':

    logger.level('dev')

    # test_auto_enlarge()
    test_auto_shrink()


# Performance test! 70-sized python processes-pool takes 5% - 7% CPU time.
'''
['EX_CANTCREAT', 'EX_CONFIG', 'EX_DATAERR', 'EX_IOERR', 'EX_NOHOST', 'EX_NOINPUT', 'EX_NOPERM', 'EX_NOUSER', 'EX_OK', 'EX_OSERR', 'EX_OSFILE', 'EX_PROTOCOL', 'EX_SOFTWARE', 'EX_TEMPFAIL', 'EX_UNAVAILABLE', 'EX_USAGE', 'F_OK', 'NGROUPS_MAX', 'O_APPEND', 'O_ASYNC', 'O_CREAT', 'O_DIRECTORY', 'O_DSYNC', 'O_EXCL', 'O_EXLOCK', 'O_NDELAY', 'O_NOCTTY', 'O_NOFOLLOW', 'O_NONBLOCK', 'O_RDONLY', 'O_RDWR', 'O_SHLOCK', 'O_SYNC', 'O_TRUNC', 'O_WRONLY', 'P_NOWAIT', 'P_NOWAITO', 'P_WAIT', 'R_OK', 'SEEK_CUR', 'SEEK_END', 'SEEK_SET', 'TMP_MAX', 'UserDict', 'WCONTINUED', 'WCOREDUMP', 'WEXITSTATUS', 'WIFCONTINUED', 'WIFEXITED', 'WIFSIGNALED', 'WIFSTOPPED', 'WNOHANG', 'WSTOPSIG', 'WTERMSIG', 'WUNTRACED', 'W_OK', 'X_OK', '_Environ', '__all__', '__builtins__', '__doc__', '__file__', '__name__', '__package__', '_copy_reg', '_execvpe', '_exists', '_exit', '_get_exports_list', '_make_stat_result', '_make_statvfs_result', '_pickle_stat_result', '_pickle_statvfs_result', '_spawnvef', 'abort', 'access', 'altsep', 'chdir', 'chflags', 'chmod', 'chown', 'chroot', 'close', 'closerange', 'confstr', 'confstr_names', 'ctermid', 'curdir', 'defpath', 'devnull', 'dup', 'dup2', 'environ', 'errno', 'error', 'execl', 'execlProcesses: 315 total, 3 running, 8 stuck, 304 sleeping, 1208 threads   11:25:29
Load Avg: 1.98, 1.94, 1.94  CPU usage: 6.22% user, 7.41% sys, 86.36% idle
SharedLibs: 16M resident, 9060K data, 0B linkedit.
MemRegions: 58190 total, 1965M resident, 83M private, 1496M shared.
PhysMem: 8061M used (3174M wired), 130M unused.
VM: 784G vsize, 1066M framework vsize, 33755(0) swapins, 39195(0) swapouts.
Networks: packets: 4168451/1318M in, 2157783/313M out.
Disks: 1661002/41G read, 2497756/101G written.

PID    COMMAND      %CPU      TIME     #TH    #WQ  #PORT MEM    PURG   CMPRS
73870  Python       0.0       00:00.01 2      0    8     3944K  0B     0B
73869  Python       0.0       00:00.02 2      0    8     3944K  0B     0B
73868  Python       0.0       00:00.01 2      0    8     3928K  0B     0B
73867  Python       0.0       00:00.01 2      0    8     3932K  0B     0B
73866  Python       0.0       00:00.02 2      0    8     3896K  0B     0B
73865  Python       0.0       00:00.01 2      0    8     3892K  0B     0B
73864  Python       0.0       00:00.02 2      0    8     3836K  0B     0B
73863  Python       0.0       00:00.02 2      0    8     3816K  0B     0B
73862  Python       0.0       00:00.01 2      0    8     3776K  0B     0B
73861  Python       0.0       00:00.01 2      0    8     3760K  0B     0B
73860  Python       0.0       00:00.02 2      0    8     3756K  0B     0B
73859  Python       0.0       00:00.01 2      0    8     3720K  0B     0B
73858  Python       0.0       00:00.02 2      0    8     3688K  0B     0B
73857  Python       0.0       00:00.01 2      0    8     3660K  0B     0B
73856  Python       0.0       00:00.01 2      0    8     3616K  0B     0B

'''
