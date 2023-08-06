from concurrent.futures import ProcessPoolExecutor, Future
from infiniguard_api.lib.logging import iguard_logging
from threading import Thread
from time import sleep, time
from sqlalchemy.dialects import sqlite
from sqlalchemy.orm import scoped_session
from queue import Empty
from multiprocessing import Queue
import signal
import sys
from typing import List
from types import SimpleNamespace
from datetime import datetime


log = iguard_logging.get_logger(__name__)

run = True
threads = list()


def signal_handler(sig, frame):
    log.info('Got signal {}'.format(sig))
    global run
    run = False
    for thread in threads:
        try:
            thread.join()
        except Exception:
            pass
    sys.exit()


class MyPriorityQueue(object):
    def __init__(self, levels=2):
        self._q = list()
        self.levels = levels
        for i in range(0, levels):
            self._q.append(Queue())

    def put(self, level, data):
        self._q[level].put(data, timeout=1)

    def get(self):
        while run:
            for level in range(0, self.levels):
                try:
                    if self._q[level].qsize() > 0:
                        return self._q[level].get()
                except NotImplementedError:
                    # Mac OS does not implement qsize for mutliprocessing queue
                    # Linux, on the other side, is not working well with empty()
                    if not self._q[level].empty():
                        return self._q[level].get()
            sleep(0.01)

    def stats(self):
        return [self._q[a].qsize() for a in range(0, self.levels)]


q = Queue()
pq = MyPriorityQueue(3)
resultq = Queue()

def worker():
    def remove_old(futures_list: List[Future]):
        for ftr in futures_list:
            if ftr.done():
                exc = ftr.exception()
                if exc:
                    log.error('Process finished with error: {}'.format(exc))
                futures_list.remove(ftr)

    executor = ProcessPoolExecutor(max_workers=4)
    futures = list()

    while run:
        try:
            try:
                item = q.get(timeout=1)
            except Empty:
                remove_old(futures)
                item = None
            if item is not None:
                try:
                    task, args, kwargs = item
                    future = executor.submit(task, *args, **kwargs)
                    futures.append(future)
                except Exception as e:
                    log.error('WORKER error {}'.format(e))
        except Exception as e:
            log.error('WORKER error {}'.format(e))

    log.info('Shutting down worker')
    for future in futures:
        future.cancel()
    executor.shutdown()
    log.info('Worker done')


def log_long_running_sql(elapsed, args):
    log.warn('sqlalchemy_worker took {:.2f} sec'.format(elapsed))
    log.warn('{}'.format(args))


def sqlalchemy_worker(session: scoped_session):
    while run:
        statement = pq.get()
        if statement is not None:
            try:
                start = time()
                s = session()
                if str(statement).startswith("SELECT"):
                    res = s.execute(statement)
                    # convert resulting tuple into dict
                    res_dict = [dict(zip(res.keys(), a)) for a in res]
                    # Convert datetime columns from string to datetime
                    for item in res_dict:
                        for key in ['start', 'end']:
                            if item.get(key):
                                item[key] = datetime.strptime(
                                    item[key], '%Y-%m-%d %H:%M:%S.%f')
                    # Convert resulting dicts to namespace
                    res_ns = [SimpleNamespace(**a) for a in res_dict]
                    # Put back into result queue
                    resultq.put(res_ns)
                else:
                    with s.begin():
                        s.execute(statement)
                elapsed = time() - start
                if elapsed > 1:  # Log everything that longer than a second
                    log_long_running_sql(elapsed, statement)
            except Exception as e:
                log.error('sqlalchemy_worker {}'.format(e))
    log.info('sqlalchemy_worker done')


def start_worker(session: scoped_session):
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    worker_thread = Thread(target=worker, daemon=True)
    worker_thread.start()
    threads.append(worker_thread)
    sqlalchemy_thread = Thread(target=sqlalchemy_worker, args=[
                               session], daemon=True)
    sqlalchemy_thread.start()
    threads.append(sqlalchemy_thread)


def submit_task(task, *args, **kwargs):
    try:
        log.info('Adding task {}({})'.format(task.__name__, args))
        q.put((task, args, kwargs), timeout=1)
    except Exception as e:
        log.error('submit_task error {} {} {} {}'.format(
            e, task, args, kwargs))


def submit_sql(statement, priority=1):
    try:
        compiled = statement.compile(dialect=sqlite.dialect(
            paramstyle="named"), compile_kwargs={"literal_binds": True})
        pq.put(priority, str(compiled))
    except Exception as e:
        log.error('submit_sql error {} {}'.format(e, statement))
