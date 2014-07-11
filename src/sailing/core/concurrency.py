import time
import threading

import logging
class TaskQueue(object):
    #logger = logging.getLogger("task_queue")
    def __init__(self, logger=None):
        self.is_running = True
        self.tasks = {}
        self.running_groups = []
        self.queue_lock = threading.Lock()
        self.conditions = threading.Condition(self.queue_lock)
        self.queue_count = 0
        self.async_group = ['default', ]
        self.group_prority = []
        self.logger = logger or logging.getLogger("task_queue")

    def add_task(self, func, args, group=None):
        self.queue_lock.acquire()

        group = group or 'default'
        queue = self.tasks.setdefault(group, [])
        queue.insert(0, (func, args or ()))
        
        self.queue_count += 1
        
        self.conditions.notify()
        self.queue_lock.release()

    def next_task(self, group=None):
        self.queue_lock.acquire()
        task, args = (None, None)
        
        if group in self.running_groups: #the thread running sync group, can't move to other group.
            queue = self.tasks.setdefault(group, [])
        else:
            group, queue = self._next_prority_group()
            queue = queue or []

        if len(queue) > 0:
            task, args = queue.pop()
        else:
            for gname, queue in self.tasks.iteritems():
                if gname in self.running_groups or len(queue) == 0: continue
                task, args = queue.pop()
                group = gname
                if group not in self.async_group:
                    self.running_groups.append(group)
                break

            if task is None:
                self.conditions.wait()
                group = 'default'
                
        self.queue_count -= 1

        self.queue_lock.release()

        return (task, args, group)
    
    def _next_prority_group(self):
        for e in self.group_prority:
            if e not in self.tasks: continue
            q = self.tasks[e]
            if len(q) == 0: continue
            return e, q
        return (None, None)

    def done_group(self, group=None):
        self.queue_lock.acquire()
        queue = self.tasks[group]

        if group and group in self.running_groups and len(queue) == 0:
            self.logger.debug("task group done '%s'." % group)
            self.running_groups.remove(group)
        self.queue_lock.release()

    def notify_all_worker(self):
        self.queue_lock.acquire()
        self.conditions.notifyAll()
        self.queue_lock.release()

    def queue_size(self, group=None):
        if group is None: 
            return self.queue_count
        else:
            self.queue_lock.acquire()
            queue = self.tasks.setdefault(group, [])
            self.queue_lock.release()
            return len(queue)

    def close(self):
        self.is_running = True
        self.notify_all_worker()

    def running(self): return self.is_running

class Worker(threading.Thread):
    #logger = logging.getLogger("worker")
    def __init__(self, task_queue, name='worker', logger=None):
        threading.Thread.__init__(self)
        self.task_queue = task_queue
        self.is_running = True
        self.setDaemon(True)
        self.setName(name)
        self.group = None
        self.logger = logger or logging.getLogger("worker")

    def run(self):
        self.logger.debug("starting -- %s" % self.getName())
        while self.is_running and self.task_queue.running():
            call_back, args, cur_group = self.task_queue.next_task(self.group)
            if call_back is not None:
                try:
                    self.logger.debug("running -- '%s' for group '%s'" % \
                                      (self.getName(), cur_group))
                    call_back(*args)
                except BaseException, e:
                    self.logger.debug("exception -- %s" % self.getName())
                    self.logger.exception(e)
                finally:
                    self.task_queue.done_group(cur_group)
                    self.group = cur_group
            else:
                time.sleep(0.01)
        self.logger.debug("closed -- %s" % self.getName())

    def close(self):
        self.logger.debug("closing -- %s" % self.getName())
        self.is_running = False
        #wake up thread closed self.
        self.task_queue.notify_all_worker()

class TaskScheduler(object):
    def __init__(self, concurrent_count=3, logger=None):
        self.task_queue = TaskQueue(logger)
        self.worker_list = []
        for i in range(concurrent_count):
            self.worker_list.append(Worker(self.task_queue, "worker_%s" % i, logger))
            self.worker_list[-1].start()

    def add_task(self, func, args=(), group='default'):
        self.task_queue.add_task(func, args, group)

    def concurrent_count(self, count=None):
        if count is not None:
            cur_count = len(self.worker_list)
            if count > cur_count:
                for i in range(cur_count, count):
                    self.worker_list.append(Worker(self.task_queue, "worker_%s" % i))
                    self.worker_list[-1].start()
            else:
                for i in self.worker_list[count: cur_count]:
                    i.close()
                self.worker_list = self.worker_list[:count]

        return len(self.worker_list)
    
    def pending_count(self, group=None):
        return self.task_queue.queue_size(group)
    
    def async_group(self, groups=[]):
        self.task_queue.async_group = groups
        
    def group_prority(self, groups=[]):
        self.task_queue.group_prority = groups

    def close(self):
        for t in self.worker_list: t.close()
        self.task_queue.close()

SCHEDULER = None #TaskScheduler()
def add_task(func, args, group='default'):
    """add concurrent task into task queue, the task is synchronized 
    running in the same group. 
    """
    global SCHEDULER
    if SCHEDULER is None: SCHEDULER = TaskScheduler()
    SCHEDULER.add_task(func, args, group)

def concurrent_count(count=None):
    if SCHEDULER is None: SCHEDULER = TaskScheduler()
    return SCHEDULER.concurrent_count(count)

if __name__ == "__main__":
    #init_loging()
    def task_1(x): print "xx:%s" % x
    
    add_task(task_1, ('ddd', ))
    add_task(task_1, ('eee', ))
    
    time.sleep(2)
    print "done"
