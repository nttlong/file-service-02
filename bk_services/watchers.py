import sys
import threading
import time
import logging
from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler, FileCreatedEvent

import os


class Info:
    def __init__(self):
        self.full_path: str = None
        self.rel_path: str = None
        self.root_path: str = None


class Watcher(LoggingEventHandler):
    def __init__(self, watch_path):
        LoggingEventHandler.__init__(self)
        self.run = None
        self.watch_path = watch_path

    def on_created(self, event: FileCreatedEvent):
        if not event.is_directory:
            info = Info()
            info.rel_path = os.path.relpath(event.src_path, self.watch_path)
            info.full_path = event.src_path
            info.root_path = self.watch_path

            if info.rel_path.split(os.sep).__len__() == 1:
                if callable(self.run):
                    def runner(info):
                        self.run(info)
                    th =threading.Thread(target=runner,args=(info,))
                    th.start()






def __all_files__(p):
    if not os.path.isdir(p):
        os.makedirs(p)
    ret = []
    dirs=list(os.walk(p))
    dirpath, dirnames, filenames = dirs[0]
    print(filenames)
    for x in filenames:
        ret+=[os.path.join(p,x)]



    return ret



def start(watch_path, handler):
    event_handler = Watcher(watch_path)
    event_handler.run = handler
    logs_file = os.path.join(watch_path, "data.txt")
    files = __all_files__(watch_path)
    def thread_running(h,d):

        th=threading.Thread(target=h,args=(d,))
        th.start()
    for f in files:
        try:
            info = Info()
            info.rel_path = os.path.relpath(f, watch_path)
            info.full_path = f
            info.root_path = watch_path
            thread_running(handler,info)
        except Exception as e:
            print(e)



    observer = Observer()
    observer.schedule(event_handler, watch_path, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

def start_thead(watch_path, handler):
    th=threading.Thread(target=start,args=(watch_path,handler,))
    th.start()
    # th.join()